# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["demucs==4.0.1", "torch==2.6.0", "torchaudio==2.6.0", "soundfile>=0.12"]
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
"""Pull a clean voice out of a recording with background music and noise, locally (CPU).

Usage:
  uv run isolate_voice.py <input audio> --out <dir>
Writes <dir>/voice.wav (48 kHz mono): Demucs htdemucs vocals stem (removes music), then
ffmpeg high-pass + FFT denoise + gentle de-ess and loudness at -16 LUFS for the mix step.
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

import soundfile as sf
import torch
from demucs.apply import apply_model
from demucs.audio import AudioFile
from demucs.pretrained import get_model


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--denoise", type=float, default=12, help="ffmpeg afftdn noise reduction in dB (0 = off)")
    args = ap.parse_args()

    model = get_model("htdemucs")
    model.eval()
    wav = AudioFile(args.input).read(streams=0, samplerate=model.samplerate, channels=model.audio_channels)
    ref = wav.mean(0)
    wav = (wav - ref.mean()) / ref.std()
    with torch.no_grad():
        sources = apply_model(model, wav[None], device="cpu", progress=True, split=True, overlap=0.25)[0]
    sources = sources * ref.std() + ref.mean()
    vocals = sources[model.sources.index("vocals")].mean(0).numpy()

    args.out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "vocals.wav"
        sf.write(raw, vocals, model.samplerate)
        sf.write(args.out / "vocals-demucs.wav", vocals, model.samplerate)
        chain = ["highpass=f=80"]
        if args.denoise > 0:
            chain.append(f"afftdn=nr={args.denoise}:nf=-45:tn=1")
        chain += ["deesser=i=0.3", "loudnorm=I=-16:TP=-1.5:LRA=11"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", ",".join(chain),
                        "-ar", "48000", "-ac", "1", str(args.out / "voice.wav")], check=True)
    print(f"voice.wav (music removed, denoised) -> {args.out}")


if __name__ == "__main__":
    main()
