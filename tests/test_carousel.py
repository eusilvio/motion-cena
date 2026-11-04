"""dc_to_carousel.py (Claude Design canvas -> HyperFrames composition) and the parts of
render_carousel.py that run before HyperFrames takes the snapshots (which needs Chromium: not run)."""
import json
import os
import stat
import subprocess

from conftest import SCRIPTS, run_script

ARTBOARD = """<!doctype html>
<html><body data-props='{props}'>
<x-dc><helmet><style>.slide {{ color: red; }}</style></helmet>
<div class="slide"><h1>{{{{ titulo }}}}</h1><p>{{{{n}}}} passos</p>
<img data-asset="flag-br.svg" src="/_blob/abc123" alt="bandeira"><img src="foto.png" alt="foto"></div>
</x-dc></body></html>
"""


def artboard(props: dict) -> str:
    return ARTBOARD.format(props=json.dumps(props, ensure_ascii=False).replace("&", "&amp;"))


def make_canvas(tmp_path, props=None):
    project = tmp_path / "project"
    project.mkdir()
    props = props or {"titulo": {"type": "string", "default": "Café & pão"}, "n": {"default": 3}}
    (project / "capa.dc.html").write_text(artboard(props), encoding="utf-8")
    (project / "fim.dc.html").write_text(artboard({"titulo": {"default": "Fim"}, "n": {"default": 0}}), encoding="utf-8")
    (project / "canvas.json").write_text(json.dumps({"order": ["capa.dc.html", "fim.dc.html"], "title": "Teste & cia"}),
                                         encoding="utf-8")
    return project


def test_dc_to_carousel(tmp_path):
    project = make_canvas(tmp_path)
    out = tmp_path / "render"
    (out / "assets" / "fonts").mkdir(parents=True)
    (out / "assets" / "fonts" / "InstrumentSerif-Italic.ttf").write_bytes(b"")
    proc = run_script("dc_to_carousel.py", project, "--out", out)
    assert f"2 slides 1080x1350 -> {out / 'index.html'}" in proc.stdout
    page = (out / "index.html").read_text(encoding="utf-8")
    assert '<section id="slide1" class="clip" data-start="0" data-duration="1"' in page
    assert '<section id="slide2" class="clip" data-start="1" data-duration="1"' in page
    assert 'data-duration="2" data-width="1080" data-height="1350"' in page
    assert "<h1>Café & pão</h1><p>3 passos</p>" in page and "<h1>Fim</h1><p>0 passos</p>" in page
    assert 'src="assets/icons/flag-br.svg"' in page and "/_blob/" not in page
    assert '<img src="foto.png" alt="foto">' in page          # images without data-asset are untouched
    assert "<helmet>" not in page and "color: red" not in page
    assert "<title>Teste &amp; cia</title>" in page
    assert '@font-face { font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-Italic.ttf")' in page
    assert "font-style: italic" in page


def test_dc_to_carousel_square_preset(tmp_path):
    out = tmp_path / "render"
    run_script("dc_to_carousel.py", make_canvas(tmp_path), "--out", out, "--preset", "ig-carousel-square")
    assert 'data-width="1080" data-height="1080"' in (out / "index.html").read_text(encoding="utf-8")


def test_dc_to_carousel_hole_without_default_fails(tmp_path):
    project = make_canvas(tmp_path, props={"n": {"default": 3}})
    proc = run_script("dc_to_carousel.py", project, "--out", tmp_path / "render", check=False)
    assert proc.returncode != 0 and "hole {{titulo}} has no data-props default" in proc.stderr


def test_render_carousel_rejects_bad_arguments(tmp_path):
    proc = run_script("render_carousel.py", tmp_path, "--slides", "3", "--out", tmp_path / "o", "--preset", "ig-reels", check=False)
    assert proc.returncode == 2 and "'ig-reels' is not a carousel preset" in proc.stderr
    proc = run_script("render_carousel.py", tmp_path, "--slides", "21", "--out", tmp_path / "o", check=False)
    assert proc.returncode == 2 and "21 slides > max 20 for ig-carousel" in proc.stderr


def test_hyperframes_cmd_resolves_npx_on_path(tmp_path):
    """subprocess cannot run Windows' npx.cmd by bare name: the command must carry the resolved path."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    fake = bindir / ("npx.cmd" if os.name == "nt" else "npx")
    fake.write_text("@echo off\n" if os.name == "nt" else "#!/bin/sh\n", encoding="utf-8")
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    comp = tmp_path / "comp"
    comp.mkdir()
    (comp / "package.json").write_text('{"scripts": {"render": "npx hyperframes@0.9.13 render"}}', encoding="utf-8")
    code = (
        "import importlib.util, sys; from pathlib import Path\n"
        f"spec = importlib.util.spec_from_file_location('rc', {str(SCRIPTS / 'render_carousel.py')!r})\n"
        "rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)\n"
        "print(rc.hyperframes_cmd(Path(sys.argv[1])))\n"
    )
    env = {**os.environ, "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}", "PYTHONDONTWRITEBYTECODE": "1"}
    out = subprocess.run(["uv", "run", "-q", "--no-project", "--with", "pillow>=10", "python", "-c", code, str(comp)],
                         capture_output=True, text=True, env=env, check=True).stdout
    assert out.strip() == str([str(fake), "--yes", "hyperframes@0.9.13"])
