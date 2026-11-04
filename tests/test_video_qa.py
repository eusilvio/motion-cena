"""qa_video.sh and analyze_reference.sh on tiny generated videos (ffmpeg only, no network).

analyze_reference.sh is run on a video without audio: with audio it calls align_words.py, which
downloads a Whisper model (not run here)."""
import os

import pytest

from conftest import ffmpeg, ffprobe, needs_ffmpeg, run_script

pytestmark = needs_ffmpeg


def make_video(path, size="1080x1920", fps=30, seconds=2, audio=True):
    args = ["-f", "lavfi", "-i", f"testsrc2=size={size}:rate={fps}:duration={seconds}"]
    if audio:
        # lavfi's sine peaks at 1/8 (-18 dBFS); +7 dB puts a 997 Hz mono tone at -11 dBFS, about -14 LUFS
        args += ["-f", "lavfi", "-i", f"sine=frequency=997:sample_rate=48000:duration={seconds}",
                 "-af", "volume=7dB", "-c:a", "aac", "-shortest"]
    ffmpeg(*args, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", path)
    return path


@pytest.fixture(scope="module")
def reel(tmp_path_factory):
    return make_video(tmp_path_factory.mktemp("video") / "peca-ig-reels.mp4")


def qa(video, *args, qa_dir):
    return run_script("qa_video.sh", video, *args, check=False, env={**os.environ, "QA_DIR": str(qa_dir)})


def test_qa_passes_a_compliant_reel(reel, tmp_path):
    proc = qa(reel, "ig-reels", qa_dir=tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    out = proc.stdout
    for line in ("OK   resolution 1080x1920 (expected 1080x1920)", "OK   fps 30.00 (expected 30)",
                 "OK   video codec h264 / yuv420p", "OK   audio track aac", "OK   duration <= 180s (preset ig-reels)",
                 "OK   true peak", "OK   no silent gaps > 1.5s (found 0)", "RESULT: PASS"):
        assert line in out, line
    assert "OK   loudness" in out
    contact, frame0 = tmp_path / "peca-ig-reels_contact.jpg", tmp_path / "peca-ig-reels_frame0.jpg"
    assert ffprobe(contact, "stream=width") == "1440" and ffprobe(contact, "stream=height") == "854"  # 6x2 tiles of 240 px
    assert ffprobe(frame0, "stream=width") == "540"


def test_qa_fails_on_the_wrong_canvas(reel, tmp_path):
    proc = qa(reel, "yt-long", qa_dir=tmp_path)
    assert proc.returncode == 1
    assert "FAIL resolution 1080x1920 (expected 1920x1080)" in proc.stdout
    assert proc.stdout.rstrip().endswith("RESULT: FAIL")


def test_qa_with_explicit_size(reel, tmp_path):
    assert qa(reel, "1080", "1920", "30", qa_dir=tmp_path).returncode == 0
    proc = qa(reel, "1080", "1920", "60", qa_dir=tmp_path)
    assert proc.returncode == 1 and "FAIL fps 30.00 (expected 60)" in proc.stdout


def test_qa_flags_missing_audio(tmp_path):
    silent = make_video(tmp_path / "mudo.mp4", audio=False)
    proc = qa(silent, "ig-reels", qa_dir=tmp_path)
    assert proc.returncode == 1 and "FAIL audio track none" in proc.stdout


def test_qa_unknown_preset(reel, tmp_path):
    assert qa(reel, "nope", qa_dir=tmp_path).returncode == 2


def test_analyze_reference_without_audio(tmp_path):
    video = make_video(tmp_path / "ref.mp4", size="640x360", seconds=3, audio=False)
    out = tmp_path / "ref"
    proc = run_script("analyze_reference.sh", video, out)
    assert "(1 sheet(s)" in proc.stdout
    for name in ("probe.txt", "sheet-01.jpg", "key-10.png", "key-50.png", "key-90.png"):
        assert (out / name).stat().st_size > 0, name
    assert not (out / "words.json").exists()  # no audio: no transcription
    assert ffprobe(out / "sheet-01.jpg", "stream=width") == "1920"  # 8 tiles of 240 px
    assert "codec_name=h264" in (out / "probe.txt").read_text()
