from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_SIDE = 2400
THUMB_SIDE = 360


class BadImage(ValueError):
    pass


@dataclass
class PreparedImage:
    content: bytes
    thumb: bytes
    width: int
    height: int


def _jpeg(img: Image.Image, quality: int) -> bytes:
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def prepare(data: bytes) -> PreparedImage:
    try:
        img = Image.open(BytesIO(data))


        img.draft("RGB", (MAX_SIDE, MAX_SIDE))
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
    except Image.DecompressionBombError as e:
        raise BadImage("Зображення завелике (забагато пікселів).") from e
    except (UnidentifiedImageError, OSError) as e:
        raise BadImage("Не вдалося відкрити зображення. Підтримуються JPEG, PNG, WebP, BMP, GIF.") from e
    if max(img.size) > MAX_SIDE:
        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    thumb = img.copy()
    thumb.thumbnail((THUMB_SIDE, THUMB_SIDE), Image.LANCZOS)
    return PreparedImage(content=_jpeg(img, 90), thumb=_jpeg(thumb, 80),
                         width=img.width, height=img.height)
