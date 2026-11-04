---
name: motion-cena
description: Complete framework to create motion-design videos from any input - the user's script or text (always adapted for video; verbatim only when asked), notes, a loose topic, PDF, article, URL, data, recorded audio, a talking-head video or a product's code repository. Works for any genre (story, motivational, technical, explainer, data, product, opinion) and outputs each platform's format (Instagram Stories, Reels, Feed, TikTok, YouTube Shorts, horizontal YouTube, LinkedIn), or, with the carousel flag, a static slide carousel for Instagram/LinkedIn without narration (Claude Design or local PNG). Takes duration as a parameter (otherwise the platform default). Runs narrative format → script with 3 hooks at the requested length → central idea (3 concepts, vetoes repeats of past videos) → storyboard → visual identity → TTS voiceover with word timestamps → speech-synced animation (HyperFrames or Remotion) → sound design → render and QA. Understands requests in any language (users often write in Brazilian Portuguese) and delivers in the user's language. Use whenever the user asks "make a video", "faz um vídeo", "faz um carrossel", "narra esse texto", "transforma esse texto em vídeo", "story", "reels", "vídeo pro YouTube", "vídeo motivacional", "reels sobre esse PDF", "motion design", "vídeo animado", "explainer", "vídeo com locução", "storyboard", "roteiro de reels", or mentions Remotion, HyperFrames, GSAP, Higgsfield, ElevenLabs or synced narration, even if they only ask for one of the steps.
---

# Motion Cena: from content to MP4

Method: **input → format → script → central idea → scenes → video**. Order matters. Asking "make a video about X" straight away produces pretty, random animation that does not talk to the narration. Every step writes a file the next one consumes; the storyboard is the contract between story and animation.

The heavy lifting is **direction**: which story, which format, which visual idea, what each scene shows. Spend the effort there; animating is the easy part.

**Creativity is mandatory, not optional.** Every video is born from its own central idea (`references/concept.md`): a device where the whole script happens, chosen among 3 different concepts and vetoed if it repeats a video already delivered (`creatives/registro.md`). Illustrating sentence by sentence with an icon and a caption is what makes every video look the same. The minimum bar is `references/quality-bar.md`. Old video folders are not templates: do not copy their structure, layout or code.

**Neutral tool.** Everything comes from the request: script, topic, duration, platform, audio. Brand, voice, persona or tone from another project only come in if the request says so (section "Brand, voice and tone" below). Do not go looking for references in blogs, other repositories or previous videos on your own.

**Copy that does not sound like AI** (`references/writing-style.md`): no symmetric "it's not X, it's Y" lines, bait questions, clichés or dramatic dashes (the pt-BR list: "não é X, é Y", "o segredo?", "mergulhar", "jornada", "isso muda tudo", travessão de efeito). Concrete, direct, in the user's vocabulary. Run `uv run scripts/lint_copy.py` on the script, on-screen text, slides and caption before the review gate and before delivering; an error means rewrite (in `narracao-literal`, point it out to the user instead of rewriting).

**Emoji is forbidden in every piece** (art, on-screen text, captions, post caption, end card, slides). It looks amateur. No exceptions, even if the user's source text has emoji: remove it from the piece.

## Language

These instructions are in English; the user may write in any language, and most write in Brazilian Portuguese.

- Understand the request in whatever language it arrives, including Portuguese trigger phrases ("faz um vídeo", "narra esse texto", "faz em carrossel", "quero ver ao vivo", "usa exatamente").
- Everything the user reads or hears is in the user's language: chat replies and questions, `brief.md`, `plan.md`, narration, on-screen text, captions, slides, post caption (`legenda.txt`), alt text and the delivery summary. Default = the language of the request; the voiceover follows it (Portuguese request → pt-BR text and pt-BR voice).
- Switch the output language only when the request asks for it ("faz em inglês", "make it in Spanish").
- The concrete phrase lists in `references/writing-style.md` and `references/hooks.md` are pt-BR, and `scripts/lint_copy.py` only checks pt-BR. For another output language, apply the same principles by hand with that language's equivalents.
- Fixed identifiers stay as they are, in Portuguese: input modes (`roteiro`, `narracao-literal`, `notas`, `tema`, `fonte-longa`, `dados`, `audio-gravado`, `video-gravado`, `codigo`), file names (`registro.md`, `legenda.txt`, `narration.txt`) and folders (`creatives/carrossel/`).

## Brand, voice and tone: from each request

There is no fixed profile: each video can have a different brand, voice and tone. In step 0, find out where they come from, record the source in `brief.md` (section "Brand and voice") and save the brand in the project's `brand.json`:

| The request brings | Brand | Voice and tone |
|---|---|---|
| Colors, fonts, logo or website ("no estilo do site X", "verde #0A7", "logo em anexo") | extract it from what came (`references/brand-and-motion.md`) | the request's; with nothing, the genre's |
| **A product's code** (local path, repository, "analisa o app em ../loja") | taken from the code: theme, tokens, logo, fonts (`brand-and-motion.md` → "Extract the brand from code") | real facts, names and screens of the product; tone of the app's own copy |
| **Video or audio of someone speaking** (talking head, talk, interview, recording) | only if the request brings one | the voice is the recording's: do not re-record; tone and vocabulary come from the speech (mode `video-gravado` / `audio-gravado`) |
| "Same brand as project X" | copy `projects/X/brand.json` | X's brief, if the request says so |
| Nothing | own direction from the central idea | natural tone for the genre and platform |

Never pull brand, voice or persona from another project unless the request says so. First video on the machine: if `creatives/registro.md` does not exist, create it from `assets/registro.template.md`.

## Project structure

Create (or reuse) one folder per project in `projects/` (never in the repository root). A project can produce reels, carousel and post:

```
projects/<slug>/
  brief.md            # step 0: input mode, genre, platform(s), audience, duration, voice
  source/             # step 0: what the user sent (text, PDF, notes), untouched
  plan.md             # steps 1–3: format analysis, script, hooks, storyboard (human review)
  storyboard.json     # step 3: machine version of the storyboard (schema in assets/storyboard.schema.json)
  brand.json          # step 4: colors, fonts, motion tokens
  audio/voice.mp3     # step 5
  audio/words.json    # step 5: per-word timestamps
  timeline.json       # step 5: scenes anchored in seconds/frames (scripts/build_timeline.py)
  video/              # step 6: HyperFrames or Remotion project
  audio/sfx/ + audio/mix.wav   # step 7
  out/                # step 8: QA images (contact sheet, frame 0), out of git
```

The final piece **always** goes to `creatives/`, split by type, never inside the project folder: video (reels, stories, shorts, YouTube) in `creatives/reels/<slug>-<preset>.mp4` (e.g. `creatives/reels/juros-compostos-ig-stories.mp4`), carousel in `creatives/carrossel/<slug>-<preset>/`, static post in `creatives/post/<slug>-<preset>.png`. `creatives/demos/` holds the skill's demos and `creatives/registro.md` the history (local, created from `assets/registro.template.md` on the first video). `<preset>` comes from `assets/platforms.json`. More than one format → the project gets a `video-<preset>/` folder per extra format, same narration.

Scripts use `uv run` (inline dependencies, nothing installed globally). Script path: this skill's directory + `scripts/`.

### Asset library: search before generating

Fonts, SFX, music, voice takes, icons, logos, flags and images already produced are indexed in `projects/_library.json`. **Before downloading, synthesizing or generating any of them** (step 4 fonts/symbols, 5 voice, 7 SFX), search the history and reuse:

```bash
uv run scripts/asset_library.py find --kind sfx whoosh            # kinds: font sfx music voice voice-ref icon logo flag image
uv run scripts/asset_library.py get <id|termo> --to projects/<slug>/video/assets/icons   # copies + CREDITS.md line
uv run scripts/asset_library.py scan                              # after creating a new asset, and at the end of each project
```

Only generate when the search finds nothing or what exists does not fit (style, duration, color). Logo: check it is still the current one. Voice: only reuse a take with the **same final text** (`find --kind voice` shows the text); a take with "tu" or an old script does not count. Only raw assets come in: composition, layout and storyboard of old projects stay out (they are not templates).

## Output: video or carousel (the flag)

`output: video` (default) or `output: carrossel`. Turns the carousel on: "carrossel"/"carousel"/`--carrossel` in the request, a "Carrossel" format coming from the user's calendar, or "também em carrossel" (then both come from the same brief). Informative content, step by step, data or marketing campaign → recommend a carousel; story and motivational → video. **A carousel has no narration**: skip steps 5 (voiceover/timeline) and 7 (sound); step 6 becomes a static layout and step 8 becomes slide export. Everything is in `references/carousel.md`: **Claude Design** engine when the agent has it (Claude with Artifact, Design type, one artboard per slide), local engine (works in any agent) `scripts/dc_to_carousel.py` + `scripts/render_carousel.py` (PNG/PDF from the same `.dc.html`), presets `ig-carousel` / `ig-carousel-square` / `linkedin-carousel`, output in `creatives/carrossel/<slug>-<preset>/`. The cover follows `references/hooks.md`: 5 hooks with a trigger, the gap test, and each slide pulls the next.

## Reference styles

Reference video sent by the user → analyze it with `bash scripts/analyze_reference.sh <video> training/referencias/ref-NN <lang>`, **look** at the contact sheets and frames and write the recipe in `references/styles/<nome>.md` (catalog in `references/styles/README.md`). Request "no estilo X" → read the recipe and apply its grammar (structure, timing, components) with the user's brand, text and numbers. Saved styles: the `.md` files in `references/styles/` (except `README.md` and `_template.md`); the repository ships none, each person creates their own from their own references.

## Step 0: Brief (input, genre, platform)

Read `references/inputs-and-genres.md` and `references/platforms.md`. Classify four things before anything else (plus the output, above):

1. **Input mode**: `roteiro` (the user's text or script, including "narra isso": **always adapted for video**, keeping facts, intent and voice), `narracao-literal` (only when the user explicitly asks "usa exatamente", "ao pé da letra", "não muda nada"), `notas`, `tema`, `fonte-longa` (PDF/article/URL), `dados`, `audio-gravado`, `video-gravado` (video of someone speaking: speech and image are the base), `codigo` (a product's repository: facts, screens and brand come from the code). The mode decides which steps run (table in `inputs-and-genres.md`).
2. **Genre**: story, motivational, technical, explainer, data/news, product, opinion. Drives structure, voice pacing, visual direction, dictionary effects and music.
3. **Platform(s)**: preset from `assets/platforms.json` (`ig-stories`, `ig-reels`, `ig-feed`, `fb-reels`, `tiktok`, `yt-shorts`, `yt-long`, `linkedin`, `square`). "Story" → `ig-stories`; "Reels", "TikTok", "Shorts" or a vertical video with no platform → **`vertical`** (the most restrictive zone of the three; one render serves all and is delivered as `-ig-reels.mp4` **and** `-tiktok.mp4`, plus `-yt-shorts.mp4` if asked); "YouTube" without saying Shorts → `yt-long`. `uv run scripts/platform_preset.py <preset>` shows canvas, safe zone, default duration and limits.
4. **Duration**: a parameter of the request ("30 s", "1 minuto", "até 45 s"). When given, it is the target: the script is written or adapted to fit it (±10%). Without a duration, use the preset's `default_duration` (Reels/TikTok 30 s, Stories 15 s, Shorts 40 s, YouTube 90 s, LinkedIn 45 s). Duration above the platform maximum: warn and offer to split into parts.

Collect the rest (ask only what cannot be inferred; a sensible default when reversible), write it to `brief.md` and keep the original input in `source/`:

| Field | Default |
|---|---|
| Input mode | inferred from what arrived; user text = `roteiro` (adapt), unless verbatim is explicitly requested |
| Genre | inferred from the text/request |
| Platform | `ig-reels` |
| Audience and tone of voice | whatever comes in the request, the product's code or the recorded speech; otherwise the natural tone of the genre and platform (do not look for a persona in other projects) |
| Brand | see "Brand, voice and tone"; source recorded in `brief.md` |
| Target duration | the request's; otherwise the preset's `default_duration` (`narracao-literal`: whatever the text takes) |
| Voiceover language | the request's language (see "Language"); pt-BR for a Portuguese request |
| Voice provider | see step 5 |
| Brand | only if the request brings it (site, brand kit, "na minha identidade"); no brand → palette and typography come from the central idea |

User text much longer or shorter than the target duration? Adapt it (condense or develop) and show what changed. In `narracao-literal` that exceeds the platform maximum: warn and offer to split into parts or change platform; never cut silently.

Long sources (a 90-page PDF): read everything and extract **takes** (surprising numbers, contrasts, trends, quotes) with the source page. Loose topic: research on the web (the agent's search tool) and record the sources. Wrong numbers destroy credibility.

## Step 1: Narrative format (the step everybody skips)

`narracao-literal` and `audio-gravado` skip this step. In `roteiro`, identify the format the text already has and test whether another format tells the same thing better (compact: 2–3 candidates).

Before writing a line, test the same content in several formats and pick one. Read `references/narrative-formats.md` (experiment, tutorial, comparison, listicle, ranking, transformation, myth × truth, prediction, behind the scenes, character story).

Combine with the genre ("genre × format" table in `inputs-and-genres.md`). For each candidate format (at least 4): angle in one sentence, central tension, why it holds attention, risk. Pick one and justify it. Comparison and transformation usually win with data because they create tension; a list of loose statistics holds nobody.

## Step 2: Script

`roteiro` (the default for user text): **adapt it for video**. The user's text is raw material, not the final voiceover. Keep facts, intent, names and the sentences that carry the user's voice; adjust the rest for: the target duration (word budget below), a hook in the first 2 seconds, the ear (short sentences, spoken numbers), an ending chosen by intent and whatever the central idea asks for (e.g. open in silence, let the image say a sentence instead of the voice). Never invent facts. Record in `plan.md` the original and the adapted text side by side, with the reason for each relevant change.

`narracao-literal` (only on explicit request): narration = the user's text word for word. Only speech adjustments (numbers spelled out, pronounceable acronyms) in a separate `narration.tts.txt`; the screen uses the original spelling.

**Word budget**: words ≈ duration × genre pace (2.0–2.3 words/s motivational and story, 2.5 explainer, 2.6–2.8 data, technical and promo), minus the seconds the central idea reserves for image without speech. E.g. a 30 s story Reels with a 3 s silent opening ≈ 27 × 2.3 ≈ 60 words. (Measured pace varies by voice: check after step 5.)

Other modes: read `references/script-writing.md`. Core rules:
- Write in the **user's tone of voice**. If a script/tone skill of theirs exists, use it. If not, offer to create one from old scripts (via skill-creator).
- **3 alternative hooks** (the first 3 s decide), each with a trigger from `references/hooks.md` and a score on the gap test. Recommend the highest score. A hook that only informs (gives away the conclusion) fails.
- Write for the ear: short sentences, rounded spoken numbers ("quase 9 em cada 10"), one idea per sentence.
- Genre structure (`inputs-and-genres.md`); default: hook → minimal context → tension/turn → payoff → ending by intent (`script-writing.md`; not every video ends in a question or a lesson).
- Count words and check them against the target-duration budget. After the voiceover (step 5), if the voice lands outside ±10% of the target, adjust the text and generate again (or adjust the voice speed between 0.9 and 1.1).

## Step 2.5: Central idea (what keeps the video from looking like all the others)

Read `references/concept.md` and `references/quality-bar.md`. Find the script's mechanism (what the viewer should feel, where it turns, what is concrete), write **3 central ideas** that diverge on at least 4 axes (device, technique, camera, light and palette, role of the text, time structure, relationship with the viewer), read `creatives/registro.md` and veto the ones that repeat previous videos. Pick one, defend it in `plan.md` (section "Central idea") and only then do the storyboard. Do not ask the user which one they prefer: decide and explain at delivery.

## Step 3: Storyboard

Read `references/storyboard.md`. Break the script into scenes at the platform's pace (Reels/TikTok/Shorts: visual change every 1.5–3 s; Stories: one card per idea, 5–15 s; horizontal YouTube: 3–6 s), **all inside the central idea's device** (or a transformation of it). For each scene: the exact narration excerpt, visual, entrance/emphasis/exit motion, the anchor word that fires the emphasis, transition, SFX, on-screen text.

Each scene's `motion` field uses the terms of `references/motion-dictionary.md` with duration and ease. Think like a motion designer: **the visual demonstrates what the voice says** (voice says "100 maiores empresas" → a grid of 100 squares lighting up). Never just "text + icon".

**Visual map (support, inside the central idea)**: read `references/visual-mapping.md`. It resolves the details of each sentence (which flag, which logo, which number), which enter as objects of the idea's world, not as a loose icon in the middle of the screen. Read each sentence in five layers (entities, concrete, number, idea, tone) and pick **one main visual** by the ladder: real symbol (flag, logo, medal) → concrete object (line icon or illustration/silhouette) → free photo → data visual → the piece's abstract metaphor → typography. Record the "Visual map" table in `plan.md` (excerpt, reading, visual, rung, command, why) and the items in each scene's `icons`. Test: without the audio, does the image still tell what the sentence says? Concept → icon lexicon in `assets/visual-lexicon.json`; search, style and licenses in `references/iconography.md`.

Deliver `plan.md` (structure in `assets/plan.template.md`: formats + choice, script, 3 hooks, storyboard), `narration.txt` (only the spoken text) and `storyboard.json` (schema in `assets/storyboard.schema.json`, example in `assets/storyboard.example.json`). `plan.md` must be self-sufficient: another agent can produce the video from it alone.

**Review gate:** show the plan and ask for approval before spending voice/render credits. If the user asked for "faz tudo direto" (do it all), proceed and record that the gate was skipped.

## Step 4: Visual identity

Read `references/brand-and-motion.md`. The visual direction (palette, typography, texture, layout) comes from the central idea; the user's brand only when the request brings it, and then it goes on top of the idea as color and font, without imposing layout. Download the symbols listed in the storyboard (first, `asset_library.py find` for fonts and symbols that already exist) with `uv run scripts/fetch_icon.py <flag|icon|logo|image> <termo> --out projects/<slug>/video/assets/icons` (records the license in `CREDITS.md`; for images, list candidates, **look** and pick with `--pick`; check the logo is the current one). If there is a website: open it (the agent's web tool or `curl` for CSS/text; a browser for screenshots if available), extract palette, fonts (Google Fonts when possible), border radius, icon style, tone. Write `brand.json` (format in `assets/brand.example.json`). No brand: choose an intentional visual direction and record it.

## Step 5: Voiceover first, then sync

The voiceover comes **before** the animation: with the audio ready, every word has a timestamp and the scenes anchor to it. Read `references/voiceover.md` to choose a provider:

1. **Higgsfield MCP** if connected (voices you can hear in the chat; model aggregator).
2. **ElevenLabs** (`with-timestamps` API or MCP): best quality, native timestamps.
3. **edge-tts**: free, good pt-BR (`pt-BR-FranciscaNeural`, `pt-BR-AntonioNeural`), no key; for another output language pick a voice in that language:
   ```bash
   uv run scripts/tts_edge.py --text-file projects/<slug>/narration.txt --voice pt-BR-FranciscaNeural --out projects/<slug>/audio
   ```
4. Audio without timestamps (Higgsfield, the user's recording) → align with Whisper:
   ```bash
   uv run scripts/align_words.py projects/<slug>/audio/voice.mp3 --lang pt --out projects/<slug>/audio/words.json
   ```

Then anchor the storyboard to the speech:
```bash
uv run scripts/build_timeline.py projects/<slug>/storyboard.json projects/<slug>/audio/words.json --fps 30 --out projects/<slug>/timeline.json
```
It matches each scene's narration excerpt to the words, generates `start/end` in seconds and frames, and resolves each emphasis's `anchor_word`. Review matching warnings (word not found = the script diverged from the speech).

## Step 6: Animation

Read `references/engines.md` and choose:

| Situation | Engine |
|---|---|
| Default, dynamic Reels, the agent writing free HTML/CSS/GSAP | **HyperFrames** (`npx skills add heygen-com/hyperframes`) |
| Existing React project, componentized data/charts, word-by-word captions, rendering at scale/Lambda | **Remotion** (`npx skills add remotion-dev/skills`) |
| Technical/math explainer, procedural animation | Motion Canvas |

If the engine's official skill is installed, **load it**: it has the up-to-date API rules. This skill gives direction; the engine's gives syntax.

### Live preview (optional)

**Off by default.** Only open the Studio when:
- the request asks for it ("quero ver ao vivo", "abre o preview", "me mostra montando", "abre no Studio", "I want to watch it live"); or
- the user wants to point on screen at what to change ("vou te mostrar no Studio", "abre que eu aponto"); or
- you are inside the `tools/studio` interface (`MOTION_CENA_UI=1`): there the interface itself starts the preview; you just do not open a browser.

Without any of these, do not start a preview server or open a browser, not even at the end: the "Open the final Studio preview" step of the `hyperframes-cli` skill does not apply here. Visual review comes from snapshots and the contact sheet (steps 6 and 8), and the MP4 path goes in the delivery. At the end, offer it in one line ("quer abrir no Studio para ajustar à mão?", in the user's language).

When it is on: as soon as `projects/<slug>/video/index.html` exists (even with just the background and the first scene), open the Studio and keep it open until delivery. It reloads on every saved file, so whoever asked watches the video being built:

```bash
cd projects/<slug>/video
npx hyperframes preview --status --json        # one already running? use its studioUrl
npx hyperframes preview --background ${MOTION_CENA_UI:+--no-open}  # otherwise: start it and open the browser (not inside the motion-cena interface)
npx hyperframes preview --status --json        # gets the studioUrl (http://127.0.0.1:<port>/#project/video)
```

- On: send the `studioUrl` to the user **right away**, before continuing to animate. Inside `tools/studio` (`MOTION_CENA_UI=1`) the preview shows up by itself next to the chat; no browser needed.
- On: build **scene by scene** and save after each one (layout, then entrance, then emphasis) instead of writing the whole HTML at the end: every save becomes a visible step.
- A request pointing at something in the Studio ("muda isso", "esse texto") → `npx hyperframes preview --context --json --context-fields selection` tells what was clicked (file, element, time).
- Do not start a second server for the same project. At the end, leave it running and say how to stop it (`npx hyperframes preview --stop`).

Animation rules (details in `references/brand-and-motion.md`; effect terms → recipe and defaults in `references/motion-dictionary.md`):
- A request in the form **effect + duration + ease + target** ("slide in 0,4 s ease out no título") is a literal instruction: translate it through the dictionary, without reinterpreting.
- Timing comes from `timeline.json`: never guess times. Emphasis fires on the `anchor_word` frame.
- Something always moves: subtle continuous motion (drift, scale 1.00→1.04) even in static scenes.
- Ease-out for entrances, ease-in for exits, springs for "physical" elements. Nothing linear except counters.
- Canvas, fps and **safe zone come from the preset** (`uv run scripts/platform_preset.py <preset> --css` generates the `--safe-*` variables; for vertical use `vertical`): text, numbers, icons, cards, charts and logo never in the UI zone, **not even partly** (the right side of TikTok/Shorts has 192 px of buttons). Build the layout inside a container with `inset: var(--safe-top) var(--safe-right) var(--safe-bottom) var(--safe-left)`; only background, texture and decoration with `data-safe-ignore` bleed out. Center the content on the canvas's horizontal center: a block of title + number counts as one group and is centered as a group. Text sizes per canvas in the "Adapting the layout to the canvas" table of `references/platforms.md` (vertical: title 90–160 px, body ≥ 56 px, ≤ 6 words on screen).
- Numbers count up to the value; they do not appear ready.
- Each visual of the map enters on the word that names it (flag `pop in`/`mask reveal`, medal `pop in` + `glow`, silhouette `slide in`, logo a sober `fade in`); real symbols in their original colors, never redrawn; icons and silhouettes in the brand color.
- Burned-in captions are optional (ask; muted autoplay is common, so the default is on; on LinkedIn, always).
- Several formats: compose the main one, get approval, then recompose each extra preset in `video-<preset>/` reusing `timeline.json` (same narration and timing; layout changes).

Before the final render, **measure the safe zone** (opens the composition, steps the timeline every 0.25 s and measures the real box of every text and image):
```bash
uv run scripts/safe_zone_check.py projects/<slug>/video --preset vertical
```
Zero ERRO is mandatory (ERRO = something held ≥ 0.5 s in the zone; aviso = a quick entrance/exit pass, check it). Then take snapshots of key frames (`npx hyperframes snapshot --at <middle of each scene>`), **look at the images** and fix before the final render.

## Step 7: Sound

Read `references/sound-design.md`. From `timeline.json`, build the cue list (whoosh on transitions, pop/click on appearances, riser before reveals, impact on the key number). Sources (first `asset_library.py find --kind sfx <tipo>`): ElevenLabs Sound Effects, Higgsfield, the local library, or synthesized with `scripts/synth_sfx.py` (free, offline). Mix:
```bash
uv run scripts/mix_audio.py projects/<slug>/timeline.json --voice projects/<slug>/audio/voice.mp3 --sfx-dir projects/<slug>/audio/sfx --music <optional> --out projects/<slug>/audio/mix.wav
```
Voice always on top; music ducked (−18 to −22 dB under the voice); final loudness −14 LUFS (social media). Place each SFX by the visual event it marks, compensating the file's peak (a whoosh peaks ~0.25 s in, a riser should end on the impact).

## Step 8: Render and QA

Render with the engine's CLI straight to `creatives/reels/<slug>-<preset>.mp4` (HyperFrames: `npx hyperframes render -o ../../../creatives/reels/<slug>-<preset>.mp4` from inside `projects/<slug>/video/`), then:
```bash
QA_DIR=projects/<slug>/out bash scripts/qa_video.sh creatives/reels/<slug>-<preset>.mp4 <preset>
```
Vertical: render once as `<slug>-ig-reels.mp4`, copy to `<slug>-tiktok.mp4` (same file; the `vertical` zone already covers TikTok) and run the QA of each with its own preset. The contact sheet comes out with the UI zone painted red and the free-area border: nothing that matters can be in the red.
It checks resolution, fps and maximum duration against the preset (you check the duration against the target, ±10%), audio present, loudness, and generates a contact sheet (`projects/<slug>/out/<slug>_contact.jpg`). **Open the contact sheet** and go through `references/qa-checklist.md` and `references/quality-bar.md`. Fix and re-render; never deliver without looking.

## Delivery

Add the video's line to `creatives/registro.md` (device and axes). Report, in the user's language: path of each MP4 (`creatives/reels/<slug>-<preset>.mp4`), platform/preset, duration (target and actual), input mode and genre, what changed in the user's script and why, central idea (and the 2 discarded, one line each), narrative format and why, hook used (and alternatives), voice provider, what was left out and why, and iteration suggestions (e.g. "version without SFX", "hook B"). Horizontal YouTube: include a thumbnail suggestion (1280×720) and chapters if > 3 min. Targeted iterations ("só adiciona SFX", "troca hook", "faz versão pra story") reuse earlier steps; do not redo everything.

## Quick mode

A short request ("faz um reels sobre X", "narra esse texto pra story") still goes through steps 1–3, including the central idea, only compact, in a single `plan.md`; the user's text is adapted to the duration. Skipping the central idea and the storyboard is what makes the video generic. Ready-made prompts for the user in `references/prompts.md`.
