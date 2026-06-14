#!/bin/bash
# Convert any end-card PNG (e.g. one rendered by the goose-graphics skill) into
# the static 3.5s MP4 the stitch step expects. No Ken-Burns — the slate lands hard.
#
# Handles any aspect ratio: a 9:16 (story) image fills exactly; a square (tweet)
# or other ratio is centered on a 1080x1920 canvas, padded with the card's own
# background colour (auto-sampled from the top-left pixel) so the seam is invisible.
#
# Usage:  bash scripts/endcard-to-mp4.sh <end-card.png> <project-dir> [bg-hex]
# Writes: <project>/clips/scene-09-endcard.mp4
set -euo pipefail

PNG="${1:?usage: endcard-to-mp4.sh <end-card.png> <project-dir> [bg-hex]}"
AD="${2:?usage: endcard-to-mp4.sh <end-card.png> <project-dir> [bg-hex]}"
BG_IN="${3:-}"
AD="$(cd "$AD" && pwd)"
mkdir -p "$AD/clips"
OUT="$AD/clips/scene-09-endcard.mp4"

# Pad colour: explicit 3rd arg, else auto-sample the PNG's top-left pixel.
if [ -n "$BG_IN" ]; then
  BG="0x${BG_IN/#\#/}"
else
  HEX=$(ffmpeg -v error -i "$PNG" -vf "crop=8:8:0:0,scale=1:1" -frames:v 1 \
        -f rawvideo -pix_fmt rgb24 - 2>/dev/null | xxd -p | tr -d '\n' | head -c 6)
  BG="0x${HEX:-000000}"
fi

# decrease+pad = exact fit for 9:16, centered letterbox for square/other ratios.
ffmpeg -y -loop 1 -i "$PNG" -t 3.5 -r 30 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=${BG},format=yuv420p" \
  -c:v libx264 -pix_fmt yuv420p -movflags +faststart "$OUT" >/dev/null 2>&1

echo "end card → $OUT (pad ${BG})"
