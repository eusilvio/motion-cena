"""snapshot_sheet.py: one HyperFrames snapshot call for all times, frames tiled small in one JPG.

Most tests put a fake `npx` first on PATH (fixtures/snapshot/fake_hyperframes.py: solid PNG per time,
argv logged), so the call, the version pin and the tiling are checked without Node or a browser.
test_real_hyperframes runs the real CLI on training/dicionario-demo and skips without npx or the
browser HyperFrames uses (~/.cache/hyperframes/chrome, puppeteer's cache or HYPERFRAMES_BROWSER_PATH)."""
import json
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import FIXTURES, HAS_FFMPEG, REPO, read_json, run_script

FAKE = FIXTURES / "snapshot" / "fake_hyperframes.py"
COLORS = [(220, 40, 40), (40, 200, 60), (40, 60, 220), (230, 200, 30)]
LOCK_REF = read_json(REPO / "skills-lock.json")["skills"]["hyperframes"]["ref"].lstrip("v")

posix_only = pytest.mark.skipif(os.name == "nt", reason="the fake npx is a shell script")


def jpeg_size(path: Path) -> tuple[int, int]:
    data = Path(path).read_bytes()
    i = 2
    while i < len(data):
        marker, length = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + length
    raise ValueError(f"{path}: no SOF marker")


def pixel(path: Path, x: int, y: int) -> tuple[int, int, int]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"format=rgb24,crop=1:1:{x}:{y}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return tuple(raw[:3])


def close(a, b, tol=30):
    return all(abs(p - q) <= tol for p, q in zip(a, b))


@pytest.fixture
def fake(tmp_path):
    """A project folder, a fake npx on PATH and the log of its calls."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    npx = bindir / "npx"
    npx.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{FAKE}" "$@"\n', encoding="utf-8")
    npx.chmod(0o755)
    project = tmp_path / "proj"
    project.mkdir()
    (project / "index.html").write_text("<!doctype html>\n", encoding="utf-8")
    log = tmp_path / "calls.jsonl"
    env = {**os.environ, "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}", "FAKE_HF_LOG": str(log)}

    def run(*args, check=True, **extra):
        return run_script("snapshot_sheet.py", project, *args, check=check, env={**env, **extra})

    def calls():
        return [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []

    return project, run, calls


@posix_only
def test_one_call_for_every_time_and_only_the_path_printed(fake):
    project, run, calls = fake
    (project / "package.json").write_text('{"scripts": {"check": "npx --yes hyperframes@0.8.181 check"}}', encoding="utf-8")
    proc = run("0.5,2", "4.25")
    out = project / "out" / "snapshot-sheet.jpg"
    assert proc.stdout == f"{out}\n"
    assert len(calls()) == 1
    args = calls()[0]
    assert args[:4] == ["--yes", "hyperframes@0.8.181", "snapshot", str(project)]  # the project's pin
    assert args[args.index("--at") + 1] == "0.5,2,4.25"
    assert "--no-end" in args and args[args.index("--describe") + 1] == "false"
    assert jpeg_size(out) == (3 * 270 + 2 * 4, 480)  # 1080x1920 -> 270x480, one row, 4 px gaps


@posix_only
@pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg reads the pixels back")
def test_frames_keep_the_order_of_the_times(fake, tmp_path):
    _, run, _ = fake
    out = tmp_path / "sheet.jpg"
    run("1,2,3,4", "--out", out)
    assert jpeg_size(out) == (4 * 270 + 3 * 4, 480)
    for k, color in enumerate(COLORS):
        assert close(pixel(out, k * 274 + 135, 300), color), k  # middle of tile k, below the label


@posix_only
def test_version_falls_back_to_skills_lock(fake):
    project, run, calls = fake
    run("1")
    assert calls()[0][1] == f"hyperframes@{LOCK_REF}"  # no package.json: the repo's skills-lock.json


@posix_only
def test_many_frames_wrap_in_balanced_rows_under_1568_px(fake):
    project, run, _ = fake
    run(",".join(str(t) for t in range(1, 7)))  # 6 frames: 5 fit in a row -> 3x2, not 5+1
    assert jpeg_size(project / "out/snapshot-sheet.jpg") == (3 * 270 + 2 * 4, 2 * 480 + 4)
    run(",".join(str(t) for t in range(1, 31)))  # 30 frames do not fit at 270 px: still one image, smaller
    w, h = jpeg_size(project / "out/snapshot-sheet.jpg")
    assert max(w, h) <= 1568


@posix_only
def test_horizontal_frames_keep_the_short_side(fake):
    project, run, _ = fake
    run("1,2,3,4", FAKE_HF_SIZE="1920x1080")
    assert jpeg_size(project / "out/snapshot-sheet.jpg") == (2 * 480 + 4, 2 * 270 + 4)  # 480x270 tiles, 2x2


@posix_only
def test_width_option(fake):
    project, run, _ = fake
    run("1,2", "--width", "200")
    assert jpeg_size(project / "out/snapshot-sheet.jpg") == (2 * 200 + 4, 356)


@posix_only
def test_zoom_crops_at_full_resolution(fake):
    project, run, _ = fake
    proc = run("1,2", "--zoom", "0,1500,1080,420")
    out = project / "out" / "snapshot-zoom.jpg"
    assert proc.stdout.strip() == str(out)
    assert jpeg_size(out) == (1080, 2 * 420 + 4)  # no downscale; two 1080 px crops do not fit side by side
    bad = run("1", "--zoom", "0,1800,1080,420", check=False)
    assert bad.returncode == 2 and "outside the 1080x1920 frame" in bad.stderr


@posix_only
def test_failures_are_reported(fake, tmp_path):
    project, run, _ = fake
    proc = run("1", check=False, FAKE_HF_FAIL="1")
    assert proc.returncode != 0 and "hyperframes snapshot failed" in proc.stderr and "no browser found" in proc.stderr
    assert not (project / "out").exists()
    proc = run_script("snapshot_sheet.py", tmp_path, "1", check=False)  # no index.html
    assert proc.returncode == 2 and "not a HyperFrames project" in proc.stderr
    assert run("um", check=False).returncode == 2


def _hyperframes_browser() -> bool:
    if os.environ.get("HYPERFRAMES_BROWSER_PATH"):
        return True
    roots = [Path.home() / ".cache" / "hyperframes" / "chrome", Path.home() / ".cache" / "puppeteer"]
    return any(r.is_dir() and any(r.iterdir()) for r in roots)


def test_real_hyperframes(tmp_path):
    demo = REPO / "training" / "dicionario-demo"
    if not (demo / "index.html").exists():
        pytest.skip("training/dicionario-demo não existe")
    if not shutil.which("npx"):
        pytest.skip("npx not on PATH")
    if not _hyperframes_browser():
        pytest.skip("no browser for HyperFrames (npx hyperframes browser ensure, or HYPERFRAMES_BROWSER_PATH)")
    project = tmp_path / "demo"
    shutil.copytree(demo, project)  # HyperFrames writes .hyperframes/ into the project
    out = tmp_path / "sheet.jpg"
    proc = run_script("snapshot_sheet.py", project, "1,3", "--out", out)
    assert proc.stdout.strip() == str(out)
    assert jpeg_size(out) == (2 * 270 + 4, 480)
