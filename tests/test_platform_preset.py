"""assets/platforms.json and platform_preset.py: every preset is complete, its safe zone fits the
canvas, and the CLI prints what the composition and qa_video.sh consume."""
import json
import re
import subprocess

import pytest

from conftest import SKILL, read_json, run_script

PRESETS = read_json(SKILL / "assets" / "platforms.json")["presets"]
VIDEO = {k: p for k, p in PRESETS.items() if p.get("type") == "video"}
CAROUSEL = {k: p for k, p in PRESETS.items() if p.get("type") == "carousel"}
EDGES = ("top", "bottom", "left", "right")


def test_every_preset_has_a_known_type():
    assert set(PRESETS) == set(VIDEO) | set(CAROUSEL)
    assert {"vertical", "ig-reels", "ig-stories", "tiktok", "yt-shorts", "yt-long"} <= set(VIDEO)
    assert {"ig-carousel", "linkedin-carousel"} <= set(CAROUSEL)


@pytest.mark.parametrize("pid", sorted(VIDEO))
def test_video_preset_keys_and_ranges(pid):
    p = VIDEO[pid]
    for key in ("label", "width", "height", "fps", "max_duration", "ideal_duration", "default_duration",
                "safe", "bitrate_mbps"):
        assert key in p, f"{pid}: falta {key}"
    lo, hi = p["ideal_duration"]
    assert 0 < lo <= hi <= p["max_duration"]
    assert lo <= p["default_duration"] <= hi
    assert p["fps"] in (24, 25, 30, 50, 60) and p["bitrate_mbps"] > 0
    assert p["width"] % 2 == 0 and p["height"] % 2 == 0  # yuv420p needs even sizes


@pytest.mark.parametrize("pid", sorted(CAROUSEL))
def test_carousel_preset_keys_and_ranges(pid):
    p = CAROUSEL[pid]
    for key in ("label", "width", "height", "max_slides", "ideal_slides", "safe", "format"):
        assert key in p, f"{pid}: falta {key}"
    lo, hi = p["ideal_slides"]
    assert 1 <= lo <= hi <= p["max_slides"]
    assert p.get("ads_max_slides", p["max_slides"]) <= p["max_slides"]
    assert p["format"] in ("png", "pdf")


@pytest.mark.parametrize("pid", sorted(PRESETS))
def test_safe_zone_fits_the_canvas(pid):
    p = PRESETS[pid]
    s = p["safe"]
    assert set(s) == set(EDGES)
    assert all(isinstance(s[e], int) and s[e] >= 0 for e in EDGES)
    # what is left in the middle must be a real area, not a sliver
    assert p["width"] - s["left"] - s["right"] >= p["width"] * 0.5
    assert p["height"] - s["top"] - s["bottom"] >= p["height"] * 0.3


def test_youtube_corner_rects_are_inside_the_canvas():
    p = VIDEO["yt-long"]
    for name, rect in p["safe_corners"].items():
        if name.startswith("_") or name == "min_margin":
            continue
        x, y, w, h = rect
        assert x >= 0 and y >= 0 and x + w <= p["width"] and y + h <= p["height"], name


def test_vertical_is_the_strictest_of_reels_tiktok_and_shorts():
    """Documented in platforms.json: one render serves the three, so each edge is the largest of the three."""
    group = [VIDEO[k] for k in ("ig-reels", "tiktok", "yt-shorts")]
    v = VIDEO["vertical"]
    assert (v["width"], v["height"]) == (group[0]["width"], group[0]["height"])
    for e in EDGES:
        assert v["safe"][e] == max(p["safe"][e] for p in group), e
    assert v["max_duration"] == min(p["max_duration"] for p in group)


def test_storyboard_schema_platforms_exist():
    schema = read_json(SKILL / "assets" / "storyboard.schema.json")
    meta = schema["properties"]["meta"]["properties"]
    assert set(meta["platform"]["enum"]) <= set(VIDEO)
    assert set(meta["extra_platforms"]["items"]["enum"]) <= set(VIDEO)


def test_cli_list():
    out = run_script("platform_preset.py", "--list").stdout.splitlines()
    assert [line.split()[0] for line in out] == list(PRESETS)
    assert "1080x1920 30fps  max 180s" in next(line for line in out if line.startswith("vertical "))
    assert "carousel  max 20 slides" in next(line for line in out if line.startswith("ig-carousel "))


def test_no_preset_lists_too():
    assert run_script("platform_preset.py").stdout == run_script("platform_preset.py", "--list").stdout


@pytest.mark.parametrize("pid", ["vertical", "yt-long", "ig-carousel"])
def test_cli_css(pid):
    p, s = PRESETS[pid], PRESETS[pid]["safe"]
    css = run_script("platform_preset.py", pid, "--css").stdout
    assert css.startswith(":root {") and css.rstrip().endswith("}")
    props = dict(re.findall(r"--([\w-]+):\s*(\d+)px;", css))
    assert props == {"canvas-w": str(p["width"]), "canvas-h": str(p["height"]),
                     "safe-top": str(s["top"]), "safe-bottom": str(s["bottom"]),
                     "safe-left": str(s["left"]), "safe-right": str(s["right"])}


def test_cli_shell_is_eval_able_by_bash():
    out = run_script("platform_preset.py", "tiktok", "--shell").stdout.strip()
    got = subprocess.run(["bash", "-c", f'{out}; echo "$W $H $FPS $MAX $ST $SB $SL $SR"'],
                         capture_output=True, text=True, check=True).stdout.split()
    p = PRESETS["tiktok"]
    assert got == [str(v) for v in (p["width"], p["height"], p["fps"], p["max_duration"],
                                    *(p["safe"][e] for e in EDGES))]


def test_cli_json_roundtrip():
    data = json.loads(run_script("platform_preset.py", "ig-stories", "--json").stdout)
    assert data == {"id": "ig-stories", **PRESETS["ig-stories"]}


@pytest.mark.parametrize("pid", ["ig-reels", "linkedin-carousel"])
def test_cli_summary(pid):
    out = run_script("platform_preset.py", pid).stdout
    assert out.startswith(f"{pid} — {PRESETS[pid]['label']}")
    assert f"top {PRESETS[pid]['safe']['top']} · bottom {PRESETS[pid]['safe']['bottom']}" in out


def test_cli_unknown_preset():
    proc = run_script("platform_preset.py", "nope", check=False)
    assert proc.returncode == 2 and "unknown preset 'nope'" in proc.stderr
