"""find_words.py: phrase timings, words near a time and pauses, from the synthetic words.json of
fixtures/timeline/ (punctuation, upper case, a missing accent, a multi-word TTS entry, a misheard word).
Phrases must land where build_timeline.py puts the same anchors (expected.json)."""
import pytest

from conftest import FIXTURES, read_json, run_script

WORDS = FIXTURES / "timeline" / "words.json"
EXPECTED = read_json(FIXTURES / "timeline" / "expected.json")
STORYBOARD = read_json(FIXTURES / "timeline" / "storyboard.json")


def find(*args, check=True):
    return run_script("find_words.py", WORDS, *args, check=check)


# anchors said once in the whole narration (the "café" of s5 is the second "café": scene-scoped there)
UNIQUE = ["maquina", "hora", "mais", "calma", "tempo"]


@pytest.mark.parametrize("anchor_id", UNIQUE)
def test_phrase_matches_build_timeline_anchor(anchor_id):
    anchor = next(a for s in EXPECTED["scenes"] for a in s["anchors"] if a["id"] == anchor_id)
    phrase = next(a["phrase"] for s in STORYBOARD["scenes"] for a in s.get("anchors", []) if a["id"] == anchor_id)
    out = find(phrase).stdout
    assert (f'"{phrase}"  {anchor["start"]:.2f}-{anchor["end"]:.2f} s  '
            f'f{anchor["startFrame"]}-{anchor["endFrame"]}') in out, out


def test_several_phrases_in_one_call_with_matched_words():
    lines = find("água e tempo", "Cafeteira!", "manhã", "12 minutos").stdout.splitlines()
    assert lines == [
        '"água e tempo"  3.34-4.30 s  f100-129  água e tempo.',
        '"Cafeteira!"  1.16-1.70 s  f35-51  CAFETEIRA',   # case and punctuation ignored
        '"manhã"  0.71-1.04 s  f21-31  manha,',          # accent ignored
        '"12 minutos"  8.41-9.01 s  f252-270  12 minutos',  # one TTS entry split in two words
    ]


def test_repeated_phrase_lists_the_other_times():
    assert find("café").stdout.strip() == '"café"  2.92-3.30 s  f88-99  Café,  (also exact at 10.86 s)'


def test_fuzzy_match_is_flagged():
    out = find("Espere 12 minutos").stdout.strip()
    assert out == '"Espere 12 minutos"  8.02-9.01 s  f241-270  Espera 12 minutos  (fuzzy)'


def test_fps():
    assert find("café", "--fps", "24").stdout.startswith('"café"  2.92-3.30 s  f70-79  ')  # round(t x fps)


def test_not_found_exits_1():
    proc = find("bicicleta azul voadora", "café", check=False)
    assert proc.returncode == 1
    assert '"bicicleta azul voadora"  NOT FOUND' in proc.stdout and '"café"  2.92' in proc.stdout


def test_around_marks_the_word_being_said():
    out = find("--around", "8.5").stdout.strip()
    assert out == ("around 8.50 s (±1.5): 8.02 Espera · >8.41 12 · 8.71 minutos · 9.05 antes · "
                   "9.41 de · 9.51 servir.")
    assert find("--around", "7", "--window", "0.5").stdout.strip() == "around 7.00 s (±0.5): no words"


def test_gaps_are_strictly_longer_than_the_threshold():
    out = find("--gaps", "0.4").stdout.splitlines()
    assert out == [
        "pauses > 0.4 s: 3",
        "  2.48-2.92 s (0.44)  f74-88  ligada. | Café,",
        "  6.20-8.02 s (1.82)  f186-241  pressa. | Espera",   # the 0.40 pause after "tempo." is not > 0.4
        "  10.00-10.62 s (0.62)  f300-319  servir. | Bom",
    ]
    assert find("--gaps", "0.2").stdout.splitlines()[0] == "pauses > 0.2 s: 5"  # + the 0.21 s before the first word


def test_needs_a_query():
    assert find(check=False).returncode == 2


def test_missing_file(tmp_path):
    proc = run_script("find_words.py", tmp_path / "nada.json", "x", check=False)
    assert proc.returncode == 2 and "cannot read" in proc.stderr
