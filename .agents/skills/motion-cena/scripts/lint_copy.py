# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Flag AI-sounding copy (pt-BR) in narration, on-screen text, slides and captions.

Usage:
  uv run lint_copy.py <files...>      # .txt/.md as-is; .json -> narration/on_screen_text/visual-free text fields;
                                       # .html/.dc.html -> visible text (tags, styles and scripts stripped)
Exit code 1 when an ERROR is found. Rules and rewrites: references/writing-style.md.
"""
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

ERROR, WARN = "ERRO", "aviso"

PATTERNS = [
    # structures
    (ERROR, r"\bn[ãa]o [ée] (s[óo] |apenas )?(sobre|s[óo]|apenas)\b[^.?!]{0,80}[,.;:]\s*[ée]\b", "contraste simétrico (\"não é X, é Y\"): diga direto o que é"),
    (ERROR, r"\bn[ãa]o [ée] [^.;?!]{1,60}; [ée]\b", "contraste simétrico (\"não é X; é Y\")"),
    (ERROR, r"\bmais do que [^.?!]{1,60}, [ée]\b", "contraste simétrico (\"mais do que X, é Y\")"),
    (ERROR, r"(^|[.!?]\s+)(o|a|os|as)\s+\w+\s*\?\s+\S", "pergunta-isca de uma palavra (\"O segredo? ...\")"),
    (ERROR, r"\b(spoiler|plot twist)\s*:", "\"spoiler:\"/\"plot twist:\""),
    (ERROR, r"\baqui (est[áa]|vai) o porqu[êe]\b|\bdeixa eu te contar\b|\be sabe o que mais\b|\be o melhor\s*:", "anúncio do que vem: comece pela informação"),
    (ERROR, r"\bisso muda tudo\b|\be tudo bem\.|\bpensa nisso\.|\bfica a reflex[ãa]o\b|\bsimples assim\.", "fecho de efeito"),
    (ERROR, r"—|\s–\s", "travessão em texto de peça: use ponto, vírgula ou dois-pontos"),
    (WARN, r"\?\s+[^.?!]{1,80}\?", "perguntas retóricas em série"),
    (WARN, r"\.\.\.|…", "reticências: só se a pausa for necessária"),
    (WARN, r"!{2,}|![^.?!]{0,60}!", "exclamações em sequência"),
    # words
    (ERROR, r"\bno mundo de hoje\b|\bnos dias de hoje\b|\bem um mundo cada vez mais\b|\bno cen[áa]rio atual\b", "abertura genérica: diga o fato e a data"),
    (ERROR, r"\bmergulh(ar|o|e|amos)\b", "\"mergulhar\""),
    (ERROR, r"\bdesbloque\w*|\bdestrav\w* (o|seu|teu) potencial|\bpotencializ\w*|\balavanc\w*", "verbo de palestra: use o verbo concreto"),
    (ERROR, r"\brevolucion\w*|\btransformador\w*|\bdivisor de [áa]guas\b|\bvirada de chave\b|\bgame.?changer\b", "hipérbole de mudança: diga o que mudou, com número"),
    (ERROR, r"\bholístic\w*|\bsinergia\b|\bparadigma\b", "jargão corporativo"),
    (ERROR, r"\bvale ressaltar\b|\b[ée] importante destacar\b|\bem suma\b|\bsem mais delongas\b", "conector de redação"),
    (ERROR, r"\bo que ningu[ée]m te conta\b|\bningu[ée]m est[áa] falando (sobre|disso)\b|\bdescubra\b", "isca de clique"),
    (ERROR, r"\babra[çc]ar a mudan[çc]a\b|\bsair da zona de conforto\b|\bnaveg(ar|ando) (por|pelo|pela|nesse|nessa)\b", "clichê"),
    (WARN, r"\bjornada\b", "\"jornada\" (fora de viagem real)"),
    (WARN, r"\bcada vez mais\b|\bem resumo\b|\bal[ée]m disso\b|\bnesse sentido\b", "conector genérico"),
    (WARN, r"\bcrucia(l|is)\b|\bfundamenta(l|is)\b|\bessencia(l|is)\b|\bvita(l|is)\b", "intensificador vazio: corte ou diga por quê"),
    (WARN, r"\brobust\w*|\becossistema\b|\balinhamento\b|\binsights?\b|\belev(ar|e) (o|a|seu|teu)\b|\bimpulsion\w*", "palavra de IA/corporativa"),
    (WARN, r"\bincr[íi]ve(l|is)\b|\bsurrea(l|is)\b|\binsan[oa]s?\b", "elogio vazio: mostre o fato"),
    (WARN, r"\bliteralmente\b|\bsimplesmente\b|\bbasicamente\b", "palavra muleta"),
    (WARN, r"\bfique ligad[oa]\b|\bvamos juntos\b", "CTA genérico"),
    (WARN, r"\b\w+, \w+ e \w+\.", "tríade: confira se não é enumeração automática"),
    # humanizer (kos): guru register, fake depth, vague authority
    (ERROR, r"\btem o cara que\b|\bexistem dois tipos de\b|\benquanto uns\b[^.?!]{0,60}\boutros\b", "dicotomia de coach: troque por um caso real"),
    (ERROR, r"\bmovimento gera movimento\b|\bdisciplina [ée] liberdade\b|\bfa[çc]a acontecer\b|\bquem quer,? d[áa] um jeito\b", "slogan sem mecanismo: diga a ação específica"),
    (ERROR, r"\banota a[íi]\b|\bo insight [ée]\b|\ba li[çc][ãa]o aqui [ée]\b|\bsacou\?|\bpegou,? galera\b", "conclusão mastigada: a cena já disse"),
    (ERROR, r",\s*(evidenciando|ressaltando|demonstrando|refor[çc]ando|destacando|proporcionando|possibilitando|refletindo|simbolizando|contribuindo)\b", "gerúndio pendurado (profundidade falsa): faça outra frase com o fato"),
    (ERROR, r"\bdesempenh\w+ (um )?papel\b|\bmarc(a|ou|ando) (um|uma) (momento|virada|era|nova fase)\b|\bum testemunho de\b|\btape[çc]aria\b", "inflação de importância: diga o que aconteceu"),
    (ERROR, r"\ba verdadeira quest[ãa]o [ée]\b|\bo que realmente importa\b", "autoridade de fachada"),
    (ERROR, r"(^|[.!?]\s+)(sinceramente|honestamente|olha s[óo]|a real)\s*[?:]", "abertura falso-sincera"),
    (ERROR, r"\b[ée] a (linguagem|moeda|arquitetura|l[íi]ngua) d[aoe]s?\b|\bvira (uma )?armadilha\b", "aforismo de fórmula: troque pela afirmação concreta"),
    (ERROR, r"\S\s-\s\S", "hífen com espaço no lugar de travessão"),
    (WARN, r"\b(especialistas|estudos|pesquisas|analistas) (dizem|mostram|apontam|afirmam|indicam)\b|\bsegundo especialistas\b", "atribuição vaga: nome da fonte e data"),
    (WARN, r"\bno fundo,|\bna ess[êe]ncia\b|\bpresta aten[çc][ãa]o\b", "autoridade/anúncio: confira se a frase precisa"),
    (WARN, r"\babordage(m|ns)\b|\bviv[êe]ncias?\b|\bprotagonismo\b|\bresili[êe]ncia\b|\bagregar valor\b|\botimiz\w+|\bcen[áa]rio\b|\bpanorama\b|\bpilar(es)?\b|\bvibrantes?\b", "palavra de IA em PT: use a coisa concreta"),
    (WARN, r"\bdo sonho [àa] realidade\b|\bdo zero ao\b", "intervalo falso (\"do X ao Y\")"),
    (WARN, r"\btalvez (possa|pudesse)\b|\bpode(ria)? potencialmente\b", "ressalva dupla"),
]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002B50\U00002B06\U0000203C\U00002049]")


def texts(path: Path) -> list[tuple[str, str]]:
    """(location, text) pairs to check."""
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        data = json.loads(raw)
        out = []
        for i, s in enumerate(data.get("scenes", [])):
            for key in ("narration", "on_screen_text"):
                if s.get(key):
                    out.append((f"{s.get('id', i)}.{key}", s[key]))
        return out
    if path.suffix in (".html", ".htm") or path.name.endswith(".dc.html"):
        body = re.sub(r"<(script|style|helmet|svg)\b.*?</\1>", " ", raw, flags=re.S | re.I)
        body = html.unescape(re.sub(r"<[^>]+>", "\n", body))
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        return [(f"texto {n}", l) for n, l in enumerate(lines, 1)]
    return [(f"linha {n}", l) for n, l in enumerate(raw.splitlines(), 1) if l.strip()]


SENT = re.compile(r"[^.!?]+[.!?]")


def rhythm(path: Path, items: list[tuple[str, str]]) -> list[tuple[str, str, str]]:
    """Whole-text checks: staccato runs and flat cadence (humanizer §31, de-default eixo 2)."""
    sents = [s.strip() for _, t in items for s in SENT.findall(unicodedata.normalize("NFC", t)) if s.strip()]
    sizes = [len(s.split()) for s in sents]
    out = []
    for i in range(len(sizes) - 2):
        if all(n <= 3 for n in sizes[i:i + 3]) and (i == 0 or sizes[i - 1] > 3):
            out.append((WARN, "staccato: 3+ frases de até 3 palavras seguidas", " ".join(sents[i:i + 3])))
    for i in range(len(sizes) - 3):
        run = sizes[i:i + 4]
        if min(run) >= 6 and max(run) - min(run) <= 2 and (i == 0 or abs(sizes[i - 1] - run[0]) > 2):
            out.append((WARN, "ritmo em linha reta: 4 frases do mesmo tamanho, quebre uma", sents[i][:60] + "…"))
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    errors = warns = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"{arg}: não encontrado", file=sys.stderr)
            continue
        items = texts(path)
        for level, msg, frag in rhythm(path, items):
            print(f"{path}:ritmo: {level}: {msg} → \"{frag}\"")
            warns += 1
        for where, text in items:
            norm = unicodedata.normalize("NFC", text)
            hits = []
            if EMOJI.search(norm):
                hits.append((ERROR, "emoji (proibido em qualquer peça)", EMOJI.search(norm).group(0)))
            for level, rx, msg in PATTERNS:
                m = re.search(rx, norm, flags=re.I)
                if m:
                    hits.append((level, msg, m.group(0).strip()))
            for level, msg, frag in hits:
                print(f"{path}:{where}: {level}: {msg} → \"{frag}\"")
                errors += level == ERROR
                warns += level == WARN
    print(f"{errors} erro(s), {warns} aviso(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
