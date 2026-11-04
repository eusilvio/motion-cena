---
title: Instalação
description: Requisitos, instalação no Linux, no macOS e no WSL, o setup.sh e as chaves de API opcionais no .env.local.
---

# Instalação

## Requisitos

| O quê | Para quê |
|---|---|
| **Node 22 ou mais novo** | o HyperFrames (render, preview, Studio) e o `npx` |
| **FFmpeg** com `libx264` e `aac` | render, mixagem de áudio e QA |
| **[uv](https://docs.astral.sh/uv/)** | roda os scripts Python com as dependências declaradas no próprio arquivo, sem instalar nada no sistema |
| **Git** | clonar o repositório |
| **Um agente de código** | Claude Code, Codex, Antigravity, Gemini CLI, OpenCode, Copilot, ou a pasta aberta no Cursor, no Windsurf ou no VS Code com Copilot |

Nenhuma chave de API é obrigatória.

## 1. Instale as dependências

::: code-group

```bash [Linux]
# Ubuntu e Debian; em outra distribuição, use o gerenciador de pacotes dela
sudo apt update && sudo apt install -y git ffmpeg
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
curl -LsSf https://astral.sh/uv/install.sh | sh
exec bash                 # recarrega o terminal com nvm e uv no PATH
nvm install --lts
```

```bash [macOS]
brew install node ffmpeg
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash [WSL]
# no terminal do Ubuntu, depois de instalar o WSL 2 (veja a página Windows)
sudo apt update && sudo apt install -y git ffmpeg
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
curl -LsSf https://astral.sh/uv/install.sh | sh
exec bash
nvm install --lts
uvx playwright install --with-deps chromium   # bibliotecas do Chrome sem janela
```

:::

No Windows, o caminho recomendado é o WSL 2. O passo a passo, e o que funciona no PowerShell nativo, estão em [Windows](/guia/windows).

## 2. Clone e rode o setup

```bash
git clone https://github.com/eusilvio/motion-cena.git
cd motion-cena
./setup.sh
```

O `setup.sh` pode rodar quantas vezes você quiser; ele nunca sobrescreve o que já existe. Ele:

- confere `node` (22 ou mais), `npx`, `ffmpeg`, `ffprobe` e `uv`, e diz o que falta;
- procura um agente no PATH (`claude`, `codex`, `agy`, `gemini`, `cursor-agent`, `opencode`, `copilot`);
- cria as pastas locais, que ficam fora do git: `projects/`, `creatives/reels/`, `creatives/carrossel/`, `creatives/post/`, `training/voz/` e `training/referencias/`;
- liga as 6 skills do pipeline em `.claude/skills/`, para o Claude Code carregar ([por que só 6](/guia/agentes#claude-skills));
- copia o `.env.example` para `.env.local` e cria o `creatives/registro.md`, o histórico de peças entregues.

## 3. Confira o motor de render

```bash
npx hyperframes doctor
```

O `doctor` confere Node, FFmpeg, Chrome, memória e disco. Ele costuma terminar com "Some checks failed" mesmo com tudo certo, por causa de `TTS (Kokoro)` e `BGM (MusicGen)`: são alternativas locais opcionais, e o motion-cena não depende delas. Pode ignorar as duas.

::: tip Dois navegadores
O HyperFrames renderiza com um Chrome próprio, baixado no primeiro render. O medidor de zona segura usa o Chromium do Playwright, que é outro. Se o medidor reclamar que o navegador não existe, rode `uv run --with playwright playwright install chromium`. Mais em [Deu erro?](/guia/deu-erro).
:::

## 4. Chaves de API (opcional)

Sem chave nenhuma, a voz sai grátis pelo edge-tts e os efeitos sonoros são sintetizados na sua máquina. Com uma chave da ElevenLabs a voz melhora, dá para clonar a sua e gerar efeitos e trilha por texto.

As chaves ficam no `.env.local`, na raiz do repositório. O `setup.sh` já cria o arquivo a partir do modelo:

```ini
# ElevenLabs: TTS com timestamps, clonagem de voz e SFX por prompt
# https://elevenlabs.io/app/settings/api-keys
ELEVENLABS_API_KEY=

# tools/upload_server.py: exige ?t=<token> em cada envio pela rede local
UPLOAD_TOKEN=
```

Preencha só o que for usar. Outra opção é rodar `npx -y @elevenlabs/cli@latest onboard init` na raiz, que configura a chave da ElevenLabs.

::: warning A chave fica só no `.env.local`
O `.env.local` está no `.gitignore`. Não cole a chave no chat do agente nem em código. Se uma chave vazar, troque-a no painel da ElevenLabs: apagar o commit não basta.
:::

## 5. Abra o agente na raiz

```bash
claude      # ou codex, agy, opencode
```

Também dá para abrir a pasta no Cursor, no Windsurf ou no VS Code com Copilot. O agente lê o `AGENTS.md` (ou o `CLAUDE.md` e o `GEMINI.md`, que só importam o `AGENTS.md`) e encontra a skill `motion-cena`.

::: tip Claude Code na primeira sessão
O Claude Code só carrega skills de `.claude/skills/`. Se você pulou o `setup.sh`, o próprio Claude cria os links na primeira sessão e avisa que as skills nativas valem a partir da sessão seguinte. Nessa primeira, ele lê a skill como documento.
:::

Pronto: siga para o [primeiro vídeo](/guia/primeiro-video).
