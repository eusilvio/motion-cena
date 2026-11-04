# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.1"]
# ///
"""Key frames of a HyperFrames composition in ONE small image, instead of one full snapshot each.

  uv run scripts/snapshot_sheet.py projects/<slug>/video 1.2,4.8,9.5,14
  uv run scripts/snapshot_sheet.py projects/<slug>/video 1.2 4.8 9.5 --out /tmp/check.jpg
  uv run scripts/snapshot_sheet.py projects/<slug>/video 4.8,9.5 --zoom 0,1500,1080,420

Runs `hyperframes snapshot` once for every time, tiles the frames with the time burned in and prints
only the path of the JPG (default <project>/out/snapshot-sheet.jpg, or snapshot-zoom.jpg).
Frames are scaled so the short side is ~270 px (a 1080x1920 frame -> 270x480; --width sets the width),
in as few rows as fit in 1568 px, the most a model looks at.
--zoom x,y,w,h crops that region of each frame at full resolution (canvas pixels): for a detail the
sheet leaves in doubt (small text, an edge near the safe zone).

HyperFrames version: the one pinned in the project's package.json (hyperframes@X.Y.Z), else the ref of
the HyperFrames skills in skills-lock.json. Needs Node (npx) and the browser HyperFrames uses.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[4]
SHORT_SIDE = 270
MAX_SIDE = 1568
GAP = 4
BG = (40, 40, 40)


def hyperframes_version(project: Path) -> str | None:
    pkg = project / "package.json"
    if pkg.is_file():
        text = pkg.read_text(encoding="utf-8")
        m = re.search(r"hyperframes@(\d[\w.\-]*)", text)
        if m:
            return m.group(1)
        try:
            data = json.loads(text)
        except ValueError:
            data = {}
        for section in ("dependencies", "devDependencies"):
            v = (data.get(section) or {}).get("hyperframes")
            if v and re.match(r"[\^~=v]*\d", v):
                return re.sub(r"^[\^~=v]+", "", v)
    for base in (project.resolve(), *project.resolve().parents, REPO):
        lock = base / "skills-lock.json"
        if lock.is_file():
            try:
                ref = json.loads(lock.read_text(encoding="utf-8"))["skills"]["hyperframes"]["ref"]
                return ref.lstrip("v")
            except (ValueError, KeyError, TypeError):
                return None
    return None


def parse_times(raw: list[str]) -> list[float]:
    times = []
    for chunk in raw:
        for t in chunk.replace(";", ",").split(","):
            if t.strip():
                times.append(float(t.strip().rstrip("s")))
    return times


def parse_zoom(raw: str | None) -> tuple[int, int, int, int] | None:
    if not raw:
        return None
    parts = [int(round(float(x))) for x in raw.split(",")]
    if len(parts) != 4 or parts[2] <= 0 or parts[3] <= 0 or parts[0] < 0 or parts[1] < 0:
        raise SystemExit("--zoom wants x,y,w,h in canvas pixels, w and h > 0 (e.g. 0,1500,1080,420)")
    return tuple(parts)  # type: ignore[return-value]


def snapshot(project: Path, times: list[float], dest: Path) -> list[Path]:
    npx = shutil.which("npx")  # on Windows it is npx.cmd, which subprocess does not find by bare name
    if not npx:
        raise SystemExit("npx not found: install Node 22+ (https://nodejs.org)")
    version = hyperframes_version(project)
    pkg = f"hyperframes@{version}" if version else "hyperframes"
    cmd = [npx, "--yes", pkg, "snapshot", str(project), "--at", ",".join(f"{t:g}" for t in times),
           "--no-end", "--output", str(dest), "--describe", "false"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    frames = sorted(dest.glob("frame-*.png"), key=lambda p: int(re.search(r"frame-(\d+)", p.name).group(1)))
    if proc.returncode != 0 or len(frames) != len(times):
        tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-15:])
        raise SystemExit(f"hyperframes snapshot failed ({pkg}, exit {proc.returncode}, "
                         f"{len(frames)} of {len(times)} frames):\n{tail}")
    return frames


def label_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow without FreeType: fixed bitmap font
        return ImageFont.load_default()


def stamp(im: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(im)
    font = label_font(max(12, min(20, im.width // 14)))
    x0, y0, x1, y1 = draw.textbbox((6, 4), text, font=font)
    draw.rectangle((x0 - 4, y0 - 3, x1 + 4, y1 + 3), fill=(0, 0, 0))
    draw.text((6, 4), text, font=font, fill=(255, 255, 255))


def grid(n: int, tw: int, th: int) -> tuple[int, int]:
    """Columns and rows: as few rows as fit in MAX_SIDE, then balanced (6 frames on 5 columns -> 3x2)."""
    cols = max(1, min(n, (MAX_SIDE + GAP) // (tw + GAP)))
    rows = math.ceil(n / cols)
    return math.ceil(n / rows), rows


def tile(images: list[Image.Image], labels: list[str], thumb_w: int | None, native: bool) -> Image.Image:
    w0, h0 = images[0].size
    if native:
        tw, th = w0, h0
    else:
        tw = thumb_w or round(SHORT_SIDE * w0 / min(w0, h0))
        th = round(h0 * tw / w0)
    cols, rows = grid(len(images), tw, th)
    # too many frames (or a big zoom): shrink the tiles, still one image within MAX_SIDE
    scale = min(1.0, (MAX_SIDE - (cols - 1) * GAP) / (cols * tw), (MAX_SIDE - (rows - 1) * GAP) / (rows * th))
    if scale < 1:
        tw, th = max(1, int(tw * scale)), max(1, int(th * scale))
    sheet_w, sheet_h = cols * tw + (cols - 1) * GAP, rows * th + (rows - 1) * GAP
    sheet = Image.new("RGB", (sheet_w, sheet_h), BG)
    for k, (im, text) in enumerate(zip(images, labels)):
        thumb = im.convert("RGB").resize((tw, th), Image.LANCZOS) if im.size != (tw, th) else im.convert("RGB")
        stamp(thumb, text)
        r, c = divmod(k, cols)
        sheet.paste(thumb, (c * (tw + GAP), r * (th + GAP)))
    return sheet


def main() -> int:
    for stream in (sys.stdout, sys.stderr):  # Windows consoles and pipes default to cp1252
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path, help="HyperFrames project folder (has index.html)")
    ap.add_argument("times", nargs="+", help="seconds, space or comma separated: 1.2,4.8 9.5")
    ap.add_argument("--out", type=Path, help="JPG path (default <project>/out/snapshot-sheet.jpg)")
    ap.add_argument("--width", type=int, help=f"frame width in the sheet (default: short side {SHORT_SIDE} px)")
    ap.add_argument("--zoom", metavar="X,Y,W,H", help="crop this canvas region of each frame, full resolution")
    args = ap.parse_args()

    if not (args.project / "index.html").is_file():
        print(f"{args.project}: not a HyperFrames project (no index.html)", file=sys.stderr)
        return 2
    try:
        times = parse_times(args.times)
    except ValueError:
        print(f"times must be seconds, e.g. 1.2,4.8 (got {' '.join(args.times)})", file=sys.stderr)
        return 2
    zoom = parse_zoom(args.zoom)
    out = args.out or args.project / "out" / ("snapshot-zoom.jpg" if zoom else "snapshot-sheet.jpg")

    with tempfile.TemporaryDirectory(prefix="snapshot-sheet-") as tmp:
        frames = snapshot(args.project, times, Path(tmp))
        images = []
        for f in frames:
            im = Image.open(f)
            im.load()
            if zoom:
                x, y, w, h = zoom
                if x + w > im.width or y + h > im.height:
                    print(f"--zoom {args.zoom} falls outside the {im.width}x{im.height} frame", file=sys.stderr)
                    return 2
                im = im.crop((x, y, x + w, y + h))
            images.append(im)
        labels = [f"{t:g}s" for t in times]
        sheet = tile(images, labels, args.width, native=bool(zoom) and not args.width)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, "JPEG", quality=85)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
