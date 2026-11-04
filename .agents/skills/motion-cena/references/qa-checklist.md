# QA before delivery

Run `QA_DIR=projects/<slug>/out scripts/qa_video.sh creatives/reels/<slug>-<preset>.mp4 <preset>` and open `projects/<slug>/out/<slug>-<preset>_contact.jpg` with Read (actually look at it).

## Technical (the script checks)
- [ ] `safe_zone_check.py projects/<slug>/video --preset vertical` with 0 errors (before the render)
- [ ] Contact sheet: nothing that matters over the red zone (text, number, card, icon, logo, CTA)
- [ ] Vertical delivered as `-ig-reels.mp4` and `-tiktok.mp4`
- [ ] Resolution, fps and maximum duration from the platform preset (`qa_video.sh ... <preset>`)
- [ ] 30 fps (or as requested), codec h264 + aac, pix_fmt yuv420p (Instagram-compatible)
- [ ] Duration ≈ voice duration + tail (≤ 1s of silence at the end)
- [ ] Duration within ±10% of the target (the requested one or the preset's `default_duration`)
- [ ] Audio track present; integrated loudness between −16 and −12 LUFS; true peak ≤ −1 dBTP

## Visual (you check in the frames)
- [ ] Frame 0 already has content and movement (no black/empty screen)
- [ ] No text cut off or inside the preset's UI zone (`uv run scripts/platform_preset.py <preset>`; e.g. Reels/Stories 269 px top / 672 px bottom / 65 px sides)
- [ ] Duration within the platform maximum (Stories: 60 s per story; Shorts with licensed music: ≤ 60 s)
- [ ] `narracao-literal`: the voiceover is the user's text word for word · `roteiro`: the original's facts and intent preserved, changes listed in `plan.md`
- [ ] Brand fonts loaded (did not fall back to Times/Arial)
- [ ] Legible contrast; no text over a conflicting light/dark area
- [ ] Numbers correct and matching the source
- [ ] No element overlapping another unintentionally
- [ ] No static frames > 1s

## Sync
- [ ] Emphases hit the anchor words (check 3 anchors: the frame at `anchor.startFrame` shows the effect starting)
- [ ] Captions (if on) follow the speech
- [ ] SFX do not cover keywords

## Narrative
- [ ] Hook delivers tension in ≤ 3s
- [ ] The visual demonstrates what the speech says in each scene
- [ ] Ending chosen by the script's intent (final fact, synthesis, question, CTA or loop)

## Creativity
- [ ] Passes the bar in `references/quality-bar.md`
- [ ] Central idea recorded in `plan.md`, with the 2 discarded ones
- [ ] Does not repeat the device or 3+ axes of any of the last 3 videos (`scripts/registro.py --recent 3`); new row added to the log

Something failed → fix it and re-render. In the delivery, list what could not be fixed.

## Real symbols
- [ ] Every country, award, brand or institution mentioned appears with its real symbol (flag, medal, logo), not an abstract shape
- [ ] No redrawn symbol; logo undistorted, current version; `CREDITS.md` present; CC BY credit in the piece if used
- [ ] Each scene follows the Visual map in `plan.md` and passes the "without audio, does it tell the sentence?" test
- [ ] **No emoji** in artwork, text, captions, post caption or end card

## Text
- [ ] `lint_copy.py` with no errors in the script, on-screen text, slides and post caption (`references/writing-style.md`)
- [ ] Read aloud, it sounds like the user talking, not like an essay
