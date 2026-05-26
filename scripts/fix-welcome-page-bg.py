#!/usr/bin/env python3
"""Remove callout 2 from welcome-page-bg.png (site background only, not banners)."""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "welcome-page-bg.png"


def is_accent(r: int, g: int, b: int) -> bool:
    return (r > 100 and b > 150 and g < 130) or (r > 130 and b > 200 and g < 100)


def sample_lavender(px, x: int, y: int) -> tuple[int, int, int]:
    for xx in range(x - 1, max(0, x - 280), -1):
        r, g, b = px[xx, y]
        if not is_accent(r, g, b):
            return (r, g, b)
    for yy in range(max(0, y - 40), y + 41):
        r, g, b = px[min(720, x), yy]
        if not is_accent(r, g, b):
            return (r, g, b)
    return (252, 250, 255)


def main() -> None:
    img = Image.open(OUT).convert("RGB")
    px = img.load()
    w, h = img.size

    for _ in range(4):
        for y in range(h):
            for x in range(w):
                if is_accent(*px[x, y]):
                    px[x, y] = sample_lavender(px, x, y)

    # Callout zone: digit, arrow stroke, compression ghosts (site bg only)
    for y in range(0, 90):
        for x in range(800, w):
            r, g, b = px[x, y]
            if is_accent(r, g, b):
                px[x, y] = sample_lavender(px, x, y)
                continue
            if x > 830 and y < 70:
                if (500 < r + g + b < 720) or (r < 100 and g < 100):
                    px[x, y] = sample_lavender(px, x, y)

    img.save(OUT, format="PNG", compress_level=3)
    print("saved", OUT, img.size)


if __name__ == "__main__":
    main()
