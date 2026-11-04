---
title: Open fronts
description: Where motion-cena still has gaps and where to start helping, with the good first contributions marked.
---

# Open fronts

Places where motion-cena still has gaps and where help is welcome. This is not a list of promises and it has no dates: each item says what is missing and where to start. The ones marked <Badge type="info" text="good first contribution" /> fit in a small PR and have a step by step in [Contributing](/en/community/contributing).

Before taking on a large front, open an [issue](https://github.com/eusilvio/motion-cena/issues) saying what you plan to do, so nobody works twice on the same thing. The source list is [ROADMAP.md](https://github.com/eusilvio/motion-cena/blob/main/ROADMAP.md) (in Brazilian Portuguese).

## Skill content

### Promoting catalog effects to the curated set <Badge type="info" text="good first contribution" />

The catalog in `references/motion-dictionary/` has 388 effects, and only 44 have a rendered demo scene. The other 344 run in the browser in the tests, but nobody has seen them in a video. Picking one, building its scene in the demo, looking at the frames and fixing what looks bad is a small PR ([door 1b](/en/community/contributing#_1b-promoting-an-effect-to-the-curated-set)). Families with no curated effect yet, such as particles, 3D and interface, need it most. Look for candidates in the [effects explorer](/en/effects).

### Effects missing from the catalog

Terms motion designers use that the catalog does not have yet go in as JSON in the right family, validated by `motion_lookup.py --validate` ([door 1a](/en/community/contributing#_1a-new-effect-in-the-catalog)).

### Community style recipes <Badge type="info" text="good first contribution" />

`references/styles/community/` starts empty. Your own grammars, or those of a genre or school, such as a Swiss typographic grid, newsroom graphics, kinetic typography or zine collage, become styles anyone can ask for by name ([door 2](/en/community/contributing#door-2-style-recipe)).

### More platform presets

`assets/platforms.json` covers Instagram, Facebook Reels, TikTok, YouTube and LinkedIn. Kwai, Threads, Pinterest, Snapchat Spotlight and WhatsApp Status have no preset yet. Each one needs canvas, durations and safe zone taken from the platform's official documentation, with the source cited. The current presets are in [Platforms and safe zones](/en/reference/platforms).

### AI-free copy in other languages

`lint_copy.py` and the phrase lists in `writing-style.md` and `hooks.md` only cover pt-BR. For video in English or Spanish, the agent applies the principles from memory. A list of patterns per language, with a test, would fix that.

## Pipeline and scripts

### More tests <Badge type="info" text="good first contribution" />

`tests/` is new and many scripts in `.agents/skills/motion-cena/scripts/` still have no test. A pure function, like the word matching in `build_timeline.py` or the preset reading in `platform_preset.py`, is a good start. See [Tests and checks](/en/reference/tests).

### Other voice engines

`references/voiceover.md` mentions Kokoro and Piper as local, offline options, but there is no script for them. Today there are `tts_edge.py`, `tts_elevenlabs.py` and `tts_chatterbox.py`. A new engine needs to produce `audio/voice.mp3` and `audio/words.json` in the same format, with native timestamps or through `align_words.py`.

### Native Windows

`setup.ps1` already exists, but `qa_video.sh`, `analyze_reference.sh` and `tools/check.sh` are bash. Those steps still need porting, or the whole pipeline needs to run in PowerShell with what requires WSL documented. The current state is on the [Windows](/en/guide/windows) page.

### Remotion end to end

`references/engines.md` describes the Remotion path, but the demos and checks only exercise HyperFrames. What is missing is a test project that goes through the voiceover, the timeline and the render in Remotion, and fixing whatever breaks along the way.

## Tools

### The `tools/studio` interface for more agents

The chat next to the video works with Claude Code, Codex and Antigravity. For OpenCode, Gemini CLI or Copilot CLI to join, each needs an entry in `tools/studio/server.mjs` that runs the agent and reads its streaming output, like the three that already exist.

### Reports from other machines

The pipeline has been exercised on few machines. Running the full flow on a different system (macOS, Windows, another Linux distribution) and opening a bug issue with what broke helps as much as code. Time and cost numbers from other machines and agents also belong in [Time and cost](/en/guide/cost-and-time).
