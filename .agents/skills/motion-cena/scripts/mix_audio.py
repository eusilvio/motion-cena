# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Mix voice + SFX cues (+ optional ducked music) into one track, loudness-normalized. Needs ffmpeg.

Usage:
  uv run mix_audio.py timeline.json --voice audio/voice.mp3 --sfx-dir audio/sfx [--music bed.mp3] --out audio/mix.wav

Cue file resolution: cue.file (relative to --sfx-dir) or <sfx-dir>/<cue.type>.(wav|mp3).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def resolve(cue: dict, sfx_dir: Path) -> Path | None:
    if cue.get("file"):
        p = Path(cue["file"])
        p = p if p.is_absolute() else sfx_dir / p
        return p if p.exists() else None
    for ext in ("wav", "mp3", "ogg"):
        p = sfx_dir / f"{cue['type']}.{ext}"
        if p.exists():
            return p
    return None


def main() -> None:
    for stream in (sys.stdout, sys.stderr):  # Windows consoles and pipes default to cp1252
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("timeline", type=Path)
    parser.add_argument("--voice", type=Path, required=True)
    parser.add_argument("--sfx-dir", type=Path)
    parser.add_argument("--music", type=Path)
    parser.add_argument("--music-db", type=float, default=-20, help="music level under voice")
    parser.add_argument("--lufs", type=float, default=-14)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    duration = timeline["meta"]["duration"]
    inputs = ["-i", str(args.voice)]
    filters = ["[0:a]aresample=48000,aformat=channel_layouts=stereo,apad[voice]"]
    sfx_labels = []

    for cue in timeline.get("sfx_cues", []) if args.sfx_dir else []:
        path = resolve(cue, args.sfx_dir)
        if path is None:
            print(f"WARN: no file for sfx '{cue.get('type')}' at {cue['time']}s", file=sys.stderr)
            continue
        idx = len(inputs) // 2
        inputs += ["-i", str(path)]
        delay = int(cue["time"] * 1000)
        gain = cue.get("gain_db", -14)
        label = f"s{idx}"
        filters.append(
            f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
            f"volume={gain}dB,adelay={delay}|{delay}[{label}]"
        )
        sfx_labels.append(f"[{label}]")

    bus = "[voice]"
    if args.music:
        idx = len(inputs) // 2
        inputs += ["-stream_loop", "-1", "-i", str(args.music)]
        filters.append("[voice]asplit=2[voice][vkey]")
        filters.append(
            f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={args.music_db}dB,"
            f"afade=t=out:st={max(0, duration - 1.2)}:d=1.2[mraw]"
        )
        filters.append("[mraw][vkey]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=300[music]")
        sfx_labels.append("[music]")

    if sfx_labels:
        filters.append(f"{bus}{''.join(sfx_labels)}amix=inputs={1 + len(sfx_labels)}:normalize=0:duration=first[sum]")
        bus = "[sum]"
    filters.append(f"{bus}atrim=0:{duration},loudnorm=I={args.lufs}:TP=-1:LRA=11,aresample=48000[out]")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
           "-filter_complex", ";".join(filters), "-map", "[out]", "-c:a", "pcm_s16le", str(args.out)]
    subprocess.run(cmd, check=True)
    print(f"mix: voice + {len(sfx_labels) - (1 if args.music else 0)} sfx"
          f"{' + music' if args.music else ''}, {duration:.2f}s -> {args.out}")


if __name__ == "__main__":
    main()
