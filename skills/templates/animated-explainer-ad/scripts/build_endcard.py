#!/usr/bin/env python3
"""Phase 6 — PIL composite of real product photo + typeset brand layer.

NEVER an AI-rendered cartoon bottle. The end card uses the real product photo
the user provides, centred on a brand-coloured background with typeset
wordmark + product line + claim rows + CTA pill below.

Encodes a 4s Ken Burns clip (1.00 → 1.04 zoom) as the final scene mp4.

Usage:
  python scripts/build_endcard.py \
    --project ./my-ad \
    --product ./inputs/soteri-bottle.jpg \
    --wordmark "Soteri Skin" \
    --subline "Baby Eczema Relief Cream" \
    --claim "Powered by pH/LOCK Technology" \
    --claim "Steroid-Free   ·   Fragrance-Free   ·   Ages 0-5" \
    --cta "soteriskin.com" \
    --primary "#2E6F5E" \
    --cta-color "#E8674C" \
    --scene 12 \
    --duration 4.0
"""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from lib import info, project_path, write_meta

W, H = 1080, 1920


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates_bold = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    candidates_reg = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in (candidates_bold if bold else candidates_reg):
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--product", required=True, help="absolute path to real product photo")
    ap.add_argument("--wordmark", required=True)
    ap.add_argument("--subline", required=True)
    ap.add_argument("--claim", action="append", default=[], help="repeatable claim line")
    ap.add_argument("--cta", required=True)
    ap.add_argument("--primary", default="#2E6F5E", help="hex bg colour (or 'seamless' to sample product)")
    ap.add_argument("--text-color", default="#FFFFFF")
    ap.add_argument("--cta-color", default="#E8674C")
    ap.add_argument("--cta-text-color", default="#FFFFFF")
    ap.add_argument("--scene", default="12", help="scene id for output filename")
    ap.add_argument("--duration", type=float, default=4.0)
    ap.add_argument("--seamless", action="store_true",
                    help="sample product edge for bg instead of --primary")
    args = ap.parse_args()

    product_path = Path(args.product).resolve()
    if not product_path.exists():
        raise SystemExit(f"ERROR: product image not found: {product_path}")

    endcard_png = project_path(args.project, "endcard", "endcard.png")
    out_mp4 = project_path(args.project, "clips", f"scene-{args.scene}.mp4")

    # Load product, resolve background colour.
    prod = Image.open(product_path).convert("RGB")
    if args.seamless:
        bg = prod.getpixel((6, 6))
    else:
        bg = _hex_to_rgb(args.primary)
    text_rgb = _hex_to_rgb(args.text_color)
    cta_bg = _hex_to_rgb(args.cta_color)
    cta_text = _hex_to_rgb(args.cta_text_color)

    # Canvas + centred product.
    canvas = Image.new("RGB", (W, H), bg)
    ph = 1015
    pw = int(prod.width * ph / prod.height)
    prod_scaled = prod.resize((pw, ph), Image.LANCZOS)
    canvas.paste(prod_scaled, ((W - pw) // 2, 88))

    d = ImageDraw.Draw(canvas)

    def line(y: int, text: str, fnt: ImageFont.FreeTypeFont, fill: tuple[int, int, int]) -> None:
        d.text((W // 2, y), text, font=fnt, fill=fill, anchor="ma")

    y = 1190
    line(y, args.wordmark, _font(100, bold=True), text_rgb); y += 128
    line(y, args.subline, _font(46, bold=True), text_rgb); y += 96
    for cl in args.claim:
        line(y, cl, _font(35, bold=False), text_rgb); y += 56
    y += 36  # gap before CTA

    # CTA pill
    cta_font = _font(43, bold=True)
    bb = d.textbbox((0, 0), args.cta, font=cta_font)
    cw, chh = bb[2] - bb[0], bb[3] - bb[1]
    padx, pady = 50, 30
    pw2, ph2 = cw + 2 * padx, chh + 2 * pady
    px = (W - pw2) // 2
    d.rounded_rectangle([px, y, px + pw2, y + ph2], radius=ph2 // 2, fill=cta_bg)
    d.text((W // 2, y + ph2 // 2), args.cta, font=cta_font, fill=cta_text, anchor="mm")

    canvas.save(endcard_png)
    info(f"end-card PNG -> {endcard_png}")

    # Ken Burns 1.00 -> 1.04 over args.duration.
    frames = int(args.duration * 30)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-loop", "1", "-t", str(args.duration), "-i", str(endcard_png),
         "-vf",
         f"scale=2160:3840:flags=lanczos,"
         f"zoompan=z='min(zoom+0.0003,1.04)':d={frames}:s=1080x1920:fps=30",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", "30", "-an", str(out_mp4)],
        check=True,
    )

    write_meta(out_mp4, {
        "scene": args.scene,
        "wordmark": args.wordmark,
        "subline": args.subline,
        "claims": args.claim,
        "cta": args.cta,
        "primary": args.primary if not args.seamless else f"seamless:{bg}",
        "duration_sec": args.duration,
        "product_image": str(product_path),
    })

    info(f"end-card clip -> {out_mp4}")


if __name__ == "__main__":
    main()
