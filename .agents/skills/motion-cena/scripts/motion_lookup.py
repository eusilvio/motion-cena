# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Look up effects in the expanded motion dictionary (references/motion-dictionary/*.json).

The catalog has ~390 effects in 16 families; never read the JSON files whole. Ask this script:

  uv run scripts/motion_lookup.py "mask reveal"            # by term, pt-BR name or alias (accents/case ignored)
  uv run scripts/motion_lookup.py "texto hacker" --brief   # one line per match, no code
  uv run scripts/motion_lookup.py --family texto           # every effect of a family
  uv run scripts/motion_lookup.py --family enfase --genre dados --intensity sutil
  uv run scripts/motion_lookup.py --families               # families and counts
  uv run scripts/motion_lookup.py --id slam --json         # raw entry
  uv run scripts/motion_lookup.py --validate               # schema + cross-reference checks (CI)
  uv run scripts/motion_lookup.py --write-index            # regenerate references/motion-dictionary/index.md

A term can match several effects (aliases overlap on purpose: "cortina" is both curtain in and wipe);
all matches are printed, best first. Pick by context and say which one you used.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
DICT_DIR = SKILL / "references" / "motion-dictionary"
SCHEMA = DICT_DIR / "schema.json"
INDEX = DICT_DIR / "index.md"
HF_SKILLS = SKILL.parent  # .agents/skills/

FAMILY_ORDER = [
    "entradas-suaves", "entradas-impacto", "saidas", "texto", "enfase", "fisica", "loops-ambiente",
    "camera", "transicoes", "formas-svg", "dados-infografico", "interface-ui", "estilizacao-textura",
    "particulas", "3d-perspectiva", "mascaras-composicao",
]
FORBIDDEN = re.compile(
    r"Math\.random|Date\.now|new Date|performance\.now|setTimeout|setInterval|requestAnimationFrame"
    r"|repeat:\s*-1|\.play\(\)")


def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def load(dict_dir: Path = DICT_DIR) -> list[dict]:
    effects: list[dict] = []
    for f in sorted(dict_dir.glob("*.json")):
        if f.name == "schema.json":
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        for e in data:
            e.setdefault("_file", f.name)
        effects.extend(data)
    order = {fam: i for i, fam in enumerate(FAMILY_ORDER)}
    effects.sort(key=lambda e: (order.get(e.get("familia"), 99), e.get("origem") != "dicionario-atual"))
    return effects


def names_of(e: dict) -> list[str]:
    return [e["id"], e["nome"], e["nome_pt"], *e.get("aliases", [])]


def _word_hit(w: str, tokens: list[str]) -> bool:
    """Same word, or same stem for longer words (revelando ~ revelacao, mascaras ~ mascara)."""
    return any(w == tok or (len(w) >= 5 and len(tok) >= 5 and w[:5] == tok[:5]) for tok in tokens)


def search(effects: list[dict], query: str, limit: int = 5) -> list[dict]:
    """Rank: exact id/term > exact pt-BR name > exact alias > all words inside one name > shared
    word stems > fuzzy spelling. Ties keep catalog order (curated first within a family)."""
    q = norm(query)
    if not q:
        return []
    words = q.split()
    scored: list[tuple[float, int, dict]] = []
    for i, e in enumerate(effects):
        names = [norm(n) for n in names_of(e)]
        if q in (norm(e["id"]), norm(e["nome"])):
            score = 3.0
        elif q == norm(e["nome_pt"]):
            score = 2.8
        elif q in names:
            score = 2.5
        elif any(all(w in n for w in words) for n in names):
            score = 2.0
        else:
            stems = max(sum(_word_hit(w, n.split()) for w in words) / len(words) for n in names)
            ratio = max(difflib.SequenceMatcher(None, q, n).ratio() for n in names)
            score = 1.0 + stems * 0.9 if stems >= 0.5 else (ratio if ratio >= 0.75 else 0.0)
        if score:
            scored.append((score, i, e))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [e for _, _, e in scored[:limit]]


def fmt_default(e: dict) -> str:
    p = e["padrao"]
    dur = "contínuo" if p.get("duracao_s") is None else f'{p["duracao_s"]:g} s'
    return f'{dur}, `{p["ease"]}`'


def fmt_params(e: dict) -> str:
    params = e["padrao"].get("parametros") or {}
    return ", ".join(f"{k}={json.dumps(v, ensure_ascii=False)}" for k, v in params.items()) or "-"


def status(e: dict) -> str:
    return ("curado: receita renderizada em references/motion-dictionary.md"
            if e.get("origem") == "dicionario-atual" else
            "catálogo: compilado e executado em navegador, ainda sem render; confira o resultado no snapshot")


def render_full(e: dict) -> str:
    out = [
        f'## {e["nome"]} · `{e["id"]}`',
        f'{e["nome_pt"]} · família `{e["familia"]}` · intensidade {e["intensidade"]} · {status(e)}',
        f'Também pedem como: {", ".join(e["aliases"]) or "-"}',
        "",
        f'O que é: {e["descricao"]}',
        f'Como funciona: {e["como_funciona"]}',
        f'Quando usar: {e["quando_usar"]}',
        f'Evitar: {e["evitar"]}',
        f'Padrão: {fmt_default(e)} · parâmetros: {fmt_params(e)}',
        f'Anima: {", ".join(e["propriedades"])} · gêneros: {", ".join(e["generos"]) or "-"}',
        f'Combina com: {", ".join(e["combina_com"]) or "-"}',
        f'Receita HyperFrames: {e["receita_hyperframes"] or "-"}',
        "",
        "```js",
        e["gsap"].rstrip(),
        "```",
    ]
    return "\n".join(out)


def render_brief(e: dict) -> str:
    mark = " [curado]" if e.get("origem") == "dicionario-atual" else ""
    return f'{e["id"]:<28} {e["nome"]} ({e["nome_pt"]}) · {fmt_default(e)}{mark}'


# ── validation ────────────────────────────────────────────────────────────────

_TYPES = {"string": str, "array": list, "object": dict, "number": (int, float), "null": type(None),
          "boolean": bool, "integer": int}


def _check(value, schema: dict, path: str, errors: list[str]) -> None:
    t = schema.get("type")
    if t is not None:
        allowed = t if isinstance(t, list) else [t]
        ok = any(isinstance(value, _TYPES[x]) and not (x in ("number", "integer") and isinstance(value, bool))
                 for x in allowed)
        if not ok:
            errors.append(f"{path}: tipo {type(value).__name__}, esperado {t}")
            return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} fora de {schema['enum']}")
    if "pattern" in schema and isinstance(value, str) and not re.search(schema["pattern"], value):
        errors.append(f"{path}: {value!r} não casa com {schema['pattern']}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: falta {key}")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                _check(value[key], sub, f"{path}.{key}", errors)
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            _check(item, schema["items"], f"{path}[{i}]", errors)


def hf_recipe_exists(name: str, corpus: str) -> bool:
    return name in corpus


def validate(effects: list[dict], dict_dir: Path = DICT_DIR) -> list[str]:
    schema = json.loads((dict_dir / "schema.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    ids: dict[str, str] = {}
    for e in effects:
        eid = e.get("id", "?")
        clean = {k: v for k, v in e.items() if not k.startswith("_")}
        _check(clean, schema, eid, errors)
        if eid in ids:
            errors.append(f"{eid}: id repetido ({ids[eid]} e {e.get('_file')})")
        ids[eid] = e.get("_file", "")
        if e.get("_file") and e.get("familia") and e["_file"] != f'{e["familia"]}.json':
            errors.append(f"{eid}: família {e['familia']} no arquivo {e['_file']}")
        m = FORBIDDEN.search(e.get("gsap", ""))
        if m:
            errors.append(f"{eid}: gsap usa {m.group(0)} (quebra o render quadro a quadro)")
        if "—" in json.dumps(clean, ensure_ascii=False):
            errors.append(f"{eid}: travessão no texto")
    for e in effects:
        for other in e.get("combina_com", []):
            if other not in ids:
                errors.append(f"{e['id']}: combina_com aponta para {other}, que não existe")
    corpus = "".join(p.read_text(encoding="utf-8", errors="ignore")
                     for p in HF_SKILLS.rglob("*.md")
                     # only the skill folder right under .agents/skills/ counts: the repo itself
                     # is often cloned into a folder named motion-cena (CI does)
                     if p.relative_to(HF_SKILLS).parts[0] != SKILL.name)
    for e in effects:
        r = e.get("receita_hyperframes")
        if r and not hf_recipe_exists(r, corpus):
            errors.append(f"{e['id']}: receita_hyperframes {r} não existe nas skills do HyperFrames")
    return errors


# ── index ─────────────────────────────────────────────────────────────────────

def build_index(effects: list[dict]) -> str:
    by_fam: dict[str, list[dict]] = {}
    for e in effects:
        by_fam.setdefault(e["familia"], []).append(e)
    curated = sum(1 for e in effects if e.get("origem") == "dicionario-atual")
    lines = [
        "# Expanded motion dictionary: index",
        "",
        "<!-- generated by scripts/motion_lookup.py --write-index; do not edit by hand -->",
        "",
        f"{len(effects)} effects in {len(by_fam)} families. **curated** marks the {curated} that are also in "
        "`../motion-dictionary.md`, with rendered demos. The rest compile and run in a browser but have not "
        "been rendered yet. Full entry with GSAP code: `uv run scripts/motion_lookup.py <term>`.",
        "",
        "Descriptions are in pt-BR (the dictionary's language, as in the requests).",
        "",
    ]
    for fam in [f for f in FAMILY_ORDER if f in by_fam] + sorted(set(by_fam) - set(FAMILY_ORDER)):
        lines += [f"## {fam} ({len(by_fam[fam])})", "",
                  "| id | term | what it is (pt-BR) | default | curated |", "|---|---|---|---|---|"]
        for e in by_fam[fam]:
            desc = e["descricao"].replace("|", "/")
            mark = "yes" if e.get("origem") == "dicionario-atual" else ""
            lines.append(f'| `{e["id"]}` | {e["nome"]} | {desc} | {fmt_default(e)} | {mark} |')
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("term", nargs="*", help="term, pt-BR name or alias")
    ap.add_argument("--id", help="exact effect id")
    ap.add_argument("--family", help="list a family (see --families)")
    ap.add_argument("--genre", help="filter: historia, motivacional, tecnico, explicativo, dados, produto, opiniao")
    ap.add_argument("--intensity", choices=["sutil", "media", "forte"], help="filter by intensity")
    ap.add_argument("--families", action="store_true", help="families and counts")
    ap.add_argument("--brief", action="store_true", help="one line per effect, no code")
    ap.add_argument("--json", action="store_true", help="raw JSON entries")
    ap.add_argument("--limit", type=int, default=5, help="max matches for a term (default 5)")
    ap.add_argument("--validate", action="store_true", help="check schema, ids and cross references")
    ap.add_argument("--write-index", action="store_true", help="regenerate index.md")
    ap.add_argument("--check-index", action="store_true", help="exit 1 if index.md is out of date")
    ap.add_argument("--dir", type=Path, default=DICT_DIR, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    effects = load(args.dir)
    index_path = args.dir / "index.md"

    if args.validate:
        errors = validate(effects, args.dir)
        for err in errors:
            print(f"ERRO {err}")
        print(f"{len(effects)} efeito(s), {len(errors)} erro(s)")
        return 1 if errors else 0
    if args.write_index:
        index_path.write_text(build_index(effects) + "\n", encoding="utf-8")
        print(f"gravado {index_path} ({len(effects)} efeitos)")
        return 0
    if args.check_index:
        current = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
        if current != build_index(effects) + "\n":
            print("index.md desatualizado: rode scripts/motion_lookup.py --write-index")
            return 1
        print("index.md em dia")
        return 0
    if args.families:
        counts: dict[str, int] = {}
        for e in effects:
            counts[e["familia"]] = counts.get(e["familia"], 0) + 1
        for fam in FAMILY_ORDER:
            if fam in counts:
                print(f"{fam:<22} {counts[fam]}")
        print(f"{'total':<22} {len(effects)}")
        return 0

    pool = effects
    if args.genre:
        pool = [e for e in pool if args.genre in e["generos"]]
    if args.intensity:
        pool = [e for e in pool if e["intensidade"] == args.intensity]

    if args.id:
        found = [e for e in pool if e["id"] == args.id]
    elif args.family:
        found = [e for e in pool if e["familia"] == args.family]
        if not found and not any(e["familia"] == args.family for e in effects):
            print(f"família desconhecida: {args.family}. Opções: {', '.join(FAMILY_ORDER)}", file=sys.stderr)
            return 2
    elif args.term:
        found = search(pool, " ".join(args.term), args.limit)
    elif args.genre or args.intensity:
        found = pool
    else:
        ap.print_help()
        return 2

    if not found:
        print("nenhum efeito encontrado. Tente outro nome, --brief com uma palavra só ou --families.", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps([{k: v for k, v in e.items() if not k.startswith("_")} for e in found],
                         ensure_ascii=False, indent=2))
    elif args.brief or args.family or (not args.term and not args.id):
        print("\n".join(render_brief(e) for e in found))
    else:
        if len(found) > 1:
            print(f"{len(found)} efeitos casam com o pedido, do mais provável ao menos: "
                  f"{', '.join(e['id'] for e in found)}\n")
        print("\n\n".join(render_full(e) for e in found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
