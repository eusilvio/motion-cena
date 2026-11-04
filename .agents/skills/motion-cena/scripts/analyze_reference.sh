#!/usr/bin/env bash
# Break down a reference video so its style can be studied and turned into a recipe.
# Usage: bash analyze_reference.sh <video.mp4> <out_dir> [lang]
# Writes: probe.txt, sheet-NN.jpg (2 fps contact sheets with timecode), key-*.png (full-res
# frames at 10/50/90%), words.json (word timestamps via align_words.py), loudness.txt.
# Then LOOK at the sheets and frames and write the style recipe (references/styles/README.md).
set -euo pipefail
export LC_ALL=C

VIDEO="${1:?usage: analyze_reference.sh video.mp4 out_dir [lang]}"
OUT="${2:?out_dir}"
LANG_CODE="${3:-pt}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"

ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate -of compact "$VIDEO" > "$OUT/probe.txt"
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VIDEO")

# 2 fps sheets, 32 frames (16 s) per sheet
SHEETS=$(awk -v d="$DUR" 'BEGIN{print int(d/16)+1}')
for ((i = 0; i < SHEETS; i++)); do
  ffmpeg -v error -y -ss $((i * 16)) -i "$VIDEO" \
    -vf "fps=2,scale=240:-1,drawtext=text='%{pts\:hms}':x=6:y=6:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.6,tile=8x4" \
    -frames:v 1 "$OUT/sheet-$(printf %02d $((i + 1))).jpg"
done

for p in 10 50 90; do
  t=$(awk -v d="$DUR" -v p="$p" 'BEGIN{printf "%.2f", d*p/100}')
  ffmpeg -v error -y -ss "$t" -i "$VIDEO" -frames:v 1 "$OUT/key-$p.png"
done

if ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 "$VIDEO" | grep -q .; then
  ffmpeg -hide_banner -nostats -i "$VIDEO" -af ebur128 -f null - 2>&1 | grep -A2 "Integrated loudness" | tail -2 > "$OUT/loudness.txt" || true
  uv run -q "$HERE/align_words.py" "$VIDEO" --lang "$LANG_CODE" --out "$OUT/words.json" || echo "transcription failed (no speech?)"
fi

echo "duration ${DUR}s -> $OUT ($SHEETS sheet(s), key frames, words.json)"
