---
title: Troubleshooting
description: Errors that have come up running motion-cena, each with its symptom, cause and fix.
---

# Something went wrong?

Run the two diagnostics first. `setup.sh` points out what is missing (Node, FFmpeg, uv), and the HyperFrames `doctor` checks Node, FFmpeg, Chrome, memory and disk:

```bash
./setup.sh
npx hyperframes doctor
```

In `doctor`, a failure on `TTS (Kokoro)` or `BGM (MusicGen)` can be ignored: they are optional local alternatives, and motion-cena does not depend on them. They are why it ends with "Some checks failed" even when everything is fine.

The cases below came up in real use. Each one has the symptom, the cause and the fix.

## Render

::: details The render is slow, stops halfway or disappears
**Symptom.** One of these messages, or a video that never shows up:

```text
Command did not complete within its 600s timeout and was moved to the background
Render cancelled: render_cancelled_parent_exited
Background command "..." was stopped because the system is running low on memory
```

Sometimes a `creatives/reels/work-*/` folder is left behind with a `video-only.mp4` that `ffprobe` rejects with `moov atom not found`.

**Cause.** A 30 s video takes 1.5 to 2.5 min to render on an ordinary laptop, and heavy compositions (full-screen photos, blur, grain) go past 6 min. When the agent's command ends or times out, HyperFrames cancels the render along with it. With other renders or Studio previews open, memory runs out.

**Fix.** Close what is open and run the render detached from the agent, with fewer workers:

```bash
npx hyperframes preview --list                 # Studio previews still running
npx hyperframes preview --stop                 # inside the project folder that no longer needs it
cd projects/<slug>/video
bash -c 'set -m; HYPERFRAMES_RENDER_DETACHED=1 npx hyperframes render -o ../../../creatives/reels/<slug>-ig-reels.mp4 --workers 2 < /dev/null > ../out/render.log 2>&1 &'
tail -f ../out/render.log                      # ends with "rendered in ..."
```

While iterating, use `--quality draft` (1 min 22 s instead of 1 min 50 s for 30 s of video, on the measured machine). Delete the `creatives/reels/work-*` folder the interrupted render left behind.
:::

::: details Render Chrome not found (HyperFrames)
**Symptom.**

```text
[BrowserManager] Chrome binary not found at ... Run `hyperframes browser ensure` to re-download.
```

or a warning that the Chrome file is corrupted.

**Cause.** HyperFrames renders with its own Chrome (about 260 MB in `~/.cache/hyperframes/chrome`). The download on the first render failed or was interrupted, or the cache was deleted.

**Fix.**

```bash
npx hyperframes browser ensure          # downloads the Chrome version pinned by HyperFrames
npx hyperframes browser ensure --force  # deletes a broken download and downloads it again
npx hyperframes browser path            # shows which executable is in use
```
:::

::: details Safe-zone checker Chrome (Playwright)
**Symptom.** `safe_zone_check.py` stops with:

```text
BrowserType.launch: Executable doesn't exist at .../ms-playwright/chromium_headless_shell-.../chrome-headless-shell
Looks like Playwright was just installed or updated.
Please run the following command to download new browsers:
    playwright install
```

**Cause.** The checker uses Playwright, which has its own Chromium, separate from the HyperFrames one. The script tries that Chromium and then a Google Chrome installed on the system. With neither, it stops.

**Fix.**

```bash
uv run --with playwright playwright install chromium
```

On a Linux machine without the browser libraries, add `--with-deps` (asks for sudo). To see what it will download first: `--dry-run`.
:::

## Voice

::: details edge-tts produces no audio
**Symptom.**

```text
edge_tts.exceptions.NoAudioReceived: No audio was received. Please verify that your parameters are correct.
```

**Cause.** A wrong voice name, no internet, or an outdated edge-tts version after a change in Microsoft's service (the service is free and unofficial).

**Fix.** Check the voice name and force the newest version:

```bash
uv run --with edge-tts edge-tts --list-voices | grep pt-BR
# pt-BR-AntonioNeural, pt-BR-FranciscaNeural, pt-BR-ThalitaMultilingualNeural
uv run --refresh-package edge-tts .agents/skills/motion-cena/scripts/tts_edge.py --text-file projects/<slug>/narration.txt --voice pt-BR-FranciscaNeural --out projects/<slug>/audio
```

For a video in another language, list that language's voices instead of `pt-BR`. If it keeps failing, ask for the voiceover through ElevenLabs.
:::

::: details ElevenLabs rejects the request
**Symptom.** One of these:

```text
ELEVENLABS_API_KEY not set (run: npx -y @elevenlabs/cli@latest onboard init)
status_code: 401 ... 'Neither authorization header nor xi-api-key received, please provide one.'
status_code: 400 ... 'code': 'voice_not_found'
status_code: 429 ... 'code': 'concurrent_limit_exceeded', 'message': 'Too many concurrent requests. ...'
```

**Cause.** The key is not in `.env.local` (or the script ran outside the repository); the requested `voice_id` no longer exists in your account (a cloned voice that was deleted, for example); or the agent fired more generations in parallel than your plan allows.

**Fix.** Put `ELEVENLABS_API_KEY=...` in the `.env.local` at the repository root and list the voices your account can see:

```bash
uv run .agents/skills/motion-cena/scripts/tts_elevenlabs.py --list-voices
```

On a 429, ask the agent to generate one voiceover at a time.
:::

## Machine

::: details Node, FFmpeg or uv missing or on the wrong version
**Symptom.**

```text
HyperFrames requires Node.js >= 22 (current: v20...). Switch Node versions and retry.
[FFmpeg] ffmpeg not found
Unknown encoder 'libx264'
uv: command not found
```

**Cause.** An old Node, FFmpeg missing or built without H.264, or `uv` not installed. The QA and mixing scripts call the `ffmpeg` on the PATH, so the first `ffmpeg` on the PATH needs `libx264` and `aac`.

**Fix.**

```bash
node -v                                             # must be 22 or higher; with nvm: nvm install 22
which -a ffmpeg                                     # which ffmpeg comes first on the PATH
ffmpeg -hide_banner -encoders | grep -E ' libx264 | aac '
curl -LsSf https://astral.sh/uv/install.sh | sh     # installs uv
```

If HyperFrames needs a different FFmpeg, point to it with `HYPERFRAMES_FFMPEG_PATH` and `HYPERFRAMES_FFPROBE_PATH`, then check with `npx hyperframes doctor`.
:::

## QA

::: details QA failed the video
**Symptom.** `qa_video.sh` ends in `RESULT: FAIL` with one of these lines:

```text
FAIL no silent gaps > 1.5s (found 1)
FAIL audio track none
FAIL loudness -16.55 LUFS (want -16..-12)
```

**Cause.** The first is the most common: the end card goes silent after the last word. The second shows up when the render came out without `mix.wav`. The third, when the mix came out too quiet.

**Fix.** Shorten the end card or keep music and a sound effect under it. For the audio, redo the mix and render again:

```bash
uv run .agents/skills/motion-cena/scripts/mix_audio.py projects/<slug>/timeline.json --voice projects/<slug>/audio/voice.mp3 --sfx-dir projects/<slug>/audio/sfx --lufs -14 --out projects/<slug>/audio/mix.wav
```
:::

::: details The safe-zone checker reported an ERRO
**Symptom.** `safe_zone_check.py` ends with `1 erro(s)` or more and lists the element, the time and the edge that entered the zone (`right +38px`, for example). The report is in Portuguese: `ERRO` is an error, `aviso` is a warning.

**Cause.** A text, card, icon or logo stayed 0.5 s or longer inside the band the app interface covers.

**Fix.** Move or shrink the element until it fits in the free area. If it is only background decoration, mark it with `data-safe-ignore`, and the checker skips that element. The [safe-zone playground](/en/reference/platforms) shows how much fits in each preset.
:::

## Also seen

- `Prompt is too long` in a 16-hour session: run `/compact` or open a new session per video. Every step is saved in `projects/<slug>/`, so the agent picks up where it left off.
- `[Compiler] WARNING: Failed to download CDN script: https://cdn.jsdelivr.net/npm/gsap@.../gsap.min.js (TypeError: fetch failed)` with no internet: save `gsap.min.js` in `video/assets/vendor/` and point the `<script>` to it.
- `Continuing render despite lint issues` is a warning, not an error. To see the issues: `npx hyperframes check`.

Found another error? Open a [bug issue](https://github.com/eusilvio/motion-cena/issues) with the message, your system and the agent you use.
