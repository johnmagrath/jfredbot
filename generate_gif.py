#!/usr/bin/env python3
"""
Optional hero GIF generator for jfredbot.

The current index.html uses an inline SVG + CSS gradient hero that perfectly matches
the original branding and loads instantly with zero extra bytes on the wire.

Run this only if you want the old animated 640x360 GIF asset.

Performance:
- Original per-pixel Python loop was very slow (~seconds per frame on CPython).
- This version uses numpy (fast path) when available, otherwise a faster PIL path.
- Still not recommended for production TMAs — prefer vector/SVG or WebP.

Usage:
    python generate_gif.py
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os
import time

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

W, H = 640, 360
N_FRAMES = 30
OUT = "assets/hero-640x360.gif"


def make_frame_numpy(i: int) -> Image.Image:
    """Vectorized radial animated gradient using numpy (10-100x faster)."""
    x = np.arange(W) - W / 2
    y = np.arange(H) - H / 2
    X, Y = np.meshgrid(x, y)
    dist = np.hypot(X, Y)

    t = (np.sin(dist / 30 - i * 0.2) + 1) / 2

    r = (43 * (1 - t) + 14 * t).astype(np.uint8)
    g = (142 * (1 - t) + 165 * t).astype(np.uint8)
    b = (214 * (1 - t) + 164 * t).astype(np.uint8)

    img = np.stack([r, g, b], axis=2)
    pil = Image.fromarray(img, mode="RGB")
    draw = ImageDraw.Draw(pil)

    # Moving hexagon outline
    cx, cy = W / 2, H / 2
    pts = [
        (cx + 100 * math.cos(i * 0.3 + k * 2 * math.pi / 6),
         cy + 100 * math.sin(i * 0.3 + k * 2 * math.pi / 6))
        for k in range(6)
    ]
    draw.polygon(pts, outline="white")

    # Text
    try:
        font = ImageFont.truetype("Arial.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    draw.text((40, 40), "jfredbot", font=font, fill="white")
    return pil


def make_frame_pil(i: int) -> Image.Image:
    """Fallback pure-PIL implementation (still better than original point-by-point)."""
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # Sampled gradient (much fewer operations)
    step = 3
    for yy in range(0, H, step):
        for xx in range(0, W, step):
            dx = xx - W / 2
            dy = yy - H / 2
            dist = math.hypot(dx, dy)
            t = (math.sin(dist / 30 - i * 0.2) + 1) / 2
            r = int(43 * (1 - t) + 14 * t)
            g = int(142 * (1 - t) + 165 * t)
            b = int(214 * (1 - t) + 164 * t)
            draw.rectangle([xx, yy, xx + step, yy + step], fill=(r, g, b))

    # Moving hexagon
    cx, cy = W / 2, H / 2
    pts = [
        (cx + 100 * math.cos(i * 0.3 + k * 2 * math.pi / 6),
         cy + 100 * math.sin(i * 0.3 + k * 2 * math.pi / 6))
        for k in range(6)
    ]
    draw.polygon(pts, outline="white")

    try:
        font = ImageFont.truetype("Arial.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    draw.text((40, 40), "jfredbot", font=font, fill="white")
    return img


def main():
    start = time.time()
    frames = []

    maker = make_frame_numpy if HAS_NUMPY else make_frame_pil
    print(f"Generating {N_FRAMES} frames using {'numpy' if HAS_NUMPY else 'pure PIL'}...")

    for i in range(N_FRAMES):
        frames.append(maker(i))
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{N_FRAMES}")

    print("Saving GIF...")
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        optimize=True,   # helps a little
    )
    size = os.path.getsize(OUT)
    print(f"Done: {OUT} ({len(frames)} frames, {size / 1024:.1f} KB) in {time.time() - start:.2f}s")
    if not HAS_NUMPY:
        print("Tip: pip install numpy  →  much faster next time")


if __name__ == "__main__":
    main()
