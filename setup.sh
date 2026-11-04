#!/usr/bin/env bash
# Prepara o motion-cena numa máquina nova: confere dependências e cria os arquivos locais
# (fora do git). Pode rodar de novo: nunca sobrescreve o que já existe.
set -euo pipefail
cd "$(dirname "$0")"

ok=1
check() {
  if command -v "$1" >/dev/null 2>&1; then
    printf '  ok      %s\n' "$1"
  else
    printf '  FALTA   %s  (%s)\n' "$1" "$2"
    ok=0
  fi
}

echo "Dependências:"
check node   "Node 22+: https://nodejs.org"
check npx    "vem com o Node"
check ffmpeg "https://ffmpeg.org/download.html"
check ffprobe "vem com o FFmpeg"
check uv     "https://docs.astral.sh/uv/"
if command -v node >/dev/null 2>&1; then
  major=$(node -p 'process.versions.node.split(".")[0]')
  [ "$major" -ge 22 ] || { echo "  Node $major encontrado; precisa de 22+"; ok=0; }
fi

echo
echo "Agente de código (basta um):"
found=0
for a in claude codex agy gemini cursor-agent opencode copilot; do
  if command -v "$a" >/dev/null 2>&1; then printf '  ok      %s\n' "$a"; found=1; fi
done
[ "$found" -eq 1 ] || echo "  nenhum encontrado no PATH (Cursor, Windsurf e Copilot no editor também servem: abra a pasta)"

echo
echo "Pastas locais:"
mkdir -p projects creatives/reels creatives/carrossel creatives/post training/voz training/referencias
echo "  projects/  creatives/{reels,carrossel,post}/  training/{voz,referencias}/"

copy() {
  if [ -e "$2" ]; then
    printf '  mantido %s\n' "$2"
  else
    cp "$1" "$2"
    printf '  criado  %s\n' "$2"
  fi
}

echo
# Só as skills da lista viram skill nativa do Claude Code: cada uma manda a descrição em toda
# chamada. As outras ficam em .agents/skills/ e são lidas como documento quando o motion-cena pede.
LIST=.agents/skills/claude-links.txt
echo "Skills para o Claude Code (.claude/skills/ -> .agents/skills/, lista em $LIST):"
mkdir -p .claude/skills
wanted=" "
if [ -f "$LIST" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%%#*}
    line=$(printf '%s' "$line" | tr -d '[:space:]')
    [ -n "$line" ] && wanted="$wanted$line "
  done <"$LIST"
else
  printf '  FALTA   %s: nenhum link criado\n' "$LIST"
  ok=0
fi
# Tira só o que este script criaria: link para .agents/skills/ que sumiu ou saiu da lista.
# Skill sua, pasta de verdade e link para outro lugar ficam como estão.
r=0
here=$(pwd -P)
for l in .claude/skills/*; do
  [ -L "$l" ] || continue
  target=$(readlink "$l")
  case "$target" in
    ../../.agents/skills/* | "$PWD/.agents/skills/"* | "$here/.agents/skills/"*) ;;
    *) continue ;;
  esac
  name=$(basename "$l")
  if [ ! -e "$l" ] || { [ -f "$LIST" ] && [ "${wanted#* "$name" }" = "$wanted" ]; }; then
    rm -f "$l"   # só o link: rm sem -r nunca entra no destino
    r=$((r + 1))
  fi
done
n=0
for name in $wanted; do
  d=".agents/skills/$name"
  link=".claude/skills/$name"
  if [ ! -d "$d" ]; then
    printf '  aviso   %s está na lista, mas %s não existe\n' "$name" "$d"
    continue
  fi
  { [ -e "$link" ] || [ -L "$link" ]; } && continue
  ln -s "../../.agents/skills/$name" "$link" 2>/dev/null || cp -R "$d" "$link"
  n=$((n + 1))
done
echo "  $n criado(s). Outros agentes leem .agents/skills/ direto."
[ "$r" -eq 0 ] || echo "  $r removido(s): link para skill fora da lista ou que não existe mais."
for d in .claude/skills/*/; do
  name=$(basename "$d")
  link=".claude/skills/$name"
  # cópia (feita quando o link falhou) de skill que saiu da lista: avisa, não apaga
  if [ ! -L "$link" ] && [ -f "$LIST" ] && [ -d ".agents/skills/$name" ] && [ "${wanted#* "$name" }" = "$wanted" ]; then
    printf '  aviso   %s é uma cópia de skill fora da lista; apague à mão se não quiser carregá-la\n' "$link"
  fi
done

echo
echo "Arquivos locais:"
copy .env.example .env.local
chmod 600 .env.local
copy .agents/skills/motion-cena/assets/registro.template.md creatives/registro.md

echo
if [ "$ok" -eq 1 ]; then
  echo "Pronto. Próximos passos:"
else
  echo "Instale o que falta e rode ./setup.sh de novo. Depois:"
fi
echo "  1. (opcional) Coloque a chave da ElevenLabs em .env.local. Sem ela, a voz sai grátis pelo edge-tts."
echo "  2. Abra seu agente na raiz (claude, codex, agy, Cursor...) e peça, por exemplo: \"faz um reels de 30 s explicando juros compostos\"."
echo "     Marca, voz e tom vão no próprio pedido (site, cores, código do produto ou a gravação de quem fala)."
echo "  3. Para ver o vídeo sendo editado ao vivo, com chat e preview lado a lado: node tools/studio/server.mjs"
