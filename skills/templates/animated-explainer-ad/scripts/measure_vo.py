#!/usr/bin/env python3
"""Phase 3 — measure per-scene VO durations + emit scene_timing.json.

Reads every vo-NN-*.mp3 in project/audio/vo/, ffprobes each, and writes
project/scene_timing.json that compose.sh consumes for per-scene retiming.

Each scene gets a small padding (+0.3s default) so the visual breathes a beat
after the VO line ends.

Usage:
  python scripts/measure_vo.py --project ./my-ad --pad 0.3
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from lib import ffprobe_duration, info, project_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--pad", type=float, default=0.3,
                    help="seconds added to each scene's VO duration (default 0.3)")
    ap.add_argument("--endcard-duration", type=float, default=4.0,
                    help="held duration for the end-card scene (default 4.0)")
    args = ap.parse_args()

    vo_dir = project_path(args.project, "audio", "vo")
    vo_dir = Path(args.project).resolve() / "audio" / "vo"
    if not vo_dir.exists():
        raise SystemExit(f"ERROR: {vo_dir} not found — run render_vo.py first")

    vo_files = sorted(vo_dir.glob("vo-*.mp3"))
    if not vo_files:
        raise SystemExit(f"ERROR: no vo-*.mp3 in {vo_dir}")

    scenes = []
    total = 0.0
    for f in vo_files:
        m = re.match(r"vo-(\d+)-?(.*)\.mp3", f.name)
        if not m:
            info(f"skip non-conforming filename: {f.name}")
            continue
        scene_id = m.group(1)
        slug = m.group(2) or ""
        dur = ffprobe_duration(f)
        target = round(dur + args.pad, 2)
        scenes.append({
            "scene": scene_id,
            "slug": slug,
            "vo_file": str(f.relative_to(Path(args.project).resolve())),
            "vo_duration_sec": round(dur, 2),
            "target_duration_sec": target,
        })
        total += target

    # End card scene — held to args.endcard-duration.
    # If the last VO file is the end-card line, it's already included above;
    # we add an explicit "endcard" entry only if the user wants it separate.
    # Convention: VO line N+1 is the end card if it exists. Otherwise the
    # end card is a held image with no VO and uses --endcard-duration.

    out = Path(args.project).resolve() / "scene_timing.json"
    out.write_text(json.dumps({
        "scenes": scenes,
        "total_sec": round(total, 2),
        "pad_sec": args.pad,
        "endcard_duration_sec": args.endcard_duration,
    }, indent=2))

    info(f"wrote {out.relative_to(Path(args.project).resolve())}")
    info(f"total VO+pad = {total:.2f}s across {len(scenes)} scenes")


if __name__ == "__main__":
    main()
