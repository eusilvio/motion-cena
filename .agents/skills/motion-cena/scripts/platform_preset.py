# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Print a platform preset from assets/platforms.json.

Usage:
  uv run platform_preset.py --list                 # all presets, one per line
  uv run platform_preset.py ig-stories             # human-readable summary
  uv run platform_preset.py ig-stories --json      # the preset as JSON
  uv run platform_preset.py ig-stories --shell     # W=1080 H=1920 FPS=30 MAX=60 (for eval in bash)
  uv run platform_preset.py ig-stories --css       # :root custom properties for the composition
"""
import argparse
import json
import sys
from pathlib import Path

PRESETS_FILE = Path(__file__).resolve().parent.parent / "assets" / "platforms.json"


def load() -> dict:
    return json.loads(PRESETS_FILE.read_text(encoding="utf-8"))["presets"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("preset", nargs="?")
    ap.add_argument("--list", action="store_true")
    fmt = ap.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_true")
    fmt.add_argument("--shell", action="store_true")
    fmt.add_argument("--css", action="store_true")
    args = ap.parse_args()

    presets = load()
    if args.list or not args.preset:
        for pid, p in presets.items():
            if p.get("type") == "carousel":
                print(f"{pid:18} {p['width']}x{p['height']} carousel  max {p['max_slides']} slides  {p['label']}")
            else:
                print(f"{pid:18} {p['width']}x{p['height']} {p['fps']}fps  max {p['max_duration']}s  {p['label']}")
        return 0

    p = presets.get(args.preset)
    if p is None:
        print(f"unknown preset '{args.preset}'. Options: {', '.join(presets)}", file=sys.stderr)
        return 2

    s = p["safe"]
    if args.json:
        print(json.dumps({"id": args.preset, **p}, ensure_ascii=False, indent=2))
    elif args.shell:
        if p.get("type") == "carousel":
            print(f"W={p['width']} H={p['height']} SLIDES={p['max_slides']} TYPE=carousel")
        else:
            print(f"W={p['width']} H={p['height']} FPS={p['fps']} MAX={p['max_duration']} "
                  f"ST={s['top']} SB={s['bottom']} SL={s['left']} SR={s['right']}")
    elif args.css:
        print(":root {")
        print(f"  --canvas-w: {p['width']}px; --canvas-h: {p['height']}px;")
        print(f"  --safe-top: {s['top']}px; --safe-bottom: {s['bottom']}px; --safe-left: {s['left']}px; --safe-right: {s['right']}px;")
        print("}")
    elif p.get("type") == "carousel":
        lo, hi = p["ideal_slides"]
        ads = f" · ads max {p['ads_max_slides']}" if "ads_max_slides" in p else ""
        print(f"{args.preset} — {p['label']}")
        print(f"  slide    {p['width']}x{p['height']} {p['format']}")
        print(f"  slides   max {p['max_slides']}{ads} · ideal {lo}–{hi}")
        print(f"  safe     top {s['top']} · bottom {s['bottom']} · left {s['left']} · right {s['right']} px")
    else:
        lo, hi = p["ideal_duration"]
        print(f"{args.preset} — {p['label']}")
        print(f"  canvas   {p['width']}x{p['height']} @ {p['fps']} fps")
        print(f"  duration default {p.get('default_duration', lo)}s · ideal {lo}–{hi}s · max {p['max_duration']}s")
        print(f"  safe     top {s['top']} · bottom {s['bottom']} · left {s['left']} · right {s['right']} px")
        print(f"  bitrate  ~{p['bitrate_mbps']} Mbps (h264, yuv420p, aac 48k, +faststart)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
