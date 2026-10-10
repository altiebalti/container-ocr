import pytest

vision = pytest.importorskip("google.cloud.vision")
from google.auth.credentials import AnonymousCredentials

from app.ocr import OcrError, VisionOcr


def word(text, x0, y0, x1, y1):
    return vision.EntityAnnotation(
        description=text,
        bounding_poly=vision.BoundingPoly(vertices=[
            vision.Vertex(x=x0, y=y0), vision.Vertex(x=x1, y=y0),
            vision.Vertex(x=x1, y=y1), vision.Vertex(x=x0, y=y1)]))


def make_ocr(monkeypatch, response):
    captured = {}
    client = vision.ImageAnnotatorClient(credentials=AnonymousCredentials())

    def fake_batch(requests, retry=None, timeout=None, metadata=()):
        captured["requests"] = [vision.AnnotateImageRequest(r) if isinstance(r, dict) else r
                                for r in requests]
        captured["timeout"] = timeout
        return vision.BatchAnnotateImagesResponse(responses=[response])

    monkeypatch.setattr(client, "batch_annotate_images", fake_batch)
    ocr = VisionOcr.__new__(VisionOcr)
    ocr._vision = vision
    ocr.client = client
    ocr.language_hints = ["en"]
    ocr.timeout = 30
    return ocr, captured


def test_parses_text_and_word_boxes(monkeypatch):
    response = vision.AnnotateImageResponse(text_annotations=[
        vision.EntityAnnotation(description="CSQU 305438 3\n45G1"),
        word("CSQU", 10, 20, 60, 40), word("305438", 70, 20, 150, 40), word("3", 160, 18, 170, 42),
        word("45G1", 10, 50, 60, 70),
    ])
    ocr, captured = make_ocr(monkeypatch, response)
    result = ocr.detect(b"jpeg-bytes", mode="text")

    assert result.text.startswith("CSQU")
    assert [t.text for t in result.tokens] == ["CSQU", "305438", "3", "45G1"]
    assert result.tokens[2].box == [160, 18, 170, 42]
    request = captured["requests"][0]
    assert request.features[0].type_ == vision.Feature.Type.TEXT_DETECTION
    assert list(request.image_context.language_hints) == ["en"]
    assert request.image.content == b"jpeg-bytes"
    assert captured["timeout"] == 30


def test_document_mode(monkeypatch):
    ocr, captured = make_ocr(monkeypatch, vision.AnnotateImageResponse())
    result = ocr.detect(b"x", mode="document")
    assert result.text == "" and result.tokens == []
    assert captured["requests"][0].features[0].type_ == vision.Feature.Type.DOCUMENT_TEXT_DETECTION


def test_error_in_response(monkeypatch):
    response = vision.AnnotateImageResponse(error={"code": 3, "message": "Bad image data."})
    ocr, _ = make_ocr(monkeypatch, response)
    with pytest.raises(OcrError, match="Bad image data"):
        ocr.detect(b"x")
