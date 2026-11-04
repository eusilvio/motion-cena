# Sound design

Synced SFX change perceived quality a lot: it is the first adjustment users ask for after v1. Do it in v1.

## Cue map (derive it from timeline.json)

| Visual event | SFX | Volume relative to the voice |
|---|---|---|
| Scene transition (whip, wipe) | short whoosh 200–400ms, starting ~150ms before the cut | −12 dB |
| Element appears (pop) | soft pop / click | −16 dB |
| Staggered items | light ticks, one per item (max. ~8, otherwise it becomes noise; group them) | −20 dB |
| Counter rising | accelerating tick or tonal riser | −18 dB |
| Key number reveal | impact / low thump + light reverb | −10 dB |
| Before a reveal | 1–2s riser ending on the impact | −16 dB |
| Typing text | typing clicks | −20 dB |
| Error / negative | short buzz, glitch | −14 dB |

Riser: use `"offset": -1.6` (the riser's duration) so it ends exactly on the anchor.

Rules: less is more, 1 SFX per important action; never cover keywords; all SFX come from the same "kit" (timbral coherence).

## SFX sources

1. **ElevenLabs Sound Effects** (`POST /v1/sound-generation`, `{"text": "short airy whoosh, cinematic, clean", "duration_seconds": 0.5}`), generates to order. Script: `scripts/tts_elevenlabs.py --sfx "<prompt>" --duration 0.5 --out audio/sfx/whoosh.mp3`.
2. **Higgsfield MCP** (audio), if connected.
3. **Free libraries**: Pixabay Sound Effects, Freesound (check the CC0/CC-BY license and give attribution when required), Kenney (CC0, UI sounds).
4. **Synthesized locally** (free, offline, always works): `uv run scripts/synth_sfx.py --out projects/<slug>/audio/sfx` generates whoosh, pop, tick, impact, riser, click, glitch.

## Music (optional)

A light instrumental bed, 100–128 BPM for Reels. Sources: the user's library, Pixabay Music, generation via ElevenLabs Music/Higgsfield. Ducking −18 to −22 dB under the voice. Cut at the end of a bar; 1s fade out.

## cues in storyboard.json / timeline.json

Each scene has `sfx: [{"type": "whoosh", "at": "scene_start"|"scene_end"|"anchor:<id>"|<segundos relativos>, "file": "opcional", "gain_db": -12}]`. `build_timeline.py` resolves them to absolute time in `timeline.json.sfx_cues`; `mix_audio.py` consumes them.

## Final mix

`scripts/mix_audio.py`: places each cue (adelay), applies gain, sums with the voice, adds music with sidechain ducking, and normalizes loudness to −14 LUFS / true peak −1 dBTP. Export `mix.wav` and use it as the single track in the engine (turn off the engine's individual audio so nothing is duplicated).
