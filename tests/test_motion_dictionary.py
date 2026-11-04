"""Expanded motion dictionary (references/motion-dictionary/*.json) and motion_lookup.py: the data
stays valid, the generated index stays in sync, and lookups find what people actually ask for."""
import json
import re

import pytest

from conftest import SKILL, load_script, run_script

ml = load_script("motion_lookup.py")
DICT_DIR = SKILL / "references" / "motion-dictionary"
EFFECTS = ml.load(DICT_DIR)
BY_ID = {e["id"]: e for e in EFFECTS}
CURATED_MD = (SKILL / "references" / "motion-dictionary.md").read_text(encoding="utf-8")


def test_catalog_is_not_empty_and_covers_every_family():
    assert len(EFFECTS) >= 388
    assert {e["familia"] for e in EFFECTS} == set(ml.FAMILY_ORDER)


def test_validate_passes():
    assert ml.validate(EFFECTS, DICT_DIR) == []
    proc = run_script("motion_lookup.py", "--validate")
    assert "0 erro(s)" in proc.stdout


def test_files_are_json_arrays_with_house_formatting():
    for f in DICT_DIR.glob("*.json"):
        text = f.read_text(encoding="utf-8")
        assert text.endswith("\n"), f"{f.name}: falta quebra de linha no fim"
        data = json.loads(text)
        if f.name != "schema.json":
            assert isinstance(data, list), f"{f.name}: precisa ser uma lista de efeitos"


def test_index_is_in_sync():
    proc = run_script("motion_lookup.py", "--check-index", check=False)
    assert proc.returncode == 0, proc.stdout


@pytest.mark.parametrize("eid", sorted(e["id"] for e in EFFECTS if e["origem"] == "dicionario-atual"))
def test_curated_entries_exist_in_the_md(eid):
    term = BY_ID[eid]["nome"]
    assert re.search(rf"\*\*{re.escape(term)}\*\*", CURATED_MD, re.I), \
        f"{eid}: marcado como dicionario-atual, mas **{term}** não está em motion-dictionary.md"


def test_gsap_snippets_are_deterministic():
    for e in EFFECTS:
        assert not ml.FORBIDDEN.search(e["gsap"]), e["id"]
        assert "tl." in e["gsap"] or "tl\n" in e["gsap"], f"{e['id']}: snippet não usa o tl"


@pytest.mark.parametrize("query,expected", [
    ("mask reveal", "mask-reveal"),
    ("Máscara revelando", None),          # accents and case never block a match
    ("texto hacker", "scramble"),
    ("puch zom", "punch-zoom"),            # typo tolerance
    ("SLAM", "slam"),
    ("bolhas", "bubbles"),
])
def test_search_finds_common_requests(query, expected):
    found = ml.search(EFFECTS, query)
    if expected is None:
        assert found
    else:
        assert found and found[0]["id"] == expected, [e["id"] for e in found]


def test_ambiguous_alias_returns_every_candidate():
    ids = [e["id"] for e in ml.search(EFFECTS, "cortina", limit=10)]
    assert {"curtain-in", "wipe"} <= set(ids)


def test_norm_strips_accents_and_punctuation():
    assert ml.norm("Revelação  por-MÁSCARA!") == "revelacao por mascara"


def test_cli_full_entry_has_code_block():
    out = run_script("motion_lookup.py", "slam").stdout
    assert "```js" in out and "tl.fromTo" in out and "curado" in out


def test_cli_filters_and_errors():
    fam = run_script("motion_lookup.py", "--family", "particulas").stdout.strip().splitlines()
    assert len(fam) == sum(1 for e in EFFECTS if e["familia"] == "particulas")
    assert run_script("motion_lookup.py", "--family", "nao-existe", check=False).returncode == 2
    assert run_script("motion_lookup.py", "qwertyuiop", check=False).returncode == 1
    data = json.loads(run_script("motion_lookup.py", "--id", "slam", "--json").stdout)
    assert data[0]["id"] == "slam" and "_file" not in data[0]


def test_validate_catches_broken_entries(tmp_path):
    good = BY_ID["fade-in"]
    bad = {k: v for k, v in good.items() if not k.startswith("_")}
    bad.update(id="Bad Id", combina_com=["nao-existe"], gsap="tl.to(el, {x: Math.random()}, t);")
    bad.pop("evitar")
    (tmp_path / "schema.json").write_text((DICT_DIR / "schema.json").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "entradas-suaves.json").write_text(json.dumps([bad], ensure_ascii=False), encoding="utf-8")
    errors = "\n".join(ml.validate(ml.load(tmp_path), tmp_path))
    for needle in ("falta evitar", "não casa", "nao-existe", "Math.random"):
        assert needle in errors, errors
