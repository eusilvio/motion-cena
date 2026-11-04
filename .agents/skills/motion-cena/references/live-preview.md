# Live preview (optional)

**Off by default.** Only open the HyperFrames Studio when:
- the request asks for it ("quero ver ao vivo", "abre o preview", "me mostra montando", "abre no Studio", "I want to watch it live"); or
- the user wants to point on screen at what to change ("vou te mostrar no Studio", "abre que eu aponto"); or
- you are inside the `tools/studio` interface (`MOTION_CENA_UI=1`): there the interface itself starts the preview; you just do not open a browser.

Without any of these, do not start a preview server or open a browser, not even at the end: the "Open the final Studio preview" step of the `hyperframes-cli` skill does not apply here. Visual review comes from the snapshot sheet and the contact sheet (steps 6 and 8), and the MP4 path goes in the delivery. At the end, offer it in one line ("quer abrir no Studio para ajustar à mão?", in the user's language).

When it is on: as soon as `projects/<slug>/video/index.html` exists (even with just the background and the first scene), open the Studio and keep it open until delivery. It reloads on every saved file, so whoever asked watches the video being built:

```bash
cd projects/<slug>/video
npx hyperframes preview --status --json        # one already running? use its studioUrl
npx hyperframes preview --background          # otherwise: start it and open the browser; add --no-open when MOTION_CENA_UI=1 (the motion-cena interface already shows it)
npx hyperframes preview --status --json        # gets the studioUrl (http://127.0.0.1:<port>/#project/video)
```

- On: send the `studioUrl` to the user **right away**, before continuing to animate. Inside `tools/studio` (`MOTION_CENA_UI=1`) the preview shows up by itself next to the chat; no browser needed.
- On: build **scene by scene** and save after each one (layout, then entrance, then emphasis) instead of writing the whole HTML at the end: every save becomes a visible step. Use small edits, not full rewrites.
- A request pointing at something in the Studio ("muda isso", "esse texto") → `npx hyperframes preview --context --json --context-fields selection` tells what was clicked (file, element, time).
- Do not start a second server for the same project. At the end, leave it running and say how to stop it (`npx hyperframes preview --stop`).
