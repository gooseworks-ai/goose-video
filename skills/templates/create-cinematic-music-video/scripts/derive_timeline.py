#!/usr/bin/env python3
"""S4 — derive the per-tableau TIMELINE from the actual sung word timestamps.

For each tableau, find its `lyric_anchor`'s first word in the sung words and
set that tableau's IN time to the word's start. The next tableau's IN becomes
the current tableau's OUT. Tableaux whose anchor never gets sung (lyrics longer
than the song) are distributed evenly across the gap to the next match. The
END_CARD tableau reserves a minimum hold at the end.

Beat timings vary per song — ElevenLabs never lands exactly on the spec, so the
TIMELINE is always computed per run. Never hard-code timings across runs.

Reads:  <run>/concept.json, <run>/audio/words.json
Writes: <run>/working/timeline.json   ([[tableau_id, in_s, out_s], ...])

Usage:
  python scripts/derive_timeline.py --concept <run>/concept.json [--print]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from lib import die, ensure_dir, info, run_root_for

MIN_DUR = 0.4
END_CARD_MIN = 1.0


def normalize(tok: str) -> str:
    return re.sub(r"[^a-z0-9']+", "", tok.lower())


def _first_token(anchor_text: str) -> str | None:
    for tok in re.findall(r"[A-Za-z']+", anchor_text):
        n = normalize(tok)
        if n:
            return n
    return None


def derive_timeline(concept: dict, words: list[dict]) -> list[tuple]:
    duration = float(concept.get("duration_s", 28))
    tableaux = concept["tableaux"]
    n = len(tableaux)

    flat = [(normalize(w["text"]), float(w["start"]), float(w["end"])) for w in words]
    last_word_end = flat[-1][2] if flat else duration

    # Step 1: greedy first-word anchor matching.
    anchored: list[tuple[str, float | None]] = []
    li = 0
    for t in tableaux:
        anchor_text = t.get("lyric_anchor", "") or ""
        first_tok = _first_token(anchor_text)
        if not first_tok or "intro" in anchor_text.lower():
            anchored.append((t["id"], None))
            continue
        hit = None
        for j in range(li, len(flat)):
            if flat[j][0] == first_tok:
                hit = flat[j][1]
                li = j + 1
                break
        anchored.append((t["id"], hit))

    if anchored and anchored[0][1] is None:
        anchored[0] = (anchored[0][0], 0.0)

    unanchored_ids = [tid for tid, t in anchored if t is None]
    if unanchored_ids:
        info(f"WARNING: {len(unanchored_ids)} tableau(s) had no matching lyric_anchor "
             f"in the sung words: {unanchored_ids}")
        info("         Common cause: lyrics longer than the song could sing. "
             "Distributing them evenly across the unsung gap. To resolve cleanly: "
             "shorten lyrics or regenerate the music.")

    # Step 2: distribute runs of None evenly.
    times: list[float | None] = [t for _, t in anchored]
    i = 0
    while i < n:
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < n and times[j] is None:
            j += 1
        run_len = j - i
        prev_time = times[i - 1] if i > 0 else 0.0
        if j < n:
            next_time = times[j]
            step = (next_time - prev_time) / (run_len + 1)
            for k in range(run_len):
                times[i + k] = prev_time + (k + 1) * step
        else:
            a = max(last_word_end, prev_time + MIN_DUR)
            if a >= duration:
                a = max(prev_time + MIN_DUR, duration - MIN_DUR * run_len)
            last_role = tableaux[j - 1].get("role", "")
            if last_role == "END_CARD" and run_len > 1 \
                    and (duration - a) > END_CARD_MIN + MIN_DUR * (run_len - 1):
                ec_start = duration - END_CARD_MIN
                step = (ec_start - a) / (run_len - 1)
                for k in range(run_len - 1):
                    times[i + k] = a + k * step
                times[i + run_len - 1] = ec_start
            else:
                step = (duration - a) / run_len
                for k in range(run_len):
                    times[i + k] = a + k * step
        i = j

    # Step 3: (in, out) tuples.
    out_tl: list[tuple[str, float, float]] = []
    for idx in range(n):
        tid = anchored[idx][0]
        in_s = float(times[idx])
        out_s = float(times[idx + 1]) if idx + 1 < n else duration
        out_tl.append((tid, in_s, out_s))

    # Step 4: enforce non-overlap + minimum duration, monotonic in_s.
    for idx in range(len(out_tl) - 1):
        tid, in_s, out_s = out_tl[idx]
        n_tid, n_in, n_out = out_tl[idx + 1]
        if out_s > n_in:
            out_tl[idx] = (tid, in_s, n_in)
            out_s = n_in
        if n_in < in_s:
            new_n_in = min(in_s + MIN_DUR, duration)
            out_tl[idx + 1] = (n_tid, new_n_in, max(n_out, new_n_in + MIN_DUR))
        if (out_s - in_s) < MIN_DUR:
            target_out = min(in_s + MIN_DUR, out_tl[idx + 1][1])
            out_tl[idx] = (tid, in_s, target_out)

    last_tid, last_in, last_out = out_tl[-1]
    last_out = min(last_out, duration)
    if last_out - last_in < MIN_DUR:
        last_in = max(0.0, last_out - MIN_DUR)
    out_tl[-1] = (last_tid, last_in, last_out)

    return [(tid, round(s, 3), round(e, 3)) for tid, s, e in out_tl]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    ap.add_argument("--print", action="store_true")
    args = ap.parse_args()

    concept_path = Path(args.concept).resolve()
    concept = json.loads(concept_path.read_text())
    run_root = run_root_for(concept_path)
    words_path = run_root / "audio" / "words.json"
    if not words_path.exists():
        die(f"words.json not found ({words_path}) — run render_music.py first.")

    words = json.loads(words_path.read_text()).get("words", [])
    timeline = derive_timeline(concept, words)

    out = ensure_dir(run_root / "working") / "timeline.json"
    out.write_text(json.dumps(timeline, indent=2))
    info(f"wrote {out}")
    if args.print:
        for tid, s, e in timeline:
            print(f"  {tid}: {s:6.2f}s -> {e:6.2f}s  ({e - s:.2f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
