---
title: Carousel
description: The same idea as slides, without narration, as PNG for Instagram or PDF for LinkedIn. How to turn it on, presets, structure and what comes out.
---

<script setup>
import PresetTable from "../../.vitepress/theme/components/safezone/PresetTable.vue";
</script>

# Carousel

Carousel mode uses the same content and delivers static slides instead of a narrated video. It has no narration, voiceover, timeline or sound. The flow becomes brief, slide plan, design and export.

## How to turn it on

Any of these turns carousel mode on:

- the request says "carousel", "carrossel", "slides for Instagram", "swipe post" or includes `--carrossel`;
- the material comes from a content calendar with the format "Carrossel";
- you ask for it *"also as a carousel"*: then the video and the carousel come out of the same brief.

Without any of these, the default is video. When the content calls for a carousel and you said nothing, the agent recommends it in one line and follows what you asked for.

| Content | Best output |
|---|---|
| informative, data, commented news, step by step, list, comparison, reference guide | carousel: people read at their own pace, save and share |
| campaign, launch, offer with several benefits | carousel in the feed, with an optional short video |
| story, motivational, tone of voice matters, demonstration in motion | video |

## Presets

<PresetTable locale="en" kind="carousel" />

All slides share the same aspect ratio: the first one sets the crop for the rest. The safe margin exists because the app overlays the counter and icons on the edges.

## Structure

1. **Cover (slide 1).** A hook with a trigger, which opens a question and pulls the swipe. A cover that gives away the post's conclusion fails: people must leave it wanting slide 2.
2. **Slide 2 gets straight to the point.** Instagram shows the carousel again, opening on slide 2, to people who did not interact. So it works as a second cover: a strong title and complete meaning for someone who never saw the first one.
3. **Body (2 to 6 slides).** One idea per slide, a short title and up to about 40 words. Whenever one exists, a screenshot, screen, photo or mockup of what the text describes. Each slide ends with a line that pulls to the next one.
4. **Turn or synthesis (1 slide).** The idea that justifies the post.
5. **Ending.** Follows the post's intent: a question, a request to save or share, or a free material tied to the post, if it actually exists. Always with the @ and the data source.

The text goes through `lint_copy.py`, numbers have a source and emoji stays out, the post caption included.

## Two engines, one source

| Engine | When | Output |
|---|---|---|
| **Local** (HyperFrames to PNG) | any agent | `creatives/carrossel/<slug>-<preset>/01.png … NN.png`, `contact.jpg` and, for LinkedIn, `carousel.pdf` |
| **Claude Design** | only in a Claude agent with the Artifact tool | an editable canvas on claude.ai, one artboard per slide |

Both start from the same source: the `.dc.html` artboards, kept in `projects/<slug>/carousel/claude-design/project/`. The local engine converts that source, so the PNG comes out identical to the canvas. Without the Artifact tool, the agent writes the artboards the same way and uses only the local engine.

```bash
S=.agents/skills/motion-cena/scripts
uv run $S/dc_to_carousel.py projects/<slug>/carousel/claude-design/project --out projects/<slug>/carousel/render --preset ig-carousel
(cd projects/<slug>/carousel/render && npx hyperframes check)
uv run $S/render_carousel.py projects/<slug>/carousel/render --slides 7 --out creatives/carrossel/<slug>-ig-carousel
```

Before running, the brand fonts go in `projects/<slug>/carousel/render/assets/fonts/`.

::: tip Publish to Claude Design only once
The agent iterates by looking at the local render's `contact.jpg` and publishes to Claude Design when the slides are approved, or when you ask for the editable canvas. Each publish adds about 20 thousand tokens to the conversation, and every later request pays for them again.
:::

## What comes out

- One PNG per slide and `contact.jpg` in `creatives/carrossel/<slug>-<preset>/`.
- `carousel.pdf` on the LinkedIn preset (or with `--pdf`).
- `legenda.txt`: the post caption, 3 to 5 lines, whose first line is another version of the hook.
- `alt-text.txt`: the alt text for each slide.
- The link to the Claude Design canvas, if the agent has the tool.

Exporting 6 to 8 slides takes 5 to 10 s on the machine measured in [Time and cost](/en/guide/cost-and-time).
