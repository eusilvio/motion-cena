# Reference styles

A style is a recipe for a video grammar: the **mechanism, structure with timings, visual language, components, sound and how to adapt it**. Once it is saved, the user asks for it by name ("faz no estilo <nome>", "do it in the <name> style").

There are two kinds, in two places. When the user asks for a style, look in both; if the same name exists in both, the local one wins.

| Kind | Where | In git | Comes from |
|---|---|---|---|
| Local | `references/styles/<name>.md` | no | a reference video the user sent (someone else's piece) |
| Community | `references/styles/community/<name>.md` | yes | a grammar its author created, or a generic genre or school that belongs to no one |

Rule for both: the style borrows the **grammar** (structure, rhythm, kind of component). Brand, text, objects and numbers always come from the user. Never reproduce the logo, character or text of an original piece.

## Local styles (from a reference video)

The repository ships none: each one is an analysis of a video by someone else, so it stays on the machine of whoever made it (outside git), next to the video in `training/referencias/`. The folder is the catalog: list the `.md` files in `references/styles/` (except this README and `_template.md`); each recipe opens with its name and mechanism. Do not list local styles in this README, because this file is versioned.

When the user sends a reference video:

1. Copy it to `training/referencias/ref-NN.mp4`.
2. Run the analysis:
   ```bash
   bash .agents/skills/motion-cena/scripts/analyze_reference.sh training/referencias/ref-NN.mp4 training/referencias/ref-NN <lang>
   ```
   It generates contact sheets at 2 fps with timecode, 3 full-resolution frames, `words.json` with the speech, and the loudness.
3. **Look** at the contact sheets and the frames. Note down: the block structure with timings, what holds attention (the mechanism), palette, typography, density, components, transitions, text × speech relationship, sound.
4. Write `references/styles/<nome>.md` following `_template.md`, linking each component to terms in `motion-dictionary.md` and to the HyperFrames recipes.
5. Leave it there. Never save it in `community/` and never add it to this README: it describes someone else's piece.

## Community styles (versioned)

A community recipe describes a grammar its author owns, or a generic genre or school (Swiss typographic grid, newsroom lower thirds, kinetic typography, zine collage). It never breaks down one specific creator's video, series or channel: no reference to a profile, no timings measured from a piece, no logo, character, catchphrase or text of someone else. If the recipe only makes sense next to one particular video, it is a local style.

Format: `_template.md`, with two changes:

- Replace the `Reference:` line with `Origin: own grammar (<author>)` or `Origin: genre/school (<name>)`, plus generic public sources if any (a book, a design movement), never a single creator's video.
- The timings in "Structure and timing" are the recipe's own choice, not a measurement of someone's piece.

File name: short kebab-case that names the grammar (`swiss-grid.md`). Text in English, like the rest of the skill. How to propose one: `CONTRIBUTING.md` at the repository root.

| Style | Mechanism | Good for | Origin |
|---|---|---|---|
