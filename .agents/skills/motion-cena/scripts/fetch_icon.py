# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Fetch real symbols (flags, official logos), line icons and freely licensed
images/illustrations, with source and license recorded in <out>/CREDITS.md.
Never redraw a real symbol. Emoji are not offered: they are banned in every piece.

Usage:
  uv run fetch_icon.py flag br                      --out <dir>   # flag-icons, 4:3 (--ratio 1x1 for square)
  uv run fetch_icon.py icon medal                   --out <dir>   # Phosphor line icon (--weight regular|bold|fill|duotone|light|thin)
  uv run fetch_icon.py icon medal --set lucide      --out <dir>   # Lucide line icon
  uv run fetch_icon.py logo spotify                 --out <dir>   # Simple Icons (brand color applied)
  uv run fetch_icon.py logo mit --commons "MIT logo.svg" --out <dir>  # Wikimedia Commons file
  uv run fetch_icon.py search trophy                              # names across Phosphor, Lucide, Simple Icons
  uv run fetch_icon.py image "pointe shoes" --category photograph   # list CC photos (Openverse) with license
  uv run fetch_icon.py image "pointe shoes" --pick 2 --out <dir>    # download candidate #2 + attribution

Options: --color "#FF8A3D" recolors line icons / mono logos (default: currentColor for
icons, brand hex for logos). --name sets the output file stem.
Output: <out>/<kind>-<name>.svg
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

CDN = "https://cdn.jsdelivr.net"
PINS = {
    "flag-icons": "7.2.3",
    "phosphor": "2.1.1",
    "lucide": "0.460.0",
    "simple-icons": "13.21.0",
}
LICENSES = {
    "flag": "flag-icons (MIT) — bandeiras nacionais são de domínio público",
    "phosphor": "Phosphor Icons (MIT)",
    "lucide": "Lucide (ISC)",
    "simple-icons": "Simple Icons (CC0) — a marca é de quem a detém; uso só referencial",
}
UA = {"User-Agent": "motion-cena/1.0 (fetch_icon.py)"}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def recolor(svg: str, color: str) -> str:
    svg = svg.replace("currentColor", color)
    # look at the <svg ...> tag itself: Lucide files start with a license comment
    m = re.search(r"<svg\b[^>]*>", svg)
    if m and 'fill="' not in m.group(0):
        svg = svg[: m.start()] + m.group(0).replace("<svg", f'<svg fill="{color}"', 1) + svg[m.end():]
    return svg


def credit(out: Path, file: str, source: str, license_: str) -> None:
    path = out / "CREDITS.md"
    if not path.exists():
        path.write_text("# Créditos de ícones, bandeiras e logos\n\n| Arquivo | Fonte | Licença | Data |\n|---|---|---|---|\n", encoding="utf-8")
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if not l.startswith(f"| {file} |")]
    lines.append(f"| {file} | {source} | {license_} | {date.today().isoformat()} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save(out: Path, kind: str, name: str, svg: str, source: str, license_: str) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    dest = out / f"{kind}-{name}.svg"
    dest.write_text(svg, encoding="utf-8")
    credit(out, dest.name, source, license_)
    print(f"{dest}  [{license_}]")
    return dest


def commons(file: str) -> tuple[str, str, str]:
    title = "File:" + file.replace(" ", "_")
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|extmetadata", "format": "json"})
    page = next(iter(json.loads(get(api))["query"]["pages"].values()))
    if "imageinfo" not in page:
        raise SystemExit(f"Commons has no '{file}'")
    info = page["imageinfo"][0]
    meta = info.get("extmetadata", {})
    lic = meta.get("LicenseShortName", {}).get("value", "ver página")
    restr = meta.get("Restrictions", {}).get("value", "")
    license_ = f"Wikimedia Commons: {lic}" + (f" · {restr}" if restr else "") + " — uso só referencial"
    resolved = "File:" + urllib.parse.unquote(info["descriptionurl"].rsplit("File:", 1)[-1])
    if resolved != title:
        print(f"WARN: Commons redirected {title} -> {resolved}; check it is the CURRENT official logo", file=sys.stderr)
    return get(info["url"]).decode("utf-8"), info["descriptionurl"], license_


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["flag", "icon", "logo", "image", "search"])
    ap.add_argument("query")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--name")
    ap.add_argument("--color")
    ap.add_argument("--ratio", default="4x3", choices=["4x3", "1x1"])
    ap.add_argument("--set", default="phosphor", choices=["phosphor", "lucide"])
    ap.add_argument("--weight", default="regular", choices=["regular", "bold", "fill", "duotone", "light", "thin"])
    ap.add_argument("--commons", help="Wikimedia Commons file name for logos missing from Simple Icons")
    ap.add_argument("--category", choices=["photograph", "illustration", "digitized_artwork"], help="image: kind of picture")
    ap.add_argument("--license", default="cc0,pdm,by", help="image: Openverse licenses (cc0,pdm,by,by-sa…); default avoids share-alike/non-commercial")
    ap.add_argument("--pick", type=int, help="image: download this candidate number from the listing")
    args = ap.parse_args()

    if args.kind == "search":
        q = args.query.lower()
        flat = json.loads(get(f"https://data.jsdelivr.com/v1/packages/npm/@phosphor-icons/core@{PINS['phosphor']}?structure=flat"))
        names = sorted({Path(f["name"]).stem for f in flat["files"] if f["name"].startswith("/assets/regular/")})
        print("phosphor:", ", ".join(n for n in names if q in n) or "—")
        flat = json.loads(get(f"https://data.jsdelivr.com/v1/packages/npm/lucide-static@{PINS['lucide']}?structure=flat"))
        names = sorted({Path(f["name"]).stem for f in flat["files"] if f["name"].startswith("/icons/") and f["name"].endswith(".svg")})
        print("lucide (--set lucide):", ", ".join(n for n in names if q in n) or "—")
        si = json.loads(get(f"{CDN}/npm/simple-icons@{PINS['simple-icons']}/_data/simple-icons.json"))
        si = si["icons"] if isinstance(si, dict) else si
        hits = [i["title"] for i in si if q in i["title"].lower()]
        print("simple-icons (logo):", ", ".join(hits[:30]) or "—  (tente logo --commons)")
        return 0

    if args.kind == "image":
        params = {"q": args.query, "license": args.license, "page_size": 8, "mature": "false"}
        if args.category:
            params["category"] = args.category
        res = json.loads(get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params)))["results"]
        if not res:
            print("no results; try English keywords, another --category or --license by-sa", file=sys.stderr)
            return 1
        if args.pick is None:
            for i, r in enumerate(res, 1):
                print(f"{i}. {r['title'][:60]!r} · {r['license'].upper()} {r.get('license_version') or ''} · {r.get('creator') or '?'} · {r.get('width')}x{r.get('height')}\n   {r['foreign_landing_url']}")
            print("look at the candidates (open the landing pages) and rerun with --pick N --out <dir>")
            return 0
        if not args.out:
            ap.error("--out is required with --pick")
        r = res[args.pick - 1]
        ext = Path(urllib.parse.urlparse(r["url"]).path).suffix.lower() or ".jpg"
        args.out.mkdir(parents=True, exist_ok=True)
        dest = args.out / f"image-{args.name or re.sub(r'[^a-z0-9]+', '-', args.query.lower()).strip('-')}{ext}"
        dest.write_bytes(get(r["url"]))
        attribution = r.get("attribution") or f"{r['title']} by {r.get('creator')} ({r['license'].upper()})"
        credit(args.out, dest.name, r["foreign_landing_url"], f"{r['license'].upper()} {r.get('license_version') or ''} — {attribution}")
        print(f"{dest}  [{r['license'].upper()} {r.get('license_version') or ''}]")
        if r["license"] not in ("cc0", "pdm"):
            print(f"credit required in the piece: {attribution}", file=sys.stderr)
        return 0

    if not args.out:
        ap.error("--out is required")
    q = args.query

    if args.kind == "flag":
        cc = q.lower()
        url = f"{CDN}/npm/flag-icons@{PINS['flag-icons']}/flags/{args.ratio}/{cc}.svg"
        save(args.out, "flag", args.name or cc, get(url).decode("utf-8"), url, LICENSES["flag"])
    elif args.kind == "icon":
        if args.set == "phosphor":
            suffix = "" if args.weight == "regular" else f"-{args.weight}"
            url = f"{CDN}/npm/@phosphor-icons/core@{PINS['phosphor']}/assets/{args.weight}/{q}{suffix}.svg"
        else:
            url = f"{CDN}/npm/lucide-static@{PINS['lucide']}/icons/{q}.svg"
        svg = get(url).decode("utf-8")
        save(args.out, "icon", args.name or q, recolor(svg, args.color) if args.color else svg, url, LICENSES[args.set])
    elif args.kind == "logo":
        slug = q.lower()
        if args.commons:
            svg, src, lic = commons(args.commons)
            if args.color:  # mono version of a one-color logo (e.g. white on a dark background)
                fills = set(re.findall(r'fill="(#[0-9A-Fa-f]{3,8})"', svg))
                if len(fills) > 1:
                    print(f"WARN: logo has {len(fills)} colors {sorted(fills)}; recoloring a multicolor logo is not allowed, keeping originals", file=sys.stderr)
                else:
                    svg = re.sub(r'fill="#[0-9A-Fa-f]{3,8}"', f'fill="{args.color}"', svg)
                    lic += f" · versão mono {args.color}"
            save(args.out, "logo", args.name or slug, svg, src, lic)
            return 0
        url = f"{CDN}/npm/simple-icons@{PINS['simple-icons']}/icons/{slug}.svg"
        try:
            svg = get(url).decode("utf-8")
        except Exception:
            print(f"'{slug}' not in Simple Icons. Find the official file on Wikimedia Commons and pass --commons \"<File name>.svg\". "
                  "Never redraw a logo by hand.", file=sys.stderr)
            return 1
        color = args.color
        if not color:
            data = json.loads(get(f"{CDN}/npm/simple-icons@{PINS['simple-icons']}/_data/simple-icons.json"))
            data = data["icons"] if isinstance(data, dict) else data
            hexes = {re.sub(r"[^a-z0-9]", "", i["title"].lower()): i["hex"] for i in data}
            color = "#" + hexes.get(re.sub(r"[^a-z0-9]", "", slug), "000000")
        save(args.out, "logo", args.name or slug, recolor(svg, color), url, LICENSES["simple-icons"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
