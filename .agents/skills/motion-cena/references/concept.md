# Central idea (before the storyboard)

A video that illustrates sentence by sentence (each sentence gets an icon, a number or a big word) always comes out the same, whatever the subject: big caption, line icon, dark background, one element at a time. What makes a video memorable is **a single visual idea** in which the whole script happens. Example: a video about sleep doesn't need a moon, bed and clock icon; it can happen entirely in a dark bedroom lit only by the phone screen, and the suspense, the turn and the end are changes in that scene (the screen goes dark, the morning light comes in).

This step comes after the script and before the storyboard. The storyboard serves the idea; the ladder in `visual-mapping.md` becomes support for details inside it.

## Step 1: the script's mechanism

Answer in `plan.md`, section "Central idea":

- **What the viewer should feel**, in one word (curiosity, tension, laughter, pride, discomfort, relief).
- **Where the turn is** (the sentence where something changes) and what changes.
- **What is concrete** in the story: objects, places, gestures, numbers, routines. That is where the image lives.
- **What the relationship with the viewer is**: just watches, is challenged, is fooled and then finds out, participates (counts along, chooses, waits).

## Step 2: three ideas that don't look alike

Write 3 central ideas. Each one has a **device** (the world where the video happens) and decides the axes below. The three must differ from each other on at least 4 axes.

| Axis | Options (expand, don't limit yourself) |
|---|---|
| Device / world | an object in a continuous scene · a page or map the camera travels across · an app screen (chat, spreadsheet, calendar, bank, GPS) · a stage · a table with papers, cutouts and tape · a newspaper being laid out · a receipt printer · a timeline ruler · a game with a HUD · a building in cross-section · a box that opens · two screens side by side · a single number that changes meaning |
| Technique / medium | kinetic typography · realistic object with shadow · paper collage · interface (UI) · technical diagram or blueprint · data that assembles itself · cut-out real photo · flat illustration · simple 3D · wireframe · pixel grid · text as architecture |
| Camera | fixed shot · one continuous take (push-in, pan, travelling) · hard cuts on the beat · zoom that enters a detail and exits into another world · camera orbiting an object · split screen |
| Light and palette | light background (paper, off-white) · dark background · strong flat color · duotone · monochrome with one accent · changes at the turn |
| Role of text | the on-screen narration is the visual · discreet caption · text inside the world (sign, screen, paper, message) · almost no text |
| Time structure | starts in silence (image and sound only) · starts at the end and goes back · rising pace up to an impact · slow breathing with a single cut · countdown · perfect loop |
| Relationship with the viewer | watches · is challenged ("você ficou 7 segundos olhando", you stared for 7 seconds) · finds out they were fooled · completes the sentence · waits for something that only happens at the end |

For each idea, a one-sentence pitch ("a vida dele é um cupom fiscal que vai saindo da impressora, um item por profissão": his life is a receipt coming out of the printer, one line item per job) and how the **start and the end** connect inside the device.

## Step 3: veto what repeats

Check every video already delivered, on the same axes, without reading the whole log: `uv run scripts/registro.py --counts` (most used values per axis) and `uv run scripts/registro.py --recent 12` (latest rows). Open `creatives/registro.md` itself only when a veto is unclear. If it doesn't exist yet (the person's first video), create it from `assets/registro.template.md`; it is local and stays out of git. Veto the idea that:
- uses the same device as any previous video;
- repeats 3 or more axes of one of the last 3 videos;
- falls into the "house default" (dark background + big serif + line icon + word-by-word caption) without the script asking for exactly that.

If all three are vetoed, write new ones. Don't take old video folders as a starting point: they show what has already been done, not what to do.

## Step 4: choose and defend

Choose the idea that best serves the mechanism from step 1 and record it in `plan.md`: device, axes, pitch, why it is born from this script (and wouldn't work for any other), how it opens, where it turns, how it ends. Acid test: if the idea would fit any script, it is decoration; go back to step 2.

## Step 5: the storyboard lives inside the idea

- Every scene happens in the device (or in a transformation of it). No "loose" scene with an icon in the middle of the screen.
- The details of each sentence (flag, logo, number, photo) come in **as objects of the world**: the logo printed on the paper, the number on the app screen, the photo taped to the table.
- Layout, camera, caption position, background and typography come from the idea, not from a default. The user's brand, when there is one, comes in as color and font on top of the idea.
- After delivery, add the video's row to `creatives/registro.md`.
