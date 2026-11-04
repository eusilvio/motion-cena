---
title: Contributing
description: How to set up your machine, what to check before a PR, what never goes into the repository and the two easiest ways in.
---

# Contributing

motion-cena is public and ships blank: no brand, voice, client or topic from anyone. Every contribution has to keep it that way. This page summarizes [CONTRIBUTING.md](https://github.com/eusilvio/motion-cena/blob/main/CONTRIBUTING.md), which has the full step by step (in Brazilian Portuguese). Issues and pull requests in English are welcome.

Before a large change (a new pipeline step, a different engine, a new script), open an issue to agree on the approach. Small fixes, effects and recipes can go straight to a PR. The open fronts, with the good first contributions marked, are in [Open fronts](/en/community/roadmap).

## Set up your machine

Fork the repository, clone your fork and run the setup:

```bash
git clone https://github.com/<your-username>/motion-cena.git
cd motion-cena
./setup.sh          # on Windows, in PowerShell: .\setup.ps1
```

Work on a branch from `main` (`git switch -c feat/short-name`) and open the PR against `main`.

## Before opening the PR

```bash
./tools/check.sh
```

It runs the same checks as CI: Python tests, the Portuguese docs text, shellcheck, workflows, line endings and the HyperFrames skills' tests. Details in [Tests and checks](/en/reference/tests).

## What never goes into a PR

`.gitignore` already leaves almost all of this out. Never force it with `git add -f`, and check `git status` and `git diff --staged` before every commit.

| Never pushed | Where it lives on your machine | Why |
|---|---|---|
| projects in production | `projects/` | the brief, script and audio are yours |
| final pieces | `creatives/` (only the dictionary demos are pushed) | they are yours, and video bloats the history |
| voice recordings | `training/voz/` | biometric data |
| third-party video and its analysis | `training/referencias/` and the recipes in `references/styles/` outside `community/` | the piece belongs to someone else |
| keys and tokens | `.env.local` | replacing a leaked key is work; deleting the commit is not enough |
| your agent's configuration | `.claude/`, `.cursor/`, `.vscode/`, `CLAUDE.local.md` | it belongs to your machine |
| your brand, client, product, script or topic | in examples, tests, demos or documentation | the repository is neutral: use generic examples, like compound interest or a fictional store |

New fonts, icons or images in a demo only go in with a free license (OFL, CC0) and the license file next to them.

## Door 1: a new effect in the dictionary

The dictionary has two layers. `references/motion-dictionary.md` holds the **44 curated effects**, each with a rendered demo scene. `references/motion-dictionary/` holds the **388-effect catalog**, one JSON per family, which the agent queries with `motion_lookup.py`. A new effect enters through the catalog, and a catalog effect moves up to the curated set when it gets a demo. Browse both in the [effects explorer](/en/effects).

A new effect goes in when it has a name motion designers already use and is not just the sum of two that already exist.

### 1a. New effect in the catalog

1. Check whether it already exists, by name and by alias:

   ```bash
   uv run .agents/skills/motion-cena/scripts/motion_lookup.py "split flap" --brief
   ```

2. Write the entry at the end of the family's JSON (`references/motion-dictionary/<family>.json`), with every field from `schema.json` and `"origem": "expansao"`. Text in pt-BR, like its neighbors.
3. Validate, generate the index and run the checks:

   ```bash
   uv run .agents/skills/motion-cena/scripts/motion_lookup.py --validate
   uv run .agents/skills/motion-cena/scripts/motion_lookup.py --write-index
   ./tools/check.sh
   ```

The GSAP code follows the same rules as the rest of the dictionary, so the render can jump to any frame:

- a single paused `tl`, `fromTo` with an explicit initial state, `t` as the start;
- only `transform`, `opacity`, `filter`, `clip-path` and SVG attributes (no `width`, `height`, `top`);
- no `Math.random`, `Date` or `setTimeout`: use a hash by index or a generator with a fixed seed;
- loops always finite;
- a comment saying what DOM the effect expects.

### 1b. Promoting an effect to the curated set

This is the contribution that is missing most: of the 388 effects, only 44 have been seen in a rendered video. In the JSON, change `"origem"` to `"dicionario-atual"` and regenerate the index. Then add the row to the table and the GSAP recipe in `motion-dictionary.md` (in English, because the agent reads it), build the scene in the `training/dicionario-demo-2/` demo, run the HyperFrames check, look at the frames and attach a rendered clip to the PR.

::: details The demo scene steps
1. In `build.py`, add a `(family, term, parameters, demo html)` tuple to the end of `SCENES`. The first new scene is 27.
2. In `index.tpl`, the demo's CSS goes in the `<style>` and the animation in a `// N <term>` block before `window.__timelines["main"] = tl;`, using `fx(N)`.
3. Generate the HTML and push `build.py`, `index.tpl` and `index.html` together:

   ```bash
   cd training/dicionario-demo-2
   uv run --python 3.12 build.py
   npm run check
   ```

4. Scene N starts at 3 + 2.6 × (N − 1) seconds and lasts 2.6 s. Take the frames with the HyperFrames version in the demo's `package.json`:

   ```bash
   npx --yes hyperframes@0.8.181 snapshot --range 70.6:73.2 --frames 6 --output /tmp/efeito
   ```

5. Render a draft, cut your scene and drag the MP4 into the PR description. Do not push the MP4 in `creatives/demos/`.

   ```bash
   npm run render -- --quality draft -o /tmp/demo-2.mp4
   ffmpeg -ss 70.6 -t 2.6 -i /tmp/demo-2.mp4 /tmp/efeito.mp4
   ```

6. Update the count of curated effects in `README.md`, `README.en.md`, `training/README.md` and at the top of the dictionary.

The full step by step, with the format of the table row, is in [CONTRIBUTING.md](https://github.com/eusilvio/motion-cena/blob/main/CONTRIBUTING.md#1b-levar-um-efeito-para-os-curados).
:::

Suggested commits: `feat(dictionary): add split-flap to the catalog` (1a) and `feat(dictionary): promote split-flap with demo` (1b).

## Door 2: style recipe

A style recipe teaches the agent a video grammar. Community recipes live in `.agents/skills/motion-cena/references/styles/community/` and describe a grammar you created, or a genre or school that belongs to no one. Never the breakdown of one specific person's video, series or channel. The full rule is in [Reference styles](/en/reference/styles).

1. Copy the template with a short kebab-case name:

   ```bash
   S=.agents/skills/motion-cena/references/styles
   mkdir -p $S/community && cp $S/_template.md $S/community/swiss-grid.md
   ```

2. Replace the `Reference:` line with `Origin: own grammar (<your name>)` or `Origin: genre/school (<name>)`.
3. Fill it in, in English: the idea in one line, structure with timings you chose, visual language, components tied to dictionary terms and HyperFrames recipes, sound, how to adapt it and the style's checklist.
4. Add a row to the table at the end of `references/styles/README.md`.
5. Test it with your agent on a neutral topic (*"make a 15 s Reels about compound interest in the swiss-grid style"*) and attach a clip or the contact sheet to the PR. The project and the MP4 stay out of git.

Suggested commit: `docs(styles): add swiss-grid community recipe`.

## Script fixes

- Changed a script in `.agents/skills/motion-cena/scripts/`? The PR brings a test in `tests/` that fails without the fix and passes with it.
- Python scripts declare their dependencies in the file itself (a `# /// script` block) and run with `uv run`.
- Shell scripts pass shellcheck.
- Changed what a script does or its arguments? Update the places that mention it: `SKILL.md`, `references/` and the scripts table in the README.
- The HyperFrames skills are not edited by hand: bugs in them go to their repository, and the new version arrives through [`tools/update-skills.sh`](/en/reference/update-hyperframes).

## Language

- **Instructions for the agent, in English:** `AGENTS.md` and everything in `.agents/skills/motion-cena/`. The Portuguese phrase lists inside the skill stay in Portuguese, because they are for Portuguese text.
- **Documentation for people, in pt-BR:** `README.md`, `CONTRIBUTING.md`, `ROADMAP.md` and the folders' READMEs. `README.en.md` is the English version of the README.
- pt-BR text: direct, addressing the reader as "você", no emoji and no AI-sounding phrasing. `lint_copy.py` points out what to rewrite.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/) in English, in the imperative:

```text
feat(dictionary): add split-flap effect with demo
fix(build_timeline): match words with trailing punctuation
docs(styles): add swiss-grid community recipe
test(safe_zone_check): cover the vertical preset
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`. The scope is optional. When the reason is not obvious, explain it in the commit body. One subject per PR, with the PR template filled in.
