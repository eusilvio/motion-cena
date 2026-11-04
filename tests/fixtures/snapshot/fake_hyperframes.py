"""Stand-in for `npx --yes hyperframes@X snapshot DIR --at T1,T2 --no-end --output OUT ...`, for
tests/test_snapshot_sheet.py: writes one solid PNG per time, named like HyperFrames does
(frame-00-at-0.5s.png), with stdlib only. Frame k is COLORS[k]; FAKE_HF_SIZE=WxH sets the canvas
(default 1080x1920). Appends its argv as JSON to FAKE_HF_LOG; FAKE_HF_FAIL=1 makes it fail."""
import json
import os
import struct
import sys
import zlib
from pathlib import Path

COLORS = [(220, 40, 40), (40, 200, 60), (40, 60, 220), (230, 200, 30), (200, 40, 200), (30, 200, 200)]


def png(path: Path, w: int, h: int, rgb: tuple[int, int, int]) -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    raw = (b"\x00" + bytes(rgb) * w) * h
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw, 1)) + chunk(b"IEND", b""))


def main() -> int:
    args = sys.argv[1:]
    if os.environ.get("FAKE_HF_LOG"):
        with open(os.environ["FAKE_HF_LOG"], "a", encoding="utf-8") as f:
            f.write(json.dumps(args) + "\n")
    if os.environ.get("FAKE_HF_FAIL"):
        print("Error: no browser found", file=sys.stderr)
        return 1
    out = Path(args[args.index("--output") + 1])
    times = args[args.index("--at") + 1].split(",")
    w, h = (int(x) for x in os.environ.get("FAKE_HF_SIZE", "1080x1920").split("x"))
    out.mkdir(parents=True, exist_ok=True)
    for k, t in enumerate(times):
        png(out / f"frame-{k:02d}-at-{t}s.png", w, h, COLORS[k % len(COLORS)])
    print(f"{len(times)} snapshots saved to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
