---
title: Testes e checagens
description: O que o tools/check.sh roda na sua máquina, o que o CI roda em cada push e pull request, e como rodar só os testes Python.
---

# Testes e checagens

Antes de abrir um pull request, rode na raiz do repositório:

```bash
./tools/check.sh
```

Ele roda na sua máquina as mesmas checagens do CI (`.github/workflows/ci.yml`), funciona de qualquer pasta e leva cerca de meio minuto. Cada checagem roda mesmo se a anterior falhou. Quando algo quebra, o script mostra a saída da checagem que falhou e sai com erro.

## O que você precisa

`git`, `uv`, Node 22 ou mais novo, `ffmpeg` e `ffprobe`: os mesmos que o `setup.sh` confere. Se faltar algum, o `check.sh` lista o que falta e para antes das checagens. O shellcheck e o actionlint vêm pelo `uvx`, sem instalar nada no sistema.

O `check.sh` é bash. No Windows, rode pelo Git Bash ou pelo WSL.

## As checagens

| Checagem | O que confere |
|---|---|
| Fim de linha | nenhum arquivo do repositório com CRLF (o `.gitattributes` manda LF; CRLF quebra os scripts no Linux e no WSL) |
| Testes Python | os testes de `tests/` com pytest, em fixtures sintéticas |
| Texto das docs | o `lint_copy.py` nos `.md` em português da raiz (os em inglês, como `AGENTS.md` e `README.en.md`, ficam de fora); erro reprova, aviso só aparece |
| shellcheck | os scripts `.sh` do projeto e da skill `motion-cena` |
| Workflows | o actionlint no workflow do GitHub, que também passa o shellcheck nos blocos `run:` |
| Testes do HyperFrames | os testes `node --test` que vêm com as skills do HyperFrames, offline (três ficam de fora porque dependem do monorepo deles) |

### Os 388 efeitos no navegador

Um dos testes Python roda cada efeito do catálogo do dicionário num Chromium sem janela: monta o efeito numa timeline pausada e confere que não dá erro, que o tempo bate, que pular para qualquer quadro dá sempre o mesmo resultado e que entradas terminam visíveis e saídas terminam escondidas. Ele precisa do Chromium do Playwright; sem ele, o teste é pulado e o `check.sh` mostra o aviso.

```bash
uv run --with playwright==1.58.0 playwright install chromium
```

### A sincronia com a fala tem teste de referência

O `build_timeline.py`, que ancora as cenas nas palavras faladas, tem um teste de referência: um `words.json` e um storyboard fixos em `tests/fixtures/timeline/` precisam gerar exatamente o `timeline.json` esperado.

## Rodar só os testes Python

```bash
uv run -q --no-project --with "pytest>=8,<10" pytest -c tests/pytest.ini tests -q
```

Para um arquivo só, troque `tests` pelo caminho dele, como `tests/test_build_timeline.py`.

## O que o CI roda

O workflow roda em cada push e em cada pull request, com dois jobs:

- **Linux** (`ubuntu-latest`): instala uv, Node 22, FFmpeg e o Chromium do Playwright, e roda o mesmo `./tools/check.sh`. Ou seja, no CI os 388 efeitos rodam sempre no navegador.
- **Windows** (`windows-latest`): roda o `setup.ps1` no PowerShell 7 e, numa cópia nova do repositório, no Windows PowerShell 5.1. Confere que ele cria o `.env.local`, o `creatives/registro.md` e o link da skill em `.claude/skills/`, e que rodar de novo não falha nem sobrescreve o `.env.local`.

## Mudou um script?

O PR traz um teste em `tests/` que falha sem a correção e passa com ela, seguindo o padrão dos testes que já estão lá. Boa parte dos scripts ainda não tem teste, e escrever um é uma boa primeira contribuição. Veja [Como contribuir](/comunidade/contribuir) e as [frentes abertas](/comunidade/roadmap).
