---
title: Qualquer agente
description: Como o motion-cena funciona em qualquer agente de código, os arquivos de entrada e por que só 6 skills viram links para o Claude Code.
---

# Qualquer agente

O pipeline é texto e linha de comando. Qualquer agente que lê arquivos e roda comandos no terminal consegue dirigir: Claude Code, Codex, Antigravity, Cursor, GitHub Copilot, OpenCode, Windsurf, Gemini CLI e outros.

## Por onde cada agente entra

| Arquivo | Para quem |
|---|---|
| `AGENTS.md` | Codex, Antigravity, Cursor, GitHub Copilot, OpenCode, Windsurf, Amp, Zed e a maioria dos agentes |
| `CLAUDE.md` e `GEMINI.md` | só importam o `AGENTS.md`, para o Claude Code e o Gemini CLI |
| `.agents/skills/` | a skill `motion-cena` e as skills oficiais do HyperFrames, na pasta que os agentes compartilham por convenção |
| `.claude/skills/` | links para as 6 skills que o pipeline usa, só para o Claude Code |

O `AGENTS.md` manda o agente ler `.agents/skills/motion-cena/SKILL.md` inteiro e seguir as etapas na ordem. A skill cita as referências de cada etapa, e o agente lê só a da etapa em que está.

## Os links em `.claude/skills` {#claude-skills}

O Claude Code só carrega skills nativas de `.claude/skills/`, e essa pasta fica fora do git. O `setup.sh` (ou o `setup.ps1`, com junctions no Windows) cria um link para cada skill listada em `.agents/skills/claude-links.txt`:

- `motion-cena`
- `hyperframes`
- `hyperframes-core`
- `hyperframes-animation`
- `hyperframes-cli`
- `media-use`

São só 6 porque cada skill linkada manda a própria descrição em todo pedido ao modelo, e isso custa tokens em todas as chamadas. As outras skills do HyperFrames continuam em `.agents/skills/` e são lidas como documento quando a `motion-cena` aponta para elas. Se uma skill sai da lista, o setup remove o link dela na próxima execução.

Se você abriu o Claude Code sem rodar o setup, o `CLAUDE.md` manda o próprio Claude criar os links na primeira sessão. As skills nativas passam a valer na sessão seguinte; na primeira, ele lê a skill como documento.

## Ferramenta que só existe num agente

Algumas ferramentas existem só em um agente: o Claude Design para carrossel editável, um conector MCP de voz, uma busca na web. Elas são opcionais. A skill sempre descreve o caminho que funciona em qualquer agente:

| Quando a skill cita | Sem ela, o agente usa |
|---|---|
| Claude Design (carrossel editável no claude.ai) | o motor local de carrossel, que gera PNG e PDF |
| conector MCP de voz (Higgsfield, ElevenLabs) | o script da ElevenLabs com a chave no `.env.local`, ou o edge-tts |
| busca e leitura de página na web | a ferramenta equivalente do agente, ou `curl` |

## Diferenças que você vai notar

- A interface `tools/studio`, com chat e preview lado a lado, funciona com Claude Code, Codex e Antigravity. Levar outros agentes para ela é uma das [frentes abertas](/comunidade/roadmap).
- No Windows nativo, agentes que executam comandos no PowerShell não rodam os scripts bash de QA. Veja [Windows](/guia/windows).
- Os números de tempo e custo publicados foram medidos só no Claude Code. Os outros agentes contam uso de outro jeito e não foram medidos.
