---
title: First video
description: How to ask the agent for your first video, what it shows you before spending credits, what comes out at the end and how to iterate.
---

# First video

With the agent open at the repository root, talk to it the way you would talk to a video editor. A short request already triggers the whole flow:

```text
Make a 30 s Reels explaining compound interest. Research the facts.
```

Write in any language: the agent understands the request and delivers in the language you wrote in, voiceover included.

## Example requests

| You ask | You get |
|---|---|
| *"Make a 30 s Reels explaining compound interest. Research the facts."* | sourced research, a script with 3 hooks, voiceover, animation and the MP4 for Reels and TikTok |
| *"Turn this PDF into a data video in my website's style."* | the best numbers from the report, with the source page, in the website's colors and fonts |
| *"Analyze the app in ../loja and make a 40 s product video."* | facts, screens and brand taken from the code itself, without reading `.env` or production data |
| *"Animate over this video of me talking, with word-by-word captions."* | your recording as the base, with captions, keywords and cards in the rhythm of the speech |
| *"Narrate this text as a Story video. Use the text exactly as it is."* | word-for-word narration, with no adaptation of the text |
| *"Make it a 7-slide carousel."* | a cover with a hook, one slide per idea, a PNG per slide, post caption and alt text |

Say the platform ("story", "Reels", "TikTok", "YouTube") and, if you like, the duration. Without a duration, the agent uses the preset's default: 30 s for Reels and TikTok, 15 s for Stories, 40 s for Shorts, 90 s for YouTube and 45 s for LinkedIn. Reels, TikTok or Shorts with no platform specified become the `vertical` preset, which serves all three.

## Motion direction

If you already know how you want the motion, use the formula **effect + duration + ease + target**. The agent translates each term through the dictionary, without reinterpreting:

```text
Title enters with a slide in, 0.4 s ease out, benefits with a 0.15 s stagger.
Swap "idea" for "video" with a text swap. End with a punch zoom on the product.
```

The effect names are in the [effects explorer](/en/effects).

## Before spending credits, the plan

The agent does not start recording a voice right away. First it writes `plan.md`: the chosen narrative format, the script with 3 hooks, the central idea (and the two it discarded) and the storyboard scene by scene. Then it stops and asks for your approval before spending voice credits and render time.

Read it, ask for changes to what you don't like and approve it. If you asked it to *"do it all in one go"*, it skips the review and notes that in the plan.

## What comes out at the end

- The MP4 in `creatives/reels/<slug>-<preset>.mp4`. For a vertical video, the same file comes out as `-ig-reels.mp4` and `-tiktok.mp4`.
- The `projects/<slug>/` folder with every step: brief, plan, storyboard, brand, voiceover, timeline, composition and mix.
- A report in the chat with the path of each MP4, the requested and actual duration, what changed in your script and why, the central idea, the hook used and the alternatives, the voice provider, what was left out and suggestions for the next version.

None of this goes to git: `projects/` and `creatives/` stay on your machine.

## Iterating

Every step writes a file, so a change only redoes what changed:

| You ask | The agent redoes |
|---|---|
| *"Switch to hook B"* | the scene 1 voice, the timeline and the render |
| *"Add sound effects"* or *"drop the music"* | only the sound and the render |
| *"Change the title entrance to a 0.5 s blur in"* | only that effect line and the render |
| *"Make it faster"* | voice 5% faster, shorter scenes and more cuts |
| *"Make the YouTube version"* in 16:9 | the layout at 1920×1080, with the same narration and the same timeline |
| *"Split it into 3 stories"* | three parts cut at sentence ends |

::: tip One piece per session
Every request makes the agent reread the whole conversation. In the measured sessions, a second piece in the same conversation cost 35% to 41% of that session. Finished a video? Open a new session (`/clear` in Claude Code). Everything is saved in `projects/<slug>/`, and the agent picks up where it left off. Revisions to the same piece can stay in the same session. More in [Time and cost](/en/guide/cost-and-time).
:::

## Watching the edit live (optional)

Ask *"I want to watch it live"* and, during the animation step, the agent opens HyperFrames Studio as soon as the first scene exists. Studio reloads on every saved file: you watch the video come together scene by scene, with a timeline, playback and manual editing. Clicked an element and said "change this"? The agent reads the Studio selection and knows what you pointed at. If you don't ask, it works quietly and delivers the MP4.

For chat and video on the same screen, start the project's interface:

```bash
node tools/studio/server.mjs        # opens http://127.0.0.1:4400
```

On the left is the chat with Claude Code, Codex or Antigravity, with each command and file showing up as it happens. On the right, the Studio of the project being edited, with tabs for the script, storyboard and final video. Across the top, the pipeline steps light up as the files appear.

::: warning Automatic approval
The interface listens only on `127.0.0.1` and requires a token per run, but it runs the agent with automatic approval: a web page has no way to answer its permission prompts. Use it on your own machine, in repositories you trust.
:::
