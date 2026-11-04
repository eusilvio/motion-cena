# /// script
# requires-python = ">=3.10"
# dependencies = ["elevenlabs>=2.74", "python-dotenv>=1.0"]
# ///
"""ElevenLabs via the official SDK: voice cloning, TTS with word timestamps, sound effects.

The key comes from ELEVENLABS_API_KEY, or from the nearest .env.local up the tree
(set up with `npx -y @elevenlabs/cli@latest onboard init`). Never put the key in code.

Clone:  uv run tts_elevenlabs.py --clone "Nome" --sample training/voz/<amostra>.mp3
TTS:    uv run tts_elevenlabs.py --text-file projects/<slug>/narration.txt --voice-id <id> --out projects/<slug>/audio [--lang pt]
SFX:    uv run tts_elevenlabs.py --sfx "short airy whoosh, clean" --duration 0.5 --out audio/sfx/whoosh.mp3
Voices: uv run tts_elevenlabs.py --list-voices

Only clone a voice with its owner's consent.
"""
import argparse
import base64
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings


def client() -> ElevenLabs:
    if not os.environ.get("ELEVENLABS_API_KEY"):
        for d in [Path.cwd(), *Path.cwd().parents]:
            if (d / ".env.local").exists():
                load_dotenv(d / ".env.local")
                break
    if not os.environ.get("ELEVENLABS_API_KEY"):
        sys.exit("ELEVENLABS_API_KEY not set (run: npx -y @elevenlabs/cli@latest onboard init)")
    # the SDK reads the env var when it is imported, before .env.local is loaded, so pass it explicitly
    return ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])


def chars_to_words(alignment) -> list[dict]:
    words, current, start, end = [], "", None, None
    for ch, s, e in zip(alignment.characters, alignment.character_start_times_seconds, alignment.character_end_times_seconds):
        if ch.isspace():
            if current:
                words.append({"word": current, "start": round(start, 3), "end": round(end, 3)})
            current, start = "", None
            continue
        if start is None:
            start = s
        current += ch
        end = e
    if current:
        words.append({"word": current, "start": round(start, 3), "end": round(end, 3)})
    return words


def tts(el: ElevenLabs, text: str, voice_id: str, model: str, lang: str, stability: float | None, similarity: float | None, speed: float | None, out_dir: Path) -> None:
    # Same request the ElevenLabs site makes: the voice's saved settings unless overridden,
    # and language_code only where the model accepts it.
    extra = {}
    if stability is not None or similarity is not None or speed is not None:
        saved = el.voices.settings.get(voice_id)
        extra["voice_settings"] = VoiceSettings(
            stability=saved.stability if stability is None else stability,
            similarity_boost=saved.similarity_boost if similarity is None else similarity,
            style=saved.style, use_speaker_boost=saved.use_speaker_boost,
            speed=saved.speed if speed is None else speed)  # speed is ignored by eleven_v4
    if lang and model not in ("eleven_multilingual_v2",):
        extra["language_code"] = lang
    res = el.text_to_speech.convert_with_timestamps(voice_id=voice_id, text=text, model_id=model, **extra)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "voice.mp3").write_bytes(base64.b64decode(res.audio_base_64))
    words = chars_to_words(res.alignment)
    (out_dir / "words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1))
    print(f"voice.mp3 + words.json ({len(words)} words, ~{words[-1]['end']:.1f}s) -> {out_dir}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clone", metavar="NAME", help="create an Instant Voice Clone from --sample")
    ap.add_argument("--sample", type=Path, nargs="+", help="clean recordings of the speaker (1–2 min total)")
    ap.add_argument("--text-file", type=Path)
    ap.add_argument("--text")
    ap.add_argument("--voice-id")
    ap.add_argument("--model", default="eleven_v4")
    ap.add_argument("--lang", default="pt")
    ap.add_argument("--accent", default="pt-brazilian", help="clone label; set it or the voice has no accent on ElevenLabs")
    ap.add_argument("--locale", default="pt-BR", help="clone label")
    ap.add_argument("--denoise", action="store_true", help="ElevenLabs noise removal on the sample (can make the clone sound metallic; off by default)")
    ap.add_argument("--stability", type=float, help="override the voice's saved stability")
    ap.add_argument("--similarity", type=float, help="override the voice's saved similarity_boost")
    ap.add_argument("--speed", type=float, help="0.7–1.2, v2/v3 models only")
    ap.add_argument("--sfx", help="sound effect prompt")
    ap.add_argument("--duration", type=float, help="sfx duration in seconds (0.5-30)")
    ap.add_argument("--list-voices", action="store_true")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    el = client()

    if args.list_voices:
        for v in el.voices.get_all().voices:
            print(v.voice_id, v.name, v.category)
        return
    if args.clone:
        if not args.sample:
            sys.exit("--clone needs --sample")
        files = [(p.name, p.read_bytes()) for p in args.sample]
        voice = el.voices.ivc.create(name=args.clone, files=files, remove_background_noise=args.denoise,
                                     description="Instant voice clone made by the motion-cena skill",
                                     labels={"language": args.lang, "accent": args.accent, "locale": args.locale})
        print(f"voice_id {voice.voice_id} ({args.clone})")
        return
    if not args.out:
        sys.exit("--out required")
    if args.sfx:
        audio = el.text_to_sound_effects.convert(text=args.sfx, duration_seconds=args.duration, prompt_influence=0.5)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(b"".join(audio))
        print(f"sfx -> {args.out}")
        return
    text = args.text or (args.text_file.read_text(encoding="utf-8") if args.text_file else None)
    if not text or not args.voice_id:
        sys.exit("TTS needs --text/--text-file and --voice-id")
    tts(el, " ".join(text.split()), args.voice_id, args.model, args.lang, args.stability, args.similarity, args.speed, args.out)


if __name__ == "__main__":
    main()
