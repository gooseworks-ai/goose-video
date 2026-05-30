#!/usr/bin/env python3
"""S9a — generate cinematic word-synced ASS captions from the sung-word
timestamps + the locked lyrics.

Aligns the timed words to the lyric spelling, chunks them into short bursts
(respecting punctuation, line breaks, silence gaps, and accent words), and
writes an .ass file. The actual burn happens in compose.py with a
libass-enabled ffmpeg.

Caption styling comes from concept.json `caption_overrides` (all optional):
  { "placement": "low" | "mid" | "high",
    "chunk_size": 4, "font": "Georgia", "font_size": 64,
    "accent_hex": "#E63878" }

Reads:  <run>/concept.json, <run>/audio/words.json, lyrics file, accent_words
Writes: <run>/working/captions.ass

Usage:
  python scripts/make_captions.py --concept <run>/concept.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from lib import die, ensure_dir, info, run_root_for

PUNCT_BOUNDARIES = set(".,!?;:—")
SILENCE_BREAK_S = 0.60


def _norm(tok: str) -> str:
    return re.sub(r"[^a-z0-9']+", "", tok.lower())


def parse_lyrics(path: Path) -> tuple[list[str], list[int]]:
    """Flat word list + line-break indices. Skips frontmatter, headings,
    table rows, blockquotes, fenced blocks, and [section] markers."""
    raw = path.read_text()
    if raw.startswith("---"):
        end = raw.find("---", 3)
        if end > 0:
            raw = raw[end + 3:]
    raw = re.sub(r"\[[^\]]+\]", "", raw)
    words: list[str] = []
    line_breaks: list[int] = []
    in_fence = False
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or s.startswith(("|", "#", ">")):
            continue
        if re.match(r"^[-*]\s", s) and ":" in s:
            continue
        words.extend(s.split())
        line_breaks.append(len(words))
    return words, line_breaks


def align_to_lyrics(timed: list[dict], lyric_words: list[str]) -> tuple[list[dict], list[str]]:
    """Re-spell timed tokens to lyric spelling, dropping transcription artifacts."""
    warnings: list[str] = []
    aligned: list[dict] = []
    li = drops = 0
    for w in timed:
        ntok = _norm(w["text"])
        if not ntok:
            continue
        matched = False
        for look in range(0, min(4, len(lyric_words) - li)):
            if _norm(lyric_words[li + look]) == ntok:
                aligned.append({"text": lyric_words[li + look], "start": w["start"], "end": w["end"]})
                li += look + 1
                matched = True
                break
        if not matched:
            drops += 1
    if li < len(lyric_words):
        warnings.append(f"{len(lyric_words) - li} lyric word(s) never matched a timed token")
    if drops:
        warnings.append(f"dropped {drops} timed token(s) with no lyric match")
    drift = abs(len(aligned) - len(lyric_words)) / max(1, len(lyric_words))
    if drift > 0.20:
        warnings.append(f"WORD-COUNT DRIFT {drift:.0%} — review captions before shipping")
    # If alignment collapsed (e.g. lyric file unparsable), fall back to raw timed text.
    if len(aligned) < max(3, 0.4 * len(lyric_words)):
        warnings.append("alignment weak — falling back to raw sung-word text for captions")
        aligned = [{"text": w["text"], "start": w["start"], "end": w["end"]} for w in timed if _norm(w["text"])]
    return aligned, warnings


def chunk_bursts(words: list[dict], breaks_list: list[int], max_words: int, accent_set: set[str]) -> list[dict]:
    breaks = set(breaks_list)
    accent_norms = {_norm(t) for t in accent_set}
    chunks: list[dict] = []
    cur: list[dict] = []
    for i, w in enumerate(words):
        cur.append(w)
        is_last = i == len(words) - 1
        ends_punct = any(w["text"].endswith(p) for p in PUNCT_BOUNDARIES)
        gap_next = (words[i + 1]["start"] - w["end"]) if not is_last else 0
        on_break = (i + 1) in breaks
        accent_here = _norm(w["text"]) in accent_norms
        if (len(cur) >= max_words or ends_punct or on_break or gap_next >= SILENCE_BREAK_S
                or is_last or (accent_here and len(cur) >= 2)):
            chunks.append(_finalize(cur))
            cur = []
    if cur:
        chunks.append(_finalize(cur))
    # Merge sub-180ms chunks forward.
    out: list[dict] = []
    for c in chunks:
        if out and (c["end"] - c["start"]) < 0.18:
            out[-1]["end"] = c["end"]
            out[-1]["words"].extend(c["words"])
        else:
            out.append(c)
    # Clip overlaps.
    for i in range(len(out) - 1):
        if out[i]["end"] > out[i + 1]["start"] - 0.02:
            out[i]["end"] = max(out[i]["start"] + 0.18, out[i + 1]["start"] - 0.02)
    return out


def _finalize(words: list[dict]) -> dict:
    return {"start": max(0.0, words[0]["start"] - 0.03), "end": words[-1]["end"] + 0.08, "words": list(words)}


ASS_HEADER = """[Script Info]
Title: create-cinematic-music-video captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{size},&H00F5EDE0,&H00000000,&H00141414,&H80000000,0,0,0,0,100,100,0,0,1,3,2,{align},80,80,{marginv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _ass_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    return f"{h:01d}:{m:02d}:{t % 60:05.2f}"


def _ass_color(hex_str: str) -> str:
    r, g, b = (int(hex_str.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    return f"&H00{b:02X}{g:02X}{r:02X}"


def render_ass(chunks: list[dict], accent_set: set[str], placement: str, font: str, size: int, accent_hex: str | None) -> str:
    align, marginv = {"mid": (5, int(1920 * 0.50)), "high": (8, int(1920 * 0.22))}.get(placement, (2, int(1920 * 0.20)))
    accent_norms = {_norm(t) for t in accent_set}
    accent_tag = f"\\c{_ass_color(accent_hex)}" if accent_hex else ""
    lines = [ASS_HEADER.format(font=font, size=size, align=align, marginv=marginv)]
    for c in chunks:
        parts = []
        for w in c["words"]:
            tok = w["text"].replace("{", "(").replace("}", ")")
            if _norm(tok) in accent_norms:
                parts.append(f"{{\\b1\\i1{accent_tag}}}{tok}{{\\b0\\i0\\c}}")
            else:
                parts.append(tok)
        lines.append(f"Dialogue: 0,{_ass_time(c['start'])},{_ass_time(c['end'])},Default,,0,0,0,,{' '.join(parts)}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    args = ap.parse_args()

    concept_path = Path(args.concept).resolve()
    concept = json.loads(concept_path.read_text())
    run_root = run_root_for(concept_path)

    words_path = run_root / "audio" / "words.json"
    if not words_path.exists():
        die(f"words.json not found ({words_path}) — run render_music.py first.")
    timed = json.loads(words_path.read_text()).get("words", [])
    if not timed:
        die("words.json has no words — the song may be instrumental; cannot beat-sync captions.")

    lyrics_path = (run_root / concept.get("lyrics_locked_md", "source/lyrics-locked.md")).resolve()
    if not lyrics_path.exists():
        die(f"lyrics file not found: {lyrics_path}")
    lyric_words, line_breaks = parse_lyrics(lyrics_path)

    ov = concept.get("caption_overrides", {}) or {}
    accent_set = set(concept.get("accent_words", []) or [])
    aligned, warnings = align_to_lyrics(timed, lyric_words)
    chunks = chunk_bursts(aligned, line_breaks, int(ov.get("chunk_size", 4)), accent_set)
    ass = render_ass(
        chunks, accent_set,
        placement=ov.get("placement", "low"),
        font=ov.get("font", "Georgia"),
        size=int(ov.get("font_size", 64)),
        accent_hex=ov.get("accent_hex"),
    )

    out = ensure_dir(run_root / "working") / "captions.ass"
    out.write_text(ass)
    info(f"wrote {out} — {len(chunks)} caption chunks")
    for w in warnings:
        info(f"  caption warning: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
