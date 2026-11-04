#!/usr/bin/env bash
# Technical QA for a rendered video + contact sheet for visual review.
# Usage: [QA_DIR=projects/<slug>/out] bash qa_video.sh creatives/reels/<slug>-<preset>.mp4 [<preset> | expected_width expected_height expected_fps]
#   <preset>: id from assets/platforms.json (ig-reels, ig-stories, tiktok, yt-shorts, yt-long, ...)
#             -> canvas, fps and max duration come from the preset.
# QA_DIR: where the contact sheet / first frame go (default: next to the video).
set -euo pipefail
export LC_ALL=C  # decimal point, not comma, in printf/awk

VIDEO="${1:?usage: qa_video.sh video.mp4 [w h fps]}"
MAX_DUR=""
if [ -n "${2:-}" ] && ! [[ "$2" =~ ^[0-9]+$ ]]; then
  PRESET_ENV=$(uv run -q "$(dirname "$0")/platform_preset.py" "$2" --shell) || exit 2
  eval "$PRESET_ENV"
  EXP_W=$W; EXP_H=$H; EXP_FPS=$FPS; MAX_DUR=$MAX
else
  EXP_W="${2:-1080}"; EXP_H="${3:-1920}"; EXP_FPS="${4:-30}"
fi
BASE="${VIDEO%.*}"
if [ -n "${QA_DIR:-}" ]; then mkdir -p "$QA_DIR"; BASE="$QA_DIR/$(basename "$BASE")"; fi
FAIL=0

probe() { ffprobe -v error -select_streams "$1" -show_entries "$2" -of default=nw=1:nk=1 "$VIDEO" | head -1; }

W=$(probe v:0 stream=width); H=$(probe v:0 stream=height)
FPS_RAW=$(probe v:0 stream=r_frame_rate); FPS=$(awk -F/ '{printf "%.2f", $1/($2?$2:1)}' <<<"$FPS_RAW")
VCODEC=$(probe v:0 stream=codec_name); PIXFMT=$(probe v:0 stream=pix_fmt)
ACODEC=$(probe a:0 stream=codec_name || true)
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VIDEO")

check() { if [ "$2" = "ok" ]; then echo "  OK   $1"; else echo "  FAIL $1"; FAIL=1; fi; }

echo "== $VIDEO"
check "resolution ${W}x${H} (expected ${EXP_W}x${EXP_H})" "$([ "$W" = "$EXP_W" ] && [ "$H" = "$EXP_H" ] && echo ok)"
check "fps $FPS (expected $EXP_FPS)" "$(awk -v a="$FPS" -v b="$EXP_FPS" 'BEGIN{print (a-b<0.1 && b-a<0.1)?"ok":""}')"
check "video codec $VCODEC / $PIXFMT (want h264 / yuv420p)" "$([ "$VCODEC" = "h264" ] && [ "$PIXFMT" = "yuv420p" ] && echo ok)"
check "audio track ${ACODEC:-none}" "$([ -n "$ACODEC" ] && echo ok)"
printf "  INFO duration %.2fs\n" "$DUR"
if [ -n "$MAX_DUR" ]; then
  check "duration <= ${MAX_DUR}s (preset $2)" "$(awk -v d="$DUR" -v m="$MAX_DUR" 'BEGIN{print (d<=m)?"ok":""}')"
fi

if [ -n "$ACODEC" ]; then
  LOUD=$(ffmpeg -hide_banner -nostats -i "$VIDEO" -af loudnorm=print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  I=$(grep '"input_i"' <<<"$LOUD" | grep -o '[-0-9.]*' | head -1)
  TP=$(grep '"input_tp"' <<<"$LOUD" | grep -o '[-0-9.]*' | head -1)
  check "loudness ${I} LUFS (want -16..-12)" "$(awk -v i="$I" 'BEGIN{print (i>=-16.5 && i<=-11.5)?"ok":""}')"
  check "true peak ${TP} dBTP (want <= -1)" "$(awk -v p="$TP" 'BEGIN{print (p<=-0.9)?"ok":""}')"
  SIL=$(ffmpeg -hide_banner -nostats -i "$VIDEO" -af silencedetect=n=-45dB:d=1.5 -f null - 2>&1 | grep -c silence_start || true)
  check "no silent gaps > 1.5s (found $SIL)" "$([ "$SIL" = "0" ] && echo ok)"
fi

# Contact sheet: 12 evenly spaced frames, plus first frame (hook check).
# With a preset, the platform UI zones are tinted red: nothing that matters may sit there.
# 240 px per frame: a model downsizes a 6x2 sheet of wider frames to about this size anyway, so
# wider frames only cost tokens (at 200 px the small captions start to blur).
ZONES=""
if [ -n "${ST:-}" ]; then
  ZONES="drawbox=x=0:y=0:w=iw:h=${ST}:color=red@0.16:t=fill,drawbox=x=0:y=ih-${SB}:w=iw:h=${SB}:color=red@0.16:t=fill,"
  ZONES+="drawbox=x=0:y=${ST}:w=${SL}:h=ih-${ST}-${SB}:color=red@0.16:t=fill,drawbox=x=iw-${SR}:y=${ST}:w=${SR}:h=ih-${ST}-${SB}:color=red@0.16:t=fill,"
  ZONES+="drawbox=x=${SL}:y=${ST}:w=iw-${SL}-${SR}:h=ih-${ST}-${SB}:color=red@0.9:t=6,"
fi
ffmpeg -hide_banner -loglevel error -y -i "$VIDEO" \
  -vf "fps=12/${DUR},${ZONES}scale=240:-1,drawtext=text='%{pts\:hms}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile=6x2" \
  -frames:v 1 "${BASE}_contact.jpg"
ffmpeg -hide_banner -loglevel error -y -i "$VIDEO" -frames:v 1 -vf scale=540:-1 "${BASE}_frame0.jpg"
echo "  contact sheet: ${BASE}_contact.jpg  first frame: ${BASE}_frame0.jpg"

if [ "$FAIL" = "0" ]; then
  echo "RESULT: PASS (now review the images)"
else
  echo "RESULT: FAIL"
  exit 1
fi
