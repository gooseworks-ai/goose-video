#!/usr/bin/env python3
"""S5 + S6 — generate beat-locked keyframes via FAL nano-banana.

Each tableau prompt is composed as:
    STYLE_OPENER (from the look pack) + tableau.prompt + NEGATIVE_TAIL

so the photographic style is locked across all 14 frames. Output is normalised
to exactly 1080x1920. Runs in parallel, is idempotent (skips existing PNGs),
and accepts a subset of tableau IDs for re-rolls.

A tableau may set "ref": ["path/to/brand.png", ...] to thread brand/product
reference images through nano-banana/edit for visual consistency.

Reads:  <run>/concept.json + lookpacks/<look_pack>.md
Writes: <run>/assets/keyframes/T01..T14.png  (+ .meta.json, raw under _raw/)

Usage:
  python scripts/render_keyframes.py --concept <run>/concept.json            # all
  python scripts/render_keyframes.py --concept <run>/concept.json T01        # gate test
  python scripts/render_keyframes.py --concept <run>/concept.json T08 T12    # re-roll subset
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import fal_client
from PIL import Image

from lib import (compose_keyframe_prompt, ensure_dir, info, load_lookpack,
                 require_env, run_root_for, write_meta)

W, H = 1080, 1920


def _normalize_to_vertical(src: Path, dst: Path) -> None:
    """Cover-crop + resize any nano-banana output to exactly 1080x1920."""
    img = Image.open(src).convert("RGB")
    w, h = img.size
    target = W / H
    cur = w / h
    if abs(cur - target) > 0.01:
        if cur > target:
            nw = int(h * target)
            left = (w - nw) // 2
            img = img.crop((left, 0, left + nw, h))
        else:
            nh = int(w / target)
            top = (h - nh) // 2
            img = img.crop((0, top, w, top + nh))
    img.resize((W, H), Image.LANCZOS).save(dst)


def submit_keyframe(t: dict, pack: dict, run_root: Path, out_dir: Path) -> dict:
    name = t["id"]
    out_path = out_dir / f"{name}.png"
    if out_path.exists() and out_path.stat().st_size > 50_000:
        return {"name": name, "status": "skipped", "size": out_path.stat().st_size}

    prompt = compose_keyframe_prompt(pack, t["prompt"])
    raw_dir = ensure_dir(out_dir / "_raw")
    raw_path = raw_dir / f"{name}.png"

    # Optional brand/product reference images → nano-banana/edit.
    ref_urls = []
    for ref in t.get("ref", []) or []:
        ref_p = (run_root / ref).resolve() if not Path(ref).is_absolute() else Path(ref)
        if ref_p.exists():
            ref_urls.append(fal_client.upload_file(str(ref_p)))

    args_dict: dict = {"prompt": prompt, "num_images": 1, "output_format": "png", "aspect_ratio": "9:16"}
    model = "fal-ai/nano-banana"
    if ref_urls:
        model = "fal-ai/nano-banana/edit"
        args_dict["image_urls"] = ref_urls

    t0 = time.time()
    try:
        result = fal_client.subscribe(model, arguments=args_dict, with_logs=False)
        img_url = result["images"][0]["url"]
        urllib.request.urlretrieve(img_url, raw_path)
        _normalize_to_vertical(raw_path, out_path)
    except Exception as e:  # noqa: BLE001 — surface per-job, keep the batch alive
        return {"name": name, "status": "fail", "elapsed": time.time() - t0, "err": str(e)[-300:]}

    write_meta(out_path, {
        "tableau": name, "role": t.get("role"), "prompt": prompt,
        "provider": model, "refs": list(t.get("ref", []) or []), "raw_url": img_url,
    })
    return {"name": name, "status": "ok", "elapsed": time.time() - t0, "size": out_path.stat().st_size}


def main() -> int:
    require_env("FAL_KEY")
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    ap.add_argument("tableaux", nargs="*", help="optional subset of tableau IDs (default: all)")
    ap.add_argument("--max-workers", type=int, default=8)
    args = ap.parse_args()

    concept_path = Path(args.concept).resolve()
    concept = json.loads(concept_path.read_text())
    run_root = run_root_for(concept_path)
    out_dir = ensure_dir(run_root / "assets" / "keyframes")
    pack = load_lookpack(concept["look_pack"])

    tableaux = concept["tableaux"]
    if args.tableaux:
        sel = set(args.tableaux)
        tableaux = [t for t in tableaux if t["id"] in sel]

    info(f"Generating {len(tableaux)} keyframe(s) via FAL nano-banana — look pack {concept['look_pack']}")

    results = []
    with ThreadPoolExecutor(max_workers=min(len(tableaux) or 1, args.max_workers)) as ex:
        futs = {ex.submit(submit_keyframe, t, pack, run_root, out_dir): t["id"] for t in tableaux}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            if r["status"] == "ok":
                info(f"  [OK]   {r['name']} — {r['elapsed']:.0f}s, {r['size']:,} bytes")
            elif r["status"] == "skipped":
                info(f"  [skip] {r['name']} — already exists ({r['size']:,} bytes)")
            else:
                info(f"  [FAIL] {r['name']} — {r.get('err', '?')}")

    fail = [r for r in results if r["status"] == "fail"]
    info(f"Summary: {len(results) - len(fail)} ok, {len(fail)} failed")
    if fail:
        info("Re-run only the failures, e.g.: "
             f"python scripts/render_keyframes.py --concept {args.concept} {' '.join(r['name'] for r in fail)}")
    return 0 if not fail else 2


if __name__ == "__main__":
    raise SystemExit(main())
