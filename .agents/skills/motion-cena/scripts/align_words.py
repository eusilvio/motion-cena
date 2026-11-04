# /// script
# requires-python = ">=3.10"
# dependencies = ["faster-whisper>=1.0", "numpy"]
# ///
"""Word-level timestamps for any audio (Higgsfield, user recording, local TTS).

Usage:
  uv run align_words.py audio/voice.mp3 --lang pt --model small --out audio/words.json [--script narration.txt]
With --script, transcribed words are replaced by the script's spelling (timing kept).
"""
import argparse
import difflib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel


def norm(token: str) -> str:
    token = unicodedata.normalize("NFKD", token.lower())
    token = "".join(c for c in token if not unicodedata.combining(c))
    return re.sub(r"[^\w%]", "", token)


def load_audio(path: Path) -> np.ndarray:
    """Decode with ffmpeg (avoids PyAV version breakage) -> 16 kHz mono float32."""
    raw = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(raw, np.float32)


def apply_script_spelling(words: list[dict], script: str) -> list[dict]:
    script_tokens = script.split()
    matcher = difflib.SequenceMatcher(
        a=[norm(w["word"]) for w in words], b=[norm(t) for t in script_tokens], autojunk=False
    )
    for block in matcher.get_matching_blocks():
        for k in range(block.size):
            words[block.a + k]["word"] = script_tokens[block.b + k]
    return words


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    parser.add_argument("--lang", default="pt")
    parser.add_argument("--model", default="small", help="tiny|base|small|medium|large-v3")
    parser.add_argument("--script", type=Path, help="narration text to fix spelling")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    model = WhisperModel(args.model, device="auto", compute_type="int8")
    segments, _ = model.transcribe(load_audio(args.audio), language=args.lang, word_timestamps=True, vad_filter=True)
    words = [
        {"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
        for seg in segments for w in seg.words if w.word.strip()
    ]
    if args.script:
        words = apply_script_spelling(words, args.script.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(words, ensure_ascii=False, indent=1))
    print(f"{len(words)} words -> {args.out}")


if __name__ == "__main__":
    main()
