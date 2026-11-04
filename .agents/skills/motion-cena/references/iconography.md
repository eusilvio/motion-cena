# Icons, real symbols and images

Complements `references/visual-mapping.md` (which decides **what** to show in each sentence). This file covers **how** to search, style and license.

> **Emoji is forbidden** in any piece (artwork, on-screen text, captions, post caption, end card). No exceptions: it looks amateurish. `fetch_icon.py` does not even offer emoji.

**Golden rule:** when the speech or text mentions something with a recognizable symbol, show the real symbol. "japonesa" (Japanese) → the flag of Japan. "ouro" (gold) → a gold medal. "NASA", "Spotify" → official logo. Never hand-draw a real symbol: download it with `scripts/fetch_icon.py`, which saves the file and records source and license in `CREDITS.md`.

## What to use

| The speech/text mentions | Show | `fetch_icon.py` |
|---|---|---|
| Country, nationality, national team | **official flag** (4:3; `--ratio 1x1` in a circle) | `flag br` · `flag us` · `flag pt` |
| Award, placement (gold, silver, bronze, champion) | **medal/trophy** as a filled icon in the metal's color | `icon medal --weight fill --color "#D4A72C"` (gold) · `#A8A9AD` (silver) · `#B87333` (bronze) · `icon trophy --weight fill --color "#D4A72C"` |
| Company, university, app, product, media outlet | **official logo** | `logo <slug>` (Simple Icons) → otherwise `logo <slug> --commons "<arquivo>.svg"` |
| Common object, place or concept | **line icon** in the brand color | `icon <nome>` (Phosphor) · `--set lucide` · names in `assets/visual-lexicon.json`; `search <termo>` |
| Human action/figure (dance, sport, work) | recolored CC0 **illustration/silhouette** | `image "<termo em inglês>" --category illustration --license cc0,pdm` |
| Real place, real scene | **free photo** with credit | `image "<termo>" --category photograph` |
| Real person | photo **with usage rights** (from the user, or CC with credit); no photo → name in typography | never generate a real person's face with AI |

### When NOT to use

- The concept is the piece's metaphor: it stays abstract on purpose.
- More than 2 visuals per scene/slide turns into a collage.
- A visual that is not in the speech or text: do not decorate with it.
- A logo in a context that suggests a nonexistent partnership/endorsement; party or politician logos.

## Style and consistency

- **One family per piece**: one icon set (Phosphor *or* Lucide) in the same weight; illustrations in the same style (e.g. flat silhouettes); photos with the same treatment.
- Icons and silhouettes **in the brand color**: icon with `--color` on download; pre-colored PNG silhouette (`convert … -alpha extract -background "#HEX" -alpha shape …`). CSS `mask` in video only.
- Single-color logo that disappears against the background: `logo … --commons "…" --color "#F6F1EA"` generates the mono version (the script refuses to recolor a multicolor logo).
- **Real symbols keep their real colors**: flags and multicolor logos do not change color, are not distorted, and get no shadow/outline. Dark mono logo on a dark background → mono version in the text color (`--color "#F6F1EA"`) or a light chip behind it; contrast ≥ 3:1.
- Medal/trophy: filled icon in the metal's color + the word ("ouro", "1º") in typography next to it.
- Sizes on vertical 1080 px: icon 120–240 px; flag 160–280 px wide; logo 80–160 px tall; silhouette 300–600 px tall. Inside the preset's safe zone.
- Flag with 6–8 px rounded corners or a thin border so it does not "bleed" into the background.

## Motion (video)

It enters **on the word** that mentions it (anchor in `timeline.json`): flag `pop in` or `mask reveal`; medal `pop in` + a short `glow`; silhouette `draw-on` of the outline or `slide in`; logo with a sober `fade in`/`slide in` (no bounce on logos). Terms in `motion-dictionary.md`.

## Using the files

- Video: download to `projects/<slug>/video/assets/icons/` and use `<img src="assets/icons/flag-br.svg" alt="Bandeira do Brasil">`.
- Local carousel: `projects/<slug>/carousel/render/assets/icons/`.
- **Claude Design**: upload each file as a canvas asset (`asset: true`) and write `<img data-asset="flag-br.svg" src="/_blob/<id>" alt="…">`. `dc_to_carousel.py` swaps the `src` for the local file at render time.

## Licenses and credits

| Source | License | What to do |
|---|---|---|
| flag-icons | MIT | `CREDITS.md` only |
| Phosphor / Lucide | MIT / ISC | `CREDITS.md` only |
| Openverse CC0 / public domain | free | `CREDITS.md` only |
| Openverse CC BY | attribution | credit in the piece (end card, last slide or post caption) |
| Simple Icons / Wikimedia Commons (logos) | free file, **registered trademark** | referential use only; check that it is the current logo (`fetch_icon.py` warns when Commons redirects to an old version) |

Avoid CC BY-SA and NC.

## QA

- [ ] Every named entity has its real symbol; every relevant concrete object has an icon/illustration (or a reason in the visual map)
- [ ] No redrawn symbol; logo undistorted and current
- [ ] One visual family, brand colors; **no emoji**
- [ ] `CREDITS.md` present; CC BY credits in the piece
