---
title: Como contribuir
description: Como preparar a máquina, o que conferir antes do PR, o que nunca entra no repositório e as duas portas de entrada mais fáceis.
---

# Como contribuir

O motion-cena é público e sai zerado: nenhuma marca, voz, cliente ou tema de ninguém. Toda contribuição precisa manter isso. Esta página resume o [CONTRIBUTING.md](https://github.com/eusilvio/motion-cena/blob/main/CONTRIBUTING.md), que tem o passo a passo completo. Issues e pull requests em inglês são bem-vindos.

Antes de uma mudança grande (etapa nova no pipeline, troca de motor, script novo), abra uma issue para combinar o caminho. Correção pequena, efeito e receita podem ir direto para PR. As frentes abertas, com as boas primeiras contribuições marcadas, estão em [Frentes abertas](/comunidade/roadmap).

## Prepare a máquina

Faça um fork, clone o seu fork e rode o setup:

```bash
git clone https://github.com/<seu-usuario>/motion-cena.git
cd motion-cena
./setup.sh          # no Windows, em PowerShell: .\setup.ps1
```

Trabalhe numa branch a partir de `main` (`git switch -c feat/nome-curto`) e abra o PR para `main`.

## Antes de abrir o PR

```bash
./tools/check.sh
```

Ele roda as mesmas checagens do CI: testes Python, texto das docs em português, shellcheck, workflows, fim de linha e os testes das skills do HyperFrames. Detalhes em [Testes e checagens](/referencia/testes).

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

Fonte, ícone ou imagem novos numa demo só entram com licença livre (OFL, CC0) e o arquivo da licença junto.

## Porta 1: efeito novo no dicionário

O dicionário tem duas camadas. `references/motion-dictionary.md` guarda os **44 efeitos curados**, cada um com cena de demo renderizada. `references/motion-dictionary/` guarda o **catálogo de 388 efeitos**, um JSON por família, que o agente consulta com o `motion_lookup.py`. Efeito novo entra pelo catálogo, e um efeito do catálogo sobe para os curados quando ganha demo. Navegue pelos dois no [explorador de efeitos](/efeitos).

Um efeito novo entra quando tem um nome que motion designers já usam e não é só a soma de dois que já existem.

### 1a. Efeito novo no catálogo

1. Confira se já existe, pelo nome e pelos apelidos:

   ```bash
   uv run .agents/skills/motion-cena/scripts/motion_lookup.py "split flap" --brief
   ```

2. Escreva a entrada no fim do JSON da família (`references/motion-dictionary/<família>.json`), com todos os campos do `schema.json` e `"origem": "expansao"`. Textos em pt-BR, como os vizinhos.
3. Valide, gere o índice e rode as checagens:

   ```bash
   uv run .agents/skills/motion-cena/scripts/motion_lookup.py --validate
   uv run .agents/skills/motion-cena/scripts/motion_lookup.py --write-index
   ./tools/check.sh
   ```

O código GSAP segue as regras do resto do dicionário, para o render poder pular para qualquer quadro:

- um único `tl` pausado, `fromTo` com estado inicial explícito, `t` como início;
- só `transform`, `opacity`, `filter`, `clip-path` e atributos SVG (nada de `width`, `height`, `top`);
- sem `Math.random`, `Date` ou `setTimeout`: use hash por índice ou um gerador com semente fixa;
- loop sempre finito;
- um comentário dizendo que DOM o efeito espera.

### 1b. Levar um efeito para os curados

É a contribuição que mais falta: dos 388 efeitos, só 44 foram vistos num vídeo renderizado. No JSON, troque `"origem"` para `"dicionario-atual"` e regenere o índice. Depois acrescente a linha na tabela e a receita GSAP em `motion-dictionary.md` (em inglês, porque o agente lê), monte a cena na demo `training/dicionario-demo-2/`, rode o check do HyperFrames, olhe os quadros e anexe um trecho renderizado ao PR.

::: details Os passos da cena de demo
1. Em `build.py`, acrescente ao fim de `SCENES` uma tupla `(família, termo, parâmetros, html da demo)`. A primeira cena nova é a 27.
2. Em `index.tpl`, o CSS da demo vai no `<style>` e a animação num bloco `// N <termo>` antes de `window.__timelines["main"] = tl;`, usando `fx(N)`.
3. Gere o HTML e suba `build.py`, `index.tpl` e `index.html` juntos:

   ```bash
   cd training/dicionario-demo-2
   uv run --python 3.12 build.py
   npm run check
   ```

4. A cena N começa em 3 + 2,6 × (N − 1) segundos e dura 2,6 s. Tire os quadros com a versão do HyperFrames do `package.json` da demo:

   ```bash
   npx --yes hyperframes@0.8.181 snapshot --range 70.6:73.2 --frames 6 --output /tmp/efeito
   ```

5. Renderize em rascunho, corte a sua cena e arraste o MP4 para a descrição do PR. Não suba o MP4 de `creatives/demos/`.

   ```bash
   npm run render -- --quality draft -o /tmp/demo-2.mp4
   ffmpeg -ss 70.6 -t 2.6 -i /tmp/demo-2.mp4 /tmp/efeito.mp4
   ```

6. Atualize a contagem de efeitos curados em `README.md`, `README.en.md`, `training/README.md` e na abertura do dicionário.

O passo a passo completo, com o formato da linha da tabela, está no [CONTRIBUTING.md](https://github.com/eusilvio/motion-cena/blob/main/CONTRIBUTING.md#1b-levar-um-efeito-para-os-curados).
:::

Commits sugeridos: `feat(dictionary): add split-flap to the catalog` (1a) e `feat(dictionary): promote split-flap with demo` (1b).

## Porta 2: receita de estilo

Uma receita de estilo ensina ao agente uma gramática de vídeo. As receitas da comunidade ficam em `.agents/skills/motion-cena/references/styles/community/` e descrevem uma gramática que você criou, ou um gênero ou escola sem dono. Nunca a quebra de um vídeo, série ou canal específico de outra pessoa. A regra completa está em [Estilos de referência](/referencia/estilos).

1. Copie o modelo com um nome curto em kebab-case:

   ```bash
   S=.agents/skills/motion-cena/references/styles
   mkdir -p $S/community && cp $S/_template.md $S/community/swiss-grid.md
   ```

2. Troque a linha `Reference:` por `Origin: own grammar (<seu nome>)` ou `Origin: genre/school (<nome>)`.
3. Preencha em inglês: a ideia em uma linha, estrutura com tempos escolhidos por você, linguagem visual, componentes ligados a termos do dicionário e às receitas do HyperFrames, som, como adaptar e o checklist do estilo.
4. Acrescente uma linha na tabela do fim de `references/styles/README.md`.
5. Teste com o seu agente num tema neutro (*"faz um reels de 15 s sobre juros compostos no estilo swiss-grid"*) e anexe ao PR um trecho ou a contact sheet. O projeto e o MP4 continuam fora do git.

Commit sugerido: `docs(styles): add swiss-grid community recipe`.

## Correções em scripts

- Mudou um script de `.agents/skills/motion-cena/scripts/`? O PR traz um teste em `tests/` que falha sem a correção e passa com ela.
- Script Python declara as dependências no próprio arquivo (bloco `# /// script`) e roda com `uv run`.
- Script shell passa no shellcheck.
- Mudou o que o script faz ou os argumentos? Atualize onde ele é citado: `SKILL.md`, `references/` e a tabela de scripts do README.
- As skills do HyperFrames não são editadas à mão: bug nelas vai para o repositório deles, e a versão nova chega pelo [`tools/update-skills.sh`](/referencia/atualizar-hyperframes).

## Idioma

- **Instruções para o agente, em inglês:** `AGENTS.md` e tudo em `.agents/skills/motion-cena/`. As listas de frases em português dentro da skill ficam em português, porque servem para texto em português.
- **Documentação para pessoas, em pt-BR:** `README.md`, `CONTRIBUTING.md`, `ROADMAP.md` e os README das pastas. O `README.en.md` é a versão em inglês do README.
- Texto em pt-BR: direto, com "você", sem emoji e sem frase com cara de IA. O `lint_copy.py` aponta o que reescrever.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/) em inglês, no imperativo:

```text
feat(dictionary): add split-flap effect with demo
fix(build_timeline): match words with trailing punctuation
docs(styles): add swiss-grid community recipe
test(safe_zone_check): cover the vertical preset
```

Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`. O escopo é opcional. Quando o motivo não for óbvio, explique no corpo do commit. Um assunto por PR, com o modelo de PR preenchido.
