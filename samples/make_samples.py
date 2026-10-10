import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def door(w=1600, h=1200, color=(28, 72, 140), seed=1):
    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), color)
    d = ImageDraw.Draw(img)
    step = 70
    for x in range(0, w, step):
        shade = tuple(max(0, c - 18) for c in color)
        d.rectangle([x + step // 2, 0, x + step - 1, h], fill=shade)
        d.line([x + step // 2, 0, x + step // 2, h], fill=tuple(min(255, c + 25) for c in color), width=3)
    for _ in range(4000):
        x, y = rng.randrange(w), rng.randrange(h)
        d.point((x, y), fill=tuple(min(255, c + rng.randrange(-30, 30)) for c in color))
    d.rectangle([0, 0, w - 1, 40], fill=(20, 20, 24))
    d.rectangle([w // 2 - 6, 40, w // 2 + 6, h], fill=(18, 40, 80))
    return img


def number(d, x, y, owner, serial, cd, size=96):
    f = font(size)
    d.text((x, y), owner, font=f, fill="white")
    x2 = x + d.textlength(owner + " ", font=f)
    d.text((x2, y), serial, font=f, fill="white")
    x3 = x2 + d.textlength(serial + " ", font=f)
    d.text((x3, y), cd, font=f, fill="white")
    cw = d.textlength(cd, font=f)
    top, bottom = y + size * 0.12, y + size * 1.12
    d.rectangle([x3 - 14, top - 8, x3 + cw + 14, bottom + 6], outline="white", width=7)


def small(d, x, y, lines, size=34):
    f = font(size)
    for i, line in enumerate(lines):
        d.text((x, y + i * size * 1.35), line, font=f, fill="white")


def save(img, name):
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    path = os.path.join(HERE, name)
    img.save(path, quality=88)
    print("saved", path)


def main():
    img = door()
    d = ImageDraw.Draw(img)
    number(d, 640, 120, "CSQU", "305438", "3")
    d.text((640, 250), "45G1", font=font(78), fill="white")
    small(d, 860, 900, ["MAX. GROSS  30,480 KG", "TARE          3,840 KG", "NET           26,640 KG"])
    save(img, "door_valid.jpg")

    img = door(color=(150, 30, 34), seed=2)
    d = ImageDraw.Draw(img)
    number(d, 120, 140, "MSCU", "123456", "0")
    d.text((120, 270), "22G1", font=font(78), fill="white")
    small(d, 120, 900, ["MAX. GROSS  30,480 KG", "TARE          2,200 KG"])
    save(img, "door_invalid.jpg")

    img = door(w=900, h=1700, color=(40, 110, 70), seed=3)
    d = ImageDraw.Draw(img)
    f = font(84)
    for i, ch in enumerate("CSQU305438"):
        d.text((380, 90 + i * 128), ch, font=f, fill="white")
    d.rectangle([362, 90 + 10 * 128 + 4, 452, 90 + 10 * 128 + 112], outline="white", width=6)
    d.text((380, 90 + 10 * 128), "3", font=f, fill="white")
    save(img, "door_vertical.jpg")


if __name__ == "__main__":
    main()
