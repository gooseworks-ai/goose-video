#!/usr/bin/env python3
"""S7b — build the end card: a PIL-typeset wordmark + tagline over the END_CARD
tableau's keyframe (or a solid brand colour), rendered as a short Ken Burns clip.

Brand text is NEVER AI-rendered. Image/video models cannot draw clean
typography — they produce text-shaped glyphs that read as nonsense and break
trust. So the end-card wordmark, tagline, and URL are composited here with PIL,
and the END_CARD tableau's prompt should describe a *clean backdrop with no
text*. compose.py uses this clip for the END_CARD slot in place of an i2v clip.

Reads concept.json `endcard` block (all optional):
  { "wordmark": "...", "tagline": "...", "url": "...",
    "accent_hex": "#E63878", "text_hex": "#F5EDE0", "bg_hex": "#0B0C12",
    "font_family": "serif" | "sans" }
Falls back to concept.brand / concept.campaign when fields are absent.

Reads:  <run>/concept.json + <run>/assets/keyframes/<END_CARD id>.png (optional)
Writes: <run>/assets/endcard.png, <run>/assets/clips/endcard.mp4

Usage:
  python scripts/build_endcard.py --concept <run>/concept.json
  python scripts/build_endcard.py --concept <run>/concept.json --wordmark "HYPE & VICE" --tagline "every day is game day"
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from lib import ensure_dir, info, run_root_for, write_meta

W, H = 1080, 1920

SERIF = [
    "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/Library/Fonts/Georgia.ttf",
]
SANS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def _font(family: str, size: int) -> ImageFont.FreeTypeFont:
    for c in (SERIF if family == "serif" else SANS):
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _fit_font(draw: ImageDraw.ImageDraw, text: str, family: str, start: int, max_w: int) -> ImageFont.FreeTypeFont:
    size = start
    while size > 24:
        f = _font(family, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return _font(family, 24)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    ap.add_argument("--wordmark")
    ap.add_argument("--tagline")
    ap.add_argument("--url")
    ap.add_argument("--duration", type=float, default=4.0)
    args = ap.parse_args()

    concept_path = Path(args.concept).resolve()
    concept = json.loads(concept_path.read_text())
    run_root = run_root_for(concept_path)
    ec = concept.get("endcard", {}) or {}

    wordmark = args.wordmark or ec.get("wordmark") or concept.get("brand", "BRAND").replace("-", " ").upper()
    tagline = args.tagline if args.tagline is not None else (ec.get("tagline") or concept.get("campaign", ""))
    url = args.url if args.url is not None else ec.get("url", "")
    accent = _hex(ec.get("accent_hex", "#E63878"))
    text_rgb = _hex(ec.get("text_hex", "#F5EDE0"))
    bg_rgb = _hex(ec.get("bg_hex", "#0B0C12"))
    family = ec.get("font_family", "serif")

    # Background: the END_CARD keyframe (darkened) if present, else solid brand colour.
    end_id = next((t["id"] for t in concept["tableaux"] if t.get("role") == "END_CARD"), None)
    kf = run_root / "assets" / "keyframes" / f"{end_id}.png" if end_id else None
    if kf and kf.exists():
        bg = Image.open(kf).convert("RGB").resize((W, H), Image.LANCZOS)
        scrim = Image.new("RGB", (W, H), bg_rgb)
        bg = Image.blend(bg, scrim, 0.55)
        bg = bg.filter(ImageFilter.GaussianBlur(2))
    else:
        bg = Image.new("RGB", (W, H), bg_rgb)

    canvas = bg.copy()
    d = ImageDraw.Draw(canvas)
    margin = 96
    max_w = W - 2 * margin

    def centered(y: int, text: str, font: ImageFont.FreeTypeFont, fill, shadow=True) -> int:
        if shadow:
            d.text((W // 2 + 3, y + 3), text, font=font, fill=(0, 0, 0), anchor="ma")
        d.text((W // 2, y), text, font=font, fill=fill, anchor="ma")
        bb = d.textbbox((W // 2, y), text, font=font, anchor="ma")
        return bb[3]

    wm_font = _fit_font(d, wordmark, family, 132, max_w)
    y = int(H * 0.40)
    y = centered(y, wordmark, wm_font, text_rgb) + 28
    if tagline:
        tag_font = _fit_font(d, tagline, family, 52, max_w)
        y = centered(y, tagline, tag_font, accent) + 24
    if url:
        url_font = _font("sans", 40)
        centered(y + 16, url, url_font, text_rgb)

    out_png = ensure_dir(run_root / "assets") / "endcard.png"
    canvas.save(out_png)
    info(f"end-card PNG -> {out_png}")

    out_mp4 = ensure_dir(run_root / "assets" / "clips") / "endcard.mp4"
    frames = int(args.duration * 30)
    # Subtle Ken Burns push-in. Oversample only 1.5x (not 4K) — a 1.05 zoom needs
    # very little headroom, and a 4K zoompan source is pathologically slow.
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", f"{args.duration}",
         "-i", str(out_png),
         "-vf", ("scale=1620:2880:flags=lanczos,"
                 f"zoompan=z='min(zoom+0.0004,1.05)':d={frames}:"
                 "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", "30", "-an", str(out_mp4)],
        check=True,
    )
    write_meta(out_mp4, {"wordmark": wordmark, "tagline": tagline, "url": url,
                         "duration_sec": args.duration, "from_keyframe": str(kf) if kf and kf.exists() else None})
    info(f"end-card clip -> {out_mp4}")


if __name__ == "__main__":
    main()
