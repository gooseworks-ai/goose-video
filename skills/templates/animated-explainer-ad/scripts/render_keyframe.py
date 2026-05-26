#!/usr/bin/env python3
"""Phase 4 — render one scene keyframe via FAL nano-banana with chained anchor refs.

Wraps the visual in the Pixar-3D style block, passes character anchor PNGs as
nano-banana `image_urls` for character consistency, normalises to 1080x1920,
and writes a .meta.json.

Usage:
  python scripts/render_keyframe.py \
    --project ./my-ad \
    --scene 01 \
    --visual "Eczema strolls onto a warm cartoon skin landscape, leans to camera, smug." \
    --refs ./my-ad/anchors/eczema.png \
    --negative "no text, no signage, no labels, no brand names, no wings"
"""
from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

import fal_client
from PIL import Image

from lib import info, project_path, require_env, write_meta

PIXAR_STYLE = (
    "Pixar/Disney 3D animation style, glossy, rounded forms, soft global "
    "illumination, shallow depth of field, toy-like, warm cinematic lighting, "
    "expressive characters, 9:16 vertical composition"
)


def main() -> None:
    require_env("FAL_KEY")
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--scene", required=True, help="zero-padded scene id (e.g. '01')")
    ap.add_argument("--visual", required=True)
    ap.add_argument("--refs", nargs="*", default=[], help="anchor PNG paths to thread as refs")
    ap.add_argument("--negative", default="no text, no signage, no labels, no brand names",
                    help="default already forbids brand-text contamination")
    args = ap.parse_args()

    out_path = project_path(args.project, "keyframes", f"scene-{args.scene}.png")
    raw_path = out_path.parent / "_raw" / out_path.name
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    prompt = f"{args.visual} {PIXAR_STYLE}."
    if args.negative:
        prompt += f" Negative: {args.negative}."

    # Upload each anchor ref to FAL storage (returns a URL nano-banana can pull).
    ref_urls = []
    for ref in args.refs:
        ref_p = Path(ref).resolve()
        if not ref_p.exists():
            info(f"[scene-{args.scene}] WARN: ref not found, skipping: {ref_p}")
            continue
        info(f"[scene-{args.scene}] uploading ref {ref_p.name}...")
        ref_urls.append(fal_client.upload_file(str(ref_p)))

    args_dict: dict = {
        "prompt": prompt,
        "num_images": 1,
        "output_format": "png",
        "aspect_ratio": "9:16",
    }
    if ref_urls:
        # nano-banana accepts `image_urls` for chained-ref / character consistency
        args_dict["image_urls"] = ref_urls

    info(f"[scene-{args.scene}] submitting nano-banana with {len(ref_urls)} ref(s)...")
    result = fal_client.subscribe(
        "fal-ai/nano-banana/edit" if ref_urls else "fal-ai/nano-banana",
        arguments=args_dict,
        with_logs=False,
    )

    img_url = result["images"][0]["url"]
    info(f"[scene-{args.scene}] downloading -> {raw_path}")
    urllib.request.urlretrieve(img_url, raw_path)

    # Normalise to exactly 1080x1920 cover-crop.
    img = Image.open(raw_path).convert("RGB")
    w, h = img.size
    target_ratio = 1080 / 1920
    cur_ratio = w / h
    if abs(cur_ratio - target_ratio) > 0.01:
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
        "scene": args.scene,
        "visual": args.visual,
        "negative": args.negative,
        "prompt": prompt,
        "refs": [str(Path(r).name) for r in args.refs],
        "provider": "fal/nano-banana" + ("/edit" if ref_urls else ""),
        "raw_url": img_url,
    })

    info(f"[scene-{args.scene}] DONE -> {out_path}")


if __name__ == "__main__":
    main()
