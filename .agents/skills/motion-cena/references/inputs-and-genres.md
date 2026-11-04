# Inputs and genres

The system does not depend on an article or a website. Anything that tells an idea can become a video. Two questions set the path: **what the user delivered** (input mode) and **what kind of video it is** (genre).

## Input modes

Identify the mode in Step 0 and record it in `brief.md` (`input_mode`). Each mode skips or keeps different steps:

| Mode | The user sends | What to do | Steps |
|---|---|---|---|
| `roteiro` | The user's own text or script, finished or draft ("narra isso", "esse é o texto do vídeo", a script in running bullet points) | **Adapt it for video**: keep facts, intent, names and the sentences in their voice; adjust for the target duration, hook, the ear, ending and central idea; original × adapted in `plan.md` | 1 compact; 2 as an adaptation; 2.5 onward |
| `narracao-literal` | Explicit request to use the text exactly ("usa exatamente", "ao pé da letra", "não muda nada") | Narration = literal text; only speech adjustments, in a `narration.tts.txt` | 1 and 2 skipped; 2.5 onward |
| `notas` | Topics, bullets, a loose idea, a transcript of a WhatsApp voice message | Organize it into a story; choose the format; write the script in the user's tone | 1–3 in full |
| `tema` | Just the subject ("faz um vídeo sobre juros compostos") | Research on the web (the agent's search tool) to get verifiable facts; note the sources; then proceed as `notas` | research + 1–3 |
| `fonte-longa` | PDF, report, article, URL, book | Read all of it, extract **takes** with page/origin | 0 (takes) + 1–3 |
| `dados` | Spreadsheet, CSV, numbers | Find the story in the numbers (contrast, trend, record); give each number its own visual | 1–3, comparison/forecast format |
| `audio-gravado` | Audio with someone's voice (the user's or someone they name) | `align_words.py` → `words.json`; narration = reviewed transcript; the voice is not re-recorded; tone and vocabulary come from the speech | 3 onward, Step 5 alignment only |
| `video-gravado` | Video of someone talking (talking head, talk, interview, podcast) | Extract the audio (`ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 audio/voice.wav`), align it with `align_words.py`; the recorded footage is the base and the motion goes on top (captions, keyword, cards, cuts). For plain captions follow `.agents/skills/embedded-captions/SKILL.md`; for cards over the speech, `.agents/skills/talking-head-recut/SKILL.md` (both are large: list their headings with `grep -n '^#'` and read only the sections you need). Voice and tone belong to the speaker; do not re-record | 3 onward; Step 5 alignment only; Step 6 composes over the video |
| `codigo` | Path or repository of a product ("analisa o app em ../loja e faz um reels") | Read the README, routes, screens, copy and theme; take facts, function names and real screens from the code (nothing invented) and the brand from the theme (`brand-and-motion.md` → "Extract the brand from code"). Screenshots: run the app if possible, otherwise rebuild the screen from the components. Never use `.env`, keys or production data | 0 (code reading) + 1–3 |

Default for any user text: `roteiro` (adapt). Literal only on explicit request; do not ask.

### The user's script: how to adapt

- What stays: facts, numbers, names, the intent (what they want to stick) and the sentences that sound like them.
- What changes: length (word budget for the target duration, `SKILL.md` Step 2), the first sentence (hook in the first 2 s), long sentences or sentences written for reading, endings added out of habit, and passages that the central idea's image says better without speech.
- AI jargon in their text (`lint_copy.py`): replace it during adaptation and say what you replaced.
- Never invent a fact, number or event that is not in the text or in a verified source.
- In `plan.md`: original and adapted side by side, with the word count and estimated duration of each.

### Literal narration: precautions

- The concatenation of the scenes' `narration` = the user's text, word for word (`build_timeline.py` warns if it diverges).
- AI jargon: point it out and suggest changes; the user decides.
- Speech adjustments go in a separate `narration.tts.txt` (e.g. "R$ 1.500" → "mil e quinhentos reais"); the screen shows the original spelling.
- Over the platform maximum? Offer to split it into parts or switch platform. Never cut silently.
- Estimated duration: words ÷ 2.5 (natural pt-BR) or ÷ 2.8 (Reels pace).

## Genres

Record `genre` in the brief (the id in backticks in the table). The genre sets the structure, voice pace, visual direction, motion dictionary terms (`references/motion-dictionary.md`) and music.

| Genre | Structure | Pace / voice | Visual and motion | Sound |
|---|---|---|---|---|
| **story** (`historia`; storytelling, case, journey) | hook on the conflict → character → obstacle → turn → ending (final fact/image; lesson only if the video wants to teach; question only if requested, see "Ending" in `script-writing.md`) | 2.3–2.5 words/s, pauses before the turn | recurring visual metaphor; a character/icon that crosses scenes; match cut, slow push-in, mask reveal; light/color changes at the turn | narrative music building up; riser before the turn |
| **motivational** (`motivacional`; manifesto, reflection) | shock line → recognizable pain → reframe → call to action | short sentences, 2.0–2.3 words/s, silence as breathing room | large kinetic typography (slam, line reveal, word reveal), 1 idea per screen, strong contrast, punch zoom on the peaks; few objects | emotional/epic track with a build; impact on the peaks; strong ducking |
| **technical** (`tecnico`; tutorial, how-to, code, tool) | result first → numbered steps → common pitfall → recap | 2.5–2.8 words/s, clear and neutral | UI mockups, code with typewriter/highlight, draw-on arrows, zoom into detail (coordinate-target-zoom), large numbering; no effect that gets in the way of reading | subtle track; click/tick on the steps |
| **explanatory** (`explicativo`; concept, "how it works", educational) | question → intuition via analogy → mechanism in 2–3 parts → example → synthesis | 2.5 words/s | diagram that assembles itself (draw-on, stagger, morph), recurring visual analogy, labels that come in after the object | light, curious track; pops on each piece |
| **data / news** (`dados`) | hook number → context → contrast → implication | 2.6–2.8 words/s | count-up, bar grow, highlight the data point, dim the rest (opacity 0.25), side-by-side comparison | tense/neutral track; impact on the key number |
| **product / promo** (`produto`) | pain → product as the solution → 3 benefits → proof → CTA | 2.8 words/s, energetic | pop in, stagger of benefits, punch zoom on the product, wipe in the brand color | upbeat track on the beat; whoosh on transitions |
| **opinion / analysis** (`opiniao`) | thesis → 2–3 arguments → objection → conclusion | 2.5 words/s, firm voice | large key text, split screen for the sides, myth × truth with a stamp | minimal track |

Mixing is normal (technical + story = "how I solved X"). Choose the dominant genre and note the secondary one.

### Genre × narrative format

The genre sets the **tone**; the format (`references/narrative-formats.md`) sets the **packaging**. Combinations that usually work:

- story → character story, transformation, behind the scenes
- motivational → myth × truth, transformation, open question (and the **manifesto** format: a sequence of short statements that escalate to a final line)
- technical → tutorial, experiment, listicle
- explanatory → open question, comparison, tutorial
- data → comparison, forecast, ranking
- product → transformation, experiment
- opinion → myth × truth, comparison, ranking

In `roteiro` the text suggests the format; test whether another one tells it better. In `narracao-literal` the format is already given: identify it and use it only to guide the central idea and the storyboard.

## Output

Video (default) or carousel (`references/carousel.md`). In a carousel the input mode still applies, but the script becomes **supporting text for the slides**: adapt the user's sentences for reading, one idea per slide, and cite the source on the last one. No TTS.

## Platform

Ask or infer the platform (story, reels, TikTok, Shorts, YouTube, LinkedIn) and use the preset from `references/platforms.md`. It changes the canvas, safe zone, maximum duration and pace:

- **Stories**: 5–15 s cards, one idea per card, CTA on the last one; long text → a series of stories.
- **Reels / TikTok / Shorts**: hook in the first 2 seconds, visual change every 1.5–3 s, captions on.
- **Horizontal YouTube**: can breathe more (change every 3–6 s), short intro, chapters if > 3 min, thumbnail.
- **LinkedIn**: sober tone, captions always (muted autoplay), 30–90 s.

Request with several platforms: produce the main one, then recompose the others with the same narration (see "One story, many formats" in `platforms.md`).
