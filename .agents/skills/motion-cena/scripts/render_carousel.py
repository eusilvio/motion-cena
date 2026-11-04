# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10"]
# ///
"""Render a carousel composition (HyperFrames) to one PNG per slide.

Contract: the composition has N slides, slide i (1-based) is visible during
[i-1, i) seconds of the root timeline and is fully settled by i-0.5 s.

Usage:
  uv run render_carousel.py <composition_dir> --slides 8 --out creatives/carrossel/<slug>-ig-carousel [--preset ig-carousel] [--pdf]

Writes <out>/01.png … NN.png, <out>/contact.jpg (review sheet) and, with --pdf
or a preset whose format is pdf, <out>/carousel.pdf.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

PRESETS_FILE = Path(__file__).resolve().parent.parent / "assets" / "platforms.json"


def hyperframes_cmd(comp: Path) -> list[str]:
    """Use the version pinned in the composition's package.json, so renders stay reproducible."""
    pkg = comp / "package.json"
    if pkg.exists():
        m = re.search(r"hyperframes@([\w.\-]+)", pkg.read_text(encoding="utf-8"))
        if m:
            return ["npx", "--yes", f"hyperframes@{m.group(1)}"]
    return ["npx", "--yes", "hyperframes"]


def contact_sheet(pngs: list[Path], dest: Path, cols: int = 5, thumb_w: int = 360) -> None:
    thumbs = []
    for p in pngs:
        im = Image.open(p).convert("RGB")
        thumbs.append(im.resize((thumb_w, round(im.height * thumb_w / im.width))))
    th = thumbs[0].height
    rows = (len(thumbs) + cols - 1) // cols
    gap = 12
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * gap, rows * th + (rows + 1) * gap), (40, 40, 40))
    for i, t in enumerate(thumbs):
        r, c = divmod(i, cols)
        sheet.paste(t, (gap + c * (thumb_w + gap), gap + r * (th + gap)))
    sheet.save(dest, quality=88)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("composition", type=Path)
    ap.add_argument("--slides", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--preset", default="ig-carousel")
    ap.add_argument("--pdf", action="store_true", help="also write carousel.pdf (LinkedIn document post)")
    args = ap.parse_args()

    preset = json.loads(PRESETS_FILE.read_text(encoding="utf-8"))["presets"].get(args.preset)
    if not preset or preset.get("type") != "carousel":
        print(f"'{args.preset}' is not a carousel preset", file=sys.stderr)
        return 2
    if args.slides > preset["max_slides"]:
        print(f"{args.slides} slides > max {preset['max_slides']} for {args.preset}", file=sys.stderr)
        return 2

    times = ",".join(f"{i + 0.5:g}" for i in range(args.slides))
    with tempfile.TemporaryDirectory() as tmp:
        cmd = hyperframes_cmd(args.composition) + ["snapshot", str(args.composition), "--at", times, "--no-end", "-o", tmp]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        shots = sorted(Path(tmp).glob("frame-*.png"))
        if len(shots) != args.slides:
            print(f"expected {args.slides} frames, got {len(shots)}", file=sys.stderr)
            return 1
        args.out.mkdir(parents=True, exist_ok=True)
        for old in args.out.glob("[0-9][0-9].png"):
            old.unlink()
        pngs = []
        for i, shot in enumerate(shots, 1):
            dest = args.out / f"{i:02d}.png"
            shutil.copyfile(shot, dest)
            pngs.append(dest)

    bad = [p.name for p in pngs if Image.open(p).size != (preset["width"], preset["height"])]
    if bad:
        print(f"wrong size (want {preset['width']}x{preset['height']}): {', '.join(bad)}", file=sys.stderr)
        return 1

    contact_sheet(pngs, args.out / "contact.jpg")
    if args.pdf or preset.get("format") == "pdf":
        images = [Image.open(p).convert("RGB") for p in pngs]
        images[0].save(args.out / "carousel.pdf", save_all=True, append_images=images[1:], resolution=144)
    print(f"{len(pngs)} slides {preset['width']}x{preset['height']} -> {args.out} (contact.jpg for review)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
