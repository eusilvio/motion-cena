# Visual reading of the script (visual map)

A **mandatory** step between script and storyboard, in both video and carousel. The goal is for every image on screen to reference directly what is being said and to make sense within the story. Nothing decorative, nothing generic.

Final test for each scene: **"without the audio, does the image still tell what this sentence says?"** If it does not, change the visual.

> **Emoji is forbidden** in any piece: artwork, on-screen text, captions, post caption, end card. It looks amateurish. Use a real symbol, line icon, illustration, photo or typography.

## Step 1: Read each sentence in five layers

For each passage (scene or slide), answer in writing:

| Layer | Question | Example ("Estudou balé na escola do Bolshoi aqui no Brasil" (studied ballet at the Bolshoi school here in Brazil)) |
|---|---|---|
| **Entities** | who/what has a proper name? (person, country, company, institution, award, place) | Bolshoi (school), Brasil (country) |
| **Concrete** | what object, place or physical action appears? | balé → ballerina, pointe shoes |
| **Number** | is there a quantity, value, date, ranking? | - |
| **Idea** | what is the concept behind it? which of the piece's metaphors does it feed? | discipline, stage (the "art" half of the ballet × exact sciences metaphor) |
| **Tone** | what emotion and energy? | admiration, elegance → smooth motion, warm light |

## Step 2: Choose **one** main visual by the ladder (within the central idea)

The ladder resolves the detail of each sentence; the central idea (`concept.md`) decides the video's world. The visual chosen here enters as an object of that world (the logo printed on the paper, the number on the app screen), never as a loose icon in the middle of the screen. A line icon is the last resort, not the default.

Climb the ladder until you find the first rung that applies. The most concrete one wins:

0. **Real photo/video sent by the user** (the person in the story, the place, the product): always wins. Keep the original untouched in `projects/<slug>/source/media/`, work on copies in `video/assets/photos/`. Treatments: cutout of the person without the background (`media-use` removes the background, or `hyperframes remove-background`), frame/polaroid, slow Ken Burns, mask revealing on the word, duotone in the brand color to unify photos from different sources. Face inside the safe zone. Ask the user whether they have photos when the video is about a real person; without photos, follow the ladder.
1. **Real symbol** of a named entity: flag, official logo, medal (`references/iconography.md`).
2. **Concrete object/action**: line icon or illustration/silhouette (`assets/visual-lexicon.json`, `fetch_icon.py icon|image`).
3. **Free photo** when the real place/person/scene matters and a license exists (`fetch_icon.py image --category photograph`).
4. **Data visual** when there is a number: count-up, bar, comparison (`brand-and-motion.md`).
5. **Abstract metaphor** of the piece (the curve, the grid, the dot out of line) when the sentence is pure idea.
6. Pure **typography** when the sentence is a question or a strong statement: the word itself is the image.

Rules:
- **1 main visual + at most 1 supporting visual** per scene/slide.
- The visual enters **on the word** that justifies it (anchor in `timeline.json`).
- **One visual family per piece**: same icon set and weight, same illustration language (e.g. only flat silhouettes in the brand color), photos with the same treatment.
- The piece's **recurring metaphor** appears at the start, returns at the turn and closes at the end; the concrete visuals serve it, they do not compete with it.
- Avoid stock-image clichés (light bulb for "idea", handshake for "partnership", rocket for everything) when there is something more specific in the sentence.
- Brand identity rules: colors, "no emoji", "no ornament". Icons and silhouettes recolored in the brand color; real symbols (flag, logo) keep their original colors.

## Step 3: Record the visual map

In `plan.md`, before the storyboard:

| # | Passage | Reads as | Chosen visual | Rung | Source / command | Why |
|---|---|---|---|---|---|---|
| s1 | "...o café nasceu na Etiópia?" (coffee was born in Ethiopia?) | origin | Ethiopian flag next to "Etiópia" | 1 real symbol | `flag et` | the country is the hook |
| s2 | "Diz a lenda que um pastor viu as cabras agitadas..." (legend says a shepherd saw his goats agitated) | story, discovery | goat silhouette, in the brand color | 2 concrete | `image goat --category illustration --license cc0,pdm` | the character of the legend |
| s3 | "Hoje são 2 bilhões de xícaras por dia" (today it is 2 billion cups a day) | scale | count-up + line-icon cup | 4 data + 2 | `icon coffee` | the number is the hero, the cup gives the unit |
| s4 | "e uma rede de cafeterias virou sinônimo disso" (and a coffee shop chain became synonymous with it) | company | official logo of the chain cited | 1 real symbol | `logo <marca>` (check the current version) | immediate recognition |

In `storyboard.json`, each scene carries its items in `icons` (`kind`: flag, logo, icon, image) with `role` naming the trigger word.

## Step 4: Search and check

```bash
S=.agents/skills/motion-cena/scripts
uv run $S/fetch_icon.py search <termo>                      # nomes em Phosphor, Lucide e Simple Icons
uv run $S/fetch_icon.py image "<termo em inglês>" --category illustration --license cc0,pdm   # lista candidatos
uv run $S/fetch_icon.py image "<termo>" --category illustration --license cc0,pdm --pick N --out <dir>
uv run $S/fetch_icon.py icon <nome> [--set lucide] [--weight fill] [--color "#HEX"] --out <dir>
uv run $S/fetch_icon.py flag <iso2> --out <dir>
uv run $S/fetch_icon.py logo <slug> [--commons "<arquivo>.svg"] --out <dir>
```

- Image search works better in **English** ("ballerina", "pointe shoes", "telescope").
- **Look** at the candidates before choosing (download 3–4 into a temporary folder, build a contact board and look at it). Choose the cleanest one, most consistent with the visual family.
- Prefer CC0/public domain. CC BY requires credit in the piece (end card, last slide or post caption). Avoid BY-SA and NC.
- Single-color PNG silhouette: **pre-color the file** in the brand color (works the same in the video, in Claude Design and in the local carousel render):
  ```bash
  convert image-ballerina.png -alpha extract -background "#FF8A3D" -alpha shape image-ballerina-accent.png
  ```
  In video only (own HTML), CSS `mask` also works:
  ```css
  .silhouette { background: var(--accent); -webkit-mask: url(assets/icons/image-ballerina.png) center / contain no-repeat; mask: url(assets/icons/image-ballerina.png) center / contain no-repeat; }
  ```
- SVG line icon: `--color` on download, or inline with `stroke="currentColor"`.

## Reading examples (other genres)

- **Technical**: "o banco de dados faz uma busca na tabela inteira" (the database scans the whole table) → `magnifying-glass` icon sweeping across a grid of rows (data visual + concrete), not a "brain".
- **Motivational**: "você acorda às cinco enquanto todo mundo dorme" (you wake up at five while everyone sleeps) → `moon` + a clock showing 5:00 in typography; no generic smiling person.
- **Faith/family**: "a igreja sabia quem chegava, não quem sumia" (the church knew who arrived, not who disappeared) → `church` + a row of dots in which some go out (metaphor), not praying hands.
- **Business**: "levei 3 anos de anúncio pra juntar 100 dólares" (it took me 3 years of ads to make 100 dollars) → count-up "US$ 100" + a calendar with 3 years going by; `money` only if the number is missing.
- **News**: "a empresa passou de 1 bilhão de lucro" (the company passed 1 billion in profit) → official company logo + count-up; no piggy bank.

## QA

- [ ] Every scene/slide has a row in the visual map, with the reason
- [ ] Each visual passes the "without audio, does it tell the sentence?" test
- [ ] Named entities with a real symbol; concrete objects with an icon/illustration; abstract only where it is the metaphor
- [ ] One visual family; brand colors; **no emoji anywhere**
- [ ] Licenses in `CREDITS.md`; CC BY credits present in the piece
