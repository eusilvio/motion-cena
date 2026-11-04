# motion-cena: instructions for coding agents

This repository is a motion-design pipeline driven by a coding agent (Claude Code, Codex, Antigravity, Cursor, GitHub Copilot, OpenCode, Windsurf or any other). Everything the agent needs is in text files; no tool is exclusive to one agent.

## Language

The user may write in any language; most write in Brazilian Portuguese. Understand the request in whatever language it comes and answer in that language: chat replies, questions, plans, narration, on-screen text and captions. The human docs (README) are in pt-BR; the agent instructions (this file and the skill) are in English.

## Video, carousel, post, narration, script or storyboard request

1. Read `.agents/skills/motion-cena/SKILL.md` in full and follow its steps in order. It is the complete flow.
2. Relative paths cited in the skill (`references/`, `assets/`, `scripts/`) start from `.agents/skills/motion-cena/`.
3. Animation runs on HyperFrames. The engine skills live in `.agents/skills/`; do not read them whole. Step 6 of the skill lists the few HyperFrames files the pipeline needs (composition in `hyperframes-core/references/`, effect rules in `hyperframes-animation/rules/`); open a full engine `SKILL.md` only for something those do not cover.
4. Save tokens: one piece per session (start a new session for the next piece; everything is on disk in `projects/<slug>/`), and follow the "Token economy" section of the skill.
5. If your agent loads skills by itself from `.agents/skills/`, they are already available. Claude Code only loads from `.claude/skills/`, which `./setup.sh` creates with links to `.agents/skills/`. Without native skills, read the `SKILL.md` files as documents when a step calls for them.

## Brand, voice and tone

There is no fixed profile. Each request brings its own: colors, website or logo in the request itself; a product's code (the brand comes from the repository's theme and assets); or the recording of whoever is speaking (the voice is theirs). With none of these, work neutral and do not invent a persona. Details in the "Brand, voice and tone" section of `SKILL.md`.

## Watching the edit live

Optional and off by default. Only if the user asks to watch it live ("quero ver ao vivo", "abre o preview", "I want to watch it live"), wants to point at something on screen, or runs the `tools/studio` interface (`MOTION_CENA_UI=1`): then follow `.agents/skills/motion-cena/references/live-preview.md`. Without a request, review through the snapshot sheet and deliver the MP4.

## Repository rules

- Project in `projects/<slug>/`; final piece in `creatives/<tipo>/`. Never in the root.
- Nothing personal or generated goes to git: projects, pieces, voice, reference videos and `.env.local` are already in `.gitignore`. Do not force `git add` on them.
- Python scripts: `uv run <script>` (dependencies declared in the file itself). HyperFrames: `npx hyperframes@<version>`, where `<version>` is the `ref` of the HyperFrames skills in `skills-lock.json` without the leading `v` (the CLI and the skill docs must match); a project whose `package.json` pins a version keeps that one. Update the skills only with `tools/update-skills.sh`, never `npx skills update`.
- API keys only in `.env.local` (template in `.env.example`), never in code.
- When the skill cites a tool your agent does not have (web search, page reading, MCP server, Claude Design), use your equivalent; with no equivalent, follow the alternative path the skill describes (local carousel engine, edge-tts, `curl`).
