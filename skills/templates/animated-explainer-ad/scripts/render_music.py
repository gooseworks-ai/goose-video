#!/usr/bin/env python3
"""Phase 7 — generate the music bed via ElevenLabs music API.

Default prompt is the validated whimsical-Pixar brief. Override with --prompt.
If the bed returns moody/cinematic, re-roll with sharper "NOT cinematic, NOT
moody, NOT dark" negatives.

Usage:
  python scripts/render_music.py \
    --out ./my-ad/audio/music.mp3 \
    --duration 48 \
    --prompt "whimsical Pixar/Disney instrumental — pizzicato strings, light woodwinds, xylophone..."
"""
from __future__ import annotations

import argparse
import json
import pathlib

import requests

from lib import die, info, require_env, write_meta

DEFAULT_PROMPT = (
    "Whimsical Pixar/Disney instrumental score — pizzicato strings, light "
    "woodwinds, xylophone, glockenspiel. Sneaky and playful for the villain "
    "intro, light comedic tension through the damage section, warm uplifting "
    "resolution at the hero arrival, soft resolved tail. NOT cinematic, NOT "
    "moody, NOT dark, NOT orchestral, NOT trailer-style. Light, playful, "
    "family-friendly comedy score."
)


def main() -> None:
    api_key = require_env("ELEVENLABS_API_KEY")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--duration", type=int, default=48, help="seconds")
    ap.add_argument("--prompt", default=DEFAULT_PROMPT)
    args = ap.parse_args()

    out_path = pathlib.Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    info(f"[music] requesting {args.duration}s bed...")
    url = "https://api.elevenlabs.io/v1/music"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "prompt": args.prompt,
        "music_length_ms": int(args.duration * 1000),
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=180)
    if r.status_code != 200:
        die(f"ElevenLabs music HTTP {r.status_code}: {r.text}")
    out_path.write_bytes(r.content)

    write_meta(out_path, {
        "prompt": args.prompt,
        "duration_requested_sec": args.duration,
        "provider": "elevenlabs/music",
    })

    info(f"[music] DONE -> {out_path}")


if __name__ == "__main__":
    main()
