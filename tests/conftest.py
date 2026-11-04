"""Shared helpers. The scripts under test are PEP 723 files: each runs with `uv run`, exactly as
the skill calls them, so their inline dependencies are installed and checked too."""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.dont_write_bytecode = True  # importing a script must not leave __pycache__ in the skill folder

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / ".agents" / "skills" / "motion-cena"
SCRIPTS = SKILL / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
needs_ffmpeg = pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg/ffprobe not on PATH")


def run_script(name: str, *args, check: bool = True, cwd: Path | None = None, env: dict | None = None):
    """Run a skill script the way the pipeline does and return the CompletedProcess."""
    script = SCRIPTS / name
    cmd = ["bash", str(script), *map(str, args)] if name.endswith(".sh") else \
          ["uv", "run", "-q", str(script), *map(str, args)]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=cwd, env=env, timeout=300)
    if check and proc.returncode != 0:
        raise AssertionError(f"{name} exited {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")
    return proc


def load_script(name: str):
    """Import a stdlib-only script as a module, to test its pure functions."""
    spec = importlib.util.spec_from_file_location(Path(name).stem, SCRIPTS / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, data) -> Path:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return Path(path)


def ffprobe(path: Path, entries: str, stream: str | None = None) -> str:
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream]
    cmd += ["-show_entries", entries, "-of", "default=nw=1:nk=1", str(path)]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.split()[0]


def ffmpeg(*args) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)],
                   check=True, capture_output=True)
