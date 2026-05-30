#!/usr/bin/env python3
"""S7 — animate each keyframe into a clip via FAL Seedance Pro image-to-video.

Subtle, film-documentary micro-motion only (no smooth AI-camera glide), plus
the validated anti-shake / no-letterbox suffix. Auto-detects and fixes the
cinematic black bars Seedance adds to ~25% of 9:16 outputs. Runs in parallel,
is idempotent, and accepts a subset of tableau IDs for re-rolls.

END_CARD-role tableaux are skipped — the end card is a PIL composite (see
build_endcard.py), never an i2v clip, so brand text stays crisp (never
AI-rendered).

Reads:  <run>/concept.json + <run>/assets/keyframes/T*.png
Writes: <run>/assets/clips/T01..T13.mp4  (+ .meta.json)

Usage:
  python scripts/render_clips.py --concept <run>/concept.json          # all (minus end card)
  python scripts/render_clips.py --concept <run>/concept.json T09       # re-roll one
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import fal_client
from PIL import Image

from lib import (ensure_dir, ffprobe_duration, ffprobe_resolution, info,
                 require_env, run_root_for, write_meta)

MOTION_OPENER = (
    "Subtle cinematic 35mm-film documentary motion. Handheld micro-drift, "
    "natural breath, slight forward push-in. Film grain holds. "
)
ANTI_SHAKE = (
    "NO smooth AI-camera glide, NO photoreal CGI swoop, NO shake, NO wobble, "
    "NO earthquake. Full-frame vertical 9:16, NO letterbox, NO black bars."
)


def _detect_letterbox(clip: Path) -> bool:
    frame = clip.parent / f"_probe-{clip.stem}.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.0", "-i", str(clip),
                    "-frames:v", "1", "-vf", "scale=216:384", str(frame)], check=True)
    img = Image.open(frame).convert("RGB")
    w, h = img.size
    top = img.crop((0, 0, w, max(1, int(h * 0.05))))
    bot = img.crop((0, h - max(1, int(h * 0.05)), w, h))
    top_mean = sum(sum(p) / 3 for p in top.getdata()) / (top.size[0] * top.size[1])
    bot_mean = sum(sum(p) / 3 for p in bot.getdata()) / (bot.size[0] * bot.size[1])
    frame.unlink(missing_ok=True)
    return top_mean < 8 or bot_mean < 8


def _de_letterbox(clip: Path) -> None:
    archive = ensure_dir(clip.parent / "_letterboxed") / clip.name
    shutil.copy(clip, archive)
    tmp = clip.with_suffix(".fix.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip),
                    "-vf", "scale=1088:1920:flags=lanczos,crop=1080:1920",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-r", "30", "-an", str(tmp)], check=True)
    shutil.move(str(tmp), clip)


def submit_clip(t: dict, kf_dir: Path, out_dir: Path, duration: int) -> dict:
    name = t["id"]
    out_path = out_dir / f"{name}.mp4"
    if out_path.exists() and out_path.stat().st_size > 200_000:
        return {"name": name, "status": "skipped", "size": out_path.stat().st_size}
    kf = kf_dir / f"{name}.png"
    if not kf.exists():
        return {"name": name, "status": "fail", "err": f"keyframe missing: {kf}"}

    prompt = MOTION_OPENER + (t.get("motion_hint", "") or "") + " " + ANTI_SHAKE
    t0 = time.time()
    try:
        kf_url = fal_client.upload_file(str(kf))
        result = fal_client.subscribe(
            "fal-ai/bytedance/seedance/v1/pro/image-to-video",
            arguments={"prompt": prompt, "image_url": kf_url, "duration": duration,
                       "resolution": "1080p", "aspect_ratio": "9:16"},
            with_logs=False,
        )
        urllib.request.urlretrieve(result["video"]["url"], out_path)
        if _detect_letterbox(out_path):
            _de_letterbox(out_path)
    except Exception as e:  # noqa: BLE001 — surface per-job, keep the batch alive
        return {"name": name, "status": "fail", "elapsed": time.time() - t0, "err": str(e)[-300:]}

    w, h = ffprobe_resolution(out_path)
    write_meta(out_path, {
        "tableau": name, "role": t.get("role"), "prompt": prompt,
        "duration_requested": duration, "duration_actual": ffprobe_duration(out_path),
        "resolution": f"{w}x{h}", "provider": "fal/bytedance/seedance/v1/pro/image-to-video",
    })
    return {"name": name, "status": "ok", "elapsed": time.time() - t0, "size": out_path.stat().st_size}


def main() -> int:
    require_env("FAL_KEY")
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    ap.add_argument("tableaux", nargs="*", help="optional subset of tableau IDs (default: all minus end card)")
    ap.add_argument("--duration", type=int, default=5, choices=[3, 4, 5, 6, 7])
    ap.add_argument("--max-workers", type=int, default=4, help="FAL queue ceiling is ~4 concurrent")
    args = ap.parse_args()

    concept_path = Path(args.concept).resolve()
    concept = json.loads(concept_path.read_text())
    run_root = run_root_for(concept_path)
    kf_dir = run_root / "assets" / "keyframes"
    out_dir = ensure_dir(run_root / "assets" / "clips")

    tableaux = [t for t in concept["tableaux"] if t.get("role") != "END_CARD"]
    if args.tableaux:
        sel = set(args.tableaux)
        tableaux = [t for t in concept["tableaux"] if t["id"] in sel]

    info(f"Animating {len(tableaux)} clip(s) via FAL Seedance Pro i2v ({args.duration}s each)")

    results = []
    with ThreadPoolExecutor(max_workers=min(len(tableaux) or 1, args.max_workers)) as ex:
        futs = {ex.submit(submit_clip, t, kf_dir, out_dir, args.duration): t["id"] for t in tableaux}
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
             f"python scripts/render_clips.py --concept {args.concept} {' '.join(r['name'] for r in fail)}")
    return 0 if not fail else 2


if __name__ == "__main__":
    raise SystemExit(main())
