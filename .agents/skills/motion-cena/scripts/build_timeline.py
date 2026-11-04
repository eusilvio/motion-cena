# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Anchor storyboard scenes to spoken words -> timeline.json (seconds + frames).

Usage:
  uv run build_timeline.py storyboard.json audio/words.json --fps 30 --out timeline.json

Each scene's `narration` is aligned against words.json (fuzzy, accent/punctuation-insensitive).
Scene boundaries: scene starts `--lead` seconds before its first word; ends where the next starts.
Anchors (`anchors[].phrase`) resolve to the time the phrase is spoken inside the scene.
SFX cues (`sfx[].at` = scene_start | scene_end | anchor:<id> | <seconds from scene start>) resolve to absolute time.
"""
import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path


def norm(token: str) -> str:
    token = unicodedata.normalize("NFKD", token.lower())
    token = "".join(c for c in token if not unicodedata.combining(c))
    return re.sub(r"[^\w%]", "", token)


def tokens(text: str) -> list[str]:
    return [t for t in (norm(x) for x in text.split()) if t]


def find_phrase(phrase: list[str], words: list[str], lo: int, hi: int) -> tuple[int, int] | None:
    """Best fuzzy match of phrase inside words[lo:hi]; returns (start_idx, end_idx_inclusive)."""
    n = len(phrase)
    if not n:  # phrase made only of punctuation: nothing to look for
        return None
    best, best_score = None, 0.0
    for i in range(lo, max(lo, hi - n) + 1):
        window = words[i:i + n]
        score = difflib.SequenceMatcher(a=phrase, b=window, autojunk=False).ratio()
        if score > best_score:
            best, best_score = (i, min(i + n, hi) - 1), score
    return best if best_score >= 0.6 else None


def split_multiword(words: list[dict]) -> list[dict]:
    """TTS engines sometimes emit one boundary for several words ("29 anos"); split time evenly."""
    out = []
    for w in words:
        parts = w["word"].split()
        if len(parts) < 2:
            out.append(w)
            continue
        step = (w["end"] - w["start"]) / len(parts)
        for k, p in enumerate(parts):
            out.append({**w, "word": p, "start": round(w["start"] + k * step, 3), "end": round(w["start"] + (k + 1) * step, 3)})
    return out


def main() -> None:
    for stream in (sys.stdout, sys.stderr):  # Windows consoles and pipes default to cp1252
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("storyboard", type=Path)
    parser.add_argument("words", type=Path)
    parser.add_argument("--fps", type=int)
    parser.add_argument("--lead", type=float, default=0.15, help="scene starts this long before first word")
    parser.add_argument("--tail", type=float, default=0.8, help="hold after last word")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    board = json.loads(args.storyboard.read_text(encoding="utf-8"))
    words = split_multiword(json.loads(args.words.read_text(encoding="utf-8")))
    meta = board.get("meta", {})
    fps = args.fps or meta.get("fps", 30)
    scenes = board["scenes"]
    warnings = []

    # Global alignment: script tokens (tagged by scene) -> spoken word indices.
    script_tokens, owner = [], []
    for si, scene in enumerate(scenes):
        for t in tokens(scene.get("narration", "")):
            script_tokens.append(t)
            owner.append(si)
    spoken = [norm(w["word"]) for w in words]
    matcher = difflib.SequenceMatcher(a=script_tokens, b=spoken, autojunk=False)
    script_to_word, approx = {}, {}
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                script_to_word[i1 + k] = j1 + k
        elif tag == "replace":
            # misheard or respelled words ("espere" spoken as "espera"): spread the spoken span over the
            # script span, so a scene whose first or last word differs still starts and ends on it
            na, nb = i2 - i1, j2 - j1
            for k in range(na):
                lo_k = j1 + k * nb // na
                approx[i1 + k] = (lo_k, max(lo_k, j1 + (k + 1) * nb // na - 1))
    coverage = len(script_to_word) / max(1, len(script_tokens))
    if coverage < 0.85:
        warnings.append(f"only {coverage:.0%} of script words matched the audio; narration and storyboard diverged")

    # Word range per scene: exact matches, widened by the respelled words around them.
    # A scene with no exact match at all stays unmatched (silent or diverged).
    ranges = []
    for si in range(len(scenes)):
        own = [ti for ti, o in enumerate(owner) if o == si]
        spans = [(script_to_word[ti],) * 2 for ti in own if ti in script_to_word]
        if spans:
            spans += [approx[ti] for ti in own if ti in approx]
        ranges.append((min(a for a, _ in spans), max(b for _, b in spans)) if spans else None)
    for si, r in enumerate(ranges):
        if r is None:
            warnings.append(f"scene {scenes[si].get('id', si)}: no narration matched (silent scene or mismatch)")

    # Scene starts; silent/unmatched scenes get interpolated starts.
    starts = []
    for si, r in enumerate(ranges):
        if si == 0:
            starts.append(0.0)
        elif r is not None:
            prev_start = next(s for s in reversed(starts) if s is not None)  # starts[0] is always set
            starts.append(max(prev_start + 0.3, words[r[0]]["start"] - args.lead))
        else:
            starts.append(None)
    end_time = words[-1]["end"] + args.tail if words else sum(s.get("duration", 3) for s in scenes)
    for si in range(len(starts)):
        if starts[si] is None:
            nxt = next((starts[j] for j in range(si + 1, len(starts)) if starts[j] is not None), None)
            dur = scenes[si].get("duration")
            # a silent scene starts once the previous scene's speech is over, never mid-sentence
            prev = next((ranges[j] for j in range(si - 1, -1, -1) if ranges[j] is not None), None)
            speech_over = words[prev[1]]["end"] + 0.3 if prev else starts[si - 1]
            if nxt is None:
                # closing silent scenes play one after the other, each for its own duration
                gap = 0.3
                if ranges[si - 1] is None:
                    gap = scenes[si - 1].get("duration") or (3 if not words else 0.3)
                starts[si] = max(speech_over, starts[si - 1] + gap)
                end_time = max(end_time, starts[si] + (dur or 0.3))
            else:
                start = max(speech_over, (starts[si - 1] + nxt) / 2) if not dur else max(speech_over, nxt - dur)
                need = dur or 0.3
                if nxt - start < need - 1e-6:
                    warnings.append(f"scene {scenes[si].get('id', si)}: silent scene gets {max(0.0, nxt - start):.2f}s "
                                    f"of the {need:.2f}s it needs; leave a longer pause in the narration")
                starts[si] = min(start, nxt)  # never past the next scene: times stay in order

    out_scenes, cues = [], []
    for si, scene in enumerate(scenes):
        start = starts[si]
        end = starts[si + 1] if si + 1 < len(scenes) else end_time
        lo, hi = ranges[si] if ranges[si] else (0, -1)
        scene_words = words[lo:hi + 1] if ranges[si] else []
        anchors = []
        for a in scene.get("anchors", []):
            hit = find_phrase(tokens(a["phrase"]), spoken, lo, hi + 1) if ranges[si] else None
            if hit is None:
                warnings.append(f"scene {scene.get('id', si)}: anchor '{a['phrase']}' not found in spoken words")
                continue
            t0, t1 = words[hit[0]]["start"], words[hit[1]]["end"]
            anchors.append({**a, "start": round(t0, 3), "end": round(t1, 3),
                            "startFrame": round(t0 * fps), "endFrame": round(t1 * fps)})
        anchor_by_id = {a.get("id"): a for a in anchors}
        for cue in scene.get("sfx", []):
            at = cue.get("at", "scene_start")
            if at == "scene_start":
                t = start
            elif at == "scene_end":
                t = end - 0.15  # whoosh lands on the cut
            elif isinstance(at, str) and at.startswith("anchor:"):
                a = anchor_by_id.get(at.split(":", 1)[1])
                if not a:
                    warnings.append(f"scene {scene.get('id', si)}: sfx anchor '{at}' unresolved")
                    continue
                t = a["start"]
            else:
                t = start + float(at)
            t += float(cue.get("offset", 0))  # e.g. riser: offset -1.6 so it ends on the anchor
            cues.append({**cue, "scene": scene.get("id", si), "time": round(max(0.0, t), 3)})
        out_scenes.append({
            **scene,
            "start": round(start, 3), "end": round(end, 3),
            "startFrame": round(start * fps), "durationFrames": max(1, round(end * fps) - round(start * fps)),
            "words": scene_words, "anchors": anchors,
        })

    timeline = {
        "meta": {**meta, "fps": fps, "duration": round(end_time, 3), "durationFrames": round(end_time * fps)},
        "scenes": out_scenes,
        "sfx_cues": sorted(cues, key=lambda c: c["time"]),
        "warnings": warnings,
    }
    args.out.write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out_scenes)} scenes, {len(cues)} sfx cues, {end_time:.2f}s @ {fps}fps -> {args.out}")
    for w in warnings:
        print("WARN:", w, file=sys.stderr)


if __name__ == "__main__":
    main()
