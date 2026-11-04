# Formats by platform

Source of truth for canvas, fps, duration and safe zone. The machine-readable version is `assets/platforms.json` (read by `scripts/platform_preset.py` and `scripts/qa_video.sh`). Researched in Oct 2026 (safe zones revalidated on 23 Oct 2026 against Meta's and Google's official sources); **revalidate when a platform changes** (update both files together).

## Preset table

| Preset | Platform | Canvas | Aspect ratio | Max duration | Ideal | Safe zone (top / bottom / sides) |
|---|---|---|---|---|---|---|
| **`vertical`** | **Reels + TikTok + Shorts (default)** | 1080×1920 | 9:16 | 3 min | 15–60 s | **288 / 672 / 65 left · 192 right** (the largest for each edge) |
| `ig-reels` | Instagram Reels | 1080×1920 | 9:16 | 3 min | 15–60 s | 269 / 672 / 65 px (14% / 35% / 6%) |
| `ig-stories` | Instagram Stories | 1080×1920 | 9:16 | 60 s per story | 5–15 s per story | 269 / 672 / 65 px |
| `ig-feed` | Instagram Feed | 1080×1350 | 4:5 | 3 min | 15–60 s | 60 px all around |
| `fb-reels` | Facebook Reels | 1080×1920 | 9:16 | 3 min | 15–60 s | 269 / 672 / 65 px |
| `tiktok` | TikTok | 1080×1920 | 9:16 | 10 min | 15–60 s | 160 / 480 / 60 left · 140 right |
| `yt-shorts` | YouTube Shorts | 1080×1920 | 9:16 (or 1:1) | 3 min | 20–60 s | 288 / 672 / 48 left · 192 right (Google, official) |
| `yt-long` | YouTube horizontal | 1920×1080 | 16:9 | 12 h | 1–15 min | 54 / 140 / 96 px + player corners (see rules) |
| `yt-long-4k` | YouTube 4K | 3840×2160 | 16:9 | 12 h | 1–15 min | 108 / 280 / 192 px |
| `linkedin` | LinkedIn feed | 1080×1350 | 4:5 | 15 min | 30–90 s | 60 px all around |
| `square` | Generic feed / X | 1080×1080 | 1:1 | - | 15–60 s | 60 px all around |

Carousels (static slides, no audio): `ig-carousel` 1080×1350 (4:5, up to 20 slides organic, 10 in ads), `ig-carousel-square` 1080×1080, `linkedin-carousel` 1080×1350 exported as PDF. Safe margin 80 px. Details and flow in `references/carousel.md`.

Safe zone = the margins where **critical text, numbers and logo must not go** (inside the safe area the layout is free: use the whole area, not a column; see "Composition" in `brand-and-motion.md`) (the app UI covers them: profile name, caption, like/comment buttons, progress bar). Background, textures and motion can fill the whole screen. **Cards, charts, icons and tags count as content**: they must not touch the zone nor "bleed" out of it as decoration. Verification: `scripts/safe_zone_check.py` (measures the DOM over time) and the `qa_video.sh` contact sheet with the zone painted in.

One vertical video goes to more than one network, so the layout uses `vertical`: the right margin on TikTok (140 px) and Shorts (192 px) is much larger than on Reels (65 px). A layout made only for `ig-reels` gets cut off on TikTok.

## Encoding (all platforms)

- MP4, H.264 High, `yuv420p`, **constant** frame rate, progressive, `+faststart` (moov at the start).
- Audio AAC-LC 48 kHz stereo (YouTube recommends 384 kbps stereo); loudness −14 LUFS, true peak ≤ −1 dBTP.
- Reference bitrate (YouTube, SDR): 1080p 30 fps = 8 Mbps · 1080p 60 fps = 12 Mbps · 1440p = 16 Mbps · 4K 30 fps = 35–45 Mbps.
- 30 fps is the default; 60 fps only if the video has a lot of fast motion (render time and file size double).

## Platform rules

**Instagram Reels / Facebook Reels**
- Full 9:16. Meta recommends 1440×2560 for ads; for organic, 1080×1920 is the standard (the app recompresses it anyway).
- Meta's official safe zone for Reels and Stories: **14% top, 35% bottom, 6% sides** (Meta Ads Guide, checked on 23 Oct 2026: leave at least 14% at the top, 35% at the bottom and 6% on each side). It is conservative (designed for ads with a CTA), but it is the one that guarantees legibility on any device.
- Duration: Reels go up to 3 minutes (Adam Mosseri announcement, Jan 2025). Retention drops fast: aim for 15–60 s.
- The cover (grid frame) is cropped to 3:4/1:1 on the profile: keep the title in the center of the cover frame.

**Instagram Stories**
- Same canvas and safe zone as Reels. Each story shows up to 60 s; a longer video is split into parts.
- Think in a **sequence of cards**: one idea per story (5–15 s), CTA/sticker on the last one. For a longer video, produce N parts cut at sentence ends (`timeline.json` already gives the scene boundaries).
- Leave a free area (≈ lower third) for link/poll stickers if the user will use them.

**TikTok**
- 9:16, minimum 540×960 (official ad spec), up to 10 min.
- Buttons sit on the **right** (like, comment, share) and caption + music at the bottom: larger right margin (140 px) and 480 px at the bottom.
- TikTok publishes an official safe zone file per region (TikTok Ads Help Center → Video ads specifications); the px values above are the approximation for 1080×1920.

**YouTube Shorts**
- Vertical (9:16) or square, **up to 3 minutes** (Shorts uploaded since 15/10/2024).
- **Warning**: a Short longer than 1 minute with a Content ID claim (licensed music) is blocked globally. With third-party music → keep it ≤ 60 s; tracks from the Shorts audio library can be used for up to 90 s.
- Official safe zone (Google, "Universal Video Ad Safe Zones", vertical 1080×1920): **288 px top, 672 px bottom, 48 px left, 192 px right** (like/comment/share column on the right). Free area ≈ 840×960 px. Applies to Shorts, TV, desktop and tablet.
- To **not** become a Short, use 16:9.

**YouTube horizontal**
- 16:9; YouTube accepts other aspect ratios but adds bars on desktop. Never put black bars in the video itself.
- The layout changes: horizontal text, column hierarchy, smaller captions (see "Adapting the layout to the canvas"). The bottom 140 px strip sits under the player bar when paused.
- Google's official safe zone for horizontal 1920×1080 (for ads, but it shows where the player places things): the free area **is not a rectangle**, it has cut-out corners. Minimum margins 38 px (top and left), 152 px (right), 143 px (bottom, in the center). Occupied corners: **top-left 352×166** (title/channel), **top-right 433×133**, **bottom-left 856×337** (ad info and buttons), **bottom-right 658×190 and 463×309** (skip ad). In `assets/platforms.json` as `safe_corners`. For organic: keep critical text out of these corners whenever possible; the preset uses 54 / 140 / 96 px as the general margin.
- End screen: only in the last 5–20 s, video ≥ 25 s, up to 4 elements. Leave free space and time at the end if the user will use it.
- Also generate a **thumbnail** 1280×720 (JPG/PNG, up to 2 MB, minimum width 640): a strong frame from the video + a short title.
- A long video (> 3 min) needs chapters: list the scene timestamps in the delivery text.

**LinkedIn**
- Accepts 1:2.4 to 2.4:1, 256×144 to 4096×2304, 10–60 fps, 3 s to 15 min, up to 5 GB.
- 4:5 (1080×1350) takes up more screen in the mobile feed; 16:9 for talk/desktop content. More sober tone; captions on (muted autoplay).

## Adapting the layout to the canvas

| Item | Vertical 1080×1920 | 4:5 1080×1350 | Square 1080×1080 | Horizontal 1920×1080 |
|---|---|---|---|---|
| Title | 90–160 px | 80–130 px | 72–120 px | 72–120 px |
| Body / labels | ≥ 56 px | ≥ 48 px | ≥ 44 px | ≥ 40 px |
| Hero number | 200–400 px | 180–320 px | 160–280 px | 180–320 px |
| Captions | 60–70 px, lower third above the safe zone | 52–60 px | 48–56 px | 44–52 px, centered, more than 140 px above the bottom |
| Composition | 1 column, vertical stack | 1 column, more compact | center | 2 columns (visual × text), natural split screen |
| Words on screen | ≤ 6 | ≤ 6 | ≤ 5 | ≤ 10 |

**One story, several formats**: the narration, `words.json` and `timeline.json` stay the same; only the composition (`video/`) and the preset change. Produce the main format first, get it approved, then recompose the others (`projects/<slug>/video-<preset>/`) and render each one to `creatives/reels/<slug>-<preset>.mp4`.

## Usage in the scripts

```bash
uv run scripts/platform_preset.py ig-stories          # imprime canvas, fps, zona segura e limites
uv run scripts/platform_preset.py --list              # todos os presets
bash scripts/qa_video.sh creatives/reels/<slug>-ig-stories.mp4 ig-stories   # QA contra o preset (canvas, fps, duração máx.)
```

## Sources

- Meta Ads Guide: Instagram Stories video: https://www.facebook.com/business/ads-guide/update/video/instagram-story (9:16, 1440×2560, safe zone 14% / 35% / 6%)
- Meta Ads Guide: Instagram Reels video: https://www.facebook.com/business/ads-guide/update/video/instagram-reels (9:16, up to 15 min in ads, same safe zone)
- Instagram Help: Reel size & aspect ratios: https://help.instagram.com/1038071743007909 (1.91:1 to 9:16, min. 30 fps and 720 px)
- YouTube Help: Recommended upload encoding settings: https://support.google.com/youtube/answer/1722171 (codecs, bitrates)
- YouTube Help: Resolution & aspect ratios: https://support.google.com/youtube/answer/6375112 (16:9, do not add bars)
- YouTube Help: Three-minute Shorts: https://support.google.com/youtube/answer/15424877 (up to 3 min, Content ID rule > 1 min)
- TikTok Ads Help: Video ads specifications: https://ads.tiktok.com/help/article/video-ads-specifications (9:16 ≥ 540×960, up to 10 min, ≤ 500 MB, safe zone file)
- Meta Ads Guide: Instagram Feed carousel: https://www.facebook.com/business/ads-guide/update/carousel/instagram-feed (2–10 cards in ads, 4:5 image only, min. 1080×1080, JPG/PNG up to 30 MB)
- Organic carousel up to 20 items (Instagram announcement, Aug 2024; coverage by TechRadar / Social Media Today)
- LinkedIn Help: Video specs: https://www.linkedin.com/help/linkedin/answer/a548372
- Google: Universal Video Ad Safe Zones (PDF with horizontal, vertical and square PNG overlays): https://services.google.com/fh/files/misc/universalsafezones-youtube.pdf (vertical 288 / 672 / 48 / 192 px; horizontal with cut-out corners)
- YouTube Help: End screens: https://support.google.com/youtube/answer/6388789 (last 5–20 s, video ≥ 25 s, up to 4 elements)
- Secondary (no accessible official page): Reels up to 3 min (Adam Mosseri announcement, press coverage Jan 2025); TikTok safe zone px (approximation of the official file); YouTube thumbnail 1280×720.
