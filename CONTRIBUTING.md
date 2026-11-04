# Como contribuir

> **English:** issues and pull requests in English are welcome. This guide is in Brazilian Portuguese; the agent instructions (`AGENTS.md` and `.agents/skills/motion-cena/`) are already in English.

O motion-cena é público e sai zerado: nenhuma marca, voz, cliente ou tema de ninguém. Toda contribuição precisa manter isso. O resto deste guia mostra como preparar a máquina, o que conferir antes do PR e as duas portas de entrada mais fáceis: um efeito novo no dicionário e uma receita de estilo.

Antes de mudança grande (etapa nova no pipeline, troca de motor, script novo), abra uma issue para combinar o caminho. Correção pequena, efeito e receita podem ir direto para PR. Frentes abertas e boas primeiras contribuições estão no [ROADMAP.md](ROADMAP.md).

## Preparar a máquina

Faça um fork, clone o seu fork e rode o setup:

```bash
git clone https://github.com/<seu-usuario>/motion-cena.git
cd motion-cena
./setup.sh          # Linux e macOS
```

No Windows, em PowerShell: `.\setup.ps1`.

O setup confere Node 22+, FFmpeg, uv e o agente de código, cria as pastas locais (fora do git) e o `.env.local`.

Trabalhe numa branch a partir de `main` (`git switch -c feat/nome-curto`) e abra o PR para `main`.

## Antes de abrir o PR

```bash
./tools/check.sh
```

Ele roda na sua máquina os mesmos checks que o CI (`.github/workflows/ci.yml`) roda em cada PR: os testes de `tests/` com pytest (inclusive os 388 efeitos do dicionário num Chromium, quando ele está instalado), o `lint_copy.py` nos documentos em pt-BR da raiz e de `docs/`, o shellcheck nos scripts `.sh`, o actionlint no workflow, a checagem de fim de linha e os testes das skills do HyperFrames. Shellcheck e actionlint vêm pelo `uv`, sem instalar nada. O `check.sh` é bash; no Windows, rode pelo Git Bash ou pelo WSL.

## O que nunca entra num PR

O `.gitignore` já deixa quase tudo isso de fora. Nunca force com `git add -f`, e confira `git status` e `git diff --staged` antes de cada commit.

| Nunca sobe | Onde fica na sua máquina | Por quê |
|---|---|---|
| projetos em produção | `projects/` | brief, roteiro e áudio são seus |
| peças finais | `creatives/` (só as demos do dicionário sobem) | são suas, e vídeo pesa no histórico |
| gravação de voz | `training/voz/` | dado biométrico |
| vídeo de terceiros e a análise dele | `training/referencias/` e as receitas em `references/styles/` fora de `community/` | a peça é de outra pessoa |
| chaves e tokens | `.env.local` | trocar uma chave vazada dá trabalho; apagar o commit não basta |
| configuração do seu agente | `.claude/`, `.cursor/`, `.vscode/`, `CLAUDE.local.md` | é da sua máquina |
| marca, cliente, produto, roteiro ou tema seu | em exemplo, teste, demo ou documentação | o repositório é neutro: use exemplos genéricos, como juros compostos ou uma loja fictícia |

Fonte, ícone ou imagem novos numa demo só entram com licença livre (OFL, CC0) e o arquivo da licença junto, como em `training/dicionario-demo/assets/fonts/OFL.txt`.

## Porta 1: efeito novo no dicionário

O dicionário tem duas camadas. `references/motion-dictionary.md` guarda os **44 efeitos curados**, cada um com cena de demo renderizada. `references/motion-dictionary/` guarda o **catálogo de 388 efeitos**, um JSON por família, com nome, apelidos, padrão e código GSAP, que o agente consulta com `scripts/motion_lookup.py`. Dá para contribuir nas duas: efeito novo entra pelo catálogo, e um efeito do catálogo sobe para os curados quando ganha demo.

Um efeito novo entra quando tem nome que motion designers já usam e não é só a soma de dois que já existem (combinação vai em "Combinations that work" e no campo `combina_com`). Se quiser opinião antes de escrever código, abra a issue "Efeito novo".

### 1a. Efeito novo no catálogo

1. **Confira se já existe.** Procure pelo nome e pelos apelidos:
   ```bash
   uv run .agents/skills/motion-cena/scripts/motion_lookup.py "split flap" --brief
   ```
2. **Escreva a entrada** no fim do JSON da família (`references/motion-dictionary/<família>.json`), com todos os campos do `schema.json` e `"origem": "expansao"`. Textos em pt-BR, como os vizinhos. O `gsap` segue as mesmas regras do resto do dicionário, para o render poder pular para qualquer quadro:
   - um único `tl` pausado, `fromTo` com estado inicial explícito, `t` como início;
   - só `transform`, `opacity`, `filter`, `clip-path` e atributos SVG (nada de `width`, `height`, `top`);
   - sem `Math.random`, `Date` ou `setTimeout`: use hash por índice ou um gerador com semente fixa, como no `scramble` e no `grain`;
   - loop sempre finito;
   - um comentário dizendo que DOM o efeito espera (`// items = barras do gráfico`).
3. **Valide e gere o índice:**
   ```bash
   uv run .agents/skills/motion-cena/scripts/motion_lookup.py --validate
   uv run .agents/skills/motion-cena/scripts/motion_lookup.py --write-index
   ./tools/check.sh
   ```
   O `check.sh` roda cada efeito do catálogo num Chromium sem janela quando o Chromium do Playwright está instalado (`uv run --with playwright playwright install chromium`). Sem ele, o teste é pulado.

### 1b. Levar um efeito para os curados

Vale para um efeito do catálogo ou para um termo novo que já nasce com demo. No JSON, troque `"origem"` para `"dicionario-atual"` e regenere o índice. Depois:

1. **Confira se já existe** entre os curados: tabela rápida, "Combinations that work" e "Common mistakes" de `motion-dictionary.md`.
2. **Linha na tabela.** No fim das tabelas rápidas, use a seção `### Part 3: community` (crie se ainda não existir, com as mesmas colunas da parte 2). O texto do dicionário é em inglês, porque o agente lê:
   ```markdown
   | Text | **split-flap** | letters flip like an airport board until they settle | 0,6 s, 0,04 s per letter | `hacker-flip-3d` |
   ```
   Na coluna "HyperFrames recipe", cite a regra mais próxima de `.agents/skills/hyperframes-animation/rules/`; se nenhuma servir, deixe um traço, como nas linhas vizinhas.
3. **Receita GSAP.** Em "GSAP recipes", crie ou use `### Part 3: <família>` antes de "Combinations that work". As regras são as do resto do arquivo, para o render poder pular para qualquer quadro:
   - um único `tl` pausado, `fromTo` com estado inicial explícito, `t` como início;
   - só `transform`, `opacity`, `filter` e `clip-path` (nada de `width`, `height`, `top`);
   - sem `Math.random`: use hash por índice ou um gerador com semente fixa, como no `scramble` e no `grain`;
   - loop sempre finito.
4. **Armadilha comum**, se houver: uma linha em "Common mistakes".
5. **Cena de demo.** A demo do efeito entra no fim da parte 2, `training/dicionario-demo-2/`, que é gerada por script e aceita cena nova sem mexer nas outras (a parte 3 do dicionário usa essa mesma demo). A primeira cena nova é a 27; troque `N` pelo número da sua.
   - Em `build.py`, acrescente ao fim de `SCENES` uma tupla `(família, termo, parâmetros, html da demo)`. Família e parâmetros em português, como os vizinhos (`"texto"`, `"vira as letras · <b>0,6 s</b>"`). Ids dos elementos: `fN`, `fN-a`, `fN-b`.
   - Em `index.tpl`, o CSS da demo vai no `<style>`, e a animação vai num bloco `// N <termo>` logo antes de `window.__timelines["main"] = tl;`, usando `fx(N)` (início da cena mais 0,55 s).
   - Gere o HTML (precisa de Python 3.12 ou mais novo; o uv baixa se faltar) e suba `build.py`, `index.tpl` e `index.html` juntos:
     ```bash
     cd training/dicionario-demo-2
     uv run --python 3.12 build.py
     ```
6. **Rode o check do HyperFrames.** Na mesma pasta, `npm run check`. Zero erro.
7. **Olhe os quadros.** A cena N começa em 3 + 2,6 × (N − 1) segundos e dura 2,6 s (a 27 vai de 70,6 s a 73,2 s). Use a versão do HyperFrames que está no `package.json` da demo:
   ```bash
   npx --yes hyperframes@0.8.181 snapshot --range 70.6:73.2 --frames 6 --output /tmp/efeito
   ```
   Abra os PNGs. O efeito precisa ser lido sem explicação e terminar dentro dos 2,6 s.
8. **Renderize e anexe.** Render rápido da demo inteira e corte só a sua cena:
   ```bash
   npm run render -- --quality draft -o /tmp/demo-2.mp4
   ffmpeg -ss 70.6 -t 2.6 -i /tmp/demo-2.mp4 /tmp/efeito.mp4
   ```
   Arraste `/tmp/efeito.mp4` para a descrição do PR. Não suba o MP4 de `creatives/demos/`: ele é atualizado à parte, para o histórico não ganhar um vídeo novo a cada efeito.
9. **Contagem.** O número de efeitos curados aparece em `README.md`, `README.en.md`, `training/README.md` e na abertura do dicionário. Atualize todos.

Commits sugeridos: `feat(dictionary): add split-flap to the catalog` (1a) e `feat(dictionary): promote split-flap with demo` (1b).

## Porta 2: receita de estilo

Uma receita de estilo ensina ao agente uma gramática de vídeo: como os blocos se distribuem no tempo, que linguagem visual usar, quais componentes montar e onde entra o som. As receitas que a skill cria a partir de um vídeo de referência ficam só na máquina de quem pediu, porque são análise da peça de outra pessoa. As da comunidade são outra coisa e moram em outra pasta: `.agents/skills/motion-cena/references/styles/community/`.

**A regra:** uma receita da comunidade descreve uma gramática que você criou e usa, ou um gênero ou escola que não tem dono (grade tipográfica suíça, lower thirds de telejornal, tipografia cinética, colagem de fanzine). Nunca a quebra de um vídeo, série ou canal específico de outra pessoa: nada de perfil citado, tempos medidos numa peça, logo, personagem, bordão ou texto de terceiros. Se a receita só faz sentido ao lado de um vídeo, ela é local e não entra.

Se quiser opinião antes, abra a issue "Receita de estilo".

1. **Copie o modelo** com um nome curto em kebab-case que diga a gramática:
   ```bash
   S=.agents/skills/motion-cena/references/styles
   mkdir -p $S/community && cp $S/_template.md $S/community/swiss-grid.md
   ```
2. **Troque a linha `Reference:`** por `Origin: own grammar (<seu nome>)` ou `Origin: genre/school (<nome>)`, com fontes públicas e genéricas se houver (um livro, um movimento de design).
3. **Preencha em inglês**, como o resto da skill: a ideia em uma linha, estrutura com tempos (escolhidos por você), linguagem visual, componentes ligados a termos do `motion-dictionary.md` e às receitas do HyperFrames, som, como adaptar e o checklist do estilo.
4. **Acrescente uma linha** na tabela do fim de `references/styles/README.md` (estilo, mecanismo, bom para, origem).
5. **Teste com o seu agente** num tema neutro: *"faz um reels de 15 s sobre juros compostos no estilo swiss-grid"*. Confira se ele leu a receita e se o vídeo segue a gramática. Anexe ao PR um trecho ou a contact sheet que o `qa_video.sh` gera; o projeto e o MP4 continuam fora do git.

Commit sugerido: `docs(styles): add swiss-grid community recipe`.

## Correções em scripts

- Mudou um script de `.agents/skills/motion-cena/scripts/`? O PR traz um teste em `tests/` que falha sem a correção e passa com ela. Siga o padrão dos testes que já existem lá.
- Script Python declara as dependências no próprio arquivo (bloco `# /// script`) e roda com `uv run`. Nada instalado no sistema.
- Script shell passa no shellcheck.
- Mudou o que o script faz ou os argumentos dele? Atualize onde ele é citado: `SKILL.md`, `references/` e a tabela "Scripts" do README.
- As skills do HyperFrames em `.agents/skills/` (todas menos `motion-cena/`) são cópias do repositório [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes), travadas no `skills-lock.json`. Não edite à mão: bug nelas vai para o repositório deles, e `tools/update-skills.sh` traz a versão nova.

## Idioma

- **Instruções para o agente, em inglês:** `AGENTS.md` e tudo em `.agents/skills/motion-cena/` (`SKILL.md`, `references/`, receitas de estilo). As listas de frases em português dentro da skill (padrões do `lint_copy.py`, exemplos de `writing-style.md` e `hooks.md`) ficam em português, porque servem para texto em português.
- **Documentação para pessoas, em pt-BR:** `README.md`, este guia, `ROADMAP.md` e os README das pastas. O `README.en.md` é a versão em inglês do README.
- Texto em pt-BR: direto, com "você", sem emoji e sem frase com cara de IA. O `lint_copy.py` aponta o que reescrever e já roda no `check.sh`.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/) em inglês, no imperativo:

```
feat(dictionary): add split-flap effect with demo
fix(build_timeline): match words with trailing punctuation
docs(styles): add swiss-grid community recipe
test(safe_zone_check): cover the vertical preset
```

Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`. O escopo é opcional. Quando o motivo não for óbvio, explique no corpo do commit. Um assunto por PR, com o modelo de PR preenchido.
