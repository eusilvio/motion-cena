# Visual identity + motion principles

## Extract the brand from a website

1. Read the home page (the agent's web tool or `curl`): ask for hex colors from the CSS (`--*` variables), `font-family`, Google Fonts links, and the tone of the copy.
2. If a browser is available (Claude in Chrome / built-in browser): take screenshots of the home page and one inner page; look at the screenshots for style (borders, shadows, density, illustration vs photo).
3. Fonts: prefer Google Fonts (loadable in HyperFrames via `<link>` and in Remotion via `@remotion/google-fonts`). Proprietary font → closest Google equivalent; record the swap.
4. Save `brand.json` (see `assets/brand.example.json`): `colors` (bg, surface, text, muted, primary, accent, positive, negative), `fonts` (display, body, mono), `radius`, `motion` (default easing, base duration), `logo` (path, if any).

Example from the article: earthy palette, Lora (serif, headings), Geist (sans serif, body), yellow as the primary color.

No brand: choose an intentional direction (e.g. "dark editorial, large serif, one citrus accent"), no generic purple gradient.

## Extract the brand from code

When the request points to a product repository, the brand lives in the code. Look, in this order:

1. **Tokens and theme**: `tailwind.config.*` (`theme.extend.colors`, `fontFamily`), CSS variables (`:root { --primary: ... }` in `globals.css`, `app.css`, `index.css`), theme files (`theme.ts`, `tokens.json`, `colors.ts`), design system (`packages/ui`).
2. **Fonts**: `@fontsource/*` and `next/font` in `package.json`/layout, Google Fonts `<link>` in the HTML, local `@font-face` (copy the file to `video/assets/fonts/` if the license allows).
3. **Logo and icons**: `public/`, `assets/`, `static/` (`logo.svg`, `favicon.svg`, `icon-*.png`, `apple-touch-icon`). Prefer SVG.
4. **Tone**: the interface's real copy (i18n `pt-BR.json`, landing page, onboarding, error messages) shows how the product speaks.
5. **Screens**: run the app locally if the README explains how and take screenshots; otherwise, rebuild the screen from the components using the tokens above.

Never read `.env`, secrets, dumps or production data; use sample data. Record in `brief.md` which files each color, font and logo came from.

## Motion principles for retention

**Timing**
- Base entrance duration 300–500ms; emphasis 150–250ms; scene transitions 250–400ms.
- Stagger 30–60ms between items; total cascade < 800ms.
- The entrance precedes the word by ~100–150ms (the eye arrives before the ear). In `timeline.json`, use `anchor.start - 0.12`.

**Easing**
- Entrances: strong ease-out (`power3.out`/`expo.out`; Remotion `Easing.out(Easing.cubic)` or `spring({damping: 14})`).
- Exits: ease-in (`power2.in`), faster than entrances.
- Slight overshoot (back.out 1.4 / spring) for pops. Linear only for counters and drifts.

**Constant life**
- Every frame has something moving: camera drift 1–3%, subtle particles, background parallax, animated grain.
- Avoid the "PowerPoint slide": never leave a composition still for > 1s.

**Legibility per canvas**
- Vertical 1080×1920: titles 90–160px, body ≥ 56px, hero numbers 200–400px. Other canvases: "Adapting the layout to the canvas" table in `references/platforms.md`.
- The safe zone comes from the platform preset (`uv run scripts/platform_preset.py <preset>`); Reels/Stories per Meta: 14% top, 35% bottom, 6% sides; TikTok/Shorts: larger right margin (buttons).
- Contrast ≥ 4.5:1. Max. 2 fonts, 1 dominant accent color.

**Color by the content's tone (applies to video and carousel)**
- Before applying the palette, define the post's emotion in one word (alert, grief, hope, achievement, curiosity, calm) and choose the colors from it. The user's brand goes into fonts, layout and, when it fits, the accent; the brand's orange accent is **not mandatory** in a post that calls for a different mood.
- Starting table (adjust to the central idea):

| Tone | Background | Text | Accent | Example |
|---|---|---|---|---|
| Alert / sadness (debt, loss, risk, tragedy) | cold bluish black `#0b0d10` | cold gray `#e6e8eb` / `#9ba4ae` | alert red `#e5484d`, only on what is the problem | debt, crisis, accident |
| Hope / turnaround | neutral dark | warm light | amber or soft green on the way out | after the fall, the fresh start |
| Achievement / celebration | dark or clean light | high contrast | gold, brand orange | record, award, goal reached |
| Curiosity / neutral | default identity | default identity | brand accent | curious fact, news |
| Faith / reflection | warm dark | cream | warm light, little accent | Bible verse, testimony |

- Color carries meaning across the piece: if red = problem, whatever is the solution or relief (the author's home, the way out, the rule that works) does **not** get red; it goes to the light neutral or to a relief color.
- Record the tone and the chosen palette in `brief.md`/`brand.json` and in the `creatives/registro.md` row.

**Composition: use the whole screen (inside the safe zone)**
- The safe zone limits where critical text goes; inside it the layout is free. Do not build the whole video in a left column or a central block: it ends up rigid.
- Vary the anchor per scene: top-left corner, bottom-right, center, diagonal, two poles in dialogue. Elements enter from different sides (top, bottom, left, right, diagonally from a corner, from the inside out) according to the meaning of the speech.
- Plan it in the storyboard: each scene records where the main visual sits and where it enters from; two consecutive scenes do not repeat the same position and direction.
- Background elements, shapes and movement may bleed outside the safe zone and the screen; only text, numbers, logos and faces stay inside.
- Captions can also move when the scene calls for it (e.g. they move up when the visual takes up the bottom), always inside the safe zone.

**Real symbols**
- Flags, medals and logos in their original colors; line icons recolored in the brand color, one family only. Rules and sources in `references/iconography.md`.

**Data**
- Numbers count up with ease-out (slowing down as they reach the value).
- Charts draw themselves (bars grow from the base, lines with draw-on), labels come in afterwards.
- Highlight = light up the relevant data point and dim the rest (opacity 0.25), do not add arrows.

**Burned-in captions (on by default)**
- 1–3 words at a time, active word highlighted in the accent color, positioned in the lower third above the safe zone.
- Use `words.json` directly; group words with a gap < 200ms.
