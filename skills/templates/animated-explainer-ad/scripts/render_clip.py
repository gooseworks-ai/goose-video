#!/usr/bin/env python3
"""Phase 5 — render one scene clip via FAL Seedance Pro i2v with auto de-letterbox.

Suffixes the motion prompt with the validated anti-shake block, submits to
Seedance Pro at 1080p 9:16, downloads the result, and auto-detects + fixes
letterbox bars (the most common Seedance failure mode on 9:16 output).

Usage:
  python scripts/render_clip.py \
    --project ./my-ad \
    --scene 01 \
    --keyframe ./my-ad/keyframes/scene-01.png \
    --motion "Eczema turns his head slightly toward camera, narrowing his eyes with a smug confident grin. Subtle gentle camera float." \
    --duration 4
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import urllib.request
from pathlib import Path

import fal_client
from PIL import Image

from lib import ffprobe_duration, ffprobe_resolution, info, project_path, require_env, write_meta

ANTI_SHAKE = (
    "Pixar 3D animation style preserved throughout. NO shake, NO wobble, "
    "NO earthquake, smooth steady camera. Full-frame vertical 9:16, "
    "NO letterbox, NO black bars."
)


def _detect_letterbox(clip_path: Path) -> bool:
    """Sample frame at t=1.0s, check if top/bottom 5% rows are near-solid black."""
    frame = clip_path.parent / f"_probe-{clip_path.stem}.png"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.0", "-i", str(clip_path),
         "-frames:v", "1", "-vf", "scale=216:384", str(frame)],
        check=True,
    )
    img = Image.open(frame).convert("RGB")
    w, h = img.size
    top = img.crop((0, 0, w, max(1, int(h * 0.05))))
    bot = img.crop((0, h - max(1, int(h * 0.05)), w, h))
    top_mean = sum(sum(p) / 3 for p in top.getdata()) / (top.size[0] * top.size[1])
    bot_mean = sum(sum(p) / 3 for p in bot.getdata()) / (bot.size[0] * bot.size[1])
    frame.unlink(missing_ok=True)
    return top_mean < 8 or bot_mean < 8


def _de_letterbox(clip_path: Path) -> None:
    """Scale-to-cover crop to wipe out cinematic black bars. Archives original."""
    archive_dir = clip_path.parent / "_letterboxed"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archived = archive_dir / clip_path.name
    shutil.copy(clip_path, archived)
    tmp = clip_path.with_suffix(".fix.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip_path),
         "-vf", "scale=1088:1920:flags=lanczos,crop=1080:1920",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", "30", "-an", str(tmp)],
        check=True,
    )
    shutil.move(str(tmp), clip_path)
    info(f"[scene-?] de-letterboxed (archived original -> {archived.relative_to(clip_path.parent.parent)})")


def main() -> None:
    require_env("FAL_KEY")
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--scene", required=True)
    ap.add_argument("--keyframe", required=True)
    ap.add_argument("--motion", required=True, help="motion prompt — describe what moves, not the static composition")
    ap.add_argument("--duration", type=int, default=4, choices=[3, 4, 5, 6, 7])
    args = ap.parse_args()

    out_path = project_path(args.project, "clips", f"scene-{args.scene}.mp4")
    keyframe_path = Path(args.keyframe).resolve()
    if not keyframe_path.exists():
        raise SystemExit(f"ERROR: keyframe not found: {keyframe_path}")

    info(f"[scene-{args.scene}] uploading keyframe...")
    keyframe_url = fal_client.upload_file(str(keyframe_path))

    prompt = f"{args.motion} {ANTI_SHAKE}"

    info(f"[scene-{args.scene}] submitting Seedance Pro i2v ({args.duration}s)...")
    result = fal_client.subscribe(
        "fal-ai/bytedance/seedance/v1/pro/image-to-video",
        arguments={
            "prompt": prompt,
            "image_url": keyframe_url,
            "duration": args.duration,
            "resolution": "1080p",
            "aspect_ratio": "9:16",
        },
        with_logs=False,
    )

    video_url = result["video"]["url"]
    info(f"[scene-{args.scene}] downloading -> {out_path}")
    urllib.request.urlretrieve(video_url, out_path)

    # De-letterbox check.
    if _detect_letterbox(out_path):
        info(f"[scene-{args.scene}] letterbox detected — fixing...")
        _de_letterbox(out_path)

    duration_actual = ffprobe_duration(out_path)
    w, h = ffprobe_resolution(out_path)
    write_meta(out_path, {
        "scene": args.scene,
        "motion": args.motion,
        "prompt": prompt,
        "duration_requested": args.duration,
        "duration_actual": duration_actual,
        "resolution": f"{w}x{h}",
        "provider": "fal/bytedance/seedance/v1/pro/image-to-video",
        "keyframe": str(keyframe_path.name),
        "video_url": video_url,
    })

    info(f"[scene-{args.scene}] DONE ({duration_actual:.2f}s, {w}x{h})")


if __name__ == "__main__":
    main()
