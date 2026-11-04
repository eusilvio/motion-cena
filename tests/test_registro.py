"""registro.py: a small view of creatives/registro.md, so the agent vetoes repeated concepts without
reading the whole log. The logs here are synthetic, built on the real template's header."""
import pytest

from conftest import SKILL, load_script, run_script

rg = load_script("registro.py")
TEMPLATE = (SKILL / "assets/registro.template.md").read_text(encoding="utf-8")
LONG = ("um tabuleiro de xadrez visto de cima, cada peça é um gasto do mês, a rainha é o aluguel, "
        "os peões são os cafés, a partida inteira acontece em uma tarde chuvosa de domingo")


def row(date, file, device="cartões de frase", technique="tipografia + ícones de linha", camera="cortes secos",
        light="fundo escuro, acento laranja", text="título curto por cena", time="linear (pergunta no fim)",
        relation="observa"):
    return f"| {date} | `{file}` | {device} | {technique} | {camera} | {light} | {text} | {time} | {relation} |"


def write_log(tmp_path, rows, header=TEMPLATE):
    path = tmp_path / "registro.md"
    path.write_text(header.rstrip("\n") + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return path


def view(path, *flags):
    proc = run_script("registro.py", path, *flags)
    return proc.stdout


def data_lines(out):
    return [x for x in out.splitlines()[1:] if x.strip()]


def test_missing_log_is_not_an_error(tmp_path):
    proc = run_script("registro.py", tmp_path / "nao-existe.md")
    assert proc.returncode == 0
    assert "No log yet" in proc.stdout and "registro.template.md" in proc.stdout


def test_empty_template(tmp_path):
    path = tmp_path / "registro.md"
    path.write_text(TEMPLATE, encoding="utf-8")
    assert "no pieces logged yet" in view(path)


def test_default_is_the_last_12_rows_small(tmp_path):
    rows = [row(f"2026-10-{d:02d}", f"peca-{d:02d}-ig-reels.mp4", device=f"mapa de metrô, cada linha um hábito ({d})",
                technique="recorte", light="papel creme, vermelho", text="legenda", time=f"{d},5 s; abre no fim",
                relation="escolhe") for d in range(1, 21)]
    out = view(write_log(tmp_path, rows))
    assert len(out.encode("utf-8")) <= 1500, len(out.encode("utf-8"))
    lines = data_lines(out)
    assert len(lines) == 12
    assert lines[0].startswith("peca-09-ig-reels · ") and lines[-1].startswith("peca-20-ig-reels · ")
    assert out.splitlines()[0] == ("registro.md, last 12 of 20 rows (2026-10-09 to 2026-10-20), oldest first, "
                                   "cells cut (--full): File · Device · Technique · Camera · Light · Role · Time · Relationship")
    assert all(x.count(" · ") == 7 for x in lines)  # 8 columns (the dates are in the heading)
    assert "20,5 s" in lines[-1]                     # a decimal comma is not an item separator
    assert ".mp4" not in out and "`" not in out and "(20)" not in out  # no extension, backticks or parentheticals


def test_a_verbose_log_is_cut_hard(tmp_path):
    rows = [row(f"2026-10-{d:02d}", f"peca-{d:02d}.mp4", device=LONG, technique=LONG, camera=LONG, light=LONG,
                text=LONG, time=LONG, relation=LONG) for d in range(1, 21)]
    out = view(write_log(tmp_path, rows))
    assert len(out.encode("utf-8")) < 2000  # over the 1.5 KB aim: cells stop shrinking at 12 characters
    assert "…" in out and LONG not in out


def test_fewer_rows_keep_more_of_each_cell(tmp_path):
    rows = [row("2026-10-01", "a.mp4", device=LONG), row("2026-10-02", "b.mp4", device=LONG)]
    path = write_log(tmp_path, rows * 7)
    narrow = data_lines(view(path))[-1]
    wide = data_lines(view(path, "--recent", "2"))[-1]
    assert len(data_lines(view(path, "--recent", "2"))) == 2
    assert len(wide) > len(narrow)
    full = view(path, "--recent", "1", "--full")
    assert LONG in full and data_lines(full)[0].startswith("2026-10-02 · b · ")


def test_same_as_previous_version_is_shown_as_equals(tmp_path):
    rows = [row("2026-10-01", "peca.mp4"), row("2026-10-02", "peca.mp4 v2", camera="igual à v1", relation="same as v1")]
    last = data_lines(view(write_log(tmp_path, rows)))[-1]
    assert last.split(" · ")[3] == "=" and last.split(" · ")[7] == "="


def test_counts_repeated_values_once_per_piece(tmp_path):
    rows = [
        row("2026-10-01", "um.mp4", light="fundo escuro, acento laranja"),
        row("2026-10-02", "um.mp4 v2", light="fundo escuro, acento laranja"),  # a version: same piece
        row("2026-10-03", "dois.mp4", light="Fundo escuro; acento azul"),
        row("2026-10-04", "tres.mp4", light="papel claro, acento laranja", camera="igual à v1"),
    ]
    out = view(write_log(tmp_path, rows), "--counts")
    assert out.splitlines()[0].startswith("Last 4 rows (3 pieces; versions count once)")
    light = next(x for x in out.splitlines() if x.startswith("- Light and palette:"))
    assert "fundo escuro 2" in light and "acento laranja 2" in light  # case folded; v2 is not a third use
    assert "acento azul" not in light                                  # used once: not repeated
    camera = next(x for x in out.splitlines() if x.startswith("- Camera:"))
    assert "cortes secos 2" in camera and "igual" not in camera        # "um" and "dois" both; "same as" skipped
    assert len(out.encode("utf-8")) < 1500


def test_counts_use_only_the_last_30_rows(tmp_path):
    old = [row(f"2026-09-{d:02d}", f"velho-{d}.mp4", technique="massinha") for d in range(1, 11)]
    new = [row(f"2026-10-{d:02d}", f"novo-{d}.mp4", technique="recorte de papel") for d in range(1, 31)]
    out = view(write_log(tmp_path, old + new), "--counts")
    assert "Last 30 rows (30 pieces" in out
    assert "massinha" not in out and "recorte de papel 30" in out


def test_counts_repeated_words_catch_the_same_idea_worded_twice(tmp_path):
    rows = [row("2026-10-01", "a.mp4", device="relógio antigo na parede"),
            row("2026-10-02", "b.mp4", device="dois relógios lado a lado"),
            row("2026-10-03", "c.mp4", device="um mapa dobrado")]
    device = next(x for x in view(write_log(tmp_path, rows), "--counts").splitlines() if x.startswith("- Device"))
    assert "relógio 2" in device  # singular and plural are one word


def test_header_in_another_language(tmp_path):
    header = ("| Data | Arquivo | Dispositivo / mundo | Técnica | Câmera | Luz e paleta | Papel do texto | "
              "Estrutura de tempo | Relação com quem assiste |\n|---|---|---|---|---|---|---|---|---|\n")
    rows = [row("2026-10-01", "a.mp4"), row("2026-10-02", "b.mp4")]
    path = write_log(tmp_path, rows, header=header)
    assert view(path, "--full").splitlines()[0].endswith(": Data · Arquivo · Dispositivo · Técnica · Câmera · Luz · "
                                                         "Papel · Estrutura · Relação")
    assert "- Luz e paleta: fundo escuro 2" in view(path, "--counts")


@pytest.mark.parametrize("text, cap, expected", [
    ("cortes secos", 20, "cortes secos"),                                   # fits
    ("fundo escuro, acento laranja, grão", 20, "fundo escuro"),            # whole items while they fit
    ("tipografia + ícones de linha", 15, "tipografia"),
    ("fixa com push-in lento no rosto", 14, "fixa push-in…"),              # filler words go first, then a word cut
    ("45,7 s; abre no fim", 10, "45,7 s"),                                  # decimal comma kept
])
def test_trim(text, cap, expected):
    assert rg.trim(text, cap) == expected


def test_parse_escaped_pipe_and_trailing_text():
    header, rows = rg.parse("# t\n\n| A | B | C |\n|---|---|---|\n| 1 | x \\| y | z |\n\nnota depois da tabela | não é linha\n")
    assert header == ["A", "B", "C"] and rows == [["1", "x | y", "z"]]
