#!/usr/bin/env python3
"""S8 — compose the final master.

  1. Retime each tableau clip to its TIMELINE slot at 1080x1920 / 30fps.
     (The END_CARD slot uses the PIL end-card clip, never an i2v clip.)
  2. Concat segments -> silent master.
  3. Mux the music bed with fades + loudnorm to -14 LUFS.
  4. Burn word-synced captions with a libass-enabled ffmpeg.

Reads:  <run>/concept.json, <run>/working/timeline.json,
        <run>/assets/clips/T*.mp4 (+ endcard.mp4), <run>/audio/music.mp3,
        <run>/working/captions.ass (auto-generated if absent)
Writes: <run>/finals/master-final.mp4  (the deliverable) + master-final.ass

Usage:
  python scripts/compose.py --concept <run>/concept.json
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from lib import ensure_dir, ffmpeg_with_libass, ffprobe_duration, info, run_root_for

SCRIPTS = Path(__file__).resolve().parent


def _ff(cmd: list[str]) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *cmd], check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    args = ap.parse_args()

    concept_path = Path(args.concept).resolve()
    concept = json.loads(concept_path.read_text())
    run_root = run_root_for(concept_path)
    duration = float(concept.get("duration_s", 28))

    clips_dir = run_root / "assets" / "clips"
    audio = run_root / "audio" / "music.mp3"
    timeline_path = run_root / "working" / "timeline.json"
    working = ensure_dir(run_root / "working")
    seg_dir = ensure_dir(working / "segments")
    silent = working / "master-silent.mp4"
    no_caps = working / "master-no-captions.mp4"
    final = ensure_dir(run_root / "finals") / "master-final.mp4"

    if not timeline_path.exists():
        sys.exit(f"ERROR: timeline.json missing — run derive_timeline.py first ({timeline_path})")
    if not audio.exists():
        sys.exit(f"ERROR: music.mp3 missing — run render_music.py first ({audio})")
    timeline = json.loads(timeline_path.read_text())

    # Which tableau is the end card? Its slot uses the PIL end-card clip.
    end_id = next((t["id"] for t in concept["tableaux"] if t.get("role") == "END_CARD"), None)
    endcard_clip = clips_dir / "endcard.mp4"

    # 1. Retime each segment to its slot.
    info("[1/4] retiming segments to the beat timeline...")
    concat_lines = []
    for tid, s, e in timeline:
        src = endcard_clip if (tid == end_id and endcard_clip.exists()) else clips_dir / f"{tid}.mp4"
        if not src.exists():
            sys.exit(f"ERROR: clip missing for {tid}: {src}")
        dur = e - s
        dst = seg_dir / f"seg_{tid}.mp4"
        vf = (f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
              f"fps=30,setsar=1,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={dur:.3f}")
        _ff(["-i", str(src), "-t", f"{dur:.3f}", "-vf", vf, "-an",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
             "-preset", "medium", "-crf", "18", str(dst)])
        concat_lines.append(f"file '{dst.name}'")
        info(f"  {tid}: {s:6.2f}s -> {e:6.2f}s  ({dur:.2f}s)")

    # 2. Concat.
    info("[2/4] concatenating...")
    listfile = seg_dir / "concat.txt"
    listfile.write_text("\n".join(concat_lines) + "\n")
    _ff(["-f", "concat", "-safe", "0", "-i", str(listfile), "-c", "copy", str(silent)])

    # 3. Mux music + loudnorm.
    info("[3/4] muxing music + loudnorm -14 LUFS...")
    out_fade = max(0.0, duration - 0.6)
    _ff(["-i", str(silent), "-i", str(audio),
         "-filter_complex",
         f"[1:a]atrim=0:{duration},afade=t=in:st=0:d=0.15,"
         f"afade=t=out:st={out_fade:.3f}:d=0.6,loudnorm=I=-14:LRA=11:tp=-1.0[aout]",
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(no_caps)])

    # 4. Captions: auto-generate the .ass if missing, then burn (or ship uncaptioned).
    info("[4/4] burning captions...")
    ass = working / "captions.ass"
    if not ass.exists():
        subprocess.run([sys.executable, str(SCRIPTS / "make_captions.py"), "--concept", str(concept_path)], check=False)
    if ass.exists():
        shutil.copy(ass, final.with_suffix(".ass"))
        ffbin = ffmpeg_with_libass()
        # Run from the .ass directory so the subtitles path needs no escaping.
        subprocess.run(
            [ffbin, "-y", "-loglevel", "error", "-i", str(no_caps),
             "-vf", f"ass={ass.name}",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
             "-c:a", "copy", str(final)],
            check=True, cwd=str(working),
        )
    else:
        info("  no captions.ass — shipping master without burned captions")
        shutil.copy(no_caps, final)

    dur_final = ffprobe_duration(final)
    size_mb = final.stat().st_size / 1e6
    info(f"\n[DONE] {final}")
    info(f"       {dur_final:.1f}s · 1080x1920 · h264+aac · -14 LUFS · {size_mb:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
