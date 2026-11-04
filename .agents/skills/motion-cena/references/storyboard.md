# Written storyboard

Storyboard = a scene-by-scene visual script. Without it, the animation improvises, and improvisation rarely follows the narration. With it, "video with animation" becomes "animation that tells the story".

## Rules

- **Scene = one visual beat**, 1.5–5s. Dynamic Reels: a meaningful change every 1.5–3s (cut, zoom, new element).
- **Exact narration per scene**: the `narration` field holds the literal passage of the script. Concatenating all of them = the full script. That is what allows anchoring to the audio.
- **Everything inside the central idea** (`concept.md`): each scene happens in the chosen device or in a transformation of it.
- **The visual demonstrates, it does not illustrate**: show the concept as an object/diagram that changes. "100 maiores empresas" (100 largest companies) → 10×10 grid; "adoção rasa" (shallow adoption) → pool with a 1m ruler; "gap crescendo" (growing gap) → two diverging lines.
- **Anchors**: every emphasis (a number appears, an item lights up, a cut) ties to a spoken word (`anchor_word`). That is what syncs it.
- **Continuity**: elements survive across scenes when possible (the grid from scene 2 shrinks and becomes an icon in scene 3). Transitions with a shared object > hard cuts > fades.
- **Hierarchy per scene**: 1 main element, ≤2 secondary ones.
- **Real symbols**: a recognizable entity in the speech (country, medal, brand, institution) → real symbol in `icons` (`references/iconography.md`). Abstract only when it is the piece's metaphor.
- **On-screen text** ≤ 6 words, reinforces (does not repeat) the speech: keyword, number, label.

## Motion vocabulary (use in the `motion` fields)

Canonical vocabulary with defaults and recipes: `references/motion-dictionary.md` (fade in, slide in, blur in, pop in, scale up, stagger, ease in-out, overshoot, bounce, typewriter, word reveal, text swap, draw-on, morph, bar grow, mask reveal, wipe, punch zoom). Write each movement as **effect + duration + ease + target** ("title: slide in 0.4s ease out"). The extra terms below remain valid:


Entrances: `pop` (scale 0→1.1→1 spring), `slide-up`, `mask-reveal` (mask wipe), `type-on` (letter by letter), `draw-on` (SVG stroke), `stagger` (items cascading 30–60ms), `count-up`, `zoom-through` (the camera passes through).
Emphasis: `pulse`, `highlight` (highlighter pen sweeping across), `shake`, `glow`, `color-flip`, `scale-punch`.
Camera: slow `push-in`, `pan`, `whip-pan` (fast transition with blur), layered `parallax`.
Exits/transitions: `match-cut` (one object becomes another), `wipe`, `shrink-to-icon`, `scatter`, hard `cut` on the beat.

## Scene template (plan.md)

Example filled in (labels as in `assets/plan.template.md`; content in the user's language, here pt-BR):

```
### Scene 3 — "Adoção é larga"  (≈4s)
Narration: "quase todas as grandes empresas americanas dizem ter um plano de IA"
Visual: grade 10×10 de quadrados cinza (100 maiores empresas). Fundo escuro da marca.
Motion: grade entra com stagger diagonal (40ms). Em "quase todas", 95 quadrados acendem em verde em onda. Contador "95%" count-up no topo.
Anchors: "quase todas" → onda verde · "plano" → contador termina
On-screen text: "95% têm plano de IA"
Exit transition: grade encolhe e desce, vira "superfície da água" da cena 4 (match-cut)
SFX: tick suave por linha acendendo; whoosh curto na transição
Icons: bandeira EUA (flag us) junto de "americanas"
```

Mirror everything in `storyboard.json` (schema `assets/storyboard.schema.json`).

## Checklist before the review gate

- [ ] Concatenation of the narrations = script (no lost words)
- [ ] Every scene has movement (nothing static > 1s)
- [ ] Scene 1 has movement at frame 0
- [ ] Each number has its own visual (not just text)
- [ ] Each country, award, brand or institution mentioned has its real symbol in `icons` (or a noted reason)
- [ ] The central idea stitches the whole video together (not just one scene)
- [ ] Ending chosen by the script's intent (final fact, synthesis, question, CTA or loop; see "Ending" in `script-writing.md`)
- [ ] Each scene's main visual has its position and entrance direction recorded; consecutive scenes do not repeat both
