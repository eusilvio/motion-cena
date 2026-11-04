# Carousel mode

Same content, different output: instead of a narrated video, a sequence of static slides for Instagram (or a PDF for LinkedIn). **No narration, no TTS, no timeline, no sound.**

## How to activate (the "flag")

Any of these turns carousel mode on (`output: carrossel` in `brief.md`):

- the request says "carrossel", "carousel", "slides pro Instagram", "post de arrastar" (swipe post), or includes `--carrossel`;
- the input comes from a calendar/briefing with the format "Carrossel" (e.g. a column `Formato = Carrossel`);
- the user asks "também em carrossel" (also as a carousel) → produce both from the same brief.

Without any of these, the default stays `output: video`. When the content calls for a carousel and the user said nothing, **recommend** it in one line and follow what they asked for.

| Content | Best output |
|---|---|
| Informative, data, commented news, step-by-step, list, comparison, reference guide ("salve este post" (save this post)) | **carousel**: people read at their own pace, save and share |
| Marketing campaign, launch, offer with several benefits | **carousel** (feed) + optional short video |
| Emotional story, motivational, tone of voice matters, demonstration in motion | **video** |

## Engines

| Engine | When | Output |
|---|---|---|
| **Claude Design** (when available) | only in a Claude agent with the Artifact tool: editable canvas in the browser, the user adjusts text and colors directly on the artboards and exports | private artifact on claude.ai (one artboard per slide) |
| **Local (HyperFrames → PNG)** | any agent; local files, no dependency on claude.ai, PNG/PDF ready to post | `creatives/carrossel/<slug>-<preset>/01.png … NN.png` + `contact.jpg` (+ `carousel.pdf`) |

Both use **the same source**: the Claude Design `.dc.html` files, kept in `projects/<slug>/carousel/claude-design/project/`. The local engine converts that source, so the PNG comes out identical to the canvas:

```bash
S=.agents/skills/motion-cena/scripts
# fontes da marca em projects/<slug>/carousel/render/assets/fonts/ (+ package.json/hyperframes.json de um projeto existente)
uv run $S/dc_to_carousel.py projects/<slug>/carousel/claude-design/project --out projects/<slug>/carousel/render --preset ig-carousel
(cd projects/<slug>/carousel/render && npx hyperframes check)
uv run $S/render_carousel.py projects/<slug>/carousel/render --slides <N> --out creatives/carrossel/<slug>-ig-carousel [--pdf]
```

Without the Artifact tool: write the `.dc.html` files anyway (format below) and use only the local engine.

## Presets

`uv run scripts/platform_preset.py ig-carousel`

| Preset | Slide | Limit | Ideal | Notes |
|---|---|---|---|---|
| `ig-carousel` | 1080×1350 (4:5) | 20 slides (organic), 10 in ads | 6–10 | default; takes up more screen in the feed |
| `ig-carousel-square` | 1080×1080 (1:1) | 20 / 10 | 6–10 | when the grid/brand calls for square |
| `linkedin-carousel` | 1080×1350 | 20 | 6–12 | also outputs `carousel.pdf` (document post) |

All slides share the same aspect ratio (the first one sets the crop for the rest). Safe margin 80 px: the app overlays the counter and icons on the edges.

## Structure

1. **Cover (slide 1)**: hook with a trigger (`references/hooks.md`, mandatory): 5 candidates using different triggers, gap test, pick the highest score. A title that stings + a swipe line that opens the question ("E a culpada nº 1 tá na sua carteira →"). A cover that gives away the post's conclusion fails: people must leave it wanting slide 2. Cover visual: one of the 3 cover types below.
2. **Slide 2 gets straight to the point**: no long intro. It already delivers the first "how to" or the main data point. Instagram shows the carousel again to people who did not interact, opening **on slide 2**, so it must work as a second cover: a strong title and complete meaning for someone who never saw the cover. Context (who/what, 2–3 big numbers) goes right here, together with the delivery, not in a context-only slide. A short early CTA ("salva pra fazer depois" (save it for later)) fits in this slide's footer.
3. **Body (2–6 slides)**: one idea per slide, short title + up to ~40 words. Step-by-step: number the steps ("Passo 3:"). **Highly visual**: a screenshot, screen, photo or real mockup of what the text describes whenever one exists (app, spreadsheet, news, chart, conversation), not a lone paragraph. The cover's gap is answered by slide 3, and each slide ends with a line that pulls to the next one (swipe chain in `hooks.md`).
4. **Turn / synthesis (1 slide)**: the insight that justifies the post.
5. **Ending (last)**: follows the post's intent. It can be a question, a save/share/follow CTA or a **lead magnet** (isca): it promises a free material tied to the post (PDF, checklist, prompt, spreadsheet), delivered by keyword ("comenta GUIA que eu te mando") via DM automation (Manychat). The lead magnet only goes in when the material actually exists and is free. Always include the @ + the **data source**.

### Reference system ("viral carousel")

The rules below were taken from screenshots of a third-party carousel, which are not included in the repository (copyright). If you have your own reference screenshots, keep them in `assets/carousel-refs/<nome>/` (outside git) and open them before designing a new carousel: they are the finish bar. Copy only the visual system, never the copy (text rules below). The numbers in parentheses (`01`–`06`) cite the original screenshots.

**3 cover types** (choose by content and alternate between posts, logging which one was used in `creatives/registro.md`):

| Type | When | How |
|---|---|---|
| **4-photo collage** (`01`) | list of insights, "roube meu…" (steal my…), trends | 2×2 grid of full-bleed photos, huge white title in the center crossing all 4, soft shadow for legibility; small labels in the corners of each photo |
| **Tutorial** (`02`, left) | step-by-step, "o jeito mais simples de…" (the simplest way to…) | one darkened behind-the-scenes photo (desk, screen, hand), large title in the upper third + small subtitle with the promise ("1 semana de conteúdo sem improviso") |
| **Simple** (`02`, right) | opinion, strong statement, controversy | full background photo + very large text, one word in italics or in the accent color |

Cover photos are real or generated from a photo (Higgsfield), with a behind-the-scenes look: desk, laptop, coffee, a person reacting. A flat background or a CSS illustration on the cover fails.

**Visual language repeated on every slide:**

- **Fixed frame**: header with the @ on the left and brand/section on the right (mixed weight: "**Social** Media"); footer with two small labels (topic on the left, category on the right). Same position on every slide, within the 80 px margin.
- **Alternating background**: light paper with grain texture (off-white, not pure white) ↔ dark photo with a 70–85% black veil. Alternating is what gives the swipe its rhythm; never use 3 slides in a row with the same background.
- **Two-weight title**: a thin uppercase label with a colon ("SLIDE 2:", "MIOLO DO CONTEÚDO:") on top and, right below, a black/extra-bold grotesque title with tight leading (0.95–1.0) and negative tracking. One line of the title can go in the accent color.
- **Highlighter block**: the slide's key phrase sits in a block with an accent-color background and white text (1 per slide, 2 at most). An isolated trigger word (the CTA's "QUERO") goes in the accent color without a block.
- **Screenshots as proof**: screens and slides in rounded-corner cards (24–32 px) with a shadow; there can be more than one side by side, slightly overflowing the edges (horizontal sequence of 4 screenshots in `05`). Explanatory text beside them (right) or below.
- **Handwritten annotation**: a hand-drawn curved arrow pointing from the text to the screenshot, a tilted sticky note with a short note. One element per slide, like someone explaining on top of it, without turning into decoration.
- **Italic serif accent**: one word per title can go in italic serif ("Treine o seu *chat*", "*Passo 3:*") to break the grotesque.
- **Swipe cue**: an outlined pill in the bottom-right corner of the cover ("arrasta pro lado →") and a pill with an arrow on the last slide; on the middle slides, an → arrow at the end of the sentence that pulls to the next one.
- **Background texture**: on dark slides, tiny running text at low opacity (5–8%) works as texture; never content that needs to be read.

The reference system's colors are black, off-white and red; swap in the project's brand accent (`brand.json`) while keeping the logic: a light neutral, a dark neutral and one warm accent for highlights only.

Text rules (`references/writing-style.md`, check with `lint_copy.py` on the `.dc.html` files and on `legenda.txt`): complete sentences on the slide (without relying on the post caption); numbers with a source; illustrative content marked as illustrative; same tone of voice as the user. Post caption kept separate (`legenda.txt`, 3–5 lines, **first line = another version of the hook**, ends in a question) and alt text per slide (`alt-text.txt`).

## Design

- **Visual map mandatory** here too (`references/visual-mapping.md`): each slide has a main visual that references the slide's text. **No emoji**, not even in the post caption.

- Color by the post's tone (`references/brand-and-motion.md`, "Color by the content's tone"): debt/loss calls for cold tones + alert red, not the default orange. Brand identity (`brand.json`); margins, typography, frame (header/footer) and the `01/07` counter identical on every slide: consistency is what makes it look like a single piece. The background alternates between two fixed states (light and dark); it does not change freely.
- One visual motif running across the slides (the curve, the grid, the dot…), the same as the video's when both exist.
- Hierarchy: small label on top → large title → support → footer (counter/@). Frame details, alternating backgrounds and highlights are in "Reference system" above.
- Text ≥ 30 px in the body, ≥ 26 px in notes; contrast ≥ 4.5:1.
- Real symbols apply to the carousel too (`references/iconography.md`): flag, medal, official logo on the slide that cites the entity; in Claude Design, upload the SVG as an asset and write `<img data-asset="<arquivo>.svg" src="/_blob/<id>" alt="…">`; the local engine swaps the `src` for the file in `projects/<slug>/carousel/render/assets/icons/`. CC BY credit on the last slide if used.
- The video vocabulary works for describing the layout, but there is no motion: no effects from the motion dictionary.

## `.dc.html` format (for both engines)

One artboard per slide, fixed root `width × height` from the preset, everything with inline `style`, literal brand colors, one optional `{{accent}}` declared in `data-props` with a `default` (the converter fills the `{{holes}}` with the defaults). Fonts via a Google Fonts `<link>` in the `<helmet>` (the local engine swaps it for `@font-face` with the files from `assets/fonts/`, named `Familia-Estilo.ttf`). `canvas.json` lists the artboards in `order` = slide order.

## Delivery

Report: the Claude Design canvas link (private until the user shares it), the folder `creatives/carrossel/<slug>-<preset>/` with the PNGs, `legenda.txt`, `alt-text.txt`, the number of slides, and what was left out. Open `contact.jpg` before delivering.
