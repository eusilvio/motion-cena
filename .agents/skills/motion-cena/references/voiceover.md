# Voiceover (TTS) and timestamps

Voiceover comes before animation. Required output of this step:
- `audio/voice.mp3` (or .wav)
- `audio/words.json` → `[{"word": "quase", "start": 0.12, "end": 0.41}, ...]` (seconds)

**The voice language follows the output language.** The pt-BR voices and `--lang pt` below are the default when the output language is pt-BR; for another output language, pick voices in that language (and pass its language code in `--lang`).

## Choosing the provider

| Provider | Cost | pt-BR quality | Timestamps | When |
|---|---|---|---|---|
| **Higgsfield MCP** | credits (paid plan) | high, several models | not guaranteed → align with Whisper | Already connected; the user wants to hear/choose voices in the chat |
| **ElevenLabs** | paid per character | very high, voice cloning | native (`/v1/text-to-speech/{voice_id}/with-timestamps`, per character) | Best result; the user's cloned voice |
| **edge-tts** | free, no key | good (Francisca, Antonio, Thalita) | native (WordBoundary) | Default without a key; prototypes |
| **Kokoro / Piper (local)** | free, offline | medium | via Whisper | No network |
| User's recording | - | their own voice | via Whisper | The user wants their own voice |

Check what is available: list MCP tools (`higgsfield`, `elevenlabs`), env `ELEVENLABS_API_KEY`. Ask only if there is a real choice (e.g. paid vs free); otherwise use the best available and say which one you used.

## Higgsfield MCP

Connect (claude.ai / Desktop): Higgsfield→Claude integration page, copy the connector link → Claude **Customize → Add custom connector** → name "Higgsfield", paste the link → adjust permissions (what runs on its own vs what asks for approval). Requires a paid Higgsfield plan; each generation consumes credits.
In Claude Code: `claude mcp add --transport http higgsfield <URL-do-conector>`. In another agent, register the same URL as an MCP server in its configuration; without MCP, use ElevenLabs or edge-tts.
Usage: ask for the available voices, generate 2–3 samples of the first sentence for the user to choose from, then generate the full narration. Download the file to `audio/voice.mp3` and run `scripts/align_words.py`.

## ElevenLabs

- **Set up**: `npx -y @elevenlabs/cli@latest onboard init` at the project root. The key goes in `.env.local` (in `.gitignore`); the script reads it from there. Never ask for the key in the chat or put it in the code.
- **Clone the user's voice** (Instant Voice Clone, Starter plan or above): 1 to 2 min of **only their voice**, without noisy passages or other voices (trim it first with ffmpeg):
  ```bash
  uv run scripts/tts_elevenlabs.py --clone "Nome" --sample training/voz/<arquivo>.mp3
  ```
  Prints the `voice_id`. Only clone the user's own voice, with consent.
- **Narration with timestamps** (official SDK, `convert_with_timestamps`, model `eleven_v4`):
  ```bash
  uv run scripts/tts_elevenlabs.py --text-file projects/<slug>/narration.txt --voice-id <id> --out projects/<slug>/audio [--lang pt]
  ```
  Produces `voice.mp3` + a per-word `words.json`. `eleven_v4` accepts only `stability` (default 0.5) and `similarity_boost` (default 0.8); pace and emotion come from punctuation and tags like `[excited]`.
- Saved voices: `uv run scripts/tts_elevenlabs.py --list-voices`. Use the voice the request names; if none, pick a library voice in the video's language and tone.
- Free local cloning (Chatterbox, `scripts/tts_chatterbox.py`) was tested with a Portuguese voice clone and **did not sound alike**; use it only if ElevenLabs is not available.

## edge-tts (free)

```bash
uv run scripts/tts_edge.py --text-file projects/<slug>/narration.txt --voice pt-BR-FranciscaNeural --rate +8% --out projects/<slug>/audio
```
Produces `voice.mp3` + `words.json`. pt-BR voices (default when the output language is pt-BR): `pt-BR-FranciscaNeural` (female, warm), `pt-BR-AntonioNeural` (male, informative), `pt-BR-ThalitaMultilingualNeural`. List: `uvx edge-tts --list-voices | grep pt-BR` (for another output language, filter by that language's locale instead). `--rate +5%..+12%` gives a Reels pace.
Warning: unofficial Microsoft service; it may change or go down. For serious commercial use, prefer ElevenLabs.

## Alignment with Whisper (any audio)

```bash
uv run scripts/align_words.py projects/<slug>/audio/voice.mp3 --lang pt --model small --out projects/<slug>/audio/words.json
```
Uses faster-whisper with `word_timestamps=True`. Pass `--script projects/<slug>/narration.txt` to fix the spelling of the transcribed words using the script (keeps Whisper's timings and the script's text). Model `small` is fine on CPU; `medium` is more accurate.

## Check

- Listen to (or ask the user to listen to) the first 5s: pronunciation of acronyms, numbers, proper names.
- Actual vs estimated duration; if > 15% over the target, cut text instead of speeding up too much (rate > +15% sounds robotic).

## User recording with music or background noise

The user records the narration on their phone (sometimes with music playing or household noise). ElevenLabs is not needed:

```bash
uv run scripts/isolate_voice.py <gravacao>.m4a --out projects/<slug>/audio-gravado     # Demucs tira a música + filtro de ruído -> voice.wav
uv run scripts/align_words.py projects/<slug>/audio-gravado/voice.wav --lang pt --out projects/<slug>/audio-gravado/words.json
```

- Check the transcript: proper names come out wrong (e.g. "Envídia" instead of "Nvidia"); fix them in `words.json`, along with sentence-initial capitals and punctuation.
- What the user **said** rules, not the script: if they swapped words ("Você" instead of "Tu"), build the storyboard from that version, with the spoken text in each scene (`narration`), so no word is left out of the scenes and position-based highlights land on the right words.
- Then: `build_timeline.py` → `mix_audio.py` → normalize the mix to −14 LUFS (`ffmpeg -af loudnorm=I=-14:TP=-1.5`).
- The raw recording stays out of git; version only the clean voice.
