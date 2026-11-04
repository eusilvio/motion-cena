"""Runtime check of the GSAP recipes in references/motion-dictionary/*.json, in headless Chromium.

fixtures/dictionary/run_dictionary.py (PEP 723: Playwright + Pillow) runs every effect once in one
page (harness.html + harness.js): fresh fixture, snippet on a paused timeline, then no exception or
GSAP warning, duration after t, deterministic seek (any direction, and a cold build that jumps to the
end), something changes, loops inside the scene, and the family check (entrance ends visible and
starts hidden, exit ends hidden, transition goes from A to B with nothing covering).

Skips when Playwright's Chromium is not installed:
  uv run --with playwright==1.58.0 playwright install chromium
GSAP 3.14.2 is cached in ~/.cache/motion-cena (downloaded once, sha256 checked).
Contact sheets for a visual review: MOTION_DICT_SHEETS=<folder> uv run --with pytest pytest ...
"""
import glob
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import FIXTURES, SKILL, read_json

DICT = SKILL / "references" / "motion-dictionary"
HARNESS = FIXTURES / "dictionary"
RUNNER = HARNESS / "run_dictionary.py"
CANARIES = HARNESS / "canaries.json"
SKIP_CODE = 77

# Curated recipes copied from motion-dictionary.md that fail the harness. Fix the md and the JSON
# together, then remove the entry here (a recipe listed here that passes fails the test).
KNOWN: dict[str, str] = {}

FAMILY_FILES = sorted(p for p in DICT.glob("*.json") if p.name != "schema.json")
EFFECTS = [e for p in FAMILY_FILES for e in read_json(p)]


def _chromium_cached() -> bool:
    """Any Chromium downloaded by Playwright? Checked before uv installs anything."""
    roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH"), Path.home() / ".cache" / "ms-playwright",
             Path.home() / "Library" / "Caches" / "ms-playwright", Path(os.environ.get("LOCALAPPDATA", "~")) / "ms-playwright"]
    return any(glob.glob(os.path.join(str(r), "chromium*")) for r in roots if r)


def _run(out_dir: Path, *files: Path) -> dict:
    if not shutil.which("uv"):
        pytest.skip("uv not on PATH")
    if not _chromium_cached():
        pytest.skip("Playwright Chromium not installed (uv run --with playwright==1.58.0 playwright install chromium)")
    report = out_dir / "report.json"
    cmd = ["uv", "run", "-q", str(RUNNER), "--json", str(report)]
    for f in files:
        cmd += ["--effects", str(f)]
    if os.environ.get("MOTION_DICT_SHEETS"):
        cmd += ["--sheets", os.environ["MOTION_DICT_SHEETS"]]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=900)
    if proc.returncode == SKIP_CODE:
        pytest.skip(proc.stdout.strip().removeprefix("SKIP: "))
    if proc.returncode != 0:
        raise AssertionError(f"run_dictionary.py exited {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")
    return {r["id"]: r for r in read_json(report)["effects"]}


@pytest.fixture(scope="module")
def report(tmp_path_factory):
    """One browser run for the whole dictionary plus the canaries (about 10 s)."""
    return _run(tmp_path_factory.mktemp("dictionary-runtime"), *FAMILY_FILES, CANARIES)


@pytest.mark.parametrize("effect", EFFECTS, ids=lambda e: e["id"])
def test_recipe_runs_clean(report, effect):
    errors = report[effect["id"]]["errors"]
    if effect["id"] in KNOWN:
        if errors:
            pytest.xfail(KNOWN[effect["id"]])
        pytest.fail(f"{effect['id']} passou no harness: tire da lista KNOWN")
    assert not errors, f"{effect['familia']}/{effect['id']}:\n  " + "\n  ".join(errors)


@pytest.mark.parametrize("canary", read_json(CANARIES), ids=lambda c: c["id"])
def test_harness_catches_broken_recipe(report, canary):
    """Each canary breaks one rule on purpose; the harness has to say which."""
    errors = report[canary["id"]]["errors"]
    assert any(canary["esperado"] in e for e in errors), f"esperado '{canary['esperado']}', veio: {errors}"


PLUGIN_USE = {
    "DrawSVG": re.compile(r"\bdrawSVG\s*:"),
    "MorphSVG": re.compile(r"\bmorphSVG\s*:"),
    "MotionPath": re.compile(r"\bmotionPath\s*:"),
    "CustomEase": re.compile(r"\bCustomEase\."),
    "SplitText": re.compile(r"\bSplitText\.create|\bnew SplitText\b"),
}


def test_plugin_is_named_in_recipe():
    """The harness registers every plugin, so a recipe that needs one must say so in a comment."""
    missing = []
    for e in EFFECTS:
        code = e["gsap"]
        for name, use in PLUGIN_USE.items():
            if use.search(re.sub(r"//[^\n]*", "", code)) and name not in code:
                missing.append(f"{e['id']}: usa {name} sem citar o plugin")
    assert not missing, "\n".join(missing)
