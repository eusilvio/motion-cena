# Motion effects dictionary

A single vocabulary for the storyboard, user requests and code. Sources: the carousel "Dicionário de efeitos Motion" (Motion effects dictionary) by @omatheusdaia, 18 terms in part 1 (the original carousel images are not included in the repository), and research into motion glossaries, animation principles and Reels/Shorts trends (Oct/2026), 26 terms in part 2. The carousel's thesis: **asking for "a nice-looking video" does not work; asking for effect + duration + ease + target does.**

## How to ask (and how to write the `motion` field)

Formula: **`<efeito> [em <duração>] [com <ease>] [no <alvo>]`** (effect [in duration] [with ease] [on target])

> "Faça o título entrar com **slide in** em **0,4 s** e **ease out**. Revele os benefícios com **stagger** de **0,15 s**. Termine com um **punch zoom** no produto."
>
> (Make the title enter with slide in, in 0,4 s, with ease out. Reveal the benefits with a 0,15 s stagger. End with a punch zoom on the product.)

When you receive a request in this format, translate it term by term using the table below: do not reinterpret. Omitted parameter → use the table default. Vague request ("deixa mais dinâmico", "make it more dynamic") → reply by proposing phrases in this format before changing anything.

In `storyboard.json`, the `motion` field uses the same terms: `"título: slide in 0.4s ease out · benefícios: stagger 0.15s · produto: punch zoom em 'agora'"`.

## Quick table

| Family | Term | What it is | Default | HyperFrames recipe |
|---|---|---|---|---|
| Soft entrances | **fade in** | appears gradually | 0,4 s, `power2.out` | - |
| | **slide in** | slides in | 0,4 s, `power3.out`, 80–120 px | `nudge-curve` (reposition a group) |
| | **blur in** | from blurred to sharp | 0,5 s, `power2.out`, blur 24 px | `depth-of-field-blur` |
| Impact entrances | **pop in** | appears with a small scale jump | 0,4 s, `back.out(1.7)` | `spring-pop-entrance` |
| | **scale up** | grows to its final size | 0,6 s, `expo.out` | `counting-dynamic-scale` (with a number) |
| | **stagger** | elements enter one after another | 0,05–0,15 s between items; cascade ≤ 0,8 s | `waterfall-entry` |
| Rhythm (ease) | **ease in-out** | starts slow, speeds up, brakes | `power2.inOut` / `sine.inOut` | - |
| | **overshoot** | goes past the target and comes back | `back.out(1.4–2)` | `spring-pop-entrance` |
| | **bounce** | bounces before stopping | `bounce.out` (or `elastic.out(1,0.5)`) | `press-release-spring` |
| Text | **typewriter** | letters appear one by one | 25–40 ms/letter, blinking cursor | `gsap-effects` (typewriter), blueprint `typewriter-reveal` |
| | **word reveal** | words appear in sequence | anchored to `words.json`; otherwise 0,12 s/word | `asr-keyword-glow`, `waterfall-entry` |
| | **text swap** | one word swaps for another | 0,35 s, exits ↑ enters ↓ inside a mask | `vertical-spring-ticker` |
| Shapes | **draw-on** | the stroke draws itself | 0,8–1,2 s, `power2.inOut` | `svg-path-draw` |
| | **morph** | one shape becomes another | 0,6 s, `power3.inOut` | `card-morph-anchor`, `scale-swap-transition` |
| | **bar grow** | a bar grows to the value | 0,8 s, `power3.out`, + count-up | `stat-bars-and-fills` |
| Scene transitions | **mask reveal** | a mask reveals the content | 0,6 s, `power3.inOut`, `clip-path` | transitions `css-radial`, `css-cover` |
| | **wipe** | a band replaces one scene with the next | 0,5 s, `power3.inOut`, band in the accent color | transitions `css-cover` / `css-push` |
| | **punch zoom** | fast zoom for impact | 0,25 s in `power4.out`, settles over 0,4 s | `coordinate-target-zoom`, `viewport-change`, transitions `css-scale` |

### Part 2: expansion (Oct/2026 research)

| Family | Term | What it is | Default | HyperFrames recipe |
|---|---|---|---|---|
| Text | **scramble** | letters scramble and decode into the word | 0,8 s, glyph swap at 20 fps | `hacker-flip-3d` |
| | **line reveal** | each line rises from behind a mask | 0,7 s, `power4.out`, stagger 0,08 s | `waterfall-entry` (GSAP SplitText `mask: "lines"` has been free since 3.13) |
| | **highlight** | a highlighter passes behind the word | 0,4 s, `power2.out`, from the left | `css-marker-patterns` |
| | **slam** | the word drops in big and "hits" the screen | 0,22 s, `power4.out`, scale 2,4 → 1 + shake | `kinetic-beat-slam` |
| | **count-up** | a number counts up to the value | 0,8–1,2 s, `power2.out`, `tabular-nums` | `counting-dynamic-scale` |
| Emphasis | **pulse** | pulses once to draw attention | 0,18 s out + back, scale 1,08 | `asr-keyword-glow` |
| | **shake** | shakes in place (error, impact, "no") | 0,35 s, ±14 px decaying | `chromatic-glitch` (burst form) |
| | **glow** | a glow lights up around it | 0,25 s up, 0,5 s down | `ambient-glow-bloom` |
| | **wiggle** | quick, slight wobble (to invite a click) | 8 half-swings of 0,12 s, ±2° | `svg-icon-enrichment` |
| Physics (Disney principles) | **anticipation** | pulls back before moving | 0,15 s pullback + 0,45 s move `power3.out` | `press-release-spring` |
| | **squash & stretch** | squashes on impact and stretches on the jump | impact 0,08 s scale 1,3×0,7, return `elastic.out` | `physics-press-reaction` |
| | **follow-through** | secondary parts arrive later and overshoot | 0,06 s delay per layer, `back.out(2)` | `reactive-displacement` |
| | **float** | floats/breathes in a subtle loop | ±12 px, 1,2 s, `sine.inOut` yoyo (finite) | `sine-wave-loop` |
| Camera | **push-in** (Ken Burns) | the camera slowly moves in on the whole scene | scene duration, scale 1 → 1,12, `sine.inOut` | `multi-phase-camera` |
| | **parallax** | layers move at different speeds | background 0,2×, middle 0,5×, front 1× | `3d-camera-flight` |
| | **whip pan** | the camera whips with blur to the next scene | 0,35 s, `power4.inOut`, blur peak 30 px | `motion-blur-streak`, transitions `css-blur` (Directional Blur) |
| | **dolly zoom** | the background grows while the subject stays the same size (vertigo) | 1,2 s, `power1.inOut` | `viewport-change` |
| Scene transitions (part 2) | **zoom through** | the camera passes through A and lands in B | 0,4 s A `power3.in` + 0,4 s B `power3.out` | transitions `css-scale` (Zoom Through) |
| | **iris** | a circle opens to reveal B | 0,6 s, `power3.inOut`, centered on the object | transitions `css-radial` (Circle Iris) |
| | **push** | B pushes A out | 0,5 s, `power3.inOut` | transitions `css-push` |
| | **glitch** | RGB split/slices jitter and switch the scene | 0,3 s, jumps every 0,05 s | `chromatic-glitch`, transitions `css-distortion` |
| | **flash** | a burst of light/color hides the cut | 0,08 s up, 0,25 s down | transitions `css-light`, `css-dissolve` (Color Dip) |
| | **blinds** | bands close over A and open on B | 0,25 s each side, stagger 0,04 s | transitions `css-cover` |
| | **match cut** | an object in A becomes the object in B in the same place | 0,5 s, `power3.inOut` | `card-morph-anchor`, `scale-swap-transition` |
| Finishing | **motion trail** | ghost echoes follow a fast movement | 3 echoes, 0,03 s delay, opacity 0,4/0,25/0,12 | `motion-blur-streak` |
| | **grain** | film texture flickering at 12 fps | opacity 0,06–0,1, `mix-blend-mode: overlay` | see recipe |

Cited recipes: `.agents/skills/hyperframes-animation/rules/<nome>.md`; transitions in `.agents/skills/hyperframes-animation/transitions/<arquivo>.md`. Load the `hyperframes-animation` skill for the API; this file gives the term and the default.

## GSAP recipes (seek-safe)

Validated in `training/dicionario-demo/` (part 1 → `creatives/demos/dicionario-demo.mp4`) and `training/dicionario-demo-2/` (part 2, generated by `build.py` → `creatives/demos/dicionario-demo-2.mp4`), both with a clean `hyperframes check`: use them as a live example of each effect. All of them assume a single paused `tl`, `fromTo` with an explicit initial state, only transform/opacity/filter/clip-path (no `width`/`height`/`top`), and no `Math.random`. `t` = start (usually `anchor.start - 0.12`).

### Soft entrances
```js
// fade in
tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power2.out" }, t);
// slide in (da esquerda; troque x por y para slide up)
tl.fromTo(el, { x: -120, opacity: 0 }, { x: 0, opacity: 1, duration: 0.4, ease: "power3.out" }, t);
// blur in
tl.fromTo(el, { filter: "blur(24px)", opacity: 0 }, { filter: "blur(0px)", opacity: 1, duration: 0.5, ease: "power2.out" }, t);
```

### Impact entrances
```js
// pop in — pequeno salto, não de 0 (de 0 vira "scale up")
tl.fromTo(el, { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.7)" }, t);
// scale up
tl.fromTo(el, { scale: 0 }, { scale: 1, duration: 0.6, ease: "expo.out" }, t);
// stagger — itens × stagger ≤ ~0.8s
tl.fromTo(items, { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: "power3.out", stagger: 0.15 }, t);
```

### Rhythm: the ease is the effect
```js
// ease in-out: mover algo que já está na tela (A → B)
tl.fromTo(el, { x: 0 }, { x: 600, duration: 1.0, ease: "power2.inOut" }, t);
// overshoot: chega passando do destino e volta
tl.fromTo(el, { x: 0 }, { x: 600, duration: 0.7, ease: "back.out(1.8)" }, t);
// bounce: queda que quica (origem em cima, destino no "chão")
tl.fromTo(el, { y: -500 }, { y: 0, duration: 1.0, ease: "bounce.out" }, t);
```
Usage rule: ease-out for entrances, ease-in for exits, ease in-out to move what is already on screen, overshoot/bounce for "physical" objects (button, icon, ball). Never linear, except for counters and drift.

### Text
```js
// typewriter — texto completo no DOM, revela por contagem (seek-safe)
const full = el.dataset.text, p = { n: 0 };
tl.fromTo(p, { n: 0 }, { n: full.length, duration: full.length * 0.035, ease: "none",
  onUpdate: () => { el.textContent = full.slice(0, Math.round(p.n)); } }, t);
// cursor: tl.set(cursor, {opacity: k % 2}, t + k * 0.5) em loop finito

// word reveal — cada <span class="w"> no instante da palavra falada
words.forEach((w, i) => tl.fromTo(spans[i], { opacity: 0.15 }, { opacity: 1, duration: 0.12 }, w.start - 0.05));
// sem áudio: tl.fromTo(spans, {opacity:0, y:20}, {opacity:1, y:0, stagger:0.12, duration:0.3, ease:"power3.out"}, t)

// text swap — duas palavras empilhadas dentro de .slot { overflow: hidden }
tl.fromTo(oldW, { yPercent: 0 },   { yPercent: -100, duration: 0.35, ease: "power3.inOut" }, t);
tl.fromTo(newW, { yPercent: 100 }, { yPercent: 0,    duration: 0.35, ease: "power3.inOut" }, t);
```

### Shapes
```js
// draw-on — path SVG; mede comprimento no setup
const L = path.getTotalLength();
tl.fromTo(path, { strokeDasharray: L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 1.0, ease: "power2.inOut" }, t);

// morph (sem plugin): mesmo elemento muda raio + escala + cor
tl.fromTo(el, { borderRadius: "50%", scale: 1, backgroundColor: A },
              { borderRadius: "16%", scale: 1.15, backgroundColor: B, duration: 0.6, ease: "power3.inOut" }, t);
// morph de paths SVG arbitrários: MorphSVGPlugin (grátis desde GSAP 3.13) ou crossfade de dois paths no mesmo centro (scale-swap-transition)

// bar grow — scaleX a partir da esquerda + count-up no mesmo t
tl.fromTo(bar, { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: v / max, duration: 0.8, ease: "power3.out" }, t);
const c = { v: 0 };
tl.fromTo(c, { v: 0 }, { v, duration: 0.8, ease: "power3.out", onUpdate: () => (num.textContent = Math.round(c.v)) }, t);
```

### Scene transitions
```js
// mask reveal — faixa horizontal abre do centro para cima e para baixo (como no slide 7)
tl.fromTo(sceneB, { clipPath: "inset(50% 0% 50% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.6, ease: "power3.inOut" }, t);
// variantes: "circle(0% at 50% 50%)" → "circle(75% at 50% 50%)" (iris); inset(0 100% 0 0) → inset(0) (lateral)

// wipe — B entra atrás de uma faixa de acento que varre a tela
tl.fromTo(sceneB, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.5, ease: "power3.inOut" }, t);
// faixa: left:-barW/2 no CSS; mesma duração + ease do clip = fica colada na borda
tl.fromTo(bar,    { x: 0 }, { x: W, duration: 0.5, ease: "power3.inOut" }, t);

// punch zoom — soco rápido e assenta; origem no alvo
tl.fromTo(target, { scale: 1 }, { scale: 1.35, duration: 0.25, ease: "power4.out", transformOrigin: "50% 50%" }, t);
tl.to(target, { scale: 1.2, duration: 0.4, ease: "power2.out" }, t + 0.25);
// como transição: câmera (.world) dá punch zoom no objeto que vira a próxima cena (match cut)
```

### Part 2: text
```js
// scramble — glifo determinístico por (índice, passo de tempo); revela da esquerda
const GL = "!<>-_/[]{}=+*^?#ABCDEFGHJKMNPRSTUVWXYZ0123456789", word = el.dataset.text, sc = { p: 0 };
tl.fromTo(sc, { p: 0 }, { p: 1, duration: 0.8, ease: "none", onUpdate: () => {
  const shown = Math.floor(sc.p * word.length), step = Math.floor(tl.time() * 20);
  el.textContent = [...word].map((ch, i) => i < shown || ch === " " ? ch : GL[(i * 31 + step * 17) % GL.length]).join("");
} }, t);

// line reveal — cada linha: <div class="line" style="overflow:hidden"><span>texto</span></div>
tl.fromTo(lineSpans, { yPercent: 110 }, { yPercent: 0, duration: 0.7, ease: "power4.out", stagger: 0.08 }, t);

// highlight — div .hl absoluto atrás da palavra (pseudo-elemento não é tweenável)
tl.fromTo(hl, { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.4, ease: "power2.out" }, t);

// slam — cai grande, bate, tela treme
tl.fromTo(word, { scale: 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.22, ease: "power4.out" }, t);
tl.fromTo(stage, { y: 0 }, { keyframes: { y: [0, 14, -9, 5, 0] }, duration: 0.3, ease: "none" }, t + 0.2);

// count-up — font-variant-numeric: tabular-nums para não tremer a largura
const n = { v: 0 };
tl.fromTo(n, { v: 0 }, { v: 1000, duration: 1.0, ease: "power2.out", onUpdate: () => (num.textContent = Math.round(n.v).toLocaleString("pt-BR")) }, t);
```

### Part 2: emphasis
```js
// pulse
tl.fromTo(el, { scale: 1 }, { scale: 1.08, duration: 0.18, ease: "sine.inOut", yoyo: true, repeat: 1 }, t);
// shake — amplitude decaindo; valores fixos (determinístico)
tl.fromTo(el, { x: 0 }, { keyframes: { x: [0, -14, 12, -8, 6, -3, 0] }, duration: 0.35, ease: "none" }, t);
// glow — drop-shadow na cor de acento
tl.fromTo(el, { filter: "drop-shadow(0 0 0px rgba(208,89,44,0))" }, { filter: "drop-shadow(0 0 40px rgba(208,89,44,0.9))", duration: 0.25, ease: "power2.out" }, t);
tl.to(el, { filter: "drop-shadow(0 0 0px rgba(208,89,44,0))", duration: 0.5, ease: "power2.in" }, t + 0.35);
// wiggle — repeat finito
tl.fromTo(el, { rotation: -2 }, { rotation: 2, duration: 0.12, ease: "sine.inOut", yoyo: true, repeat: 7 }, t);
tl.to(el, { rotation: 0, duration: 0.1 }, t + 0.96);
```

### Part 2: physics
```js
// anticipation — recua, depois dispara
tl.fromTo(el, { x: 0 }, { x: -50, duration: 0.15, ease: "power2.inOut" }, t);
tl.to(el, { x: 600, duration: 0.45, ease: "power3.out" }, t + 0.15);
// squash & stretch — bola caindo no chão (transformOrigin na base)
tl.fromTo(ball, { y: -500, scaleX: 0.85, scaleY: 1.2 }, { y: 0, duration: 0.45, ease: "power2.in", transformOrigin: "50% 100%" }, t);
tl.to(ball, { scaleX: 1.3, scaleY: 0.7, duration: 0.08, ease: "power2.out" }, t + 0.45);
tl.to(ball, { scaleX: 1, scaleY: 1, duration: 0.5, ease: "elastic.out(1, 0.4)" }, t + 0.53);
// follow-through — corpo para; partes chegam depois e passam do ponto
tl.fromTo(body, { x: -500 }, { x: 0, duration: 0.5, ease: "power3.out" }, t);
tl.fromTo(parts, { x: -500 }, { x: 0, duration: 0.6, ease: "back.out(2)", stagger: 0.06 }, t + 0.06);
// float — loop finito dentro da cena
tl.fromTo(el, { y: 0 }, { y: -12, duration: 1.2, ease: "sine.inOut", yoyo: true, repeat: Math.floor(sceneDur / 1.2) - 1 }, t);
```

### Part 2: camera
```js
// push-in (Ken Burns) — a cena inteira, devagar
tl.fromTo(world, { scale: 1, x: 0 }, { scale: 1.12, x: -30, duration: sceneDur, ease: "sine.inOut" }, sceneStart);
// parallax — mesma duração/ease, deslocamentos proporcionais à "profundidade"
[[bg, 0.2], [mid, 0.5], [fg, 1]].forEach(([el, k]) => tl.fromTo(el, { x: 0 }, { x: -300 * k, duration: 1.6, ease: "power1.inOut" }, t));
// whip pan — A sai, B entra, borrão no pico de velocidade
tl.fromTo(A, { x: 0 }, { x: -W, duration: 0.35, ease: "power4.inOut" }, t);
tl.fromTo(B, { x: W }, { x: 0, duration: 0.35, ease: "power4.inOut" }, t);
tl.fromTo([A, B], { filter: "blur(0px)" }, { keyframes: { filter: ["blur(0px)", "blur(30px)", "blur(0px)"] }, duration: 0.35, ease: "none" }, t);
// dolly zoom — fundo aproxima, sujeito compensa
tl.fromTo(bg, { scale: 1 }, { scale: 1.6, duration: 1.2, ease: "power1.inOut" }, t);
tl.fromTo(subject, { scale: 1 }, { scale: 0.9, duration: 1.2, ease: "power1.inOut" }, t);
```

### Part 2: transitions
```js
// zoom through
tl.fromTo(A, { scale: 1, opacity: 1 }, { scale: 4, opacity: 0, duration: 0.4, ease: "power3.in" }, t);
tl.fromTo(B, { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: "power3.out" }, t + 0.25);
// iris — centro no objeto que importa
tl.fromTo(B, { clipPath: "circle(0% at 50% 50%)" }, { clipPath: "circle(75% at 50% 50%)", duration: 0.6, ease: "power3.inOut" }, t);
// push
tl.fromTo(A, { x: 0 }, { x: -W, duration: 0.5, ease: "power3.inOut" }, t);
tl.fromTo(B, { x: W }, { x: 0, duration: 0.5, ease: "power3.inOut" }, t);
// glitch — cópias R/B deslocadas em saltos fixos, troca no meio, encaixa limpo
const offs = [18, -26, 12, -8, 22, 0];
offs.forEach((o, k) => { tl.set(red, { x: o, opacity: o ? 0.8 : 0 }, t + k * 0.05); tl.set(blue, { x: -o, opacity: o ? 0.8 : 0 }, t + k * 0.05); });
tl.set(A, { opacity: 0 }, t + 0.15); tl.set(B, { opacity: 1 }, t + 0.15);
// flash — overlay branco (ou cor de acento) esconde o corte
tl.fromTo(flash, { opacity: 0 }, { opacity: 1, duration: 0.08, ease: "power2.in" }, t);
tl.set(A, { opacity: 0 }, t + 0.08); tl.set(B, { opacity: 1 }, t + 0.08);
tl.to(flash, { opacity: 0, duration: 0.25, ease: "power2.out" }, t + 0.08);
// blinds — N faixas full-width
tl.fromTo(strips, { scaleY: 0, transformOrigin: "50% 0%" }, { scaleY: 1, duration: 0.25, ease: "power3.in", stagger: 0.04 }, t);
tl.set(A, { opacity: 0 }, t + 0.45); tl.set(B, { opacity: 1 }, t + 0.45);
tl.fromTo(strips, { scaleY: 1, transformOrigin: "50% 100%" }, { scaleY: 0, duration: 0.25, ease: "power3.out", stagger: 0.04, immediateRender: false }, t + 0.45);
// match cut — objeto de A move/escala até a posição do objeto de B, então troca
tl.to(objA, { x: dx, y: dy, scale: k, borderRadius: r, duration: 0.5, ease: "power3.inOut" }, t);
tl.set(objA, { opacity: 0 }, t + 0.5); tl.set(sceneB, { opacity: 1 }, t + 0.5);
```

### Part 2: finishing
```js
// motion trail — ecos (cópias do elemento) com atraso e opacidade decrescente
[lead, echo1, echo2, echo3].forEach((el, i) =>
  tl.fromTo(el, { x: 0 }, { x: 600, duration: 0.5, ease: "power3.out" }, t + i * 0.03));
// ecos com opacity 0.4 / 0.25 / 0.12 no CSS; some depois: tl.to(echoes, {opacity: 0, duration: 0.15}, t + 0.6)
// grain — posição pseudo-aleatória determinística a 12 fps (rng com seed fixa)
for (let k = 0, r = rng(99); k < TOTAL * 12; k++) tl.set(grain, { x: (r() - 0.5) * 80, y: (r() - 0.5) * 80 }, k / 12);
```

## Combinations that work

- **Title**: slide in 0,4 s ease out → supporting text fade in 0,2 s later.
- **Benefit list**: stagger of slide in at 0,15 s, anchored to the first word of each item if there is narration.
- **Hero number**: scale up + count-up + bar grow at the same `t`; punch zoom on the frame where the final value is spoken.
- **Idea swap** ("ideia vira vídeo", "idea becomes video"): text swap, keep the rest of the sentence still.
- **Ending/CTA**: punch zoom on the product/logo + pop in of the CTA with overshoot.
- **Revealing a shocking figure**: anticipation (pull back) → slam of the number + screen shake + short flash.
- **Keyword in the narration**: highlight or pulse anchored to the word's frame in `words.json`.
- **Tech/AI**: scramble on the title + glitch as the transition (max. 1 per video).
- **"Static" scene** (chart, quote): push-in + float on the elements + grain, never frozen.
- **Before/after**: match cut if the object exists on both sides; otherwise flash.
- **Between scenes**: wipe in the accent color (energetic), mask reveal (cinematic), punch zoom on the shared object (match cut, the best option when there is visual continuity).

## Common mistakes

- Pop in starting from `scale: 0` with a strong `back.out` on large text → looks like a cartoon spring. For text, use `0.6 → 1` and `back.out(1.4)`.
- Stagger too long (10 items × 0,15 s = 1,5 s) → cut the stagger so it fits in ≤ 0,8 s.
- Blur in on many layers at once → slow render; use it on 1–2 elements.
- Bounce on a scene transition → amateurish; bounce is for objects.
- Typewriter on a long sentence without narration → slow; above 30 characters, prefer word reveal.
- Shake/glitch/flash in every scene → becomes noise; reserve them for 1–3 peaks in the video.
- Whip pan without blur → looks like a PowerPoint slide; the blur is the effect.
- Scramble with `Math.random` → breaks the render; use the hash by (index, step).
- Parallax with every layer at the same offset → no depth; use at least 3 distinct speeds.
- More than 2 types of scene transition in the same video → pick one dominant type + punch zoom for peaks.
