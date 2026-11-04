# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Compact view of the delivered-pieces log (creatives/registro.md), to veto repeated concepts
without reading the whole file.

  uv run scripts/registro.py                 # last 12 rows, one line each, cells cut to fit ~1.5 KB
  uv run scripts/registro.py --recent 3      # last 3 rows (fewer rows: more of each cell fits)
  uv run scripts/registro.py --counts        # most used values and words per axis, last 30 rows
  uv run scripts/registro.py --recent 2 --full   # last 2 rows, nothing cut
  uv run scripts/registro.py path/to/registro.md

The log is the markdown table of assets/registro.template.md: date, file, then the 7 axes (device /
world, technique, camera, light and palette, role of text, time structure, relationship with the
viewer). Column names come from the file, so a log written in any language works.
Rows view: the date range goes in the heading; each cell keeps its first items (split at , ; / +)
while they fit, "…" marks a cut inside an item, "=" is a cell that says "same as v1".
Counts: each piece counts once, however many versions it has; "words" are the content words repeated
across pieces, which catch the same idea worded twice.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

LOG = Path("creatives") / "registro.md"
REPO = Path(__file__).resolve().parents[4]
BUDGET = 1500        # bytes of the default view: cells shrink until it fits, down to MIN_CAP characters
MIN_CAP = 12
MAX_CAP = 60
COUNTS_ROWS = 30
SEP = " · "
# item separators: , ; / + -> (a comma between digits is a decimal: "45,7 s" stays whole)
ITEM_SPLIT = re.compile(r"\s*(?:,(?!\d)|(?<!\d),|[;/]|\s\+\s|\s[→-]\s)\s*")
# function words dropped from a cell before cutting it ("fixa com push-in" -> "fixa push-in")
FILLER = set("a o as os e é de da do das dos em no na nos nas um uma com por pelo pela ao à que se the of and "
             "in on to at an by for with".split())
SAME = re.compile(r"^(igual|same|idem|mesm[oa]s?\s+(que|da|do))\b", re.I)  # "igual à v1", "same as v2"
STOP_WORDS = """
para pela pelo pelas pelos cada entre sobre depois antes como quando onde mais menos mesmo mesma mesmos
mesmas igual agora todo toda todos todas outra outro outras outros isso esse essa este esta isto também
muito muita pouco pouca cena cenas quem aqui assim porque qual seja sempre quase ainda seus suas dele
dela deles delas fica ficam vira viram está estão será tudo nada fim início versão vezes cima baixo
dentro fora lado frente após sem
with from that this each same then into over only scene scenes both every their there when where while
"""


def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):  # Windows consoles and pipes default to cp1252
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def find_log(arg: Path | None) -> Path:
    if arg:
        return arg
    for base in (Path.cwd(), *Path.cwd().parents):
        if (base / LOG).is_file():
            return base / LOG
    return REPO / LOG


def split_row(line: str) -> list[str]:
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", body)]


def parse(text: str) -> tuple[list[str], list[list[str]]]:
    """First markdown table of the file: (header, rows). The separator row is skipped."""
    header, rows = [], []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            if header:
                break  # the table ended
            continue
        cells = split_row(line)
        if not header:
            header = cells
        elif all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        elif any(cells):
            rows.append((cells + [""] * len(header))[:len(header)])
    return header, rows


def clean(cell: str) -> str:
    cell = cell.replace("`", "")
    cell = re.sub(r"\s*\([^)]*\)", "", cell)  # parentheticals are detail, not the concept
    return re.sub(r"\s+", " ", cell).strip(" .")


def short_name(cell: str) -> str:
    """File column: the piece's name, without extension or trailing slash."""
    name = re.sub(r"\.(mp4|mov|webm|png|jpe?g|pdf)\b", "", clean(cell), flags=re.I)
    return re.sub(r"/(?=\s|$)", "", name)


def piece_key(cell: str) -> str:
    """The piece a row belongs to: versions (v2, v3...) of one file are the same piece."""
    name = short_name(cell).split(" ")[0] if cell.strip() else ""
    return name.lower()


def trim(text: str, cap: int) -> str:
    """First items that fit in cap; an item longer than cap is cut at a word and marked with "…"."""
    if len(text) <= cap:
        return text
    text = " ".join(w for w in text.split(" ") if w.lower() not in FILLER) or text
    if len(text) <= cap:
        return text
    ends = [m.start() for m in ITEM_SPLIT.finditer(text) if 0 < m.start() <= cap]
    if ends:
        return text[:ends[-1]]
    cut = text[:cap - 1]
    if cut.rfind(" ") >= cap // 3:
        cut = cut[:cut.rindex(" ")]
    return cut.rstrip(" ,;+/") + "…"


def row_line(row: list[str], cap: int | None) -> str:
    """cap None: every cell whole. Else axis cells cut to cap (device: double) and the first column,
    the date, left out: the heading carries the date range."""
    out = [row[0]] if cap is None else []
    for i, cell in enumerate(row[1:], start=1):
        if i == 1:
            out.append(trim(short_name(cell), min(28, cap + 8)) if cap else short_name(cell))
            continue
        text = clean(cell) or "-"
        if cap:
            out.append("=" if SAME.match(text) else trim(text, cap * 2 if i == 2 else cap))
        else:
            out.append(text)
    return SEP.join(out)


def fit(rows: list[list[str]], room: int) -> list[str]:
    """Widest cells whose lines fit in `room` bytes; MIN_CAP is the floor."""
    lines = []
    for cap in range(MAX_CAP, MIN_CAP - 1, -1):
        lines = [row_line(r, cap) for r in rows]
        if sum(len(x.encode("utf-8")) + 1 for x in lines) <= room:
            break
    return lines


def header_line(header: list[str]) -> str:
    return SEP.join(re.split(r"[\s/]", h.strip())[0] if h.strip() else "?" for h in header)


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c)).strip(" .")


STOP = {fold(w) for w in STOP_WORDS.split()}


def content_words(text: str) -> set[str]:
    """Words that carry the idea: 4+ letters or acronyms/with digits (3D, SVG, UI), minus stop words."""
    out = set()
    for w in re.findall(r"[\w-]+", text):
        if re.fullmatch(r"[vV]?\d+([.,]\d+)?", w):
            continue  # numbers and version tags
        if (len(w) >= 4 or re.search(r"\d", w) or (w.isupper() and len(w) >= 2)) and fold(w) not in STOP:
            out.add(w if w.isupper() else w.lower())
    return out


def fkey(s: str) -> str:
    """Comparison key: no case, no accents, no plural s ("linhas" and "linha" are one word)."""
    s = fold(s)
    return s[:-1] if len(s) > 4 and s.endswith("s") and " " not in s else s


def tally(values: dict[str, list[str]], top: int) -> list[tuple[str, int]]:
    """values: piece -> items. Each piece counts once per item. Returns repeated items, most used first."""
    seen: Counter[str] = Counter()
    label: dict[str, str] = {}
    for items in values.values():
        for item in {fkey(x): x for x in items}.items():
            seen[item[0]] += 1
            label.setdefault(item[0], item[1])
    return [(label[k], n) for k, n in seen.most_common() if n > 1][:top]


def counts(header: list[str], rows: list[list[str]], top: int) -> list[str]:
    pieces = {piece_key(r[1]) or str(i) for i, r in enumerate(rows)}
    lines = [f"Last {len(rows)} rows ({len(pieces)} pieces; versions count once). "
             "Per axis: repeated values | repeated words (pieces using it)."]
    for col in range(2, len(header)):
        items: dict[str, list[str]] = {}
        words: dict[str, list[str]] = {}
        latest = []
        for i, row in enumerate(rows):
            text = clean(row[col])
            if not text or text == "-" or SAME.match(text):
                continue
            key = piece_key(row[1]) or str(i)
            parts = [x for x in ITEM_SPLIT.split(text) if x and not SAME.match(x)]
            items.setdefault(key, []).extend(parts)
            words.setdefault(key, []).extend(content_words(text))
            latest.append(text)
        if not items:
            continue
        rep = tally(items, top)
        shown = {fkey(t) for t, _ in rep}
        rep_words = [(w, n) for w, n in tally(words, top + 4) if not any(fkey(w) in s for s in shown)][:top + 2]
        left = "; ".join(f"{trim(t, 36)} {n}" for t, n in rep) or "-"
        right = " · ".join(f"{w} {n}" for w, n in rep_words) or "-"
        line = f"- {header[col].strip()}: {left} | {right}"
        if not rep and not rep_words:
            line += f" (nothing repeats; latest: {trim(latest[-1], 50)})"
        lines.append(line)
    return lines


def main() -> int:
    _utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", nargs="?", type=Path, help="default: creatives/registro.md (from here or the repo root)")
    ap.add_argument("--recent", type=int, default=12, metavar="N", help="last N rows (default 12)")
    ap.add_argument("--counts", action="store_true", help=f"repeated values and words per axis, last {COUNTS_ROWS} rows")
    ap.add_argument("--top", type=int, default=4, help="repeated values per axis with --counts (default 4)")
    ap.add_argument("--full", action="store_true", help="rows view without cutting cells")
    args = ap.parse_args()

    path = find_log(args.log)
    if not path.is_file():
        print(f"No log yet ({path} not found): no delivered piece to compare with. "
              "The first video creates it from assets/registro.template.md.")
        return 0
    header, rows = parse(path.read_text(encoding="utf-8"))
    if not rows:
        print(f"{path.name}: no pieces logged yet.")
        return 0

    if args.counts:
        print("\n".join(counts(header, rows[-COUNTS_ROWS:], max(1, args.top))))
        return 0

    recent = rows[-max(1, args.recent):]
    if args.full:
        head = f"{path.name}, last {len(recent)} of {len(rows)} rows, oldest first: {header_line(header)}"
    else:
        head = (f"{path.name}, last {len(recent)} of {len(rows)} rows ({recent[0][0]} to {recent[-1][0]}), "
                f"oldest first, cells cut (--full): {header_line(header[1:])}")
    if args.full:
        lines = [row_line(r, None) for r in recent]
    else:
        lines = fit(recent, BUDGET - len(head.encode("utf-8")) - 1)
    print("\n".join([head, *lines]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
