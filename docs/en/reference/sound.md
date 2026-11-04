---
title: Sound
description: Sound effects synced to the animation, the synthesized kit, the ElevenLabs prompts and the final mix.
---

# Sound

Sound effects on the beat of the animation change perceived quality a lot, and they are the first thing people ask for after the first version. So they go in from the first one.

## Cue map

The agent builds the list of effects from `timeline.json`. Each effect marks a visual event:

| On-screen event | Effect | Volume relative to the voice |
|---|---|---|
| scene transition (whip, wipe) | short whoosh, 200 to 400 ms, starting about 150 ms before the cut | −12 dB |
| element appears | soft pop or click | −16 dB |
| staggered items | light ticks, one per item (up to about 8; more than that becomes noise) | −20 dB |
| counter rising | accelerating tick or tonal riser | −18 dB |
| key number revealed | low impact with a little reverb | −10 dB |
| before a reveal | 1 to 2 s riser ending on the impact | −16 dB |
| text being typed | keyboard clicks | −20 dB |
| error or negative | short buzz, glitch | −14 dB |

Less is more: one effect per important action, never over a keyword, all from the same "kit" so the timbres match.

The effect is placed by the visual event it marks, compensating for the file's peak. A whoosh peaks about 0.25 s after it starts; a riser starts earlier and ends exactly on the impact (in the storyboard, `"offset": -1.6`, the riser's duration).

## The synthesized kit

With no key and no network, `synth_sfx.py` generates a kit of 9 effects on your machine: whoosh, pop, tick, click, impact, riser, glitch, ding and beep. It is good enough for the first version.

```bash
uv run .agents/skills/motion-cena/scripts/synth_sfx.py --out projects/<slug>/audio/sfx
uv run .agents/skills/motion-cena/scripts/synth_sfx.py --out projects/<slug>/audio/sfx --only beep,ding
```

## ElevenLabs prompts

With an ElevenLabs key, the effect is generated to order from a text prompt. The file `assets/sfx-prompts.json` holds prompts and durations that already worked in real productions, written generically, each with a note on when to use it: transitions (whoosh, tape rewind), interface (key, error, beep, vibration), objects (stamp, signature, paper, tape, printer, metal), impact, vehicles and ambience (crowd, rain).

```bash
uv run .agents/skills/motion-cena/scripts/tts_elevenlabs.py --sfx "short airy whoosh, clean" --duration 0.5 --out projects/<slug>/audio/sfx/whoosh.mp3
```

::: warning Why the repository ships no audio
ElevenLabs terms forbid publishing the generated audio as standalone files or as a sound library. That is why only the prompts live in the repository: each person generates with their own key into `projects/<slug>/audio/sfx/`, which stays out of git. Never copy those files into the repository.
:::

## Other sources

- Free libraries: Pixabay Sound Effects, Freesound (check whether it is CC0 or CC-BY and credit it when required) and Kenney (CC0, interface sounds).
- Higgsfield, if the connector is enabled in your agent.
- The local library: before generating, the agent searches what was already produced with `asset_library.py find --kind sfx <type>`.

## Music (optional)

A light instrumental bed, 100 to 128 BPM for Reels, from your library, Pixabay Music or generated with ElevenLabs Music. It sits 18 to 22 dB below the voice, is cut at the end of a bar and fades out over 1 s.

## Mix

`mix_audio.py` places each effect in time, applies its gain, adds it to the voice, ducks the music under the speech and normalizes the result to −14 LUFS with a true peak of −1 dBTP:

```bash
uv run .agents/skills/motion-cena/scripts/mix_audio.py projects/<slug>/timeline.json --voice projects/<slug>/audio/voice.mp3 --sfx-dir projects/<slug>/audio/sfx --music trilha.mp3 --out projects/<slug>/audio/mix.wav
```

`mix.wav` becomes the composition's only audio track, so nothing plays twice. Afterwards, `qa_video.sh` checks that the loudness landed between −16 and −12 LUFS and that no silence longer than 1.5 s was left.
