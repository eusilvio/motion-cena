"""synth_sfx.py (offline SFX kit) and mix_audio.py (voice + SFX + music bed through ffmpeg)."""
import re
import subprocess
import wave
from array import array

import pytest

from conftest import ffmpeg, ffprobe, load_script, needs_ffmpeg, run_script, write_json

KIT = {"whoosh": 0.45, "pop": 0.09, "tick": 0.025, "click": 0.006, "impact": 0.9, "riser": 1.6, "glitch": 0.18, "ding": 0.8, "beep": 0.115}


@pytest.fixture(scope="module")
def sfx_dir(tmp_path_factory):
    out = tmp_path_factory.mktemp("sfx")
    proc = run_script("synth_sfx.py", "--out", out)
    assert f"{len(KIT)} sfx -> {out}" in proc.stdout
    return out


@pytest.mark.parametrize("name,seconds", sorted(KIT.items()))
def test_synth_sfx_writes_valid_wav(sfx_dir, name, seconds):
    with wave.open(str(sfx_dir / f"{name}.wav")) as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 48_000)
        assert w.getnframes() == int(48_000 * seconds)
        pcm = array("h", w.readframes(w.getnframes()))
    peak = max(abs(s) for s in pcm)
    assert peak == int(0.89 * 32767)  # normalized to about -1 dBFS
    assert sum(1 for s in pcm if s) > len(pcm) * 0.5  # sound, not silence


def test_synth_sfx_only(tmp_path):
    run_script("synth_sfx.py", "--out", tmp_path, "--only", "pop,ding")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["ding.wav", "pop.wav"]


def test_resolve_cue_file(tmp_path):
    mix = load_script("mix_audio.py")
    (tmp_path / "custom").mkdir()
    for name in ("pop.mp3", "pop.ogg", "tick.ogg", "custom/alt.wav"):
        (tmp_path / name).write_bytes(b"")
    assert mix.resolve({"type": "pop"}, tmp_path) == tmp_path / "pop.mp3"          # wav, then mp3, then ogg
    assert mix.resolve({"type": "tick"}, tmp_path) == tmp_path / "tick.ogg"
    assert mix.resolve({"type": "x", "file": "custom/alt.wav"}, tmp_path) == tmp_path / "custom/alt.wav"
    assert mix.resolve({"type": "x", "file": str(tmp_path / "pop.ogg")}, tmp_path) == tmp_path / "pop.ogg"
    assert mix.resolve({"type": "pop", "file": "nope.wav"}, tmp_path) is None     # explicit file wins, even missing
    assert mix.resolve({"type": "nope"}, tmp_path) is None


def integrated_lufs(path) -> float:
    log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", log)[-1])


@needs_ffmpeg
@pytest.mark.parametrize("with_music", [False, True])
def test_mix_audio(tmp_path, sfx_dir, with_music):
    # speech-like voice: pink noise at syllable rate with pauses, quiet (about -32 LUFS). A pure sine
    # is no good here: single-pass loudnorm never settles on a constant tone.
    voice = tmp_path / "voice.wav"
    ffmpeg("-f", "lavfi", "-i", "anoisesrc=color=pink:duration=9.5:sample_rate=44100:amplitude=0.3",
           "-af", "tremolo=f=4:d=0.9,volume='if(lt(mod(t,4),3.2),1,0.02)':eval=frame,lowpass=f=3500", voice)
    timeline = write_json(tmp_path / "timeline.json", {
        "meta": {"duration": 10.0},
        "sfx_cues": [
            {"type": "whoosh", "time": 0.5},
            {"type": "pop", "time": 1.0, "gain_db": -10},
            {"type": "inexistente", "time": 2.0},
            {"type": "x", "file": str(sfx_dir / "tick.wav"), "time": 2.5},
        ],
    })
    out = tmp_path / "out" / "mix.wav"
    args = [timeline, "--voice", voice, "--sfx-dir", sfx_dir, "--out", out]
    if with_music:
        bed = tmp_path / "bed.wav"
        ffmpeg("-f", "lavfi", "-i", "sine=frequency=110:duration=1", bed)  # shorter than the video: loops
        args += ["--music", bed]
    proc = run_script("mix_audio.py", *args)
    assert f"mix: voice + 3 sfx{' + music' if with_music else ''}, 10.00s" in proc.stdout
    assert "no file for sfx 'inexistente' at 2.0s" in proc.stderr
    assert ffprobe(out, "stream=sample_rate", "a:0") == "48000"
    assert ffprobe(out, "stream=channels", "a:0") == "2"
    assert ffprobe(out, "stream=codec_name", "a:0") == "pcm_s16le"
    assert abs(float(ffprobe(out, "format=duration")) - 10.0) < 0.05  # padded/trimmed to the timeline
    # input is about -32 LUFS; single-pass loudnorm lands within ~1 LU of -14 on a clip this short,
    # so check the window qa_video.sh enforces on the final video
    assert -16.5 <= integrated_lufs(out) <= -11.5


def test_sfx_prompt_library_is_well_formed():
    """assets/sfx-prompts.json: prompts only (no audio), unique names, durations the API accepts."""
    import json
    from conftest import SKILL
    data = json.loads((SKILL / "assets" / "sfx-prompts.json").read_text(encoding="utf-8"))
    sounds = data["sounds"]
    names = [s["name"] for s in sounds]
    assert len(names) == len(set(names))
    for s in sounds:
        assert set(s) == {"name", "category", "prompt", "duration_s", "use"}, s["name"]
        assert 0.5 <= s["duration_s"] <= 30, s["name"]  # ElevenLabs sound-generation range
        assert "—" not in s["prompt"] + s["use"], s["name"]
