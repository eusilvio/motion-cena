"""asset_library.py and fetch_icon.py: the parts that need no network.

asset_library is pointed at a temporary tree (ROOT, INDEX and SCAN_DIRS patched), so scan/find/get
never read or write the real projects/ folder. fetch_icon's downloads are not run; recolor() and the
CREDITS.md bookkeeping are."""
import json
import types

import pytest

from conftest import load_script

lib = load_script("asset_library.py")
icons = load_script("fetch_icon.py")


@pytest.mark.parametrize("raw,expected", [
    ("InstrumentSerif-Italic", ["instrument", "serif", "italic"]),
    ("Trilha_Calma 02.mp3", ["trilha", "calma", "02", "mp3"]),
    ("Ação Rápida", ["acao", "rapida"]),
])
def test_tokens(raw, expected):
    assert lib.tokens(raw) == expected


@pytest.mark.parametrize("rel,kind", [
    ("projects/p/audio/sfx/whoosh.wav", "sfx"),
    ("projects/p/audio/voice.mp3", "voice"),
    ("projects/p/audio/mix.wav", None),          # intermediate mix
    ("projects/p/audio/voice-raw.wav", None),    # raw take
    ("projects/p/audio/music/bed.mp3", "music"),
    ("projects/p/audio/trilha-calma.mp3", "music"),
    ("training/voz/take.wav", "voice-ref"),
    ("projects/p/video/assets/fonts/Inter-Bold.ttf", "font"),
    ("projects/p/video/assets/icons/flag-br.svg", "flag"),
    ("projects/p/video/assets/icons/logo-acme.svg", "logo"),
    ("projects/p/video/assets/icons/icon-medal.svg", "icon"),
    ("projects/p/video/assets/foto.png", "image"),
    ("projects/p/out/frame.png", None),          # renders are not assets
    ("projects/p/notes.txt", None),
])
def test_classify(rel, kind):
    assert lib.classify(lib.ROOT / rel) == kind


@pytest.fixture
def library(tmp_path, monkeypatch):
    """A fake repo with two projects sharing one SFX file, a voice take with its text and a credited flag."""
    root = tmp_path / "repo"
    files = {
        "projects/a/audio/sfx/whoosh.wav": b"RIFF-whoosh",
        "projects/b/audio/sfx/whoosh.wav": b"RIFF-whoosh",          # same bytes: one asset, one copy
        "projects/a/audio/voice.mp3": b"ID3-voice",
        "projects/a/audio/mix.wav": b"RIFF-mix",                    # skipped
        "projects/a/video/assets/fonts/InstrumentSerif-Italic.ttf": b"font",
        "projects/a/video/assets/icons/flag-br.svg": b"<svg/>",
        "projects/a/video/node_modules/x/icon-skip.svg": b"<svg/>",  # skipped dir
    }
    for rel, data in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(data)
    (root / "projects/a/audio/fala.txt").write_text("Água quente no filtro de papel.", encoding="utf-8")
    (root / "projects/a/video/assets/icons/CREDITS.md").write_text(
        "| Arquivo | Fonte | Licença | Data |\n|---|---|---|---|\n| flag-br.svg | cdn | MIT | 2026-01-01 |\n", encoding="utf-8")
    monkeypatch.setattr(lib, "ROOT", root)
    monkeypatch.setattr(lib, "INDEX", root / "projects" / "_library.json")
    monkeypatch.setattr(lib, "SCAN_DIRS", [root / "projects"])
    monkeypatch.setattr(lib, "duration", lambda p: 1.5)  # no ffprobe on fake audio
    lib.scan(None)
    return root


def test_scan_indexes_raw_assets_once(library):
    assets = json.loads((library / "projects/_library.json").read_text(encoding="utf-8"))["assets"]
    by_name = {a["name"]: a for a in assets}
    assert sorted(by_name) == ["InstrumentSerif-Italic.ttf", "flag-br.svg", "voice.mp3", "whoosh.wav"]
    assert len(by_name["whoosh.wav"]["copies"]) == 1 and by_name["whoosh.wav"]["duration"] == 1.5
    assert by_name["voice.mp3"]["text"] == "Água quente no filtro de papel."
    assert by_name["InstrumentSerif-Italic.ttf"]["family"] == "InstrumentSerif"
    assert by_name["InstrumentSerif-Italic.ttf"]["style"] == "Italic"
    assert by_name["flag-br.svg"]["credits"].startswith("| flag-br.svg |")
    assert "agua" in by_name["voice.mp3"]["tags"]


def test_find_scores_and_filters(library, capsys):
    assets = lib.load()
    assert [a["name"] for _, a in lib.search(assets, "whoosh", None)] == ["whoosh.wav"]
    assert [a["name"] for _, a in lib.search(assets, "filtro papel", "voice")] == ["voice.mp3"]
    assert lib.search(assets, "whoosh", "font") == []
    assert len(lib.search(assets, "", "sfx")) == 1
    lib.find(types.SimpleNamespace(query=["nada", "disso"], kind=None, limit=5))
    assert "nada no histórico" in capsys.readouterr().out


def test_get_copies_file_and_credit(library, tmp_path):
    dest = tmp_path / "dest"
    lib.get(types.SimpleNamespace(target="flag br", to=str(dest), kind="flag"))
    assert (dest / "flag-br.svg").read_bytes() == b"<svg/>"
    credits = (dest / "CREDITS.md").read_text(encoding="utf-8")
    assert credits.count("| flag-br.svg |") == 1
    lib.get(types.SimpleNamespace(target="flag br", to=str(dest), kind="flag"))  # again: no duplicate row
    assert (dest / "CREDITS.md").read_text(encoding="utf-8").count("| flag-br.svg |") == 1


def test_recolor():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path stroke="currentColor"/></svg>'
    out = icons.recolor(svg, "#FF8A3D")
    assert 'stroke="#FF8A3D"' in out and out.startswith('<svg fill="#FF8A3D" xmlns=')
    lucide = '<!-- @license lucide-static ISC --><svg width="24" fill="none" stroke="currentColor"><path/></svg>'
    out = icons.recolor(lucide, "#000")
    assert out.count('fill="') == 1 and 'fill="none"' in out and 'stroke="#000"' in out  # keeps fill="none"


def test_credit_rows_are_replaced_not_duplicated(tmp_path):
    icons.credit(tmp_path, "icon-medal.svg", "url-1", "MIT")
    icons.credit(tmp_path, "flag-br.svg", "url-2", "MIT")
    icons.credit(tmp_path, "icon-medal.svg", "url-3", "ISC")
    lines = (tmp_path / "CREDITS.md").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "# Créditos de ícones, bandeiras e logos"
    rows = [l for l in lines if l.startswith("| ") and "---" not in l and "Arquivo" not in l]
    assert [r.split(" | ")[0:3] for r in rows] == [["| flag-br.svg", "url-2", "MIT"], ["| icon-medal.svg", "url-3", "ISC"]]


def test_save_writes_svg_and_credit(tmp_path, capsys):
    dest = icons.save(tmp_path / "icons", "icon", "medal", "<svg/>", "src", "Phosphor Icons (MIT)")
    assert dest.name == "icon-medal.svg" and dest.read_text(encoding="utf-8") == "<svg/>"
    assert "| icon-medal.svg | src | Phosphor Icons (MIT) |" in (dest.parent / "CREDITS.md").read_text(encoding="utf-8")
