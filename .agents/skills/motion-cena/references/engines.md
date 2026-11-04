# Animation engines

This skill gives direction (what and when). The engine's official skill gives up-to-date syntax (how). Install/load the one for the chosen engine.

## Comparison

| | HyperFrames (HeyGen) | Remotion | Motion Canvas / Revideo |
|---|---|---|---|
| Language | HTML + CSS + GSAP (also Lottie, Three.js, Anime.js, WAAPI) | React + TS | TS with generators |
| Build | none; `index.html` opens in the browser | Vite/webpack, Studio | Vite |
| Official skills | `npx skills add heygen-com/hyperframes` or plugin `claude plugin marketplace add heygen-com/hyperframes` → `claude plugin install hyperframes@hyperframes` | `npx skills add remotion-dev/skills` | community (davila7) |
| Strengths | Claude writes freely, fluid animation with GSAP, deterministic local render, audio/media skills | mature ecosystem, captions (`@remotion/captions`, whisper.cpp), Lambda, maps, `<Audio>` with per-frame volume | technical explainers, code-driven sync |
| License | Apache-2.0 | Free for individuals and companies of ≤ 3 people; paid license above that | MIT |
| Requirements | Node 22+, FFmpeg | Node 18+, headless Chrome (downloads itself) | Node, FFmpeg |

**Default: HyperFrames** for Reels/free-form motion. **Remotion** when the project is already React, needs reusable data components or rendering at scale, or the user asked for it. Warn about the Remotion license if it is a company of > 3 people.

## HyperFrames: workflow

```bash
cd projects/<slug>/video
npx hyperframes init .            # scaffold
npx hyperframes preview           # live reload no navegador
npx hyperframes lint && npx hyperframes check
npx hyperframes snapshot          # frames para inspeção
npx hyperframes render            # MP4
```
Engine docs, read only the part you need: composition basics in `hyperframes-core/references/` (`minimal-composition.md`, `data-attributes.md`, `determinism-rules.md`, `sub-compositions.md`), effect rules in `hyperframes-animation/rules/`, CLI in `hyperframes-cli`, media in `media-use`. `hyperframes-keyframes` (camera moves) and `hyperframes-audio` (ducking, mix) live in `.agents/skills/` too; open them as documents only when a scene needs them.
Format: root element with id/size; each timed element has the `clip` class with start/duration/track attributes; animation in a **paused** GSAP timeline registered globally so the renderer can seek any frame. Audio as an element with time and volume. Exact attribute names: `hyperframes-core/references/data-attributes.md`.
Mapping: each scene in `timeline.json` → one `clip` with `start = scene.start`, `duration = scene.end - scene.start`; each `anchor` → a label/tween in the GSAP timeline at `anchor.start - 0.12`.

## Remotion: workflow

```bash
npx create-video@latest projects/<slug>/video --template blank   # ou: bun create video
cd projects/<slug>/video && npx skills add remotion-dev/skills
npx remotion studio
npx remotion render <CompId> ../../../creatives/reels/<slug>-<preset>.mp4 --codec h264
```
Skills: `/remotion-best-practices` (umbrella), `/remotion-create`, `/remotion-markup`, `/remotion-captions`, `/remotion-render`, `/remotion-studio`.
Mapping: import `timeline.json`; each scene → `<Sequence from={scene.startFrame} durationInFrames={scene.durationFrames}>`; emphases with `interpolate(frame, [a.startFrame - 4, a.startFrame + 8], [0, 1], {extrapolateRight: 'clamp'})` or `spring({frame: frame - a.startFrame, fps})`. Audio: `<Audio src={staticFile('mix.wav')} />`. Captions: `@remotion/captions` from `words.json`.
Never use CSS transitions/animations or `setTimeout` in Remotion: everything derives from `useCurrentFrame()`.

## Support libraries

| Use | Lib |
|---|---|
| Timeline animation (HTML) | GSAP 3 (free, plugins included: SplitText, MorphSVG, DrawSVG) |
| Animated icons / illustrations | Lottie (`lottie-web`, `@remotion/lottie`); LottieFiles MCP, if connected, to search for animations |
| 3D | Three.js / `@remotion/three` |
| Charts | D3 (scales, shapes) drawing in SVG; avoid chart libs with their own animation |
| Icons | Lucide, Phosphor (SVG) |
| Fonts | Google Fonts / `@remotion/google-fonts` |
| Kinetic text | GSAP SplitText; Remotion: manual split by word/letter |
| Noise/grain | SVG `feTurbulence` or a grain PNG with a per-frame offset |
| Maps | `/remotion-maps` (Mapbox, MapLibre) |

## Local GSAP

Copy GSAP into the project (`assets/vendor/gsap.min.js`, pinned version) and use `<script src="assets/vendor/gsap.min.js">`. With the CDN, an internet outage during the render makes the compiler warn `Failed to download CDN script`, and the video may come out without animation.

```bash
curl -fsSL -o projects/<slug>/video/assets/vendor/gsap.min.js https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js
```
