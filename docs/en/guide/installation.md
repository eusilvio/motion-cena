---
title: Installation
description: Requirements, installing on Linux, macOS and WSL, setup.sh and the optional API keys in .env.local.
---

# Installation

## Requirements

| What | What for |
|---|---|
| **Node 22 or newer** | HyperFrames (render, preview, Studio) and `npx` |
| **FFmpeg** with `libx264` and `aac` | rendering, audio mixing and QA |
| **[uv](https://docs.astral.sh/uv/)** | runs the Python scripts with the dependencies declared in the file itself, without installing anything system-wide |
| **Git** | cloning the repository |
| **A coding agent** | Claude Code, Codex, Antigravity, Gemini CLI, OpenCode, Copilot, or the folder opened in Cursor, Windsurf or VS Code with Copilot |

No API key is required.

## 1. Install the dependencies

::: code-group

```bash [Linux]
# Ubuntu and Debian; on another distribution, use its package manager
sudo apt update && sudo apt install -y git ffmpeg
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
curl -LsSf https://astral.sh/uv/install.sh | sh
exec bash                 # reloads the terminal with nvm and uv on the PATH
nvm install --lts
```

```bash [macOS]
brew install node ffmpeg
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash [WSL]
# in the Ubuntu terminal, after installing WSL 2 (see the Windows page)
sudo apt update && sudo apt install -y git ffmpeg
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
curl -LsSf https://astral.sh/uv/install.sh | sh
exec bash
nvm install --lts
uvx playwright install --with-deps chromium   # libraries for the headless Chrome
```

:::

On Windows, the recommended path is WSL 2. The walkthrough, and what works in native PowerShell, are on the [Windows](/en/guide/windows) page.

## 2. Clone and run the setup

```bash
git clone https://github.com/eusilvio/motion-cena.git
cd motion-cena
./setup.sh
```

You can run `setup.sh` as many times as you like; it never overwrites what already exists. It:

- checks `node` (22 or newer), `npx`, `ffmpeg`, `ffprobe` and `uv`, and tells you what is missing;
- looks for an agent on the PATH (`claude`, `codex`, `agy`, `gemini`, `cursor-agent`, `opencode`, `copilot`);
- creates the local folders, which stay out of git: `projects/`, `creatives/reels/`, `creatives/carrossel/`, `creatives/post/`, `training/voz/` and `training/referencias/`;
- links the pipeline's 6 skills into `.claude/skills/` so Claude Code loads them ([why only 6](/en/guide/agents#claude-skills));
- copies `.env.example` to `.env.local` and creates `creatives/registro.md`, the log of delivered pieces.

## 3. Check the render engine

```bash
npx hyperframes doctor
```

`doctor` checks Node, FFmpeg, Chrome, memory and disk. It usually ends with "Some checks failed" even when everything is fine, because of `TTS (Kokoro)` and `BGM (MusicGen)`: they are optional local alternatives, and motion-cena does not depend on them. You can ignore both.

::: tip Two browsers
HyperFrames renders with its own Chrome, downloaded on the first render. The safe-zone checker uses Playwright's Chromium, which is a different one. If the checker complains that the browser does not exist, run `uv run --with playwright playwright install chromium`. More in [Troubleshooting](/en/guide/troubleshooting).
:::

## 4. API keys (optional)

With no key at all, the voice comes free from edge-tts and the sound effects are synthesized on your machine. With an ElevenLabs key the voice gets better, you can clone your own, and you can generate sound effects and music from text.

Keys live in `.env.local`, at the repository root. `setup.sh` already creates the file from the template, whose comments are in Portuguese (they say what each key is for: ElevenLabs for TTS with timestamps, voice cloning and SFX by prompt; `UPLOAD_TOKEN` for `tools/upload_server.py`):

```ini
# ElevenLabs: TTS com timestamps, clonagem de voz e SFX por prompt
# https://elevenlabs.io/app/settings/api-keys
ELEVENLABS_API_KEY=

# tools/upload_server.py: exige ?t=<token> em cada envio pela rede local
UPLOAD_TOKEN=
```

Fill in only what you will use. Another option is to run `npx -y @elevenlabs/cli@latest onboard init` at the root, which sets up the ElevenLabs key.

::: warning The key stays in `.env.local`
`.env.local` is in `.gitignore`. Do not paste the key into the agent's chat or into code. If a key leaks, replace it in the ElevenLabs dashboard: deleting the commit is not enough.
:::

## 5. Open the agent at the root

```bash
claude      # or codex, agy, opencode
```

You can also open the folder in Cursor, Windsurf or VS Code with Copilot. The agent reads `AGENTS.md` (or `CLAUDE.md` and `GEMINI.md`, which only import `AGENTS.md`) and finds the `motion-cena` skill.

::: tip Claude Code in the first session
Claude Code only loads skills from `.claude/skills/`. If you skipped `setup.sh`, Claude creates the links itself in the first session and tells you that the native skills apply from the next session. In that first one, it reads the skill as a document.
:::

Done: go on to your [first video](/en/guide/first-video).
