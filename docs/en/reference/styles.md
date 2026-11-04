---
title: Reference styles
description: Video grammar recipes you ask for by name. Local ones come from a reference video; community ones live in the repository.
---

# Reference styles

A style is the recipe for a video grammar: the mechanism that holds attention, the structure with timings, the visual language, the components, the sound and how to adapt it. Once saved, you ask for it by name:

```text
Make a 15 s Reels about compound interest in the <name> style.
```

The style borrows the **grammar**: structure, rhythm, kind of component. Brand, text, objects and numbers are always yours; no logo, character or text from the original piece comes in.

## Two kinds, two places

| Kind | Where | In git | Comes from |
|---|---|---|---|
| Local | `references/styles/<name>.md` | no | a reference video you sent, someone else's piece |
| Community | `references/styles/community/<name>.md` | yes | a grammar its author created, or a genre or school that belongs to no one |

When you ask for a style, the agent looks in both places. If the same name exists in both, the local one wins. The paths are relative to `.agents/skills/motion-cena/`.

## Local style, from a video

1. Copy the video to `training/referencias/ref-01.mp4` (that folder stays out of git).
2. Ask: *"analyze this video and create a style"*.
3. The agent runs the analysis:

   ```bash
   bash .agents/skills/motion-cena/scripts/analyze_reference.sh training/referencias/ref-01.mp4 training/referencias/ref-01 pt
   ```

   It generates sheets at 2 frames per second with timecode, three full-resolution frames, the speech with timestamps and the loudness.
4. The agent looks at the sheets and writes the recipe following `references/styles/_template.md`: structure with timings, mechanism, palette, typography, density, components, transitions, how the text relates to the speech, sound. Each component points to a term in the effects dictionary and to a HyperFrames recipe.

A local recipe stays only on your machine, because it is the analysis of someone else's piece. It never goes into `community/` or into the folder's README.

## Community recipes

A community recipe describes a grammar you created and use, or a genre or school that belongs to no one: Swiss typographic grid, newsroom lower thirds, kinetic typography, zine collage. It never breaks down one specific person's video, series or channel: no profile mentioned, no timings measured from a piece, no logo, character, catchphrase or text from someone else.

The format is the same `_template.md`, with two changes:

- the `Reference:` line becomes `Origin: own grammar (<author>)` or `Origin: genre/school (<name>)`, with generic public sources if there are any;
- the timings in the structure are the recipe's own choice, not the measurement of a piece.

The text is in English, like the rest of the skill, and the file has a short kebab-case name (`swiss-grid.md`).

::: tip The folder starts empty
`references/styles/community/` has no recipe yet. Writing the first one is a good first contribution: the step by step is in [Contributing](/en/community/contributing#door-2-style-recipe).
:::

If a recipe only makes sense next to one specific video, it is local and stays out of the repository.
