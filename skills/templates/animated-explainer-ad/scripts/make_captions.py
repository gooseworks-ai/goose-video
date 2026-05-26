#!/usr/bin/env python3
"""Phase 8 — emit project/audio/captions.ass for libass burn.

Style: Arial 64, white #FFFFFF, 6px outline #141414, 3px shadow, bottom-third
MarginV=330. Validated on Soteri.

Reads scene_timing.json (from measure_vo.py) and a captions table (one line
per scene) from --captions-file (one caption per line, empty line = scene
with no caption / end card).

Usage:
  python scripts/make_captions.py \
    --project ./my-ad \
    --captions-file ./my-ad/captions.txt
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from lib import info

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Arial,64,&H00FFFFFF,&H000000FF,&H00141414,&H00000000,-1,0,0,0,100,100,0,0,1,6,3,2,90,90,330,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ts(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--captions-file", required=True,
                    help="text file: one caption per line, in scene order. Empty line = no caption (end card).")
    ap.add_argument("--lead-in", type=float, default=0.08,
                    help="seconds AFTER each scene start to fire the cue (avoids cut-flash)")
    args = ap.parse_args()

    proj = Path(args.project).resolve()
    timing = json.loads((proj / "scene_timing.json").read_text())
    captions = (Path(args.captions_file).resolve()).read_text().splitlines()

    if len(captions) != len(timing["scenes"]):
        info(f"WARN: captions.txt has {len(captions)} lines, scene_timing.json has "
             f"{len(timing['scenes'])} scenes. Mismatched. Padding/truncating.")
        captions = captions[:len(timing["scenes"])] + [""] * max(0, len(timing["scenes"]) - len(captions))

    out = proj / "audio" / "captions.ass"
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    t = 0.0
    for scene, cap in zip(timing["scenes"], captions):
        dur = scene["target_duration_sec"]
        cap = cap.strip()
        if cap:
            lines.append(f"Dialogue: 0,{ts(t + args.lead_in)},{ts(t + dur)},Cap,,0,0,0,,{cap}")
        t += dur

    # End card scene (held image, no VO) — typically NO caption (its own typeset carries it).
    # The compose script handles the end-card hold; we don't emit a caption for it here.

    out.write_text(HEADER + "\n".join(lines) + "\n")
    info(f"wrote {out.relative_to(proj)} — {len(lines)} cues, total {t:.2f}s")


if __name__ == "__main__":
    main()
