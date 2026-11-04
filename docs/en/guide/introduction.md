---
title: What it is
description: A motion-design video pipeline driven by a coding agent, from the request to the MP4, with the speech setting the timing.
---

# What motion-cena is

motion-cena is a motion-design video pipeline driven by a coding agent. You send the idea. The agent writes the script, records the voiceover, animates every scene on the beat of the speech and delivers an MP4 ready to post.

![Five dictionary effects rendered by the pipeline: scramble, line reveal, count-up, parallax and zoom through](../../dicionario.gif)

## Why it exists

Asking a model to "make a nice video" produces random animation that has nothing to do with the narration. motion-cena works like a small production company: first it decides which story to tell, in which format and what each scene shows. Only then does it animate.

- **The speech sets the timing.** The voiceover comes before the animation. Every word gets a timestamp, and every emphasis fires on the frame where that word is spoken.
- **One visual idea per video.** Each piece is built around its own device (an ID card, a dashboard, a page), chosen from three concepts. The system vetoes anything that repeats earlier videos.
- **Every step writes a file.** You can stop, review and ask for only the part that changed: "switch the hook", "make the story version".
- **Nothing sits under the buttons.** A checker steps through the video every quarter of a second and fails any text, card or logo that enters the area covered by the Reels, TikTok or Shorts interface. Try it in the [safe-zone playground](/en/reference/platforms).

## What goes in

Almost anything can become a video. The agent works out the input mode from what you sent:

| You send | What happens |
|---|---|
| a text or script of yours | becomes a video script: keeps the facts, the intent and the sentences in your voice; adjusts the duration, the hook and the ending |
| a text with "use it exactly as it is" | word-for-word narration |
| topics, bullets, a transcript | organizes them into a story, picks a format and writes the script |
| just the subject | web research with sources, then the script |
| PDF, report, article, URL | reads all of it and pulls the best excerpts, with the source page |
| spreadsheet, CSV, numbers | finds the story in the numbers; each number gets a visual |
| a recorded voiceover | transcribes it with timestamps and animates over that voice |
| a video of someone speaking | the footage and the voice are the base; the motion goes on top |
| the path to a repository | facts, screens and brand come from the product's code |

## What comes out

- **Video**: one MP4 per platform (Reels, Stories, TikTok, Shorts, YouTube, LinkedIn), with voiceover, sound effects and, if you want, burned-in captions.
- **Carousel**: the same idea as slides, without narration, as PNG for Instagram or PDF for LinkedIn. See [Carousel](/en/reference/carousel).

The repository ships blank: no brand, voice or persona from anyone. Each video's identity comes from the request (a website, colors, the product's code, the recording of whoever is speaking) or grows out of the video's central idea.

## Under the hood

The animation runs on [HyperFrames](https://github.com/heygen-com/hyperframes), which renders HTML, CSS and GSAP to video. The motion vocabulary comes from a dictionary with 44 curated effects and a catalog of 388, which you can [browse here](/en/effects). The agent can be Claude Code, Codex, Antigravity, Cursor, GitHub Copilot, OpenCode, Windsurf or any other that reads files and runs commands: see [Any agent](/en/guide/agents).

With no API key at all, the whole pipeline runs, with free voice through edge-tts and sound effects synthesized on your machine.

## Next steps

1. [Install](/en/guide/installation) Node, FFmpeg, uv and your agent.
2. Make your [first video](/en/guide/first-video).
3. Learn [each step of the pipeline](/en/guide/how-it-works) and the files it writes.

Code and docs under the MIT License. The animation engine, HyperFrames, is Apache-2.0.
