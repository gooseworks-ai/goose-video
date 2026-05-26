#!/usr/bin/env python3
"""Phase 3 — render one VO line via ElevenLabs eleven_v3 + silence-trim.

Uses the validated voice_settings from the Soteri Austin pass:
  stability 0.34, similarity_boost 0.80, style 0.40, use_speaker_boost true,
  speed 1.12 (override via --speed).

Applies ffmpeg silenceremove start=0.05s end=0.12s after the TTS render so
lines cut cleanly in compose. Writes a .meta.json with the exact text + voice
settings used.

Usage:
  python scripts/render_vo.py \
    --voice-id Bj9UqZbhQsanLzgalpEG \
    --text "[whispers] Psst. I'm Eczema. I live on your baby's skin." \
    --out ./my-ad/audio/vo/vo-01-intro.mp3 \
    --speed 1.12
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import tempfile

import requests

from lib import die, info, require_env, write_meta


def main() -> None:
    api_key = require_env("ELEVENLABS_API_KEY")
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-id", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", required=True, help="output mp3 path")
    ap.add_argument("--model", default="eleven_v3")
    ap.add_argument("--speed", type=float, default=1.12)
    ap.add_argument("--stability", type=float, default=0.34)
    ap.add_argument("--similarity-boost", type=float, default=0.80)
    ap.add_argument("--style", type=float, default=0.40)
    ap.add_argument("--no-trim", action="store_true",
                    help="skip the post-TTS silenceremove pass")
    args = ap.parse_args()

    out_path = pathlib.Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    voice_settings = {
        "stability": args.stability,
        "similarity_boost": args.similarity_boost,
        "style": args.style,
        "use_speaker_boost": True,
        "speed": args.speed,
    }
    payload = {
        "text": args.text,
        "model_id": args.model,
        "voice_settings": voice_settings,
    }

    info(f"[vo] {args.voice_id} | {args.text[:60]!r}{'...' if len(args.text) > 60 else ''}")

    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/{args.voice_id}"
        f"?output_format=mp3_44100_128"
    )
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as raw_tmp:
        raw_path = pathlib.Path(raw_tmp.name)
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    if r.status_code != 200:
        die(f"ElevenLabs HTTP {r.status_code}: {r.text}")
    raw_path.write_bytes(r.content)

    if args.no_trim:
        raw_path.replace(out_path)
    else:
        # Silence-trim both ends. Same recipe as the Soteri Austin pass.
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw_path),
             "-af",
             "silenceremove=start_periods=1:start_silence=0.05:start_threshold=-50dB:detection=peak,"
             "areverse,"
             "silenceremove=start_periods=1:start_silence=0.12:start_threshold=-50dB:detection=peak,"
             "areverse",
             str(out_path)],
            check=True,
        )
        raw_path.unlink(missing_ok=True)

    dur = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(out_path)]
    ).decode().strip()

    write_meta(out_path, {
        "voice_id": args.voice_id,
        "model": args.model,
        "voice_settings": voice_settings,
        "text": args.text,
        "duration_sec": float(dur),
        "trimmed": not args.no_trim,
    })

    info(f"[vo] DONE -> {out_path.name} ({dur}s)")


if __name__ == "__main__":
    main()
