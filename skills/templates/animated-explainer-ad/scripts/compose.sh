#!/usr/bin/env bash
# Phase 8 — ffmpeg compose: retime per-scene clips to VO line durations,
# concat, mix VO + music with ducking, burn captions, mux to finals/master.mp4.
#
# Reads:
#   <project>/scene_timing.json   (from measure_vo.py)
#   <project>/clips/scene-NN.mp4  (from render_clip.py + build_endcard.py)
#   <project>/audio/vo/vo-NN-*.mp3 (from render_vo.py)
#   <project>/audio/music.mp3     (from render_music.py)
#   <project>/audio/captions.ass  (from make_captions.py)
#
# Writes:
#   <project>/finals/master.mp4
#
# Usage:
#   bash scripts/compose.sh ./my-ad/ [atempo]
#   atempo defaults to 1.0; set to 1.2-1.3 if the VO read came back slow.

set -euo pipefail

PROJECT="${1:?usage: compose.sh <project-dir> [atempo]}"
ATEMPO="${2:-1.0}"

PROJECT="$(cd "$PROJECT" && pwd)"
TIMING="$PROJECT/scene_timing.json"
CLIPS="$PROJECT/clips"
VO_DIR="$PROJECT/audio/vo"
MUSIC="$PROJECT/audio/music.mp3"
CAPS="$PROJECT/audio/captions.ass"
WORK="$PROJECT/.work"
FINAL="$PROJECT/finals/master.mp4"

mkdir -p "$WORK" "$PROJECT/finals"
rm -f "$WORK"/seg-*.mp4 "$WORK"/vo-*.wav "$WORK"/concat.txt "$WORK"/voconcat.txt

[ -f "$TIMING" ] || { echo "ERROR: $TIMING not found — run measure_vo.py first"; exit 1; }

# Parse scene_timing.json without jq dependency (use python3).
read_scenes() {
  python3 -c "
import json, sys
t = json.load(open('$TIMING'))
for s in t['scenes']:
    print(s['scene'], s['target_duration_sec'], s['vo_file'])
print('ENDCARD', t.get('endcard_duration_sec', 4.0), '')
"
}

echo "[1/7] retiming per-scene video segments..."
: > "$WORK/concat.txt"
ENDCARD_DUR=""
while IFS=' ' read -r scene dur vo_file; do
  if [ "$scene" = "ENDCARD" ]; then
    ENDCARD_DUR="$dur"
    continue
  fi
  clip="$CLIPS/scene-$scene.mp4"
  [ -f "$clip" ] || { echo "ERROR: missing $clip"; exit 1; }
  src_dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$clip")
  vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1"
  pad=$(python3 -c "print(max(0, $dur - $src_dur))")
  if python3 -c "import sys; sys.exit(0 if $pad > 0.05 else 1)"; then
    vf="$vf,tpad=stop_mode=clone:stop_duration=$pad"
  fi
  ffmpeg -y -loglevel error -i "$clip" -vf "$vf" -t "$dur" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -an \
    "$WORK/seg-$scene.mp4"
  echo "file 'seg-$scene.mp4'" >> "$WORK/concat.txt"
  printf "  scene-%s  clip %.2fs -> %.2fs\n" "$scene" "$src_dur" "$dur"
done < <(read_scenes)

# Append the end-card clip if present (looks for highest-numbered scene-*.mp4 not in scene_timing).
LAST_TIMED=$(python3 -c "
import json
t = json.load(open('$TIMING'))
print(max(int(s['scene']) for s in t['scenes']))
")
ENDCARD_ID=$(printf "%02d" $((LAST_TIMED + 1)))
ENDCARD_CLIP="$CLIPS/scene-$ENDCARD_ID.mp4"
if [ -f "$ENDCARD_CLIP" ]; then
  ec_src_dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$ENDCARD_CLIP")
  ffmpeg -y -loglevel error -i "$ENDCARD_CLIP" \
    -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1" \
    -t "${ENDCARD_DUR:-4.0}" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -an \
    "$WORK/seg-$ENDCARD_ID.mp4"
  echo "file 'seg-$ENDCARD_ID.mp4'" >> "$WORK/concat.txt"
  printf "  scene-%s  endcard %.2fs -> %.2fs\n" "$ENDCARD_ID" "$ec_src_dur" "${ENDCARD_DUR:-4.0}"
else
  echo "  (no end-card clip $ENDCARD_CLIP — skipping)"
fi

echo "[2/7] concat video segments..."
ffmpeg -y -loglevel error -f concat -safe 0 -i "$WORK/concat.txt" -c copy "$WORK/video.mp4"

echo "[3/7] VO track (atempo $ATEMPO)..."
: > "$WORK/voconcat.txt"
while IFS=' ' read -r scene dur vo_file; do
  if [ "$scene" = "ENDCARD" ]; then continue; fi
  vo_abs="$PROJECT/$vo_file"
  [ -f "$vo_abs" ] || { echo "ERROR: missing VO $vo_abs"; exit 1; }
  ffmpeg -y -loglevel error -i "$vo_abs" \
    -af "atempo=$ATEMPO,apad" -t "$dur" -ar 44100 -ac 2 "$WORK/vo-$scene.wav"
  echo "file 'vo-$scene.wav'" >> "$WORK/voconcat.txt"
done < <(read_scenes)

# Silent track for the end card.
if [ -f "$ENDCARD_CLIP" ]; then
  ffmpeg -y -loglevel error -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
    -t "${ENDCARD_DUR:-4.0}" -ar 44100 -ac 2 "$WORK/vo-$ENDCARD_ID.wav"
  echo "file 'vo-$ENDCARD_ID.wav'" >> "$WORK/voconcat.txt"
fi

ffmpeg -y -loglevel error -f concat -safe 0 -i "$WORK/voconcat.txt" -c copy "$WORK/vo-track.wav"
TOTAL=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$WORK/vo-track.wav")
echo "  total runtime: ${TOTAL}s"

echo "[4/7] music bed (fit + fade)..."
if [ -f "$MUSIC" ]; then
  FADE=$(python3 -c "print(max(0, $TOTAL - 1.4))")
  ffmpeg -y -loglevel error -i "$MUSIC" \
    -af "afade=t=in:st=0:d=0.6,afade=t=out:st=$FADE:d=1.4" -t "$TOTAL" \
    -ar 44100 -ac 2 "$WORK/music.wav"
else
  echo "  WARN: no music at $MUSIC — silent bed"
  ffmpeg -y -loglevel error -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
    -t "$TOTAL" -ar 44100 -ac 2 "$WORK/music.wav"
fi

echo "[5/7] mix VO (-14 LUFS) + music (-26 LUFS, ducked)..."
ffmpeg -y -loglevel error -i "$WORK/vo-track.wav" -i "$WORK/music.wav" \
  -filter_complex "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[vo];\
[1:a]loudnorm=I=-26:TP=-3:LRA=11,volume=0.62[mus];\
[vo][mus]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]" \
  -map "[a]" -ar 44100 -ac 2 "$WORK/mix.wav"

echo "[6/7] burn captions + mux -> master..."
if [ -f "$CAPS" ]; then
  ffmpeg -y -loglevel error -i "$WORK/video.mp4" -i "$WORK/mix.wav" \
    -vf "ass=$CAPS" \
    -map 0:v -map 1:a -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 \
    -c:a aac -b:a 192k -shortest "$FINAL"
else
  echo "  WARN: no captions at $CAPS — master without burned captions"
  ffmpeg -y -loglevel error -i "$WORK/video.mp4" -i "$WORK/mix.wav" \
    -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest "$FINAL"
fi

echo "[7/7] self-QC..."
MASTER_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL")
MASTER_SIZE=$(ls -la "$FINAL" | awk '{print $5}')
echo "  duration: ${MASTER_DUR}s"
echo "  size: ${MASTER_SIZE} bytes"
echo
echo "DONE — $FINAL"
echo "Run loudnorm pass to verify:"
echo "  ffmpeg -i $FINAL -af 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json' -f null - 2>&1 | tail -20"
