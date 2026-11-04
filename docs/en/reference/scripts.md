---
title: Scripts
description: Every script in .agents/skills/motion-cena/scripts, what it does and an example command.
---

# Scripts

The skill's scripts live in `.agents/skills/motion-cena/scripts/`. The agent calls each one at the right step, but they all run by hand too. The Python ones run with `uv run` and declare their dependencies in the file itself (a `# /// script` block), so nothing is installed system-wide. The `.sh` ones run with `bash`.

The examples below run from the repository root. Every script accepts `--help`.

## Summary

| Script | Step | Does |
|---|---|---|
| `platform_preset.py` | brief, animation | shows the platform presets and generates the safe-zone CSS variables |
| `registro.py` | central idea | summarizes the log of delivered pieces to veto a repeated concept |
| `motion_lookup.py` | storyboard, animation | searches the 388-effect catalog |
| `fetch_icon.py` | visual identity | downloads a flag, logo, icon or freely licensed image with its license |
| `asset_library.py` | identity, voice, sound | finds and reuses what was already produced |
| `tts_edge.py` | voiceover | free voice through edge-tts, with a timestamp per word |
| `tts_elevenlabs.py` | voiceover, sound | voice, cloning and sound effects through ElevenLabs |
| `tts_chatterbox.py` | voiceover | cloned voice running locally, on the CPU |
| `align_words.py` | voiceover | per-word timestamps for any audio (Whisper) |
| `isolate_voice.py` | voiceover | removes music and noise from a recording |
| `build_timeline.py` | voiceover | anchors the scenes to the spoken words and generates `timeline.json` |
| `find_words.py` | voiceover, animation | tells when a phrase is spoken, without opening `words.json` |
| `snapshot_sheet.py` | animation | tiles key frames of the composition into a single image |
| `safe_zone_check.py` | animation | fails whatever enters the interface zone |
| `synth_sfx.py` | sound | kit of 9 synthesized sound effects, offline |
| `mix_audio.py` | sound | mixes voice, effects and music at −14 LUFS |
| `qa_video.sh` | render | checks the MP4 and generates the contact sheet |
| `dc_to_carousel.py` | carousel | turns Claude Design artboards into a local composition |
| `render_carousel.py` | carousel | exports one PNG per slide, a contact sheet and a PDF |
| `lint_copy.py` | script, delivery | flags AI-sounding text (pt-BR) |
| `analyze_reference.sh` | styles | breaks a reference video into sheets, speech and loudness |

## Platform and direction

### platform_preset.py

Reads `assets/platforms.json`. With no argument it lists the presets; with a preset, it shows canvas, fps, durations and safe zone. `--css` prints the `--safe-*` variables for the composition, `--shell` prints variables for bash and `--json` the whole preset.

```bash
uv run .agents/skills/motion-cena/scripts/platform_preset.py vertical --css
```

The [safe-zone playground](/en/reference/platforms) shows the same output for each preset.

### registro.py

A compact summary of `creatives/registro.md`, the log of delivered pieces, to veto a central idea that repeats earlier videos without reading the whole file. `--recent N` shows the last N rows, `--counts` the most used values on each visual axis.

```bash
uv run .agents/skills/motion-cena/scripts/registro.py --counts
```

### motion_lookup.py

Searches the effects catalog by term, Portuguese name or alias, ignoring accents and case. It also filters by family, genre and intensity. The agent never reads the catalog's JSON files whole: it asks this script.

```bash
uv run .agents/skills/motion-cena/scripts/motion_lookup.py "texto hacker" --brief
uv run .agents/skills/motion-cena/scripts/motion_lookup.py --family enfase --genre dados --intensity sutil
```

`--validate` checks the schema and cross references (it runs in CI) and `--write-index` regenerates the index. The same catalog is in the [effects explorer](/en/effects).

## Symbols and reuse

### fetch_icon.py

Downloads real symbols (flags, official logos), line icons and freely licensed images, and records source and license in the folder's `CREDITS.md`. It never redraws a real symbol and does not offer emoji.

```bash
uv run .agents/skills/motion-cena/scripts/fetch_icon.py flag br --out projects/<slug>/video/assets/icons
uv run .agents/skills/motion-cena/scripts/fetch_icon.py icon medal --weight fill --color "#D4A72C" --out projects/<slug>/video/assets/icons
```

For images, `image "<term>"` lists Openverse candidates with their license, and `--pick N` downloads the chosen one.

### asset_library.py

An index of what earlier projects already produced (fonts, sound effects, music, voiceovers, icons, logos, flags, images), so you reuse instead of downloading, synthesizing or paying again. Only raw material goes in; the composition and layout of an old project are not a template.

```bash
uv run .agents/skills/motion-cena/scripts/asset_library.py find --kind sfx whoosh
uv run .agents/skills/motion-cena/scripts/asset_library.py scan
```

## Voice and timing

### tts_edge.py

Free voiceover through Microsoft Edge voices, no key. Writes `voice.mp3` and `words.json` with the time of each word.

```bash
uv run .agents/skills/motion-cena/scripts/tts_edge.py --text-file projects/<slug>/narration.txt --voice pt-BR-FranciscaNeural --out projects/<slug>/audio
```

### tts_elevenlabs.py

ElevenLabs through the official SDK: voiceover with a timestamp per word, voice cloning and sound effects from text. The key comes from `.env.local`. Only clone a voice with its owner's consent.

```bash
uv run .agents/skills/motion-cena/scripts/tts_elevenlabs.py --list-voices
uv run .agents/skills/motion-cena/scripts/tts_elevenlabs.py --text-file projects/<slug>/narration.txt --voice-id <id> --out projects/<slug>/audio
uv run .agents/skills/motion-cena/scripts/tts_elevenlabs.py --sfx "short airy whoosh, clean" --duration 0.5 --out projects/<slug>/audio/sfx/whoosh.mp3
```

### tts_chatterbox.py

A cloned voice with Chatterbox Multilingual (MIT), running locally on the CPU. It needs 10 to 15 clean seconds of the speaker's voice, with consent. It produces no timestamps: run the result through `align_words.py`.

```bash
uv run .agents/skills/motion-cena/scripts/tts_chatterbox.py --text-file projects/<slug>/narration.txt --ref training/voz/ref.wav --out projects/<slug>/audio
```

### align_words.py

Per-word timestamps for any audio, with faster-whisper. Use it for your own recording or for a voice from a service without timestamps. With `--script`, the transcribed words take the script's spelling while keeping their timing.

```bash
uv run .agents/skills/motion-cena/scripts/align_words.py projects/<slug>/audio/voice.mp3 --lang pt --out projects/<slug>/audio/words.json
```

### isolate_voice.py

Removes background music and noise from a recording, locally on the CPU (Demucs and FFmpeg filters). Writes `voice.wav` at 48 kHz mono, ready for the mix.

```bash
uv run .agents/skills/motion-cena/scripts/isolate_voice.py gravacao.mp3 --out projects/<slug>/audio
```

### build_timeline.py

Matches each storyboard scene's narration excerpt to the spoken words and writes `timeline.json`, with start and end in seconds and in frames, the anchor words resolved and the sound effects in absolute time. A word it cannot find becomes a warning: the script drifted from the speech.

```bash
uv run .agents/skills/motion-cena/scripts/build_timeline.py projects/<slug>/storyboard.json projects/<slug>/audio/words.json --fps 30 --out projects/<slug>/timeline.json
```

### find_words.py

When is a phrase said? It queries `words.json` with the same matching as `build_timeline.py`. `--around` lists the words near a time and `--gaps` the pauses, which make good cut points.

```bash
uv run .agents/skills/motion-cena/scripts/find_words.py projects/<slug>/audio/words.json "juro sobre juro"
uv run .agents/skills/motion-cena/scripts/find_words.py projects/<slug>/audio/words.json --gaps 0.6
```

## Visual checks

### snapshot_sheet.py

Takes the requested frames of the composition with HyperFrames and tiles them into one small image, with the time written on each. `--zoom x,y,w,h` crops a region at full resolution, to settle a doubt about a detail.

```bash
uv run .agents/skills/motion-cena/scripts/snapshot_sheet.py projects/<slug>/video 1.2,4.8,9.5,14
```

### safe_zone_check.py

Opens the composition in a headless Chrome, steps the timeline every 0.25 s and measures the real box of every text, image and box with a background. Whatever stays in the zone for 0.5 s or longer is an `ERRO` (error) and the script exits with code 1. How the zone works: [Platforms and safe zones](/en/reference/platforms).

```bash
uv run .agents/skills/motion-cena/scripts/safe_zone_check.py projects/<slug>/video --preset vertical
```

## Sound

### synth_sfx.py

A kit of sound effects synthesized on your machine, with no network: whoosh, pop, tick, click, impact, riser, glitch, ding and beep. `--only` generates just some of them.

```bash
uv run .agents/skills/motion-cena/scripts/synth_sfx.py --out projects/<slug>/audio/sfx --only whoosh,pop
```

### mix_audio.py

Places each effect along the timeline, adds it to the voice, ducks the music under the speech and normalizes loudness to −14 LUFS.

```bash
uv run .agents/skills/motion-cena/scripts/mix_audio.py projects/<slug>/timeline.json --voice projects/<slug>/audio/voice.mp3 --sfx-dir projects/<slug>/audio/sfx --out projects/<slug>/audio/mix.wav
```

More about sound in [Sound](/en/reference/sound).

## Render and QA

### qa_video.sh

Checks the MP4 against the preset: resolution, fps, maximum duration, codec, `yuv420p`, audio present, long silences and loudness. Generates the contact sheet with the zone painted in and the first frame. `QA_DIR` chooses where the images go.

```bash
QA_DIR=projects/<slug>/out bash .agents/skills/motion-cena/scripts/qa_video.sh creatives/reels/<slug>-ig-reels.mp4 ig-reels
```

## Carousel

### dc_to_carousel.py

Turns the Claude Design `.dc.html` artboards into a local HyperFrames composition, so you can export without depending on claude.ai. The brand fonts go in the output folder's `assets/fonts/` before running.

```bash
uv run .agents/skills/motion-cena/scripts/dc_to_carousel.py projects/<slug>/carousel/claude-design/project --out projects/<slug>/carousel/render --preset ig-carousel
```

### render_carousel.py

Exports one PNG per slide, `contact.jpg` for review and, with `--pdf` or on a PDF preset, `carousel.pdf`.

```bash
uv run .agents/skills/motion-cena/scripts/render_carousel.py projects/<slug>/carousel/render --slides 7 --out creatives/carrossel/<slug>-ig-carousel
```

The full flow is in [Carousel](/en/reference/carousel).

## Text and references

### lint_copy.py

Flags AI-sounding pt-BR text: symmetric contrast ("não é X, é Y"), bait questions, dramatic dashes, clichés, jargon and emoji. Reads `.txt`, storyboard `.json`, `.html` and `.md`. An error makes the script exit with code 1. The agent runs it on the script, on-screen text, slides and post caption, and CI runs it on the Portuguese documents at the repository root. It only covers Portuguese for now; for other languages the agent applies the same principles by hand.

```bash
uv run .agents/skills/motion-cena/scripts/lint_copy.py projects/<slug>/narration.txt
```

### analyze_reference.sh

Breaks down a reference video so it can become a style recipe: sheets at 2 frames per second with timecode, three full-resolution frames, the speech with timestamps and the loudness. See [Reference styles](/en/reference/styles).

```bash
bash .agents/skills/motion-cena/scripts/analyze_reference.sh training/referencias/ref-01.mp4 training/referencias/ref-01 pt
```

Changed a script? The PR brings a test in `tests/` and updates the places that mention it. See [Contributing](/en/community/contributing).
