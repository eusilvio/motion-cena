---
title: Time and cost
description: Time and tokens from real productions in Claude Code, the cost of the voice, what fits in the plans and how to spend less.
---

# How long it takes and what it costs

Numbers from real productions made with this repository in Claude Code (Opus 5.5), between Oct 20 and Nov 4, 2026, on an ordinary laptop. Treat them as an order of magnitude: yours will vary.

## Three measured pieces

| Piece | Voice | To 1st delivery | With revisions | Total tokens | Equivalent API cost | Render |
|---|---|---|---|---|---|---|
| 30 s Reels from a product's code | ElevenLabs | 30 min | 42 min (1 revision) | 24.8 M | US$ 10.58 (US$ 8.37 at 1st delivery) | 2 min 18 s |
| 46 s Reels from a product's code, with a music track | ElevenLabs (voice and music) | 25 min | 41 min (1 revision) | 25.2 M | US$ 12.18 (US$ 8.03 at 1st delivery) | 2 min 20 s to 2 min 32 s |
| 6-slide carousel from finished text, with the numbers checked on the web | no voice | 3 min | 7 min (2 revisions) | 8.5 M | US$ 3.22 (US$ 1.24 at 1st delivery) | 5 s (PNG) |

The minutes count the time the agent was working, from your request to its last action. The time you take to look and reply is not included. Each revision round on the videos added 12 to 16 min and 8 to 10 M tokens (US$ 2 to 4). In every case, 98% of the tokens were cache reads, the cheapest part.

## How to spend less

- **One piece per session.** Every request re-reads the whole conversation. In the measured sessions, a second piece in the same conversation cost 35% to 41% of that session. When a video is done, open a new session (`/clear` in Claude Code): everything is saved in `projects/<slug>/` and the agent picks up where it left off.
- **Turn off what you don't use for video.** Connectors and plugins weigh on every request. Turn them off for this project.
- **Iterate in draft.** While you adjust, rendering with `--quality draft` takes less time (1 min 22 s instead of 1 min 50 s for 30 s of video).
- **Compact before a long round of revisions** (`/compact` in Claude Code).

## Per-step timings

Measured on a 4-core Intel i5-8265U, 11.6 GB of RAM, no dedicated GPU, Linux:

| Step | Time |
|---|---|
| Render of 30.5 s at 1080×1920, 30 fps (`npx hyperframes render`, default quality) | 1 min 50 s, about 5 cores busy and 1.5 GB of extra RAM |
| The same render with `--quality draft` (for iterating) | 1 min 22 s |
| edge-tts voiceover, 77 words in pt-BR (23 s of audio) | 3 s (9 s the first time, while `uv` installs the dependency) |
| Safe zone (`safe_zone_check.py`) + QA (`qa_video.sh`) | 21 s + 7 s |
| Exporting a 6 to 8 slide carousel as PNG | 5 to 10 s |

## Voice

edge-tts is free. On ElevenLabs, a 30 s voiceover has 415 to 495 characters (82 to 96 words). At US$ 0.08 per 1,000 characters on the multilingual v2, v3 and v4 models, each generation costs about US$ 0.04, and the Starter plan (US$ 6/month, 75,000 characters on those models) covers about 150 voiceovers of 30 s. Music from Eleven Music costs US$ 0.15 per minute ([ElevenLabs API pricing](https://elevenlabs.io/pricing/api), checked on Nov 4, 2026).

## Is the Pro plan enough?

Pro (US$ 20/month) and Max (US$ 100/month, with five times Pro's usage) include Claude Code. Both have a 5-hour session limit and a weekly limit, shared between Claude and Claude Code, and Anthropic does not publish how many tokens fit in each window ([Claude Code on Pro and Max](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan), [how usage limits work](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work), [Max plan](https://support.claude.com/en/articles/11049741-what-is-the-max-plan), checked on Nov 4, 2026).

Nobody has tested it on Pro yet, so there is no way to promise how many videos fit in it. Keep an eye on the bars with `/usage` in Claude Code. If you hit the limit in the middle of a video, turn on usage credits or continue after the reset: every step is saved in `projects/<slug>/` and the agent picks up where it left off.

## Caveats on these numbers

- Claude Code only, with Opus 5.5 (`xhigh` effort on both videos, `medium` on the carousel). Codex, Antigravity, Cursor and the others count usage differently and were not measured.
- "Equivalent API cost" is tokens × the Opus 5.5 list price (per million: US$ 4 input, US$ 8 1-hour cache write, US$ 0.20 cache read, US$ 20 output). If you are on a plan, you do not pay this per video; the number is there for comparison.
- More revision rounds, a long session, a large repository to read, web research and higher effort all increase tokens and minutes.
- Rendering ran on the CPU only, with other sessions open on the same machine, so the times are a little pessimistic. Compositions with full-screen photos, blur and grain take much longer (a 62 s one took 6 min 20 s).

::: tip Send your numbers
Measurements on other machines and agents are welcome. Open an [issue on GitHub](https://github.com/eusilvio/motion-cena/issues) with your numbers.
:::
