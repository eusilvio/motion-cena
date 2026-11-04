---
title: Any agent
description: How motion-cena works with any coding agent, the entry files and why only 6 skills are linked for Claude Code.
---

# Any agent

The pipeline is text and the command line. Any agent that reads files and runs terminal commands can direct it: Claude Code, Codex, Antigravity, Cursor, GitHub Copilot, OpenCode, Windsurf, Gemini CLI and others.

## Where each agent comes in

| File | For |
|---|---|
| `AGENTS.md` | Codex, Antigravity, Cursor, GitHub Copilot, OpenCode, Windsurf, Amp, Zed and most agents |
| `CLAUDE.md` and `GEMINI.md` | they only import `AGENTS.md`, for Claude Code and Gemini CLI |
| `.agents/skills/` | the `motion-cena` skill and the official HyperFrames skills, in the folder agents share by convention |
| `.claude/skills/` | links to the 6 skills the pipeline uses, for Claude Code only |

`AGENTS.md` tells the agent to read `.agents/skills/motion-cena/SKILL.md` in full and follow the steps in order. The skill names the references for each step, and the agent reads only the one for the step it is on.

## The links in `.claude/skills` {#claude-skills}

Claude Code only loads native skills from `.claude/skills/`, and that folder stays out of git. `setup.sh` (or `setup.ps1`, with junctions on Windows) creates a link for each skill listed in `.agents/skills/claude-links.txt`:

- `motion-cena`
- `hyperframes`
- `hyperframes-core`
- `hyperframes-animation`
- `hyperframes-cli`
- `media-use`

There are only 6 because every linked skill sends its own description on every request to the model, and that costs tokens on every call. The other HyperFrames skills stay in `.agents/skills/` and are read as documents when `motion-cena` points to them. If a skill leaves the list, the setup removes its link the next time it runs.

If you opened Claude Code without running the setup, `CLAUDE.md` tells Claude to create the links itself in the first session. The native skills apply from the next session; in the first one, it reads the skill as a document.

## Tools that exist in only one agent

Some tools exist in only one agent: Claude Design for an editable carousel, an MCP voice connector, web search. They are optional. The skill always describes the path that works in any agent:

| When the skill mentions | Without it, the agent uses |
|---|---|
| Claude Design (editable carousel on claude.ai) | the local carousel engine, which produces PNG and PDF |
| an MCP voice connector (Higgsfield, ElevenLabs) | the ElevenLabs script with the key in `.env.local`, or edge-tts |
| web search and page reading | the agent's equivalent tool, or `curl` |

## Differences you will notice

- The `tools/studio` interface, with chat and preview side by side, works with Claude Code, Codex and Antigravity. Bringing other agents into it is one of the [open fronts](/en/community/roadmap).
- On native Windows, agents that run commands in PowerShell cannot run the bash QA scripts. See [Windows](/en/guide/windows).
- The published time and cost numbers were measured in Claude Code only. The other agents count usage differently and were not measured.
