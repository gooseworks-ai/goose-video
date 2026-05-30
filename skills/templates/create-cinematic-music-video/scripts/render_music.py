#!/usr/bin/env python3
"""S2 + S3 — generate the original anthem via the ElevenLabs Music API, with
word-level timestamps, then adapt those timestamps to a Whisper-shaped
words.json the caption stage can consume.

This is the load-bearing step of the whole skill: the word timestamps are what
let every visual cut land on a vocal beat. ElevenLabs `/v1/music/detailed`
returns a multipart response — a JSON metadata part (with `words_timestamps`)
and an audio part.

Reads from concept.json:
  - duration_s
  - music.bpm, music.vibe, music.structure_note
  - lyrics_locked_md  (path, relative to the run folder)
  - vocal_gender      (optional: "female" | "male" | "any"; default "female")

Writes:
  <run>/audio/music.mp3
  <run>/audio/music_metadata.json   (raw ElevenLabs response, incl. words_timestamps)
  <run>/audio/words.json            ({"words": [{text,start,end}]}, seconds)

Usage:
  python scripts/render_music.py --concept <run>/concept.json
  python scripts/render_music.py --concept <run>/concept.json --seed 42
"""
from __future__ import annotations

import argparse
import json
import re
from email import policy
from email.parser import BytesParser
from pathlib import Path

import requests

from lib import die, ensure_dir, info, require_env, run_root_for, write_meta

MUSIC_URL = "https://api.elevenlabs.io/v1/music/detailed"


def _read_lyrics(run_root: Path, rel_path: str) -> str:
    """Read the locked lyrics, strip YAML frontmatter + [section] markers, collapse whitespace."""
    p = (run_root / rel_path).resolve()
    if not p.exists():
        die(f"lyrics file not found: {p} (concept.lyrics_locked_md = '{rel_path}')")
    raw = p.read_text()
    # Strip a leading YAML frontmatter block.
    if raw.startswith("---"):
        end = raw.find("---", 3)
        if end > 0:
            raw = raw[end + 3:]
    # Strip bracketed section markers like "[Verse 1]" / "[Chorus]" — ElevenLabs
    # has been observed to sing these literally if they leak into the lyric text.
    raw = re.sub(r"\[[^\]]*\]", "", raw)
    # Drop markdown headings / table rows / blockquotes.
    kept = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "|", ">", "```")):
            continue
        kept.append(s)
    return re.sub(r"\s+", " ", " ".join(kept)).strip()


def _build_prompt(concept: dict, lyrics: str) -> str:
    music = concept.get("music", {})
    bpm = music.get("bpm", 120)
    vibe = music.get("vibe", "cinematic indie anthem")
    struct = music.get("structure_note", "")
    dur = int(concept.get("duration_s", 28))
    gender = concept.get("vocal_gender", "female")
    voc = f"confident {gender} vocal" if gender in ("female", "male") else "confident lead vocal"
    # Describe the artist *style*, never name a real artist — ElevenLabs rejects
    # prompts containing artist names with HTTP 400 bad_prompt.
    return (
        f"A cinematic {vibe} at {bpm} BPM. {struct} {dur} seconds total. No rap. "
        f"Sing these exact lyrics in a {voc}: {lyrics}"
    )


def _parse_multipart(resp: requests.Response, out_dir: Path) -> tuple[Path, Path]:
    """Split the multipart/mixed body into music.mp3 + music_metadata.json."""
    ctype = resp.headers.get("content-type", "")
    m = re.search(r'boundary="?([^";]+)"?', ctype)
    if not m:
        die(f"expected a multipart response, got content-type: {ctype!r}")
    boundary = m.group(1)
    header = f'Content-Type: multipart/mixed; boundary="{boundary}"\r\n\r\n'.encode()
    msg = BytesParser(policy=policy.default).parsebytes(header + resp.content)

    audio_path = out_dir / "music.mp3"
    meta_path = out_dir / "music_metadata.json"
    got_audio = got_meta = False
    for part in msg.iter_parts():
        ct = (part.get_content_type() or "").lower()
        payload = part.get_payload(decode=True) or b""
        if "json" in ct:
            meta_path.write_bytes(payload)
            got_meta = True
        elif ct.startswith("audio/") or "octet-stream" in ct or "mpeg" in ct:
            audio_path.write_bytes(payload)
            got_audio = True
    if not (got_audio and got_meta):
        die("multipart response missing the audio or JSON part")
    return audio_path, meta_path


def _adapt_words(meta_path: Path, words_path: Path) -> int:
    """ElevenLabs words_timestamps (start_ms/end_ms) → Whisper shape (seconds)."""
    meta = json.loads(meta_path.read_text())
    src = meta.get("words_timestamps") or meta.get("word_timestamps") or []
    words = []
    for w in src:
        s = w.get("start_ms", w.get("start"))
        e = w.get("end_ms", w.get("end"))
        text = (w.get("word") or w.get("text") or "").strip()
        if s is None or e is None or not text:
            continue
        # Heuristic: values that look like ms get divided; values that look like
        # seconds pass through.
        if s > 100 and e > 100 and s < 1e7:
            s, e = float(s) / 1000.0, float(e) / 1000.0
        words.append({"text": text, "start": float(s), "end": float(e)})
    words_path.write_text(json.dumps({"words": words}, indent=2))
    return len(words)


def main() -> None:
    api_key = require_env("ELEVENLABS_API_KEY")
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    ap.add_argument("--seed", type=int, default=None, help="optional ElevenLabs seed for reproducibility")
    ap.add_argument("--model", default="music_v1")
    ap.add_argument("--force", action="store_true", help="regenerate even if music.mp3 exists")
    args = ap.parse_args()

    concept_path = Path(args.concept).resolve()
    concept = json.loads(concept_path.read_text())
    run_root = run_root_for(concept_path)
    out_dir = ensure_dir(run_root / "audio")

    if (out_dir / "music.mp3").exists() and (out_dir / "words.json").exists() and not args.force:
        info("[music] music.mp3 + words.json already exist — skipping (use --force to regenerate)")
        return

    lyrics = _read_lyrics(run_root, concept.get("lyrics_locked_md", "source/lyrics-locked.md"))
    if not lyrics:
        die("no lyrics found — write the locked lyrics file referenced by concept.lyrics_locked_md")
    prompt = _build_prompt(concept, lyrics)
    dur_ms = int(concept.get("duration_s", 28)) * 1000

    payload: dict = {
        "prompt": prompt,
        "music_length_ms": dur_ms,
        "model_id": args.model,
        "force_instrumental": False,
        "with_timestamps": True,
    }
    if args.seed is not None:
        payload["seed"] = args.seed

    info(f"[music] requesting {dur_ms/1000:.0f}s anthem with word timestamps...")
    r = requests.post(
        f"{MUSIC_URL}?output_format=mp3_44100_128",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=240,
    )
    if r.status_code != 200:
        hint = ""
        try:
            body = r.json()
            sug = body.get("detail", {}).get("prompt_suggestion") if isinstance(body.get("detail"), dict) else None
            if sug:
                hint = f"\n  API prompt_suggestion: {sug}"
        except Exception:
            pass
        die(
            f"ElevenLabs music HTTP {r.status_code}: {r.text[:400]}{hint}\n"
            "  If this is `bad_prompt`, your music.vibe field likely names a real "
            "artist — use descriptive language only (e.g. 'indie-electronic anthem "
            "with female vocal grit')."
        )

    audio_path, meta_path = _parse_multipart(r, out_dir)
    n_words = _adapt_words(meta_path, out_dir / "words.json")
    write_meta(audio_path, {
        "provider": "elevenlabs/music/detailed",
        "model_id": args.model,
        "duration_ms": dur_ms,
        "with_timestamps": True,
        "word_count": n_words,
        "seed": args.seed,
    })
    info(f"[music] DONE -> {audio_path}  ({n_words} word timestamps -> words.json)")
    if n_words < 8:
        info("[music] WARNING: very few word timestamps — the song may be mostly "
             "instrumental, or lyrics were too long to sing. Captions/beat-sync may be sparse.")


if __name__ == "__main__":
    main()
