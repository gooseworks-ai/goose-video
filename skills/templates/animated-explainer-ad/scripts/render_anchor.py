#!/usr/bin/env python3
"""Phase 2 — render one character anchor PNG via FAL nano-banana.

Wraps the descriptor in the validated Pixar-3D prompt prefix, hits nano-banana
at the highest supported portrait resolution, normalises to 1080x1920, and
writes a .meta.json with the prompt used.

Usage:
  python scripts/render_anchor.py \
    --project ./my-ad \
    --name eczema \
    --descriptor "small knee-high gremlin, rough sandpapery hot coral-red skin..." \
    --negative "no wings, no horns, no tail"
"""
from __future__ import annotations

import argparse
import urllib.request

import fal_client
from PIL import Image

from lib import die, info, project_path, require_env, write_meta

PIXAR_PREFIX = (
    "character portrait, neutral pale background, full body visible, "
    "Pixar/Disney 3D animation style, glossy, rounded forms, soft global "
    "illumination, shallow depth of field, toy-like, expressive face, "
    "kid-friendly comedy character"
)


def main() -> None:
    require_env("FAL_KEY")
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--name", required=True, help="character key (e.g. 'eczema')")
    ap.add_argument("--descriptor", required=True)
    ap.add_argument("--negative", default="", help="negative constraints (e.g. 'no wings')")
    ap.add_argument("--out", default=None, help="override output path; default project/anchors/<name>.png")
    args = ap.parse_args()

    out_path = (
        project_path(args.project, "anchors", f"{args.name}.png")
        if not args.out
        else project_path(args.project, args.out)
    )

    prompt = f"{PIXAR_PREFIX}. {args.descriptor}."
    if args.negative:
        prompt += f" Negative: {args.negative}."

    info(f"[anchor:{args.name}] submitting nano-banana...")
    result = fal_client.subscribe(
        "fal-ai/nano-banana",
        arguments={
            "prompt": prompt,
            "num_images": 1,
            "output_format": "png",
            "aspect_ratio": "9:16",
        },
        with_logs=False,
    )

    img_url = result["images"][0]["url"]
    raw_path = out_path.parent / "_raw" / out_path.name
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    info(f"[anchor:{args.name}] downloading -> {raw_path}")
    urllib.request.urlretrieve(img_url, raw_path)

    # Normalise to 1080x1920 (cover-crop).
    img = Image.open(raw_path).convert("RGBA")
    w, h = img.size
    target_ratio = 1080 / 1920
    cur_ratio = w / h
    if abs(cur_ratio - target_ratio) > 0.01:
        # cover-crop to match 9:16
        if cur_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))
    img = img.resize((1080, 1920), Image.LANCZOS)
    img.save(out_path)

    write_meta(out_path, {
        "name": args.name,
        "descriptor": args.descriptor,
        "negative": args.negative,
        "prompt": prompt,
        "provider": "fal/nano-banana",
        "raw_url": img_url,
        "raw_path": str(raw_path.relative_to(out_path.parent.parent)),
    })

    info(f"[anchor:{args.name}] DONE -> {out_path}")


if __name__ == "__main__":
    main()
