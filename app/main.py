from __future__ import annotations

import logging
import os
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, File, HTTPException, Query, Security, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.security import APIKeyHeader, APIKeyQuery

from . import images
from .iso6346 import analyze
from .ocr import OcrError, OcrResult

log = logging.getLogger("container-ocr")
STATIC = Path(__file__).parent / "static"
VERSION = "1.0.0"

DESCRIPTION = """Фото контейнера -> Cloud Vision OCR -> номер за ISO 6346 з перевіркою контрольної цифри.
Якщо задано API_KEY, ключ передається в заголовку X-API-Key."""


class Settings:
    def __init__(self):
        self.api_key = os.getenv("API_KEY", "")
        self.store = os.getenv("STORE", "memory").lower()
        self.bucket = os.getenv("GCS_BUCKET") or None
        self.collection = os.getenv("FIRESTORE_COLLECTION", "scans")
        self.database = os.getenv("FIRESTORE_DATABASE") or None
        self.max_upload = int(float(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024)


def create_app(ocr=None, store=None, settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="Container OCR API", version=VERSION, description=DESCRIPTION)
    app.state.settings = settings
    app.state.ocr = ocr
    app.state.store = store

    def get_ocr():
        if app.state.ocr is None:
            from .ocr import VisionOcr
            app.state.ocr = VisionOcr()
        return app.state.ocr

    def get_store():
        if app.state.store is None:
            if settings.store == "gcp":
                from .store import GcpStore
                app.state.store = GcpStore(settings.collection, settings.bucket, settings.database)
            else:
                from .store import MemoryStore
                app.state.store = MemoryStore()
        return app.state.store

    key_header = APIKeyHeader(name="X-API-Key", auto_error=False,
                              description="API-ключ сервісу (змінна API_KEY)")
    key_query = APIKeyQuery(name="key", auto_error=False,
                            description="Те саме в URL - для <img src=...>")

    def require_key(header: str | None = Security(key_header), query: str | None = Security(key_query)):
        if not settings.api_key:
            return
        given = header or query or ""
        if not secrets.compare_digest(given.encode(), settings.api_key.encode()):
            raise HTTPException(401, "Потрібен правильний API-ключ (заголовок X-API-Key).")


    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/healthz", include_in_schema=False)
    def healthz():
        return {"status": "ok"}

    @app.get("/api/info", tags=["service"], summary="Інформація про сервіс")
    def info():
        return {"version": VERSION, "auth_required": bool(settings.api_key),
                "store": settings.store, "image_storage": bool(settings.bucket) or settings.store == "memory",
                "ocr": "google-cloud-vision", "max_upload_mb": settings.max_upload // (1024 * 1024)}


    @app.post("/api/scan", tags=["scan"], summary="Розпізнати номер контейнера на фото",
              dependencies=[Depends(require_key)])
    def scan(
        file: UploadFile = File(..., description="Фото контейнера (JPEG, PNG, WebP...)"),
        mode: Literal["text", "document"] = Query(
            "text", description="text = TEXT_DETECTION, document = DOCUMENT_TEXT_DETECTION"),
        save: bool = Query(True, description="Зберегти результат в історію"),
    ):
        started = time.perf_counter()
        data = file.file.read(settings.max_upload + 1)
        if not data:
            raise HTTPException(400, "Порожній файл.")
        if len(data) > settings.max_upload:
            raise HTTPException(413, "Файл завеликий (максимум %d МБ)."
                                % (settings.max_upload // (1024 * 1024)))
        try:
            prepared = images.prepare(data)
        except images.BadImage as e:
            raise HTTPException(415, str(e))
        t_prepare = time.perf_counter()

        try:
            result: OcrResult = get_ocr().detect(prepared.content, mode=mode)
        except OcrError as e:
            raise HTTPException(502, "Vision API повернув помилку: %s" % e)
        except Exception as e:
            log.exception("Vision API call failed")
            raise HTTPException(502, "Не вдалося викликати Vision API: %s" % e)
        t_ocr = time.perf_counter()

        analysis = analyze(result.tokens, result.text)
        now = datetime.now(timezone.utc)
        record = {
            "id": now.strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(3),
            "created_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "filename": (file.filename or "")[:200],
            "ocr_mode": mode,
            "ocr_engine": result.engine,
            **analysis,
            "image": {"width": prepared.width, "height": prepared.height},
            "text": result.text[:5000],
            "timings_ms": {
                "prepare": round((t_prepare - started) * 1000),
                "ocr": round((t_ocr - t_prepare) * 1000),
            },
            "stored": False,
            "image_stored": False,
        }
        record["timings_ms"]["total"] = round((time.perf_counter() - started) * 1000)
        if save:
            store = get_store()

            record["stored"] = True
            record["image_stored"] = store.stores_images
            t_save = time.perf_counter()
            try:
                store.save(record, prepared.content, prepared.thumb)
            except Exception as e:
                log.exception("Saving scan failed")
                record["stored"] = record["image_stored"] = False
                record["store_error"] = str(e)[:300]
            record["timings_ms"]["save"] = round((time.perf_counter() - t_save) * 1000)
        log.info("scan %s status=%s number=%s ocr=%dms", record["id"], record["status"],
                 (record["container"] or {}).get("number"), record["timings_ms"]["ocr"])
        return record

    @app.get("/api/scans", tags=["history"], summary="Останні сканування",
             dependencies=[Depends(require_key)])
    def list_scans(limit: int = Query(20, ge=1, le=100)):
        return {"items": get_store().list(limit)}

    @app.get("/api/scans/{scan_id}", tags=["history"], summary="Одне сканування",
             dependencies=[Depends(require_key)])
    def get_scan(scan_id: str):
        record = get_store().get(scan_id)
        if record is None:
            raise HTTPException(404, "Сканування не знайдено.")
        return record

    @app.get("/api/scans/{scan_id}/image", tags=["history"], summary="Фото сканування",
             dependencies=[Depends(require_key)],
             responses={200: {"content": {"image/jpeg": {}}}})
    def get_image(scan_id: str, thumb: bool = False):
        data = get_store().image(scan_id, thumb=thumb)
        if data is None:
            raise HTTPException(404, "Фото не збережено.")
        return Response(data, media_type="image/jpeg",
                        headers={"Cache-Control": "private, max-age=86400"})

    return app


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
app = create_app()
