---
title: Platforms and safe zones
description: Each network's presets, the zone the app interface covers and how motion-cena checks that nothing important goes into it.
aside: false
---

<script setup>
import PresetTable from "../../.vitepress/theme/components/safezone/PresetTable.vue";
</script>

# Platforms and safe zones

Every network covers part of the video with its own interface: profile name, caption, like and comment buttons, progress bar. That band is the safe zone. Background, texture and motion can fill the whole screen, but text, numbers, cards, icons and logos stay out of it, without touching it even partly.

Pick a preset, drag the block and see the distance to each edge, in canvas pixels.

<SafeZonePlayground locale="en" />

## Presets

Each platform is a preset in `assets/platforms.json`, taken from the official documentation. The table below is generated from that file when the site is built, so it changes along with it.

<PresetTable locale="en" kind="video" />

- **Default** is the duration used when the request does not say how long the video is.
- **Ideal** is the range where retention tends to hold.
- **Max** is the platform's limit. Text longer than that makes the agent warn you and offer to split it into parts, condense it or switch platforms.

To see a preset in the terminal:

```bash
uv run .agents/skills/motion-cena/scripts/platform_preset.py --list
uv run .agents/skills/motion-cena/scripts/platform_preset.py tiktok
```

## One vertical video for three networks

A request for Reels, TikTok or Shorts that does not name the platform uses the `vertical` preset. It takes the most restrictive zone on each edge across `ig-reels`, `tiktok` and `yt-shorts`, so one render serves all three. The agent delivers the same file as `-ig-reels.mp4` and `-tiktok.mp4` (and `-yt-shorts.mp4`, if you ask).

The difference is on the right: Reels reserves 65 px, TikTok 140 px and Shorts 192 px, because of the column of buttons. A layout made only for `ig-reels` gets cut off on TikTok. In the playground, place the title in `ig-reels` and switch to `tiktok`: the block stays where it is and its right edge enters the zone.

::: tip Center on the middle of the canvas
The skill centers content on the canvas's horizontal center (x 540 on vertical), and a title with a number under it counts as a single group. With the right edge at 192 px, a block centered on `vertical` can be at most 696 px wide. The "Center horizontally" button shows this.
:::

## Use the variables in the composition

`platform_preset.py` with `--css` prints the preset's variables. The composition builds the layout inside a container that respects the zone; only background, texture and decoration marked with `data-safe-ignore` go outside it.

```css
.safe {
  position: absolute;
  inset: var(--safe-top) var(--safe-right) var(--safe-bottom) var(--safe-left);
}
```

Text size depends on the canvas too. On vertical 1080×1920: titles from 90 to 160 px, body text 56 px or more, hero numbers from 200 to 400 px, captions from 60 to 70 px just above the zone, up to 6 words on screen. The full table per format is in [`references/platforms.md`](https://github.com/eusilvio/motion-cena/blob/main/.agents/skills/motion-cena/references/platforms.md).

## How the zone is measured

Before the final render, `safe_zone_check.py` opens the composition in a headless Chrome, steps the timeline every 0.25 s and measures the real box of every text, image and box with a background or border:

```bash
uv run .agents/skills/motion-cena/scripts/safe_zone_check.py projects/<slug>/video --preset vertical
```

| Result | When |
|---|---|
| `ERRO` (error) | something stayed in the zone for 0.5 s or longer. The video does not go on to the render. |
| `aviso` (warning) | a quick pass, on an entrance or exit. Check the frame. |

Details the checker takes into account:

- Up to 4 px inside the zone pass (`--tol 4`), so edge antialiasing does not fail. The playground is stricter and flags from 1 px.
- Cards, charts, phone frames, labels and chips count as content.
- A background shape that covers more than 45% of the canvas, or is blurred more than 20 px, is treated as decoration and skipped. For any other decorative element, add `data-safe-ignore`.

Zero `ERRO` is mandatory. After the render, `qa_video.sh` generates the contact sheet with the zone painted red and the outline of the free area: nothing that matters can show up in the red.

## Horizontal YouTube

On 16:9 the free area is not a rectangle. The player covers corners: title and channel at the top left, icons at the top right, info and buttons at the bottom. The `yt-long` preset stores those corners in `safe_corners`, from Google's universal safe zones. The checker only measures the general margins (54 / 140 / 96 px), but the skill asks you to keep important text out of those corners whenever possible. In the playground, the corners are hatched.

## Encoding

Every preset comes out in the same format: MP4 H.264 High, `yuv420p`, constant frame rate, progressive, `+faststart`, AAC-LC 48 kHz stereo audio and −14 LUFS loudness. One narration and one timeline produce every version; only the layout is recomposed.

## Sources

The margins and limits come from the official pages of Meta, Google, TikTok and LinkedIn, researched in October 2026 (Meta's and Google's zones were checked again on Oct 23, 2026). The list of links is at the end of [`references/platforms.md`](https://github.com/eusilvio/motion-cena/blob/main/.agents/skills/motion-cena/references/platforms.md). When a platform changes, both files change together. Other networks still have no preset: see the [open fronts](/en/community/roadmap).
