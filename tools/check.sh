#!/usr/bin/env bash
# Roda na sua máquina tudo o que o CI roda (.github/workflows/ci.yml). Funciona de qualquer pasta:
#   ./tools/check.sh
# Sai com erro se alguma checagem falhar e, nesse caso, mostra a saída dela.
# Sem set -e: cada checagem roda mesmo se a anterior falhou. Compatível com o bash 3.2 do macOS.
set -o pipefail
cd "$(dirname "$0")/.." || exit 1
export PYTHONDONTWRITEBYTECODE=1  # nada de __pycache__ novo na skill

SHELLCHECK="shellcheck-py==0.11.0.1"
ACTIONLINT="actionlint-py==1.7.12.25"
PYTEST="pytest>=8,<10"
# Testes das skills do HyperFrames que dependem do monorepo deles (packages/cli, versão fixa
# no package.json da raiz) e não passam numa cópia das skills. Os outros rodam offline como vieram.
NODE_SKIP="
.agents/skills/hyperframes/scripts/lib/main-module.test.mjs
.agents/skills/hyperframes-animation/scripts/package-loader.test.mjs
.agents/skills/hyperframes-creative/scripts/package-loader.test.mjs
"

log=$(mktemp)
trap 'rm -f "$log"' EXIT
fails=0

ok() { printf '  ok      %s\n' "$1"; }
indent() { sed 's/^/          /'; }
failed() {
  printf '  FALHOU  %s\n' "$1"
  indent <"$log"
  fails=$((fails + 1))
}

echo "Ferramentas:"
need() {
  if command -v "$1" >/dev/null 2>&1; then
    ok "$1"
  else
    printf '  FALTA   %s  (%s)\n' "$1" "$2"
    fails=$((fails + 1))
  fi
}
need git     "https://git-scm.com"
need uv      "https://docs.astral.sh/uv/"
need node    "Node 22+: https://nodejs.org"
need ffmpeg  "https://ffmpeg.org/download.html"
need ffprobe "vem com o FFmpeg"
if command -v node >/dev/null 2>&1; then
  major=$(node -p 'process.versions.node.split(".")[0]')
  [ "$major" -ge 22 ] || { echo "  Node $major encontrado; precisa de 22+"; fails=$((fails + 1)); }
fi
if [ "$fails" -gt 0 ]; then
  echo "Instale o que falta e rode ./tools/check.sh de novo."
  exit 1
fi

echo
echo "Checagens:"

# 1. Fim de linha: o .gitattributes manda LF. CRLF no índice quebra os scripts no Linux e no WSL.
#    Arquivo marcado -text (OFL.txt das fontes) fica como veio do autor.
git ls-files --eol | awk -F'\t' '{ split($1, f, / +/); if (f[1] == "i/crlf" || (f[1] == "i/mixed" && f[3] != "attr/-text")) print f[1], $2 }' >"$log"
if [ -s "$log" ]; then
  failed "fim de linha: arquivo com CRLF no repositório (rode git add --renormalize .)"
else
  ok "fim de linha LF em $(git ls-files | wc -l | tr -d ' ') arquivos"
fi

# 2. Testes Python (tests/): scripts da skill, fixtures sintéticas.
if uv run -q --no-project --with "$PYTEST" pytest -c tests/pytest.ini tests -q >"$log" 2>&1; then
  passed=$(grep -oE '[0-9]+ passed' "$log" | tail -1 | cut -d' ' -f1)
  skipped=$(grep -oE '[0-9]+ skipped' "$log" | tail -1 | cut -d' ' -f1)
  ok "testes Python: ${passed:-0} passaram${skipped:+, $skipped pulados}"
  grep '^SKIPPED' "$log" | indent
else
  failed "testes Python (uv run --with pytest pytest -c tests/pytest.ini tests)"
fi

# 3. Texto das docs em pt-BR (raiz e site em docs/): erro reprova, aviso só aparece.
#    Ficam de fora o que está em inglês: as instruções dos agentes, as traduções (*.en.md)
#    e as páginas em inglês do site (docs/en/).
docs=()
for f in *.md; do
  case "$f" in AGENTS.md | CLAUDE.md | GEMINI.md | *.en.md) continue ;; esac
  [ -f "$f" ] && docs+=("$f")
done
while IFS= read -r f; do docs+=("$f"); done < <(git ls-files -co --exclude-standard -- 'docs/*.md' ':!docs/en/*' ':!docs/node_modules/*')
if [ "${#docs[@]}" -eq 0 ]; then
  ok "texto das docs: nenhum .md em pt-BR"
elif uv run -q .agents/skills/motion-cena/scripts/lint_copy.py "${docs[@]}" >"$log" 2>&1; then
  ok "texto das docs (${#docs[@]} arquivos): $(tail -1 "$log")"
  grep ': aviso: ' "$log" | indent
else
  failed "texto das docs (${#docs[@]} arquivos)"
fi

# 4. shellcheck nos scripts do projeto (os do HyperFrames em .agents/skills/ vêm de fora, como estão).
shs=()
while IFS= read -r f; do
  [ -f "$f" ] && shs+=("$f")
done < <(git ls-files -co --exclude-standard -- '*.sh' | grep -vE '^\.agents/skills/' ; git ls-files -co --exclude-standard -- '.agents/skills/motion-cena/*.sh')
if uvx -q --from "$SHELLCHECK" shellcheck "${shs[@]}" >"$log" 2>&1; then
  ok "shellcheck: ${#shs[@]} scripts"
else
  failed "shellcheck"
fi

# 5. Workflows do GitHub (actionlint também passa o shellcheck nos blocos run:).
if [ -d .github/workflows ]; then
  if uvx -q --from "$ACTIONLINT" --with "$SHELLCHECK" actionlint >"$log" 2>&1; then
    ok "workflows do GitHub (actionlint)"
  else
    failed "workflows do GitHub (actionlint)"
  fi
fi

# 6. Testes que vêm com as skills do HyperFrames (node --test), offline.
mjs=()
skipped=0
while IFS= read -r f; do
  case "$NODE_SKIP" in *"
$f
"*) skipped=$((skipped + 1)); continue ;; esac
  mjs+=("$f")
done < <(git ls-files -- '*.test.mjs')
if [ "${#mjs[@]}" -eq 0 ]; then
  ok "testes do HyperFrames: nenhum encontrado"
elif node --test --test-reporter=dot "${mjs[@]}" >"$log" 2>&1; then
  ok "testes do HyperFrames: ${#mjs[@]} arquivos (${skipped} fora: dependem do monorepo do HyperFrames)"
else
  failed "testes do HyperFrames (node --test)"
fi

echo
if [ "$fails" -eq 0 ]; then
  echo "Tudo certo em ${SECONDS} s."
else
  echo "$fails checagem(ns) falharam (${SECONDS} s)."
  exit 1
fi
