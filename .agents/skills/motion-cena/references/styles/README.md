# Reference styles

Recipes taken from videos the user sent as references. Each style describes the **mechanism, structure with timings, visual language, components, sound and how to adapt it** without copying the original piece. Once it is saved, the user asks for it by name ("faz no estilo <nome>", "do it in the <name> style").

The repository ships no ready-made styles: each recipe comes from a reference video belonging to whoever uses the skill, so it stays local (outside git), together with the video in `training/referencias/`. The available styles are the `.md` files in this folder (except this README and `_template.md`); keep the table below up to date on your machine.

| Style | Mechanism | Good for | Original reference |
|---|---|---|---|

## When the user sends a reference video

1. Copy it to `training/referencias/ref-NN.mp4`.
2. Run the analysis:
   ```bash
   bash .agents/skills/motion-cena/scripts/analyze_reference.sh training/referencias/ref-NN.mp4 training/referencias/ref-NN <lang>
   ```
   It generates contact sheets at 2 fps with timecode, 3 full-resolution frames, `words.json` with the speech, and the loudness.
3. **Look** at the contact sheets and the frames. Note down: the block structure with timings, what holds attention (the mechanism), palette, typography, density, components, transitions, text × speech relationship, sound.
4. Write `references/styles/<nome>.md` following `_template.md`, linking each component to terms in `motion-dictionary.md` and to the HyperFrames recipes.
5. Add the row to the table above.

Rule: the style borrows the **grammar** (structure, rhythm, kind of component). Brand, text, objects and numbers always come from the user. Never reproduce the logo, character or text of the original piece.
