# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26"]
# ///
"""Offline synthesized SFX kit (free, no network). Good enough for v1; swap for library/AI sounds later.

Usage: uv run synth_sfx.py --out audio/sfx [--only whoosh,pop]
Writes <type>.wav for: whoosh, pop, tick, click, impact, riser, glitch, ding.
"""
import argparse
import wave
from pathlib import Path

import numpy as np

SR = 48_000
rng = np.random.default_rng(7)


def t(seconds: float) -> np.ndarray:
    return np.arange(int(SR * seconds)) / SR


def lowpass_sweep(x: np.ndarray, f_start: float, f_end: float) -> np.ndarray:
    """One-pole lowpass with exponentially swept cutoff."""
    cutoffs = np.geomspace(f_start, f_end, len(x))
    alphas = 1 - np.exp(-2 * np.pi * cutoffs / SR)
    y, acc = np.empty_like(x), 0.0
    for i, (s, a) in enumerate(zip(x, alphas)):
        acc += a * (s - acc)
        y[i] = acc
    return y


def env(n: int, attack: float, release_curve: float = 4.0) -> np.ndarray:
    a = max(1, int(n * attack))
    return np.concatenate([np.linspace(0, 1, a), np.exp(-release_curve * np.linspace(0, 1, n - a))])


def whoosh() -> np.ndarray:
    n = len(t(0.45))
    noise = rng.standard_normal(n)
    up = lowpass_sweep(noise, 300, 6000)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 2
    return up * shape


def pop() -> np.ndarray:
    x = t(0.09)
    freq = np.geomspace(900, 180, len(x))
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * env(len(x), 0.03, 6)


def tick() -> np.ndarray:
    x = t(0.025)
    return np.sin(2 * np.pi * 2400 * x) * env(len(x), 0.02, 9)


def click() -> np.ndarray:
    n = len(t(0.006))
    return rng.standard_normal(n) * env(n, 0.05, 7)


def impact() -> np.ndarray:
    x = t(0.9)
    freq = np.geomspace(120, 40, len(x))
    body = np.sin(2 * np.pi * np.cumsum(freq) / SR) * env(len(x), 0.005, 5)
    burst = lowpass_sweep(rng.standard_normal(len(x)), 4000, 200) * env(len(x), 0.002, 14)
    return body + 0.6 * burst


def riser() -> np.ndarray:
    x = t(1.6)
    freq = np.geomspace(200, 1600, len(x))
    tone = np.sin(2 * np.pi * np.cumsum(freq) / SR) * 0.4
    air = lowpass_sweep(rng.standard_normal(len(x)), 400, 9000) * 0.8
    shape = np.linspace(0, 1, len(x)) ** 2
    return (tone + air) * shape


def glitch() -> np.ndarray:
    n = len(t(0.18))
    sq = np.sign(np.sin(2 * np.pi * 110 * t(0.18)))
    gate = np.repeat(rng.random(n // 400 + 1) > 0.4, 400)[:n]
    return (0.5 * sq + 0.5 * rng.standard_normal(n)) * gate * env(n, 0.01, 3)


def ding() -> np.ndarray:
    x = t(0.8)
    tone = sum(np.sin(2 * np.pi * f * x) * g for f, g in [(1320, 1), (2640, 0.3), (3960, 0.12)])
    return tone * env(len(x), 0.005, 6)


KIT = {f.__name__: f for f in (whoosh, pop, tick, click, impact, riser, glitch, ding)}


def write_wav(path: Path, signal: np.ndarray) -> None:
    peak = np.max(np.abs(signal)) or 1.0
    pcm = (signal / peak * 0.89 * 32767).astype(np.int16)  # ~ -1 dBFS
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--only", help="comma-separated subset")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    names = args.only.split(",") if args.only else list(KIT)
    for name in names:
        write_wav(args.out / f"{name}.wav", KIT[name]())
    print(f"{len(names)} sfx -> {args.out}: {', '.join(names)}")


if __name__ == "__main__":
    main()
