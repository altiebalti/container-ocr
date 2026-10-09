from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.iso6346 import Token
from app.main import Settings, create_app
from app.ocr import OcrError, OcrResult
from app.store import MemoryStore


class FakeOcr:

    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def detect(self, content, mode="text"):
        self.calls.append((len(content), mode))
        if self.error:
            raise self.error
        return self.result


def jpeg(w=800, h=600, exif_rotate=False):
    img = Image.new("RGB", (w, h), (40, 80, 160))
    buf = BytesIO()
    if exif_rotate:
        exif = Image.Exif()
        exif[0x0112] = 6
        img.save(buf, "JPEG", exif=exif)
    else:
        img.save(buf, "JPEG")
    return buf.getvalue()


SAMPLE = OcrResult(
    text="CSQU 305438 3\n45G1\nMAX GROSS 30480 KG",
    tokens=[Token("CSQU", [100, 50, 200, 90]), Token("305438", [210, 50, 380, 90]),
            Token("3", [395, 48, 420, 92]), Token("45G1", [100, 110, 190, 140]),
            Token("MAX", [100, 400, 140, 420]), Token("GROSS", [150, 400, 220, 420]),
            Token("30480", [230, 400, 300, 420]), Token("KG", [310, 400, 340, 420])],
)


def make_client(ocr=None, api_key="", store=None):
    settings = Settings()
    settings.api_key = api_key
    settings.store = "memory"
    app = create_app(ocr=ocr or FakeOcr(SAMPLE), store=store or MemoryStore(), settings=settings)
    return TestClient(app)


def upload(client, data=None, **params):
    return client.post("/api/scan", params=params,
                       files={"file": ("photo.jpg", data or jpeg(), "image/jpeg")})


def test_scan_finds_number_and_stores_history():
    client = make_client()
    r = upload(client)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "valid"
    assert body["container"]["formatted"] == "CSQU 305438 3"
    assert body["container"]["box"] == [100, 48, 420, 92]
    assert body["size_type"]["code"] == "45G1"
    assert body["image"] == {"width": 800, "height": 600}
    assert body["stored"] and body["image_stored"]

    items = client.get("/api/scans").json()["items"]
    assert [i["id"] for i in items] == [body["id"]]

    assert items[0]["stored"] is True and items[0]["image_stored"] is True
    assert client.get("/api/scans/%s" % body["id"]).json()["container"]["number"] == "CSQU3054383"
    img = client.get("/api/scans/%s/image" % body["id"], params={"thumb": 1})
    assert img.status_code == 200 and img.headers["content-type"] == "image/jpeg"
    assert max(Image.open(BytesIO(img.content)).size) <= 360


def test_exif_orientation_is_applied_before_ocr():
    client = make_client()
    body = upload(client, jpeg(800, 600, exif_rotate=True)).json()
    assert body["image"] == {"width": 600, "height": 800}


def test_large_image_is_downscaled():
    ocr = FakeOcr(SAMPLE)
    client = make_client(ocr)
    body = upload(client, jpeg(4000, 3000)).json()
    assert body["image"] == {"width": 2400, "height": 1800}


def test_mode_is_passed_to_ocr():
    ocr = FakeOcr(SAMPLE)
    client = make_client(ocr)
    upload(client, mode="document")
    assert ocr.calls[-1][1] == "document"


def test_save_false_skips_history():
    client = make_client()
    body = upload(client, save="false").json()
    assert body["stored"] is False
    assert client.get("/api/scans").json()["items"] == []


def test_not_found():
    client = make_client(FakeOcr(OcrResult(text="HELLO WORLD", tokens=[Token("HELLO"), Token("WORLD")])))
    body = upload(client).json()
    assert body["status"] == "not_found" and body["container"] is None


def test_empty_ocr_result():
    client = make_client(FakeOcr(OcrResult(text="")))
    assert upload(client).json()["status"] == "not_found"


def test_bad_image():
    r = upload(make_client(), b"definitely not an image")
    assert r.status_code == 415


def test_too_large():
    client = make_client()
    client.app.state.settings.max_upload = 1000
    assert upload(client).status_code == 413


def test_vision_error_is_reported():
    client = make_client(FakeOcr(error=OcrError("Bad image data")))
    r = upload(client)
    assert r.status_code == 502 and "Bad image data" in r.json()["detail"]


def test_store_failure_does_not_break_scan():
    class BrokenStore(MemoryStore):
        def save(self, *a, **k):
            raise RuntimeError("firestore unavailable")

    body = upload(make_client(store=BrokenStore())).json()
    assert body["status"] == "valid" and body["stored"] is False
    assert "firestore unavailable" in body["store_error"]


@pytest.mark.parametrize("path", ["/api/scans", "/api/scans/x", "/api/scans/x/image"])
def test_api_key_required(path):
    client = make_client(api_key="s3cret")
    assert upload(client).status_code == 401
    assert client.get(path).status_code == 401
    ok = client.post("/api/scan", headers={"X-API-Key": "s3cret"},
                     files={"file": ("p.jpg", jpeg(), "image/jpeg")})
    assert ok.status_code == 200
    assert client.get("/api/scans", params={"key": "s3cret"}).status_code == 200


def test_public_pages():
    client = make_client(api_key="s3cret")
    assert client.get("/").status_code == 200
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/api/info").json()["auth_required"] is True
    schema = client.get("/openapi.json").json()
    assert "/api/scan" in schema["paths"]
    assert "APIKeyHeader" in schema["components"]["securitySchemes"]
