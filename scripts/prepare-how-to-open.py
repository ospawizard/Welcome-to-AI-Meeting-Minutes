#!/usr/bin/env python3
"""Rebuild how-to-open.png from Meet screenshot: cleanups + sharpen + @2x."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(
    "/Users/olgasparyshkina/.cursor/projects/Users-olgasparyshkina-Desktop-lavsit-landing/assets/image-ac8774ce-f902-490b-82ac-8d78475e6f77.png"
)
OUT_1X = ROOT / "images" / "how-to-open.png"
OUT_2X = ROOT / "images" / "how-to-open@2x.png"
TARGET_W = 1024


def load_base() -> Image.Image:
    img = Image.open(SRC).convert("RGB")
    if img.width != TARGET_W:
        h = int(img.height * TARGET_W / img.width)
        img = img.resize((TARGET_W, h), Image.Resampling.LANCZOS)
    return img


def is_meet_teal(r: int, g: int, b: int) -> bool:
    return g >= 50 and b >= 55 and 20 <= r <= 65


def sample_teal(px, x: int, y: float, h: int) -> tuple[int, int, int] | None:
    y0 = int(y)
    y1 = min(y0 + 1, h - 1)
    a = y - y0
    c0 = column_teal_ref_at_row(px, x, y0)
    c1 = column_teal_ref_at_row(px, x, y1)
    if c0 and c1:
        return (
            int(c0[0] * (1 - a) + c1[0] * a),
            int(c0[1] * (1 - a) + c1[1] * a),
            int(c0[2] * (1 - a) + c1[2] * a),
        )
    return c0 or c1


def column_teal_ref_at_row(px, x: int, y: int) -> tuple[int, int, int] | None:
    r, g, b = px[x, y]
    if is_meet_teal(r, g, b):
        return (r, g, b)
    for dy in (-2, -4, 2, 4, -8, 8):
        yy = y + dy
        if yy < 0:
            continue
        r, g, b = px[x, yy]
        if is_meet_teal(r, g, b):
            return (r, g, b)
    return None


def paint_meet_gradient_strip(img: Image.Image) -> None:
    """Replace name/black smear with the same horizontal+vertical Meet teal gradient."""
    px = img.load()
    h = img.size[1]
    y_dst_start, y_dst_end = 496, 511
    y_src_start, y_src_end = 468, 490
    span_dst = y_dst_end - y_dst_start
    span_src = y_src_end - y_src_start

    for y_dst in range(y_dst_start, y_dst_end + 1):
        t = (y_dst - y_dst_start) / span_dst
        y_src = y_src_start + t * span_src
        for x in range(14, 320):
            color = sample_teal(px, x, y_src, h)
            if color:
                px[x, y_dst] = color

    # Left edge: blend smears into gradient from the nearest clean column.
    for y_dst in range(y_dst_start, y_dst_end + 1):
        t = (y_dst - y_dst_start) / span_dst
        y_src = y_src_start + t * span_src
        edge_color = sample_teal(px, 22, y_src, h) or sample_teal(px, 30, y_src, h)
        if not edge_color:
            continue
        for x in range(0, 14):
            r, g, b = px[x, y_dst]
            if r < 12 and g < 20 and b < 35:
                px[x, y_dst] = edge_color


def apply_cleanups(img: Image.Image) -> None:
    px = img.load()
    w, h = img.size

    paint_meet_gradient_strip(img)

    white_ref = (255, 255, 255)
    for y in range(36, 52):
        for x in range(905, w):
            r, g, b = px[x, y]
            if r + g + b < 650:
                px[x, y] = white_ref


def sharpen_ui(img: Image.Image) -> Image.Image:
    return img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=125, threshold=3))


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", compress_level=3)


def main() -> None:
    base = load_base()
    apply_cleanups(base)
    sharp = sharpen_ui(base)
    save_png(sharp, OUT_1X)

    w2, h2 = TARGET_W * 2, sharp.height * 2
    up = sharp.resize((w2, h2), Image.Resampling.LANCZOS)
    up = up.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=4))
    save_png(up, OUT_2X)

    print("1x", sharp.size, OUT_1X.stat().st_size // 1024, "KB")
    print("2x", up.size, OUT_2X.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
