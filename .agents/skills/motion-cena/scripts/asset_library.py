# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Asset library: index of reusable raw material already produced by past
creatives (fonts, SFX, music, voice takes, icons/logos/flags, images), so a new
piece reuses what exists instead of downloading, synthesizing or paying again.

Only raw assets are indexed. Compositions, layouts and storyboards are not:
old projects are not a model (see SKILL.md).

Usage:
  uv run asset_library.py scan                          # rebuild projects/_library.json
  uv run asset_library.py find whoosh                   # search all kinds
  uv run asset_library.py find --kind font serif italic
  uv run asset_library.py find --kind voice "8 em cada 10"  # narration with that text
  uv run asset_library.py get <id|query> --to projects/<slug>/video/assets/icons
  uv run asset_library.py report                        # totals + duplicated copies

Kinds: font, sfx, music, voice, voice-ref, icon, logo, flag, image.
`get` copies the file (and its CREDITS.md row, when there is one) into --to.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INDEX = ROOT / "projects" / "_library.json"
SCAN_DIRS = [
    ROOT / "projects",
    ROOT / ".agents/skills/motion-cena/assets",
    ROOT / "training/voz",
]
SKIP_DIRS = {"node_modules", ".hyperframes", "out", ".git", "__pycache__", "dist", "renders", "snapshots"}
SKIP_DIR_RE = re.compile(r"^snap")
# intermediate audio: mixes, stems, source cuts. Not reusable on their own.
SKIP_AUDIO_RE = re.compile(r"^(mix|orig|vocals|cut|audio|render)|-raw$|-src$|16k")

FONT_EXT = {".ttf", ".otf", ".woff", ".woff2"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.lower()


def tokens(s: str) -> list[str]:
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    return [t for t in re.split(r"[^a-z0-9]+", norm(s)) if t]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def duration(p: Path) -> float | None:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
            capture_output=True, text=True, timeout=20,
        ).stdout.strip()
        return round(float(out), 2)
    except (ValueError, subprocess.SubprocessError, FileNotFoundError):
        return None


def credits_row(p: Path) -> str | None:
    c = p.parent / "CREDITS.md"
    if not c.exists():
        return None
    for line in c.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and p.name in line:
            return line
    return None


def narration_text(p: Path) -> str | None:
    d = p.parent
    for name in ("fala.txt", "script.txt", "narracao.txt"):
        if (d / name).exists():
            return (d / name).read_text(encoding="utf-8").strip()
    w = d / "words.json"
    if w.exists():
        try:
            data = json.loads(w.read_text(encoding="utf-8"))
            words = data.get("words", data) if isinstance(data, dict) else data
            return " ".join(str(x.get("word") or x.get("text") or "") for x in words).strip() or None
        except (json.JSONDecodeError, AttributeError):
            return None
    return None


def classify(p: Path) -> str | None:
    ext = p.suffix.lower()
    parts = {norm(x) for x in p.relative_to(ROOT).parts[:-1]}
    stem = norm(p.stem)
    if ext in FONT_EXT:
        return "font"
    if ext in AUDIO_EXT:
        if "voz" in parts and "training" in parts:
            return "voice-ref"
        if "sfx" in parts:
            return "sfx"
        if parts & {"music", "musica", "trilha", "bgm"} or stem.startswith(("music", "trilha", "bgm")):
            return "music"
        if SKIP_AUDIO_RE.search(stem):
            return None
        if stem.startswith("voice"):
            return "voice"
        return None
    if ext == ".svg":
        for k in ("logo", "flag"):
            if stem.startswith(k):
                return k
        return "icon"
    if ext in IMAGE_EXT and parts & {"assets", "icons", "images", "source", "carousel-refs", "photos", "fotos"}:
        return "image"
    return None


def walk(base: Path):
    if not base.exists():
        return
    for p in base.iterdir():
        if p.is_dir():
            if p.name in SKIP_DIRS or SKIP_DIR_RE.match(p.name):
                continue
            yield from walk(p)
        elif p.is_file():
            yield p


def scan(_args) -> None:
    old = {}
    if INDEX.exists():
        old = {a["id"]: a for a in json.loads(INDEX.read_text(encoding="utf-8"))["assets"]}
    by_hash: dict[str, dict] = {}
    for base in SCAN_DIRS:
        for p in walk(base):
            kind = classify(p)
            if not kind:
                continue
            h = sha(p)
            rel = str(p.relative_to(ROOT))
            if h in by_hash:
                by_hash[h]["copies"].append(rel)
                continue
            rel_parts = p.relative_to(ROOT).parts
            project = rel_parts[1] if rel_parts[0] == "projects" else rel_parts[0]
            a = {
                "id": h[:10], "kind": kind, "path": rel, "copies": [], "name": p.name,
                "project": project, "bytes": p.stat().st_size,
            }
            if kind in ("sfx", "music", "voice", "voice-ref"):
                prev = old.get(h[:10])
                a["duration"] = prev["duration"] if prev and "duration" in prev else duration(p)
            if kind == "font":
                fam, _, style = p.stem.partition("-")
                a["family"], a["style"] = fam, style or "Regular"
            if kind == "voice":
                txt = narration_text(p)
                if txt:
                    a["text"] = txt[:400]
            cr = credits_row(p)
            if cr:
                a["credits"] = cr
            by_hash[h] = a
    assets = sorted(by_hash.values(), key=lambda a: (a["kind"], a["name"]))
    for a in assets:
        bag = tokens(a["path"]) + tokens(a.get("family", "")) + tokens(a.get("text", ""))
        a["tags"] = sorted(set(bag) - {"projects", "assets", "video", "claude", "skills", "motion"})
    INDEX.write_text(json.dumps({"updated": str(date.today()), "assets": assets}, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    dup = sum(len(a["copies"]) for a in assets)
    print(f"{len(assets)} assets únicos ({dup} cópias duplicadas) → {INDEX.relative_to(ROOT)}")


def load() -> list[dict]:
    if not INDEX.exists():
        sys.exit("índice não existe: rode `asset_library.py scan` primeiro")
    return json.loads(INDEX.read_text(encoding="utf-8"))["assets"]


def search(assets, query: str, kind: str | None) -> list[tuple[int, dict]]:
    q = tokens(query)
    out = []
    for a in assets:
        if kind and a["kind"] != kind:
            continue
        if not q:
            out.append((0, a))
            continue
        tags = set(a["tags"])
        score = sum(2 if t in tags else 1 for t in q if t in tags or any(t in x for x in tags))
        if score:
            out.append((score, a))
    out.sort(key=lambda x: (-x[0], -len(x[1]["copies"])))
    return out


def fmt(a: dict) -> str:
    extra = []
    if "duration" in a and a["duration"] is not None:
        extra.append(f"{a['duration']}s")
    if "family" in a:
        extra.append(f"{a['family']} {a['style']}")
    if a["copies"]:
        extra.append(f"+{len(a['copies'])} cópias")
    if "credits" in a:
        extra.append("crédito")
    line = f"{a['id']}  {a['kind']:<9} {a['path']}" + (f"  ({', '.join(extra)})" if extra else "")
    if "text" in a:
        line += f"\n            texto: {a['text'][:90]}…"
    return line


def find(args) -> None:
    hits = search(load(), " ".join(args.query), args.kind)
    if not hits:
        print("nada no histórico: pode gerar/baixar (e rodar `scan` depois)")
        return
    for _, a in hits[: args.limit]:
        print(fmt(a))


def get(args) -> None:
    assets = load()
    match = [a for a in assets if a["id"] == args.target] or [a for _, a in search(assets, args.target, args.kind)[:1]]
    if not match:
        sys.exit(f"nada encontrado para {args.target!r}")
    a = match[0]
    dest = Path(args.to)
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / a["path"], dest / a["name"])
    if "credits" in a:
        c = dest / "CREDITS.md"
        if not c.exists():
            c.write_text("# Créditos de ícones, bandeiras e logos\n\n| Arquivo | Fonte | Licença | Data |\n|---|---|---|---|\n",
                         encoding="utf-8")
        if a["name"] not in c.read_text(encoding="utf-8"):
            with c.open("a", encoding="utf-8") as f:
                f.write(a["credits"] + "\n")
    print(f"{a['path']} → {dest / a['name']}")


def report(_args) -> None:
    assets = load()
    kinds: dict[str, int] = {}
    for a in assets:
        kinds[a["kind"]] = kinds.get(a["kind"], 0) + 1
    print("  ".join(f"{k}: {n}" for k, n in sorted(kinds.items())))
    dups = sorted((a for a in assets if a["copies"]), key=lambda a: -len(a["copies"]))
    if dups:
        print("\nduplicados (mesmo arquivo em várias pastas):")
        for a in dups:
            print(f"  {a['name']:<32} {len(a['copies']) + 1}x  ({a['path']})")


def main() -> None:
    for stream in (sys.stdout, sys.stderr):  # Windows consoles and pipes default to cp1252
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan").set_defaults(fn=scan)
    f = sub.add_parser("find")
    f.add_argument("query", nargs="*")
    f.add_argument("--kind")
    f.add_argument("--limit", type=int, default=15)
    f.set_defaults(fn=find)
    g = sub.add_parser("get")
    g.add_argument("target")
    g.add_argument("--to", required=True)
    g.add_argument("--kind")
    g.set_defaults(fn=get)
    sub.add_parser("report").set_defaults(fn=report)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
