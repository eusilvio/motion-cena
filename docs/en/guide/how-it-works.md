---
title: From request to MP4
description: The pipeline steps, the file each one writes, the review before spending credits and the sync with the speech.
---

# From request to MP4

The method is **input, format, script, central idea, scenes, video**, in that order. Every step writes a file the next one consumes, and the storyboard is the contract between the story and the animation. The heavy lifting is direction: which story, which format, which visual idea, what each scene shows. Animating is the easy part.

## The steps and what each one writes

Everything lives in `projects/<slug>/`, one folder per project, out of git.

| Step | What happens | Writes |
|---|---|---|
| **0. Brief** | classifies the input mode, the genre, the platform and the duration; keeps the original material | `brief.md`, `source/` |
| **1. Narrative format** | tests the content in at least 4 formats (comparison, transformation, listicle, myth × truth and others) and picks one | `plan.md` |
| **2. Script** | writes or adapts the text to the duration, with 3 alternative hooks; in verbatim mode, uses your text word for word | `plan.md`, `narration.txt` |
| **2.5. Central idea** | proposes 3 different visual devices, vetoes the ones that repeat earlier videos and picks one | `plan.md` |
| **3. Storyboard** | breaks the script into scenes: spoken excerpt, visual, motion, anchor word, transition, sound effect | `plan.md`, `storyboard.json` |
| **Review** | shows the plan and waits for your approval | |
| **4. Visual identity** | palette, fonts and rhythm from the central idea and the brand, if the request brings one; downloads the symbols with their licenses | `brand.json`, `video/assets/` |
| **5. Voiceover** | generates the voice with a timestamp per word and anchors the scenes to the speech | `audio/voice.mp3`, `audio/words.json`, `timeline.json` |
| **6. Animation** | builds the composition in HyperFrames and measures the safe zone | `video/` |
| **7. Sound** | places the effects along the timeline and mixes voice, effects and music | `audio/sfx/`, `audio/mix.wav` |
| **8. Render and QA** | renders, checks canvas, fps, duration, codec and loudness, and generates the contact sheet | `creatives/reels/<slug>-<preset>.mp4`, `out/` |

At the end, the agent adds a line to `creatives/registro.md` with the central idea and the video's visual axes. That log is what it checks in step 2.5 so it does not repeat a concept.

In a carousel, steps 5 and 7 do not exist: step 6 becomes a static layout and step 8 becomes slide export. See [Carousel](/en/reference/carousel).

## The review before spending credits

After the storyboard, the agent stops and shows `plan.md`: the formats it tested and the one it chose, the script next to your original text (with the reason for each change), the 3 hooks, the central idea with the two discarded ones and the storyboard. Only with your approval does it spend voice credits and render time.

`plan.md` is self-sufficient: another agent can produce the video from it alone. If you ask it to *"do it all in one go"*, the review is skipped, and the plan records that.

## The speech sets the timing

The voiceover comes **before** the animation. With the audio ready, every word has a timestamp:

```json
[{"word": "quase", "start": 0.12, "end": 0.41}, ...]
```

`build_timeline.py` matches each scene's narration excerpt to those words (ignoring accents, punctuation and case) and generates `timeline.json`, with the start and end of each scene in seconds and in frames. Every emphasis in the storyboard has an anchor word, and the effect fires on the frame where that word is spoken.

```bash
uv run .agents/skills/motion-cena/scripts/build_timeline.py projects/<slug>/storyboard.json projects/<slug>/audio/words.json --fps 30 --out projects/<slug>/timeline.json
```

The voice can come from three places:

- **edge-tts**, free and keyless, with native timestamps;
- **ElevenLabs**, with a key in `.env.local`, native timestamps and voice cloning;
- **audio without timestamps** (your recording, another service), which goes through `align_words.py` (Whisper) to get the time of each word.

If the voice lands more than 10% off the requested duration, the agent adjusts the text and generates it again, or changes the speed between 0.9 and 1.1.

## Animation and checks

The default engine is HyperFrames: HTML, CSS and a paused GSAP timeline that the renderer steps through frame by frame. Remotion and Motion Canvas are alternatives described in the skill, for when you already have a React project or want a technical explainer.

Before the final render, two checks:

- `safe_zone_check.py` steps through the video every 0.25 s and fails whatever stays in the interface zone (see [Platforms and safe zones](/en/reference/platforms));
- `snapshot_sheet.py` tiles key frames into a single image, which the agent looks at before rendering.

After the render, `qa_video.sh` checks resolution, fps, maximum duration, codec, audio and loudness (−14 LUFS), and generates the contact sheet with the zone painted in. The agent opens that image and goes through the QA checklist before delivering.

## Revisions redo only what changed

Since every step lives in a file, *"switch the hook"* redoes the first scene's voice, the timeline and the render; *"drop the music"* redoes only the sound and the render; *"make the story version"* recomposes the layout in `video-ig-stories/` with the same narration. The scripts behind each step are listed in [Scripts](/en/reference/scripts).
