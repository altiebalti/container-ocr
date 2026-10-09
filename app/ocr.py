"""Розпізнавання тексту через Google Cloud Vision API."""
from __future__ import annotations

from dataclasses import dataclass, field

from .iso6346 import Token

MODES = {
    # TEXT_DETECTION - для окремих написів на фото (вивіски, маркування контейнерів)
    "text": "TEXT_DETECTION",
    # DOCUMENT_TEXT_DETECTION - для щільного тексту (документи, накладні)
    "document": "DOCUMENT_TEXT_DETECTION",
}


class OcrError(Exception):
    pass


@dataclass
class OcrResult:
    text: str
    tokens: list[Token] = field(default_factory=list)
    engine: str = "google-cloud-vision"


def _box(poly) -> list[int] | None:
    xs = [v.x for v in poly.vertices]
    ys = [v.y for v in poly.vertices]
    if not xs:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


class VisionOcr:
    """Обгортка над vision.ImageAnnotatorClient.

    Автентифікація - Application Default Credentials: на Cloud Run це сервісний акаунт
    сервісу, локально - `gcloud auth application-default login`.
    """

    def __init__(self, language_hints: tuple[str, ...] = ("en",), timeout: float = 30.0):
        from google.cloud import vision   # імпорт тут, щоб тести не потребували бібліотеки

        self._vision = vision
        self.client = vision.ImageAnnotatorClient()
        self.language_hints = list(language_hints)
        self.timeout = timeout

    def detect(self, content: bytes, mode: str = "text") -> OcrResult:
        vision = self._vision
        image = vision.Image(content=content)
        context = {"language_hints": self.language_hints}
        if MODES.get(mode) == "DOCUMENT_TEXT_DETECTION":
            response = self.client.document_text_detection(
                image=image, image_context=context, timeout=self.timeout)
        else:
            response = self.client.text_detection(
                image=image, image_context=context, timeout=self.timeout)
        if response.error.message:
            raise OcrError(response.error.message)

        annotations = response.text_annotations
        if not annotations:
            return OcrResult(text="")
        # перша анотація - увесь текст, далі - окремі слова з координатами
        return OcrResult(
            text=annotations[0].description,
            tokens=[Token(a.description, _box(a.bounding_poly)) for a in annotations[1:]],
        )
