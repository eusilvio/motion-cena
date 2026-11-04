#!/usr/bin/env bash
# Confere e atualiza as skills oficiais do HyperFrames em .agents/skills/ a partir de uma
# versão publicada (tag vX.Y.Z do heygen-com/hyperframes = pacote npm hyperframes@X.Y.Z).
# Nunca mexe em .agents/skills/motion-cena/.
#
#   tools/update-skills.sh                   confere (o mesmo que --check), não muda nada
#   tools/update-skills.sh --apply           atualiza para a última versão
#   tools/update-skills.sh --apply --to 0.9.13
#
# Opções:
#   --check                 só confere e mostra o que mudaria (padrão)
#   --apply                 aplica a atualização
#   --to <versão>           versão de destino (padrão: hyperframes@latest no npm)
#   --from <versão>         versão de onde vieram as skills instaladas, quando o
#                           skills-lock.json não registra (só serve para comparar arquivos)
#   --allow-breaking        aplica mesmo se sair uma skill que o motion-cena cita
#   --overwrite-local a,b   sobrescreve essas skills mesmo com mudança local
#
# Saída do --check: 0 em dia, 2 há atualização, 1 erro.
#
# O skills-lock.json segue o formato do `npx skills` (vercel-labs/skills): o computedHash
# usa o mesmo algoritmo e o script grava `ref` (a tag), que o `npx skills update` respeita.
set -euo pipefail
cd "$(dirname "$0")/.."

REPO_SLUG="heygen-com/hyperframes"
REPO_URL="https://github.com/$REPO_SLUG.git"
SKILLS_DIR=".agents/skills"
LOCK="skills-lock.json"
OWN_SKILL="motion-cena"
LICENSE_FILE="$SKILLS_DIR/HYPERFRAMES-LICENSE"

mode="check"
to=""
from=""
allow_breaking=0
overwrite_local=""

die() { printf 'Erro: %s\n' "$1" >&2; exit 1; }
usage() { sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --check) mode="check" ;;
    --apply) mode="apply" ;;
    --to) [ $# -ge 2 ] || die "--to precisa de uma versão"; to="$2"; shift ;;
    --to=*) to="${1#--to=}" ;;
    --from) [ $# -ge 2 ] || die "--from precisa de uma versão"; from="$2"; shift ;;
    --from=*) from="${1#--from=}" ;;
    --allow-breaking) allow_breaking=1 ;;
    --overwrite-local) [ $# -ge 2 ] || die "--overwrite-local precisa de nomes"; overwrite_local="$2"; shift ;;
    --overwrite-local=*) overwrite_local="${1#--overwrite-local=}" ;;
    -h|--help) usage; exit 0 ;;
    *) die "opção desconhecida: $1 (veja --help)" ;;
  esac
  shift
done
overwrite_local=" $(printf '%s' "$overwrite_local" | tr ',' ' ') "

for c in git node npm; do
  command -v "$c" >/dev/null 2>&1 || die "falta $c no PATH (rode ./setup.sh para conferir as dependências)"
done
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "rode dentro do repositório git do motion-cena"
[ -f "$LOCK" ] || die "não achei $LOCK na raiz"
[ -d "$SKILLS_DIR" ] || die "não achei $SKILLS_DIR"

norm_version() {
  local v="${1#v}"
  printf '%s' "$v" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' || die "versão inválida: $1 (use X.Y.Z)"
  printf '%s' "$v"
}

work=$(mktemp -d "${TMPDIR:-/tmp}/update-skills.XXXXXX")
applying=0
rollback_cmd=""
on_exit() {
  local code=$?
  if [ "$code" -ne 0 ] && [ "$applying" -eq 1 ]; then
    echo
    echo "A atualização parou no meio. Para voltar ao estado do último commit:"
    printf '  %s\n' "$rollback_cmd"
    echo "  ./setup.sh   # refaz os links de .claude/skills"
  fi
  rm -rf "$work"
  exit "$code"
}
trap on_exit EXIT

# ── Ajudante em Node: hash igual ao do `npx skills`, plano e lock ──────────────
cat >"$work/helper.mjs" <<'JS'
import { createHash } from "node:crypto";
import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { readdir, readFile } from "node:fs/promises";
import { join, relative } from "node:path";

// Lixo de execução que não conta como mudança local (mesma lista do `hyperframes skills`).
const RUNTIME_DIRS = new Set(["__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"]);
const RUNTIME_FILES = new Set([".DS_Store", "Thumbs.db"]);
const RUNTIME_SUFFIXES = [".pyc", ".pyo", ".swp", ".swo", "~"];

async function collect(base, cur, out, skipRuntime) {
  const entries = await readdir(cur, { withFileTypes: true });
  for (const e of entries) {
    const full = join(cur, e.name);
    if (e.isDirectory()) {
      if (e.name === ".git" || e.name === "node_modules") continue;
      if (skipRuntime && RUNTIME_DIRS.has(e.name)) continue;
      await collect(base, full, out, skipRuntime);
    } else if (e.isFile()) {
      if (skipRuntime && (RUNTIME_FILES.has(e.name) || RUNTIME_SUFFIXES.some((s) => e.name.endsWith(s)))) continue;
      out.push({ rel: relative(base, full).split("\\").join("/"), full });
    }
  }
}
async function listFiles(dir, skipRuntime) {
  const out = [];
  await collect(dir, dir, out, skipRuntime);
  return out.sort((a, b) => a.rel.localeCompare(b.rel, "en"));
}
// computeSkillFolderHash do skills@1.7.6: sha256 de (caminho relativo + conteúdo), em ordem.
async function hashDir(dir, skipRuntime = false) {
  const h = createHash("sha256");
  for (const f of await listFiles(dir, skipRuntime)) {
    h.update(f.rel);
    h.update(await readFile(f.full));
  }
  return h.digest("hex");
}
const slugOf = (s) => (s ?? "").replace(/^git\+/, "").replace(/^https?:\/\/github\.com\//, "").replace(/\.git$/, "").toLowerCase();
const readLock = (p) => {
  const lock = JSON.parse(readFileSync(p, "utf8"));
  if (lock.version !== 1 || typeof lock.skills !== "object" || lock.skills === null) throw new Error(`${p}: formato inesperado (esperava version 1)`);
  return lock;
};
const ours = (lock, slug) => Object.entries(lock.skills).filter(([, e]) => slugOf(e.source) === slug || slugOf(e.sourceUrl) === slug);
const NAME_RE = /^[a-z0-9][a-z0-9._-]*$/;
function upstreamSkills(dir) {
  return readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isDirectory() && existsSync(join(dir, e.name, "SKILL.md")))
    .map((e) => e.name)
    .sort();
}
function frontmatterName(file) {
  const m = readFileSync(file, "utf8").match(/^---\r?\n([\s\S]*?)\r?\n---/);
  const n = m && m[1].match(/^name:\s*["']?([^"'\r\n]+?)["']?\s*$/m);
  return n ? n[1] : "";
}

const [cmd, ...args] = process.argv.slice(2);
const out = (...cols) => console.log(cols.join("\t"));

if (cmd === "plan") {
  // plan <lock> <skillsDir> <upstreamSkillsDir> <slug> <ownSkill>
  const [lockPath, skillsDir, upDir, slug, own] = args;
  const lock = readLock(lockPath);
  const mine = new Map(ours(lock, slug));
  const foreign = new Set(Object.keys(lock.skills).filter((n) => !mine.has(n)));
  const refs = [...new Set([...mine.values()].map((e) => e.ref ?? ""))];
  out("installed", refs.join(","));
  const up = upstreamSkills(upDir);
  for (const name of up) {
    const fm = frontmatterName(join(upDir, name, "SKILL.md"));
    if (fm !== name || !NAME_RE.test(name)) { out("badname", name, fm); continue; }
    const hash = await hashDir(join(upDir, name));
    if (name === own) { out("collision", name, "mesmo nome da skill do repositório"); continue; }
    if (foreign.has(name)) { out("collision", name, "já existe no lock vinda de outra fonte"); continue; }
    if (!mine.has(name) && existsSync(join(skillsDir, name))) { out("collision", name, "pasta já existe e não veio do HyperFrames"); continue; }
    if (!mine.has(name)) out("added", name, hash);
    else out(mine.get(name).computedHash === hash ? "same" : "changed", name, hash);
  }
  for (const [name, entry] of mine) {
    if (!up.includes(name)) out("removed", name, "");
    const dir = join(skillsDir, name);
    if (!existsSync(join(dir, "SKILL.md"))) out("missing", name, "");
    else if ((await hashDir(dir, true)) !== entry.computedHash) out("modified", name, "");
  }
} else if (cmd === "filediff") {
  // filediff <local> <base>: arquivos que diferem, ignorando lixo de execução
  const [a, b] = args;
  const fa = new Map((await listFiles(a, true)).map((f) => [f.rel, f.full]));
  const fb = new Map((await listFiles(b, true)).map((f) => [f.rel, f.full]));
  for (const [rel, full] of fa) {
    if (!fb.has(rel)) out("local-only", rel);
    else if (!readFileSync(full).equals(readFileSync(fb.get(rel)))) out("changed", rel);
  }
  for (const rel of fb.keys()) if (!fa.has(rel)) out("base-only", rel);
} else if (cmd === "write-lock") {
  // write-lock <lock> <upstreamSkillsDir> <slug> <ref> <nomes...>
  const [lockPath, upDir, slug, ref, ...names] = args;
  const lock = readLock(lockPath);
  const source = ours(lock, slug)[0]?.[1].source ?? slug;
  for (const [name] of ours(lock, slug)) delete lock.skills[name];
  for (const name of names) {
    lock.skills[name] = { source, ref, sourceType: "github", skillPath: `skills/${name}/SKILL.md`, computedHash: await hashDir(join(upDir, name)) };
  }
  // Mesma serialização do writeLocalLock do `npx skills`: chaves ordenadas, 2 espaços.
  const skills = Object.fromEntries(Object.keys(lock.skills).sort().map((k) => [k, lock.skills[k]]));
  writeFileSync(lockPath, JSON.stringify({ version: lock.version, skills }, null, 2) + "\n");
} else if (cmd === "verify") {
  // verify <lock> <skillsDir> <slug>: confere pasta instalada x computedHash
  const [lockPath, skillsDir, slug] = args;
  for (const [name, entry] of ours(readLock(lockPath), slug)) {
    const dir = join(skillsDir, name);
    if (!existsSync(join(dir, "SKILL.md"))) out("missing", name);
    else if ((await hashDir(dir, true)) !== entry.computedHash) out("mismatch", name);
  }
} else if (cmd === "names") {
  // names <lock> <slug>: skills do HyperFrames registradas no lock
  for (const [name] of ours(readLock(args[0]), args[1])) out(name);
} else {
  console.error(`comando desconhecido: ${cmd}`);
  process.exit(1);
}
JS
helper() { node "$work/helper.mjs" "$@"; }

# ── Versões ──────────────────────────────────────────────────────────────────
echo "Versões (HyperFrames, $REPO_SLUG):"
if [ -n "$to" ]; then
  target=$(norm_version "$to")
else
  latest=$(npm view hyperframes dist-tags.latest 2>/dev/null) || die "não consegui consultar o npm (sem rede?)"
  target=$(norm_version "$latest")
fi
npm view "hyperframes@$target" version >/dev/null 2>&1 || die "hyperframes@$target não existe no npm"
GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote --exit-code --tags "$REPO_URL" "refs/tags/v$target" >/dev/null 2>&1 \
  || die "a tag v$target não existe em $REPO_URL"

clone_at() { # clone_at <versão> <pasta>: só skills/ e os arquivos da raiz, na tag
  GIT_TERMINAL_PROMPT=0 git -c credential.helper= -c advice.detachedHead=false \
    clone --quiet --depth 1 --branch "v$1" --filter=blob:none --sparse "$REPO_URL" "$2" \
    || die "não consegui baixar v$1 de $REPO_URL"
  git -C "$2" sparse-checkout set skills >/dev/null || die "não consegui baixar skills/ de v$1"
  [ -d "$2/skills" ] || die "v$1 não tem a pasta skills/"
}
up="$work/target"
clone_at "$target" "$up"

helper plan "$LOCK" "$SKILLS_DIR" "$up/skills" "$REPO_SLUG" "$OWN_SKILL" >"$work/plan.tsv" \
  || die "não consegui comparar as skills (skills-lock.json válido?)"
pick() { awk -F'\t' -v k="$1" '$1 == k { print $2 }' "$work/plan.tsv" | tr '\n' ' ' | sed 's/ $//'; }
installed=$(pick installed)
added=$(pick added); changed=$(pick changed); same=$(pick same); removed=$(pick removed)
missing=$(pick missing); modified=$(pick modified)
collisions=$(awk -F'\t' '$1 == "collision" { printf "  BLOQUEIA %s (%s)\n", $2, $3 }' "$work/plan.tsv")
badnames=$(awk -F'\t' '$1 == "badname" { printf "  BLOQUEIA skills/%s (name no SKILL.md: \"%s\")\n", $2, $3 }' "$work/plan.tsv")

case "$installed" in
  "") installed_label="não registrada no $LOCK (instalada antes deste script)" ;;
  *,*) installed_label="misturada: $installed" ;;
  *) installed_label="${installed#v}" ;;
esac
[ -n "$from" ] && installed_label="$(norm_version "$from") (informada com --from)"
printf '  instalada  %s\n' "$installed_label"
printf '  destino    %s (npm hyperframes@%s, tag v%s)\n' "$target" "$target" "$target"

has() { case " $1 " in *" $2 "*) return 0 ;; esac; return 1; }
list() { if [ -n "$1" ]; then printf '%s' "$1"; else printf '(nenhuma)'; fi; }

echo
echo "O que muda nas skills:"
printf '  mudam     %s\n' "$(list "$changed")"
printf '  entram    %s\n' "$(list "$added")"
printf '  saem      %s\n' "$(list "$removed")"
printf '  iguais    %s\n' "$(list "$same")"
[ -n "$missing" ] && printf '  faltam    %s (o update baixa de novo)\n' "$missing"

# ── Mudanças locais nas skills vendorizadas ──────────────────────────────────
# Uma skill conta como modificada quando a pasta (sem __pycache__ e afins) não bate com o
# computedHash do lock. Com a versão de origem conhecida, compara arquivo a arquivo e
# desconsidera arquivo do upstream que o .gitignore deixou fora do git (clone novo não tem).
base_ref="${installed#v}"
[ -n "$from" ] && base_ref=$(norm_version "$from")
case "$base_ref" in *,*) base_ref="" ;; esac
blocked_local=""; restore=""; kept=""
echo
echo "Mudanças locais nas skills do HyperFrames:"
if [ -z "$modified" ]; then
  echo "  ok        nenhuma (lixo de execução como __pycache__ não conta)"
else
  base=""
  if [ -n "$base_ref" ]; then
    if [ "$base_ref" = "$target" ]; then base="$up"; else base="$work/base"; clone_at "$base_ref" "$base"; fi
  fi
  for name in $modified; do
    if [ -z "$base" ]; then
      printf '  MUDOU     %s (sem a versão de origem não dá para listar os arquivos; use --from <versão>)\n' "$name"
    elif [ ! -d "$base/skills/$name" ]; then
      printf '  MUDOU     %s (não existe na versão de origem %s)\n' "$name" "$base_ref"
    else
      helper filediff "$SKILLS_DIR/$name" "$base/skills/$name" >"$work/diff-$name.tsv"
      real=""; benign=""
      while IFS=$'\t' read -r kind rel; do
        if [ "$kind" = "base-only" ] && git check-ignore -q -- "$SKILLS_DIR/$name/$rel"; then
          benign="$benign $rel"
        else
          case "$kind" in changed) kind="alterado" ;; local-only) kind="só-aqui" ;; base-only) kind="apagado" ;; esac
          real="$real $kind:$rel"
        fi
      done <"$work/diff-$name.tsv"
      if [ -z "$real" ]; then
        printf '  ok        %s (só falta arquivo que o git ignora:%s)\n' "$name" "$benign"
        has "$same" "$name" && restore="$restore $name"   # o --apply copia de novo do upstream
        continue
      fi
      printf '  MUDOU     %s: %s\n' "$name" "$(printf '%s' "${real# }" | tr ' ' '\n' | head -8 | paste -sd ' ' -)"
    fi
    if has "$overwrite_local" "$name"; then
      printf '            vai ser sobrescrita (--overwrite-local); o original fica no histórico do git\n'
      has "$same" "$name" && restore="$restore $name"
    elif has "$changed $removed" "$name"; then
      blocked_local="$blocked_local $name"
    else
      printf '            não muda no upstream: fica como está\n'
      kept="$kept $name"
    fi
  done
fi
blocked_local="${blocked_local# }"

# ── Skills que o motion-cena cita ───────────────────────────────────────────
old_names=$(helper names "$LOCK" "$REPO_SLUG" | tr '\n' ' ')
cite_files() {
  printf '%s\n' AGENTS.md
  find "$SKILLS_DIR/$OWN_SKILL" -type f -name '*.md' | sort
}
# Citação = nome entre crases ou colado numa barra: `hyperframes-core`, /media-use,
# .agents/skills/hyperframes-animation/rules. Palavra solta no texto não conta.
cited_missing() { # cited_missing "<nomes que vão existir>": imprime "nome<TAB>arquivo:linha"
  local exists=" $1 " name f line
  for name in $old_names $added; do
    has "$exists" "$name" && continue
    while IFS= read -r f; do
      { grep -nE "[\`/]${name}([^a-z0-9-]|\$)|(^|[^a-z0-9-])${name}[\`/]" "$f" 2>/dev/null || true; } \
        | cut -d: -f1 | while IFS= read -r line; do printf '%s\t%s:%s\n' "$name" "$f" "$line"; done
    done < <(cite_files)
  done
}
after="$same $changed $added $missing"
for name in $removed; do after=$(printf ' %s ' "$after" | sed "s/ $name / /g"); done
cited_missing "$after" >"$work/cites.tsv"
blocked_cites=$(cut -f1 "$work/cites.tsv" | sort -u | tr '\n' ' ' | sed 's/ $//')
echo
echo "Skills citadas pelo AGENTS.md e pela skill motion-cena:"
if [ -z "$blocked_cites" ]; then
  echo "  ok        todas continuam existindo"
else
  for name in $blocked_cites; do
    printf '  QUEBRA    %s sai, mas é citada em: %s\n' "$name" \
      "$(awk -F'\t' -v n="$name" '$1 == n { print $2 }' "$work/cites.tsv" | head -6 | tr '\n' ' ')"
  done
fi

# ── Versão do CLI fixada no repositório ──────────────────────────────────────
echo
echo "Versão do CLI fixada (npx hyperframes@X):"
pins=$(git grep -lE 'hyperframes@[0-9]+\.[0-9]+\.[0-9]+' -- '*package.json' ':!.agents' 2>/dev/null || true)
if [ -z "$pins" ]; then
  echo "  nenhuma: o repositório não fixa a versão do CLI; a versão das skills fica no ref do $LOCK"
else
  for p in $pins; do
    v=$(grep -oE 'hyperframes@[0-9]+\.[0-9]+\.[0-9]+' "$p" | head -1 | cut -d@ -f2)
    if [ "$v" = "$target" ]; then
      printf '  ok        %s (%s)\n' "$p" "$v"
    else
      printf '  aviso     %s fixa %s. Projeto validado com essa versão; para subir, confira antes:\n' "$p" "$v"
      printf '            (cd %s && npx hyperframes@%s upgrade --project . --check)\n' "$(dirname "$p")" "$target"
    fi
  done
fi

echo
[ -n "$collisions" ] && { echo "Conflito de nome:"; echo "$collisions"; echo; }
[ -n "$badnames" ] && { echo "Skill do upstream com nome inesperado:"; echo "$badnames"; echo; }

pending=0
{ [ -n "$changed$added$removed$missing" ] || [ "$installed" != "v$target" ]; } && pending=1

if [ "$mode" = "check" ]; then
  [ -z "$(git status --porcelain -- "$SKILLS_DIR" "$LOCK")" ] \
    || echo "Aviso: há mudanças não commitadas em $SKILLS_DIR ou $LOCK; o --apply vai recusar."
  if [ "$pending" -eq 0 ]; then
    echo "Em dia: as skills já são as do HyperFrames $target."
    exit 0
  fi
  if [ -z "$changed$added$removed$missing" ]; then
    echo "O conteúdo já é o do $target; falta só registrar a versão no $LOCK."
  else
    echo "Há atualização. Para aplicar: tools/update-skills.sh --apply --to $target"
  fi
  [ -n "$blocked_local" ] && echo "  antes: resolva as mudanças locais em $blocked_local (ou use --overwrite-local)."
  [ -n "$blocked_cites" ] && echo "  antes: o update tira skills que o motion-cena usa; ajuste as citações ou use --allow-breaking."
  exit 2
fi

# ── Aplicar ─────────────────────────────────────────────────────────────────
if [ -n "$(git status --porcelain -- "$SKILLS_DIR" "$LOCK")" ]; then
  echo "Há mudanças não commitadas em $SKILLS_DIR ou $LOCK:"
  git status --short -- "$SKILLS_DIR" "$LOCK" | sed 's/^/  /'
  die "faça commit ou guarde essas mudanças (git stash) e rode de novo"
fi
[ -z "$collisions$badnames" ] || die "o upstream tem skill com nome em conflito (veja acima); nada foi alterado"
if [ -n "$blocked_local" ]; then
  echo "As skills abaixo têm mudanças locais e o update ia sobrescrever ou apagar:"
  for name in $blocked_local; do printf '  %s\n' "$name"; done
  echo "Leve o que você mudou para a skill motion-cena (ou anote o diff) e rode com"
  echo "  --overwrite-local $(printf '%s' "$blocked_local" | tr ' ' ',')"
  die "nada foi alterado"
fi
if [ -n "$blocked_cites" ] && [ "$allow_breaking" -eq 0 ]; then
  echo "O HyperFrames $target tira skills que o AGENTS.md ou a skill motion-cena citam: $blocked_cites"
  echo "Atualize essas citações primeiro (ou rode com --allow-breaking e ajuste antes do commit)."
  die "nada foi alterado"
fi
if [ "$pending" -eq 0 ]; then
  echo "Nada a fazer: as skills já são as do HyperFrames $target."
  exit 0
fi

# Desfazer: apaga o que o update escreveu (inclusive arquivo ignorado) nas pastas que ele
# mexeu e devolve a versão do HEAD. Skill nova não existe no HEAD: só entra no clean.
clean_paths=""; restore_paths="$LOCK $LICENSE_FILE"
for name in $changed $added $restore; do clean_paths="$clean_paths $SKILLS_DIR/$name"; done
for name in $changed $removed $missing $restore; do
  has "$restore_paths" "$SKILLS_DIR/$name" || restore_paths="$restore_paths $SKILLS_DIR/$name"
done
rollback_cmd="git restore --source=HEAD --staged --worktree -- $restore_paths"
[ -n "$clean_paths" ] && rollback_cmd="git clean -fdx --$clean_paths && $rollback_cmd"
safe_name() {
  case "$1" in ""|.|..|*/*|"$OWN_SKILL") die "nome de skill inseguro: '$1'" ;; esac
}

applying=1
echo "Aplicando HyperFrames $target:"
for name in $removed; do
  safe_name "$name"
  rm -rf "${SKILLS_DIR:?}/$name"
  printf '  saiu      %s\n' "$name"
done
for name in $changed $added $missing $restore; do
  safe_name "$name"
  has "$removed" "$name" && continue
  rm -rf "${SKILLS_DIR:?}/$name"
  cp -R "$up/skills/$name" "$SKILLS_DIR/$name"
  printf '  gravada   %s\n' "$name"
done
if [ -f "$up/LICENSE" ] && ! cmp -s "$up/LICENSE" "$LICENSE_FILE"; then
  cp "$up/LICENSE" "$LICENSE_FILE"
  printf '  gravada   %s\n' "$LICENSE_FILE"
fi
# shellcheck disable=SC2086  # lista de nomes separada por espaço, de propósito
helper write-lock "$LOCK" "$up/skills" "$REPO_SLUG" "v$target" $same $changed $added
printf '  gravado   %s (ref v%s)\n' "$LOCK" "$target"

echo
echo "Skills para o Claude Code (.claude/skills/ -> .agents/skills/):"
mkdir -p .claude/skills
for name in $removed $changed; do # cópia (sem symlink) de skill que mudou fica velha
  link=".claude/skills/$name"
  if [ -d "$link" ] && [ ! -L "$link" ]; then rm -rf "$link"; fi
done
for l in .claude/skills/*; do
  [ -L "$l" ] && [ ! -e "$l" ] && rm "$l"   # link de skill que não existe mais
done
# Só as skills de .agents/skills/claude-links.txt (o setup.sh também tira as que saíram da lista)
n=0
while IFS= read -r name || [ -n "$name" ]; do
  name=$(printf '%s' "${name%%#*}" | tr -d '[:space:]')
  if [ -z "$name" ] || [ ! -d "$SKILLS_DIR/$name" ]; then continue; fi
  link=".claude/skills/$name"
  { [ -e "$link" ] || [ -L "$link" ]; } && continue
  ln -s "../../$SKILLS_DIR/$name" "$link" 2>/dev/null || cp -R "$SKILLS_DIR/$name" "$link"
  n=$((n + 1))
done < <(cat "$SKILLS_DIR/claude-links.txt" 2>/dev/null || true)
echo "  $n criado(s)."

echo
echo "Conferência:"
bad=$(helper verify "$LOCK" "$SKILLS_DIR" "$REPO_SLUG" | awk -F'\t' -v k=" $kept " 'index(k, " " $2 " ") == 0')
[ -z "$bad" ] || { printf '  ERRO      %s\n' "$bad"; die "o que está em $SKILLS_DIR não bate com o $LOCK"; }
echo "  ok        pastas batem com o $LOCK"
[ -f "$SKILLS_DIR/$OWN_SKILL/SKILL.md" ] || die "$SKILLS_DIR/$OWN_SKILL sumiu"

present=""
for d in "$SKILLS_DIR"/*/; do [ -f "$d/SKILL.md" ] && present="$present $(basename "$d")"; done
gone=$(cited_missing "$present")
if [ -n "$gone" ]; then
  echo "$gone" | awk -F'\t' '{ printf "  QUEBRA    %s citada em %s\n", $1, $2 }'
  die "o motion-cena cita skills que não existem mais; ajuste as citações antes do commit"
fi
echo "  ok        skills citadas pelo motion-cena existem"

if [ -f tools/check.sh ]; then
  bash tools/check.sh || die "tools/check.sh falhou"
  echo "  ok        tools/check.sh"
fi

ignored=$(for name in $changed $added $missing $restore; do
  [ -d "$SKILLS_DIR/$name" ] || continue
  find "$SKILLS_DIR/$name" -type f | git check-ignore --stdin 2>/dev/null || true
done)
applying=0

echo
prev="${installed#v}"; [ -n "$from" ] && prev=$(norm_version "$from")
echo "Pronto: skills do HyperFrames ${prev:-sem versão registrada} -> $target."
printf '  mudaram   %s\n  entraram  %s\n  saíram    %s\n' "$(list "$changed")" "$(list "$added")" "$(list "$removed")"
if [ -n "$ignored" ]; then
  echo
  echo "O .gitignore deixaria fora do commit arquivos que vieram do upstream. Inclua com:"
  # shellcheck disable=SC2086  # um caminho por palavra
  { printf '  git add -f --'; printf ' %s' $ignored; echo; }
fi
echo
echo "Revise e faça o commit:"
echo "  git status -- $SKILLS_DIR $LOCK"
echo "  git add $SKILLS_DIR $LOCK && git commit -m \"chore: update HyperFrames skills to v$target\""
echo "Para desfazer antes do commit:"
printf '  %s\n' "$rollback_cmd"
echo "  ./setup.sh   # refaz os links de .claude/skills"
