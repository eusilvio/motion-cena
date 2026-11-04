# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""When is something said? Query words.json instead of reading it (or writing Python to search it).

  uv run scripts/find_words.py projects/<slug>/audio/words.json "frase um" "frase dois" [--fps 30]
  uv run scripts/find_words.py words.json --around 12.3            # words within ±1.5 s of 12.3 s
  uv run scripts/find_words.py words.json --around 12.3 --around 20 --window 2
  uv run scripts/find_words.py words.json --gaps 0.6               # pauses longer than 0.6 s (cut points)

Phrases match the way build_timeline.py matches anchors (same code: case, accents and punctuation
ignored, fuzzy, multi-word TTS entries split). Each phrase prints its best match:
  "agua e tempo"  3.34-4.30 s  f100-129  água e tempo.  (also exact at 12.10 s)
Frames are round(seconds x fps), as in timeline.json. Phrases, --around and --gaps can be combined in
one call. Exit 1 if a phrase is not found.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # importing the sibling must not leave __pycache__ in the skill
_spec = importlib.util.spec_from_file_location("build_timeline", Path(__file__).resolve().with_name("build_timeline.py"))
bt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bt)


def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):  # Windows consoles and pipes default to cp1252
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def span(words: list[dict], i: int, j: int, fps: int) -> str:
    t0, t1 = words[i]["start"], words[j]["end"]
    return f"{t0:.2f}-{t1:.2f} s  f{round(t0 * fps)}-{round(t1 * fps)}"


def find(phrase: str, words: list[dict], spoken: list[str], fps: int) -> tuple[str, bool]:
    toks = bt.tokens(phrase)
    if not toks:
        return f'"{phrase}"  nothing to search (only punctuation)', False
    hit = bt.find_phrase(toks, spoken, 0, len(spoken))
    if hit is None:
        return f'"{phrase}"  NOT FOUND (no window of {len(toks)} word(s) is 60% similar)', False
    i, j = hit
    said = " ".join(w["word"] for w in words[i:j + 1])
    exact = spoken[i:j + 1] == toks
    line = f'"{phrase}"  {span(words, i, j, fps)}  {said}' + ("" if exact else "  (fuzzy)")
    others = [k for k in range(len(spoken) - len(toks) + 1) if k != i and spoken[k:k + len(toks)] == toks]
    if others:
        line += "  (also exact at " + ", ".join(f"{words[k]['start']:.2f}" for k in others[:6]) + " s)"
    return line, True


def around(t: float, window: float, words: list[dict]) -> str:
    near = [w for w in words if w["end"] >= t - window and w["start"] <= t + window]
    if not near:
        return f"around {t:.2f} s (±{window:g}): no words"
    parts = []
    for w in near:
        mark = ">" if w["start"] <= t <= w["end"] else ""
        parts.append(f"{mark}{w['start']:.2f} {w['word']}")
    return f"around {t:.2f} s (±{window:g}): " + " · ".join(parts)


def gaps(min_gap: float, words: list[dict], fps: int) -> list[str]:
    out = []
    if words and words[0]["start"] > min_gap:
        out.append(f"  0.00-{words[0]['start']:.2f} s ({words[0]['start']:.2f})  start | {words[0]['word']}")
    for a, b in zip(words, words[1:]):
        g = round(b["start"] - a["end"], 3)  # 4.70 - 4.30 is 0.40000000000000036
        if g > min_gap:
            out.append(f"  {a['end']:.2f}-{b['start']:.2f} s ({g:.2f})  f{round(a['end'] * fps)}-{round(b['start'] * fps)}"
                       f"  {a['word']} | {b['word']}")
    return [f"pauses > {min_gap:g} s: {len(out)}"] + out


def main() -> int:
    _utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words", type=Path, help="words.json from align_words.py or the TTS script")
    ap.add_argument("phrases", nargs="*", help="phrases to locate")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--around", type=float, action="append", default=[], metavar="SECONDS",
                    help="print the words near this time (repeatable)")
    ap.add_argument("--window", type=float, default=1.5, help="half width for --around (default 1.5 s)")
    ap.add_argument("--gaps", type=float, metavar="SECONDS", help="list pauses longer than this")
    args = ap.parse_args()
    if not (args.phrases or args.around or args.gaps is not None):
        ap.error("give at least one phrase, --around or --gaps")

    try:
        words = bt.split_multiword(json.loads(args.words.read_text(encoding="utf-8")))
    except (OSError, ValueError) as e:
        print(f"cannot read {args.words}: {e}", file=sys.stderr)
        return 2
    spoken = [bt.norm(w["word"]) for w in words]

    ok = True
    for phrase in args.phrases:
        line, found = find(phrase, words, spoken, args.fps)
        ok &= found
        print(line)
    for t in args.around:
        print(around(t, args.window, words))
    if args.gaps is not None:
        print("\n".join(gaps(args.gaps, words, args.fps)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
