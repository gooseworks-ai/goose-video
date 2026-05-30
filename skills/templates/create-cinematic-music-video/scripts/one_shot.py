#!/usr/bin/env python3
"""One-shot driver for create-cinematic-music-video.

Walks the 10-state pipeline from a concept.json. Idempotent + resumable via
.state.json. Pauses at Gate 2 (storyboard) and Gate 3 (T01 keyframe) unless
--continue is passed.

States:
  S0  INTAKE      validate concept.json
  S1  STORYBOARD  require storyboard.html              (Gate 2)
  S2  MUSIC       render_music.py   -> music.mp3 + words.json
  S3  TIMELINE    derive_timeline.py -> timeline.json
  S4  KF_T01      render_keyframes.py T01              (Gate 3)
  S5  KF_BATCH    render_keyframes.py (the rest)
  S6  CLIPS       render_clips.py
  S7  ENDCARD     build_endcard.py  -> endcard.mp4
  S8  CAPTIONS    make_captions.py  -> captions.ass
  S9  COMPOSE     compose.py        -> finals/master-final.mp4

Usage:
  python scripts/one_shot.py --concept <run>/concept.json              # run to next gate
  python scripts/one_shot.py --concept <run>/concept.json --from S5    # resume at a state
  python scripts/one_shot.py --concept <run>/concept.json --continue   # skip gates (auto mode)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

STATES = ["S0_INTAKE", "S1_STORYBOARD", "S2_MUSIC", "S3_TIMELINE", "S4_KF_T01",
          "S5_KF_BATCH", "S6_CLIPS", "S7_ENDCARD", "S8_CAPTIONS", "S9_COMPOSE"]

GATE_AFTER = {
    "S1_STORYBOARD": "Gate 2 — open storyboard.html and approve the 14 tableaux + look pack + music vibe.",
    "S4_KF_T01": "Gate 3 — open assets/keyframes/T01.png and confirm the look pack landed.",
}


def _py(script: str, *script_args: str) -> None:
    subprocess.run([sys.executable, str(SCRIPTS / script), *script_args], check=True)


def run_step(sid: str, run_root: Path, concept_path: Path) -> None:
    c = str(concept_path)
    concept = json.loads(concept_path.read_text())

    if sid == "S0_INTAKE":
        for req in ["brand", "run_slug", "duration_s", "look_pack", "music", "tableaux"]:
            if req not in concept:
                sys.exit(f"concept.json missing required field: {req}")
        n = len(concept["tableaux"])
        if n != 14:
            print(f"WARNING: expected 14 tableaux, got {n}")
        print(f"[OK] intake — {concept['brand']}/{concept['run_slug']} ({concept['look_pack']}, {n} tableaux)")

    elif sid == "S1_STORYBOARD":
        sb = run_root / "storyboard.html"
        if sb.exists():
            print(f"[OK] storyboard exists at {sb}")
        else:
            print(f"[!] no storyboard.html at {sb} — write one as the Gate 2 review surface "
                  "before approving the run (continuing).")

    elif sid == "S2_MUSIC":
        if (run_root / "audio" / "music.mp3").exists() and (run_root / "audio" / "words.json").exists():
            print("[skip] music.mp3 + words.json exist")
        else:
            _py("render_music.py", "--concept", c)

    elif sid == "S3_TIMELINE":
        if (run_root / "working" / "timeline.json").exists():
            print("[skip] timeline.json exists")
        else:
            _py("derive_timeline.py", "--concept", c, "--print")

    elif sid == "S4_KF_T01":
        if (run_root / "assets" / "keyframes" / "T01.png").exists():
            print("[skip] T01.png exists")
        else:
            _py("render_keyframes.py", "--concept", c, "T01")

    elif sid == "S5_KF_BATCH":
        _py("render_keyframes.py", "--concept", c)  # idempotent — fills in the rest

    elif sid == "S6_CLIPS":
        _py("render_clips.py", "--concept", c)  # idempotent — skips end card + existing

    elif sid == "S7_ENDCARD":
        if (run_root / "assets" / "clips" / "endcard.mp4").exists():
            print("[skip] endcard.mp4 exists")
        else:
            _py("build_endcard.py", "--concept", c)

    elif sid == "S8_CAPTIONS":
        if (run_root / "working" / "captions.ass").exists():
            print("[skip] captions.ass exists")
        else:
            _py("make_captions.py", "--concept", c)

    elif sid == "S9_COMPOSE":
        if (run_root / "finals" / "master-final.mp4").exists():
            print("[OK] master-final.mp4 already exists")
        else:
            _py("compose.py", "--concept", c)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    ap.add_argument("--from", dest="from_state", help="resume at a state (S0..S9)")
    ap.add_argument("--continue", dest="cont", action="store_true", help="skip human gates (auto mode)")
    args = ap.parse_args()

    concept_path = Path(args.concept).resolve()
    run_root = concept_path.parent
    state_file = run_root / ".state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {"completed": []}

    start = 0
    if args.from_state:
        match = [i for i, s in enumerate(STATES) if s.startswith(args.from_state)]
        if not match:
            sys.exit(f"unknown --from {args.from_state}")
        start = match[0]

    for i, sid in enumerate(STATES):
        if i < start or sid in state["completed"]:
            if i >= start:
                print(f"[skip] {sid} (already completed)")
            continue
        print(f"\n=== {sid} ===")
        run_step(sid, run_root, concept_path)
        state["completed"].append(sid)
        state_file.write_text(json.dumps(state, indent=2))
        if sid in GATE_AFTER and not args.cont:
            print(f"\n[GATE] {GATE_AFTER[sid]}")
            print(f"Resume with: python {Path(__file__).name} --concept {args.concept} --from S{i + 1}")
            return 0

    print("\n[OK] pipeline complete — see finals/master-final.mp4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
