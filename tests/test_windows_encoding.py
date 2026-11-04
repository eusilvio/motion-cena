"""Scripts that print non-ASCII text must not crash on a Windows console or pipe, whose default
encoding is cp1252 (it has no "→"). PYTHONIOENCODING=cp1252 reproduces that on any system."""
import json
import os
import subprocess
import sys

from conftest import FIXTURES, SCRIPTS, run_script, write_json

CP1252 = {**os.environ, "PYTHONIOENCODING": "cp1252"}


def assert_utf8_output(proc, needle):
    assert "UnicodeEncodeError" not in proc.stderr, proc.stderr
    assert needle in proc.stdout + proc.stderr


def test_lint_copy(tmp_path):
    proc = run_script("lint_copy.py", FIXTURES / "lint" / "doc-issues.md", check=False, env=CP1252)
    assert proc.returncode == 1  # errors found, not a crash
    assert_utf8_output(proc, '→ "Vale ressaltar"')


def test_build_timeline_warning(tmp_path):
    board = write_json(tmp_path / "sb.json", {"scenes": [
        {"id": "s1", "narration": "um dois", "anchors": [{"id": "a", "phrase": "→ seta", "effect": "x"}]}]})
    words = write_json(tmp_path / "w.json", [{"word": "um", "start": 0.1, "end": 0.3}, {"word": "dois", "start": 0.4, "end": 0.6}])
    proc = run_script("build_timeline.py", board, words, "--out", tmp_path / "t.json", env=CP1252)
    assert_utf8_output(proc, "anchor '→ seta' not found")


def test_platform_preset_summary():
    proc = run_script("platform_preset.py", "ig-reels", env={**os.environ, "PYTHONIOENCODING": "ascii"})
    assert_utf8_output(proc, "ig-reels — Instagram Reels")


def test_asset_library_scan(tmp_path):
    (tmp_path / "projects" / "p" / "audio" / "sfx").mkdir(parents=True)
    (tmp_path / "projects" / "p" / "audio" / "sfx" / "pop.wav").write_bytes(b"RIFF")
    driver = (
        "import importlib.util, sys; from pathlib import Path\n"
        f"spec = importlib.util.spec_from_file_location('lib', {str(SCRIPTS / 'asset_library.py')!r})\n"
        "lib = importlib.util.module_from_spec(spec); spec.loader.exec_module(lib)\n"
        "root = Path(sys.argv[1]); lib.ROOT = root; lib.INDEX = root / 'projects' / '_library.json'\n"
        "lib.SCAN_DIRS = [root / 'projects']; lib.duration = lambda p: None\n"
        "sys.argv = ['asset_library.py', 'scan']; lib.main()\n"
    )
    proc = subprocess.run([sys.executable, "-c", driver, str(tmp_path)], capture_output=True, text=True,
                          encoding="utf-8", env={**CP1252, "PYTHONDONTWRITEBYTECODE": "1"})
    assert proc.returncode == 0, proc.stderr
    assert_utf8_output(proc, "1 assets únicos (0 cópias duplicadas) → projects/_library.json".replace("/", os.sep))
    assert json.loads((tmp_path / "projects" / "_library.json").read_text(encoding="utf-8"))["assets"][0]["kind"] == "sfx"
