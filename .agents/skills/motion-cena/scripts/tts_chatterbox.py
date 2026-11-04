# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox@5de7a54aa4e5e2baadb0182dde554908b48b85c2", "torch==2.6.0", "torchaudio==2.6.0"]
#
# [[tool.uv.index]]
# name = "pytorch-cpu"
# url = "https://download.pytorch.org/whl/cpu"
# explicit = true
#
# [tool.uv.sources]
# torch = { index = "pytorch-cpu" }
# torchaudio = { index = "pytorch-cpu" }
# ///
"""Voice-cloned TTS with Chatterbox Multilingual V3 (MIT), running locally on CPU.

Usage:
  uv run tts_chatterbox.py --text-file projects/<slug>/narration.txt --ref training/voz/ref.wav --out projects/<slug>/audio [--lang pt]
Then word timestamps (Chatterbox has none):
  uv run align_words.py projects/<slug>/audio/voice.mp3 --lang pt --out projects/<slug>/audio/words.json

--ref: 10–15 s of the user's OWN voice, clean (no music, no other voices). Only clone a
voice with its owner's consent. Output carries Resemble AI's inaudible Perth watermark.
Writes <out>/voice.wav and <out>/voice.mp3.
"""
import argparse
import re
import subprocess
import time
from pathlib import Path

import torch
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS


def sentences(text: str, max_chars: int = 220) -> list[str]:
    """Split on sentence ends; long sentences split on commas so each chunk stays stable."""
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text.strip()) if p.strip()]
    out = []
    for p in parts:
        while len(p) > max_chars:
            cut = p.rfind(",", 0, max_chars)
            cut = cut if cut > 40 else max_chars
            out.append(p[: cut + 1].strip())
            p = p[cut + 1 :].strip()
        out.append(p)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-file", type=Path, required=True)
    ap.add_argument("--ref", type=Path, required=True, help="clean 10–15 s clip of the speaker")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--lang", default="pt")
    ap.add_argument("--exaggeration", type=float, default=0.5, help="0.25 calm … 0.7 expressive")
    ap.add_argument("--cfg", type=float, default=0.5, help="lower (0.3) = slower, closer to the reference pacing")
    ap.add_argument("--pause", type=float, default=0.25, help="silence between sentences (s)")
    ap.add_argument("--threads", type=int, default=0)
    args = ap.parse_args()

    if args.threads:
        torch.set_num_threads(args.threads)
    t0 = time.time()
    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu", t3_model="v3")
    print(f"model loaded in {time.time() - t0:.0f}s")

    chunks = sentences(args.text_file.read_text(encoding="utf-8"))
    gap = torch.zeros(1, int(model.sr * args.pause))
    pieces = []
    for i, s in enumerate(chunks, 1):
        t1 = time.time()
        wav = model.generate(s, language_id=args.lang, audio_prompt_path=str(args.ref),
                             exaggeration=args.exaggeration, cfg_weight=args.cfg)
        pieces += [wav, gap]
        print(f"[{i}/{len(chunks)}] {wav.shape[-1] / model.sr:.1f}s audio in {time.time() - t1:.0f}s: {s[:60]}")

    args.out.mkdir(parents=True, exist_ok=True)
    full = torch.cat(pieces[:-1], dim=-1)
    ta.save(str(args.out / "voice.wav"), full, model.sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(args.out / "voice.wav"), "-b:a", "192k",
                    str(args.out / "voice.mp3")], check=True)
    print(f"{full.shape[-1] / model.sr:.1f}s -> {args.out / 'voice.mp3'} (total {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
