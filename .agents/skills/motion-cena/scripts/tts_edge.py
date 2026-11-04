# /// script
# requires-python = ">=3.10"
# dependencies = ["edge-tts>=7.0"]
# ///
"""Free TTS via Microsoft Edge voices, with word-level timestamps.

Usage:
  uv run tts_edge.py --text-file narration.txt --voice pt-BR-FranciscaNeural --out audio/
Outputs: <out>/voice.mp3, <out>/words.json ([{word, start, end}] in seconds)
"""
import argparse
import asyncio
import json
from pathlib import Path

import edge_tts

TICKS_PER_SECOND = 10_000_000  # edge-tts offsets are in 100ns units


async def synthesize(text: str, voice: str, rate: str, pitch: str, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    words = []
    with open(out_dir / "voice.mp3", "wb") as audio:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / TICKS_PER_SECOND
                words.append({
                    "word": chunk["text"],
                    "start": round(start, 3),
                    "end": round(start + chunk["duration"] / TICKS_PER_SECOND, 3),
                })
    (out_dir / "words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1))
    duration = words[-1]["end"] if words else 0
    print(f"voice.mp3 + words.json ({len(words)} words, ~{duration:.1f}s) -> {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="narration text")
    src.add_argument("--text-file", type=Path, help="file with narration text")
    parser.add_argument("--voice", default="pt-BR-FranciscaNeural")
    parser.add_argument("--rate", default="+8%", help="speed, e.g. +8%% or -5%%")
    parser.add_argument("--pitch", default="+0Hz")
    parser.add_argument("--out", type=Path, required=True, help="output directory")
    args = parser.parse_args()
    text = args.text if args.text else args.text_file.read_text(encoding="utf-8")
    asyncio.run(synthesize(" ".join(text.split()), args.voice, args.rate, args.pitch, args.out))


if __name__ == "__main__":
    main()
