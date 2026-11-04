"""build_timeline.py: scenes, anchors and SFX anchored on the spoken words.

fixtures/timeline/ holds a synthetic storyboard + words.json and the expected timeline, checked by
hand (see the notes next to each case below). The words.json has what real TTS/ASR output has:
punctuation glued to words, upper case, a word without its accent, a multi-word entry ("12 minutos")
and one misheard word ("Espera" for the script's "Espere").
"""
import json

import pytest

from conftest import FIXTURES, load_script, read_json, run_script, write_json

TL = FIXTURES / "timeline"
bt = load_script("build_timeline.py")


def build(tmp_path, storyboard, words, *flags):
    sb = storyboard if not isinstance(storyboard, (dict, list)) else write_json(tmp_path / "storyboard.json", storyboard)
    wd = words if not isinstance(words, (dict, list)) else write_json(tmp_path / "words.json", words)
    out = tmp_path / "timeline.json"
    proc = run_script("build_timeline.py", sb, wd, "--out", out, *flags)
    return read_json(out), proc


def scene(tl, sid):
    return next(s for s in tl["scenes"] if s["id"] == sid)


def test_golden_timeline(tmp_path):
    tl, proc = build(tmp_path, TL / "storyboard.json", TL / "words.json")
    expected = read_json(TL / "expected.json")
    assert tl == expected
    assert "6 scenes, 9 sfx cues, 13.20s @ 30fps" in proc.stdout


def test_golden_hand_checked_values():
    """The numbers in expected.json, derived by hand (lead 0.15 s, tail 0.8 s, 30 fps)."""
    tl = read_json(TL / "expected.json")
    bounds = {s["id"]: (s["start"], s["end"], s["startFrame"], s["durationFrames"]) for s in tl["scenes"]}
    assert bounds == {
        "s1": (0.0, 2.77, 0, 83),      # first scene always starts at 0; ends where s2 starts
        "s2": (2.77, 6.67, 83, 117),   # "Café," at 2.92 - lead 0.15
        "s3": (6.67, 7.87, 200, 36),   # silent, 1.2 s: next start 7.87 - 1.2 (speech over at 6.2 + 0.3)
        "s4": (7.87, 10.47, 236, 78),  # starts on the misheard "Espera" (8.02 - 0.15), not on "12"
        "s5": (10.47, 11.7, 314, 37),  # "Bom" at 10.62 - 0.15
        "s6": (11.7, 13.2, 351, 45),   # silent end card: last word 11.4 + 0.3, holds its 1.5 s
    }
    assert tl["meta"]["duration"] == 13.2 and tl["meta"]["durationFrames"] == 396
    anchors = {a["id"]: (a["start"], a["end"], a["startFrame"], a["endFrame"])
               for s in tl["scenes"] for a in s["anchors"]}
    assert anchors == {
        "maquina": (1.16, 1.7, 35, 51),    # "Cafeteira!" vs spoken "CAFETEIRA": case and punctuation
        "hora": (0.71, 1.04, 21, 31),      # "manhã" vs spoken "manha,": accent
        "agua": (3.34, 3.7, 100, 111),     # "água" said twice in s2: the first one wins
        "mais": (4.7, 5.3, 141, 159),      # "Mais água" picks the second one by context
        "calma": (5.36, 6.2, 161, 186),
        "tempo": (8.41, 9.01, 252, 270),   # "12 minutos" was one TTS entry, split in two
        "final": (10.86, 11.4, 326, 342),  # "café" resolves inside s5, not the "Café," of s2
    }
    cues = [(c["scene"], c["type"], c["time"]) for c in tl["sfx_cues"]]
    assert cues == [
        ("s1", "riser", 0.0),       # scene_start - 1.6, clamped at 0
        ("s1", "pop", 1.16),        # anchor:maquina
        ("s1", "whoosh", 2.62),     # scene_end - 0.15
        ("s2", "tick", 3.27),       # 0.5 s after the scene start
        ("s2", "riser", 3.76),      # anchor:calma - 1.6, ends on the word
        ("s3", "impact", 6.67),
        ("s4", "click", 8.12),      # "at" given as a string number
        ("s5", "whoosh", 10.27),
        ("s6", "ding", 13.05),      # scene_end of the last scene
    ]
    assert tl["warnings"] == [
        "scene s3: no narration matched (silent scene or mismatch)",
        "scene s6: no narration matched (silent scene or mismatch)",
        "scene s4: anchor 'água fervendo' not found in spoken words",
        "scene s4: sfx anchor 'anchor:nunca' unresolved",
    ]


def test_every_spoken_word_lands_in_a_scene():
    tl = read_json(TL / "expected.json")
    assert [w["word"] for s in tl["scenes"] for w in s["words"]][17:20] == ["Espera", "12", "minutos"]
    assert sum(len(s["words"]) for s in tl["scenes"]) == 25  # 24 entries, one of them split in two


@pytest.mark.parametrize("flags,fps", [(("--fps", "25"), 25), (("--fps", "60"), 60), ((), 30)])
def test_fps_conversion(tmp_path, flags, fps):
    tl, _ = build(tmp_path, TL / "storyboard.json", TL / "words.json", *flags)
    golden = read_json(TL / "expected.json")
    assert tl["meta"]["fps"] == fps
    # seconds do not depend on fps; frames are seconds * fps, rounded
    assert [(s["start"], s["end"]) for s in tl["scenes"]] == [(s["start"], s["end"]) for s in golden["scenes"]]
    for s in tl["scenes"]:
        assert s["startFrame"] == round(s["start"] * fps)
        assert s["durationFrames"] == round(s["end"] * fps) - round(s["start"] * fps)
        for a in s["anchors"]:
            assert (a["startFrame"], a["endFrame"]) == (round(a["start"] * fps), round(a["end"] * fps))
    assert tl["meta"]["durationFrames"] == round(13.2 * fps)
    if fps == 25:  # a few by hand
        assert scene(tl, "s2")["startFrame"] == 69     # 2.77 * 25 = 69.25
        assert scene(tl, "s3")["startFrame"] == 167    # 6.67 * 25 = 166.75
        assert tl["meta"]["durationFrames"] == 330


def test_fps_comes_from_meta_then_defaults_to_30(tmp_path):
    board = read_json(TL / "storyboard.json")
    board["meta"]["fps"] = 24
    tl, _ = build(tmp_path, board, TL / "words.json")
    assert tl["meta"]["fps"] == 24 and tl["meta"]["durationFrames"] == round(13.2 * 24)
    del board["meta"]
    tl, _ = build(tmp_path, board, TL / "words.json")
    assert tl["meta"]["fps"] == 30 and tl["meta"]["durationFrames"] == 396


@pytest.mark.parametrize("fps", [24, 25, 30, 60])
def test_frames_tile_without_gaps_or_overlap(tmp_path, fps):
    tl, _ = build(tmp_path, TL / "storyboard.json", TL / "words.json", "--fps", fps)
    scenes = tl["scenes"]
    for a, b in zip(scenes, scenes[1:]):
        assert a["end"] == b["start"]
        assert a["start"] < b["start"]
        assert a["startFrame"] + a["durationFrames"] == b["startFrame"]
    assert scenes[-1]["startFrame"] + scenes[-1]["durationFrames"] == tl["meta"]["durationFrames"]


def test_last_scene_ends_after_last_word_plus_tail(tmp_path):
    board = read_json(TL / "storyboard.json")
    board["scenes"] = [s for s in board["scenes"] if s["id"] != "s6"]  # no closing silent card
    tl, _ = build(tmp_path, board, TL / "words.json")
    assert tl["scenes"][-1]["end"] == 12.2  # "café!" ends at 11.4, + 0.8
    tl, _ = build(tmp_path, board, TL / "words.json", "--tail", "1.5")
    assert tl["scenes"][-1]["end"] == 12.9
    assert tl["meta"]["duration"] == 12.9 and tl["meta"]["durationFrames"] == 387


def test_lead_moves_scene_starts(tmp_path):
    tl, _ = build(tmp_path, TL / "storyboard.json", TL / "words.json", "--lead", "0.4")
    assert scene(tl, "s2")["start"] == 2.52 and scene(tl, "s5")["start"] == 10.22


def test_closing_silent_scenes_each_keep_their_duration(tmp_path):
    words = [{"word": "Fim", "start": 0.2, "end": 0.6}, {"word": "aqui.", "start": 0.62, "end": 1.0}]
    board = {"meta": {"fps": 30}, "scenes": [
        {"id": "fala", "narration": "Fim aqui."},
        {"id": "logo", "narration": "", "duration": 2.0},
        {"id": "creditos", "narration": "", "duration": 1.5},
    ]}
    tl, _ = build(tmp_path, board, words)
    assert [(s["id"], s["start"], s["end"]) for s in tl["scenes"]] == [
        ("fala", 0.0, 1.3), ("logo", 1.3, 3.3), ("creditos", 3.3, 4.8)]


def test_silent_scene_without_room_in_the_audio_warns_and_keeps_order(tmp_path):
    words = [{"word": "um", "start": 0.1, "end": 0.5}, {"word": "dois", "start": 0.6, "end": 1.0}]
    board = {"scenes": [
        {"id": "a", "narration": "um"},
        {"id": "pausa", "narration": "", "duration": 2.0},
        {"id": "b", "narration": "dois"},
    ]}
    tl, _ = build(tmp_path, board, words)
    starts = [s["start"] for s in tl["scenes"]]
    assert starts == sorted(starts)
    assert all(s["end"] >= s["start"] for s in tl["scenes"])
    assert any("pausa: silent scene gets" in w for w in tl["warnings"])


def test_storyboard_without_speech_plays_scenes_back_to_back(tmp_path):
    board = {"scenes": [{"id": "a", "narration": "", "duration": 2},
                        {"id": "b", "narration": "", "duration": 4},
                        {"id": "c", "narration": ""}]}
    tl, _ = build(tmp_path, board, [])
    assert [(s["start"], s["end"]) for s in tl["scenes"]] == [(0.0, 2.0), (2.0, 6.0), (6.0, 9.0)]


def test_divergent_narration_warns_about_coverage(tmp_path):
    board = {"scenes": [{"id": "a", "narration": "um texto que ninguém gravou nesta voz"}]}
    tl, _ = build(tmp_path, board, read_json(TL / "words.json"))
    assert any("of script words matched the audio" in w for w in tl["warnings"])


def test_timeline_is_written_as_utf8(tmp_path):
    tl, _ = build(tmp_path, TL / "storyboard.json", TL / "words.json")
    raw = (tmp_path / "timeline.json").read_bytes()
    assert "sintética".encode("utf-8") in raw and json.loads(raw.decode("utf-8")) == tl


# pure functions


@pytest.mark.parametrize("raw,expected", [
    ("Às", "as"), ("MANHÃ,", "manha"), ("ação!", "acao"), ("café...", "cafe"), ("10%", "10%"),
    ("R$1.000", "r1000"), ("“aspas”", "aspas"), ("—", ""),
])
def test_norm(raw, expected):
    assert bt.norm(raw) == expected


def test_tokens_drop_pure_punctuation():
    assert bt.tokens("Água — e tempo... ") == ["agua", "e", "tempo"]


def test_find_phrase():
    spoken = ["cafe", "agua", "e", "tempo", "mais", "agua", "menos", "pressa"]
    assert bt.find_phrase(["agua"], spoken, 0, len(spoken)) == (1, 1)          # first occurrence
    assert bt.find_phrase(["agua"], spoken, 3, len(spoken)) == (5, 5)          # search starts at lo
    assert bt.find_phrase(["mais", "agua"], spoken, 0, len(spoken)) == (4, 5)
    assert bt.find_phrase(["menos", "pressa", "hoje"], spoken, 0, 8) == (5, 7)  # 2 of 3 words: ratio 0.67
    assert bt.find_phrase(["agua", "fervendo"], spoken, 0, 8) is None        # 1 of 2 words: ratio 0.5 < 0.6
    assert bt.find_phrase(["leite", "quente"], spoken, 0, 8) is None
    assert bt.find_phrase([], spoken, 0, 8) is None                          # phrase of punctuation only
    assert bt.find_phrase(["pressa"], spoken, 0, 4) is None                  # outside the scene range


def test_split_multiword():
    out = bt.split_multiword([{"word": "12 minutos", "start": 1.0, "end": 1.6, "x": 1}, {"word": "e", "start": 2, "end": 2.1}])
    assert out == [{"word": "12", "start": 1.0, "end": 1.3, "x": 1},
                   {"word": "minutos", "start": 1.3, "end": 1.6, "x": 1},
                   {"word": "e", "start": 2, "end": 2.1}]
