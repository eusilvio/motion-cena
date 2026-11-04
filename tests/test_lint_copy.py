"""lint_copy.py: AI-sounding pt-BR copy is flagged, clean prose is not, and Markdown markup
(code, URLs, HTML, tables) is not mistaken for prose."""
import json
import re

import pytest

from conftest import FIXTURES, run_script

LINT = FIXTURES / "lint"
LINE = re.compile(r"^.*?:(linha \d+|texto \d+|[\w-]+\.\w+|ritmo): (ERRO|aviso): (.*?) → \"(.*)\"$")


def lint(*paths):
    proc = run_script("lint_copy.py", *paths, check=False)
    hits = []
    for line in proc.stdout.splitlines():
        m = LINE.match(line)
        if m:
            hits.append(m.groups())  # (where, level, message, fragment)
    return proc, hits


def summary(proc):
    return proc.stdout.strip().splitlines()[-1]


# one line per case: (text, level, part of the message)
AI_COPY = [
    ("Não é sobre café, é sobre rotina.", "ERRO", "contraste simétrico"),
    ("Mais do que uma bebida, é um hábito.", "ERRO", "mais do que X, é Y"),
    ("O segredo? Água na temperatura certa.", "ERRO", "pergunta-isca"),
    ("Spoiler: o pó importa.", "ERRO", "spoiler"),
    ("Deixa eu te contar como funciona.", "ERRO", "anúncio do que vem"),
    ("Isso muda tudo na sua manhã.", "ERRO", "fecho de efeito"),
    ("O grão — e só ele — define o sabor.", "ERRO", "travessão"),
    ("No mundo de hoje, todo mundo toma café.", "ERRO", "abertura genérica"),
    ("Vamos mergulhar no preparo.", "ERRO", '"mergulhar"'),
    ("Um método revolucionário de preparo.", "ERRO", "hipérbole de mudança"),
    ("Vale ressaltar que a moagem conta.", "ERRO", "conector de redação"),
    ("O que ninguém te conta sobre o filtro.", "ERRO", "isca de clique"),
    ("O café passou no filtro, evidenciando a acidez do grão.", "ERRO", "gerúndio pendurado"),
    ("Café bom - e barato.", "ERRO", "hífen com espaço"),
    ("Disciplina é liberdade na cozinha.", "ERRO", "slogan sem mecanismo"),
    ("A verdadeira questão é a água.", "ERRO", "autoridade de fachada"),
    ("Essa jornada começou cedo na cozinha.", "aviso", '"jornada"'),
    ("É simplesmente o melhor da casa.", "aviso", "palavra muleta"),
    ("Estudos mostram que café acorda.", "aviso", "atribuição vaga"),
    ("Espera... já vai ficar pronto.", "aviso", "reticências"),
    ("Um sabor incrível logo cedo.", "aviso", "elogio vazio"),
    ("Uma abordagem nova para o coado.", "aviso", "palavra de IA em PT"),
    ("Xícara cheia ☕ na mesa.", "ERRO", "emoji"),
]


def test_ai_patterns_are_flagged(tmp_path):
    f = tmp_path / "roteiro.txt"
    f.write_text("\n".join(text for text, _, _ in AI_COPY) + "\n", encoding="utf-8")
    proc, hits = lint(f)
    assert proc.returncode == 1
    for n, (text, level, msg) in enumerate(AI_COPY, 1):
        found = [(lv, m) for where, lv, m, _ in hits if where == f"linha {n}"]
        assert any(lv == level and msg in m for lv, m in found), f"linha {n} {text!r}: esperava {level} {msg!r}, veio {found}"


def test_clean_narration_has_no_hits():
    proc, hits = lint(LINT / "clean-narration.txt")
    assert hits == [] and summary(proc) == "0 erro(s), 0 aviso(s)" and proc.returncode == 0


def test_staccato_in_plain_prose_is_still_flagged(tmp_path):
    f = tmp_path / "fala.txt"
    f.write_text("Acordei. Fiz café. Saí. Voltei para casa só à noite, cansado.\n", encoding="utf-8")
    proc, hits = lint(f)
    assert [h[2] for h in hits if h[0] == "ritmo"] == ["staccato: 3+ frases de até 3 palavras seguidas"]
    assert proc.returncode == 0  # rhythm is a warning


def test_flat_cadence_is_flagged(tmp_path):
    f = tmp_path / "fala.txt"
    f.write_text("A água ferve na chaleira da cozinha. O pó desce no filtro de papel. "
                 "A garrafa enche aos poucos sobre a pia. O cheiro chega até a sala de estar.\n", encoding="utf-8")
    _, hits = lint(f)
    assert any(h[0] == "ritmo" and "ritmo em linha reta" in h[2] for h in hits)


def test_dots_inside_numbers_do_not_end_sentences(tmp_path):
    # before the fix "0.5" and "1.5" were read as four sentences of one or two words (staccato)
    f = tmp_path / "fala.txt"
    f.write_text("Use 0.5 g. Ou 1.5 g.\nO plano custa R$ 1.000 e a versão 2.0.1 já saiu.\n", encoding="utf-8")
    proc, hits = lint(f)
    assert hits == [], hits


def test_markdown_markup_is_not_prose():
    """README-shaped doc: badges, HTML, fenced and inline code with file names, tables, URLs, a dash
    and an AI word inside code and comments. Before the fix this gave 3 errors and 7 warnings."""
    proc, hits = lint(LINT / "doc-markup.md")
    assert hits == [], hits
    assert proc.returncode == 0


def test_markdown_prose_problems_are_still_flagged():
    proc, hits = lint(LINT / "doc-issues.md")
    got = {(where, level, msg.split(":")[0]) for where, level, msg, _ in hits}
    assert got == {
        ("linha 1", "ERRO", "isca de clique"),                # heading text is still checked
        ("linha 5", "ERRO", "travessão em texto de peça"),    # dash in prose
        ("linha 7", "ERRO", "conector de redação"),
        ("linha 11", "aviso", "palavra de IA/corporativa"),   # table cell is still checked
        ("ritmo", "aviso", "staccato"),                       # staccato in prose
    }
    assert proc.returncode == 1  # the "isso muda tudo" in the code block is not flagged


def test_storyboard_json_checks_narration_and_on_screen_text(tmp_path):
    f = tmp_path / "storyboard.json"
    f.write_text(json.dumps({"scenes": [
        {"id": "s1", "narration": "Vamos mergulhar no preparo.", "on_screen_text": "SEM PRESSA",
         "visual": "um texto revolucionário fora da peça não conta"},
    ]}, ensure_ascii=False), encoding="utf-8")
    proc, hits = lint(f)
    assert [(h[0], h[2]) for h in hits] == [("s1.narration", '"mergulhar"')]


def test_html_checks_visible_text_only(tmp_path):
    f = tmp_path / "slide.dc.html"
    f.write_text('<style>/* — */</style><script>const t = "isso muda tudo.";</script>'
                 '<h1>Isso muda tudo.</h1><p>Água a 92 graus.</p>', encoding="utf-8")
    proc, hits = lint(f)
    assert [(h[0], h[1], h[2]) for h in hits] == [("texto 1", "ERRO", "fecho de efeito")]


def test_exit_codes(tmp_path):
    ok = tmp_path / "ok.txt"
    ok.write_text("Essa jornada começou cedo na cozinha.\n", encoding="utf-8")
    assert lint(ok)[0].returncode == 0        # warnings only
    assert run_script("lint_copy.py", check=False).returncode == 2  # no files: usage

