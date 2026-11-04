<script setup lang="ts">
/**
 * The landing's one orchestrated moment: a 9:16 stage over an edit-suite timeline.
 * One paused GSAP timeline holds every stage animation; its time is always set from the
 * playhead (play, drag, click, keys), frame-quantized like the render, so seeking to the
 * same instant in any order gives the same frame.
 */
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import type { HeroCopy } from "./i18n";
import { barsPath, envelope, wordBars } from "./waveform";

const props = defineProps<{ hero: HeroCopy; decimal: string; uid: string }>();

const FPS = 30;
const SPS = 40;
const PAPER = "#f2efe8";
const AMBER = "#f2b33d";
const INK = "#0f1012";

const h = props.hero;
const D = h.duration;
const words = h.words;
const lastFrame = Math.round(D * FPS);

const env = envelope(words, D, SPS);
const waveN = env.length;
const wavePath = barsPath(env);
const anchorOf = new Map(h.anchors.map((a) => [a.word, a]));
const slam = h.anchors.find((a) => a.effect === "slam")!;
const punch = h.anchors.find((a) => a.effect === "punch zoom")!;
const stageBars = wordBars(env, words[slam.word], SPS, 18);
const punchFrame = Math.round(words[punch.word].s * FPS);

const pct = (t: number) => `${((t / D) * 100).toFixed(4)}%`;
const span = (a: number, b: number) => `${(((b - a) / D) * 100).toFixed(4)}%`;
const num = (n: number) => n.toFixed(2).replace(".", props.decimal);
const p2 = (n: number) => String(n).padStart(2, "0");
function timecode(f: number) {
  const s = Math.floor(f / FPS);
  return `00:${p2(Math.floor(s / 60))}:${p2(s % 60)}:${p2(f % FPS)}`;
}
const sceneName = (label: string, id: string) => label.replace(new RegExp(`^${id}\\s*`), "");
const rulerTicks = (() => {
  let d = "";
  for (let f = 0; f <= lastFrame; f += 5) d += `M${f} 26v-${f % 30 === 0 ? 11 : f % 15 === 0 ? 7 : 4}`;
  return d;
})();
const rulerLabels = Array.from({ length: Math.floor(D) }, (_, i) => i);

// ---------------------------------------------------------------- time state
const time = ref(0);
const playing = ref(false);
const frame = computed(() => Math.min(lastFrame, Math.round(time.value * FPS)));
const tcNow = computed(() => timecode(frame.value));
const tcTotal = timecode(lastFrame);
const current = computed(() => words.findIndex((w) => time.value >= w.s && time.value < w.e));
const shown = computed(() => {
  if (current.value >= 0) return current.value;
  let k = 0;
  words.forEach((w, i) => {
    if (time.value >= w.s) k = i;
  });
  return k;
});
const inspector = computed(() => {
  const w = words[shown.value];
  return { word: w.w, start: String(w.s), end: String(w.e) };
});
const activeScene = computed(() => {
  const t = Math.min(time.value, D - 1e-6);
  return h.scenes.findIndex((s) => t >= s.start && t < s.end);
});
const anchorState = (word: number, dur: number) => {
  const s = words[word].s;
  if (time.value < s) return "";
  return time.value <= s + dur ? "is-firing" : "is-done";
};
const sfxActive = (s: number, e: number) => time.value >= s && time.value <= e;

// ---------------------------------------------------------------- refs
const stageEl = ref<HTMLElement>();
const scrollEl = ref<HTMLElement>();
const lanesEl = ref<HTMLElement>();
const wordBtns = ref<HTMLButtonElement[]>([]);
const focusIdx = ref(0);

type Tl = { time: (t: number, suppress?: boolean) => unknown; kill: () => void };
let tl: Tl | null = null;
let reduced = false;
let touched = false;
let raf = 0;
let lastNow = 0;
let dragging = false;
let io: IntersectionObserver | null = null;
let autoTimer: ReturnType<typeof setTimeout> | undefined;
let gone = false;

function seek(t: number, snap = false) {
  let v = Math.max(0, Math.min(D, t));
  if (snap) v = Math.round(v * FPS) / FPS;
  time.value = v;
  tl?.time(Math.round(v * FPS) / FPS, false);
}

function step(now: number) {
  const dt = Math.min(0.1, (now - lastNow) / 1000);
  lastNow = now;
  const t = time.value + dt;
  if (t >= D) {
    seek(D);
    playing.value = false;
    return;
  }
  seek(t);
  follow();
  raf = requestAnimationFrame(step);
}
function play() {
  if (playing.value) return;
  if (time.value >= D - 0.5 / FPS) seek(0);
  playing.value = true;
  lastNow = performance.now();
  raf = requestAnimationFrame(step);
}
function pause() {
  playing.value = false;
  cancelAnimationFrame(raf);
}
function touch() {
  touched = true;
  clearTimeout(autoTimer);
}
function togglePlay() {
  touch();
  if (playing.value) pause();
  else play();
}

/** keep the playhead in view when the timeline scrolls sideways (narrow screens) */
function follow() {
  const sc = scrollEl.value;
  const lanes = lanesEl.value;
  if (!sc || !lanes || sc.scrollWidth <= sc.clientWidth + 1) return;
  const sr = sc.getBoundingClientRect();
  const lr = lanes.getBoundingClientRect();
  // playhead x inside the visible part of the scroller; the sticky labels cover [0, labelW]
  const x = lr.left - sr.left + (time.value / D) * lr.width;
  const labelW = sc.querySelector<HTMLElement>(".labels")?.offsetWidth ?? 0;
  if (x > sc.clientWidth - 48 || x < labelW + 8) {
    sc.scrollLeft = Math.max(0, sc.scrollLeft + x - labelW - (sc.clientWidth - labelW) * 0.25);
  }
}

// ------------------------------------------------------------- scrubbing
function timeFromX(clientX: number) {
  const r = lanesEl.value!.getBoundingClientRect();
  return ((clientX - r.left) / r.width) * D;
}
function scrubStart(e: PointerEvent) {
  if (e.button !== 0) return;
  e.preventDefault();
  touch();
  pause();
  dragging = true;
  (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  seek(timeFromX(e.clientX), true);
}
function scrubMove(e: PointerEvent) {
  if (dragging) seek(timeFromX(e.clientX), true);
}
function scrubEnd() {
  dragging = false;
}
/** mouse can scrub from any empty spot of the lanes; touch keeps them for scrolling */
function lanesDown(e: PointerEvent) {
  if (e.pointerType !== "mouse") return;
  if ((e.target as HTMLElement).closest("button, [role='slider']")) return;
  scrubStart(e);
}

function onHandleKey(e: KeyboardEvent) {
  let f = frame.value;
  const n = e.shiftKey ? 10 : 1;
  switch (e.key) {
    case "ArrowRight":
    case "ArrowUp":
      f += n;
      break;
    case "ArrowLeft":
    case "ArrowDown":
      f -= n;
      break;
    case "PageUp":
      f += FPS;
      break;
    case "PageDown":
      f -= FPS;
      break;
    case "Home":
      f = 0;
      break;
    case "End":
      f = lastFrame;
      break;
    case " ":
    case "k":
    case "K":
      e.preventDefault();
      togglePlay();
      return;
    default:
      return;
  }
  e.preventDefault();
  touch();
  pause();
  seek(Math.max(0, Math.min(lastFrame, f)) / FPS);
}

function jumpTo(i: number) {
  touch();
  focusIdx.value = i;
  const w = words[i];
  if (reduced) {
    // no playback on its own: land on the settled frame right after the word
    pause();
    const a = anchorOf.get(i);
    seek(Math.max(w.e, a ? w.s + a.dur : 0), true);
  } else {
    pause();
    seek(w.s, true);
    play();
  }
}
function onWordKey(e: KeyboardEvent, i: number) {
  let k = i;
  if (e.key === "ArrowRight") k = Math.min(words.length - 1, i + 1);
  else if (e.key === "ArrowLeft") k = Math.max(0, i - 1);
  else if (e.key === "Home") k = 0;
  else if (e.key === "End") k = words.length - 1;
  else return;
  e.preventDefault();
  focusIdx.value = k;
  wordBtns.value[k]?.focus();
}

// --------------------------------------------------------- GSAP timeline
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function build(gsap: any): Tl {
  const st = stageEl.value!;
  const q = (t: number) => Math.round(t * FPS) / FPS;
  const all = (sel: string) => Array.from(st.querySelectorAll<HTMLElement>(sel));
  const scenes = all(".scene");
  const drifts = all(".drift");
  const punches = all(".punch");

  // the t = 0 state, set explicitly; every tween below is fromTo with immediateRender off,
  // so building never paints a later state and any seek order resolves to the same frame
  gsap.set(scenes, { autoAlpha: 0, yPercent: 0 });
  gsap.set(scenes[0], { autoAlpha: 1 });
  gsap.set(all(".w-in"), { yPercent: 108, autoAlpha: 0, scale: 1 });
  gsap.set(all(".w-tint"), { color: PAPER });
  gsap.set(all(".tag"), { autoAlpha: 0, yPercent: -40 });
  gsap.set(all(".hl"), { scaleX: 0, transformOrigin: "0% 50%", autoAlpha: 1 });
  gsap.set(all(".bars i"), { scaleY: 0, autoAlpha: 1 });
  gsap.set(all(".fc"), { autoAlpha: 0, y: 8 });
  gsap.set(drifts, { scale: 1 });
  gsap.set(punches, { scale: 1, transformOrigin: "50% 42%" });
  gsap.set(all(".flash"), { opacity: 0 });

  const tl = gsap.timeline({ paused: true });
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const ft = (el: any, from: object, to: object, at: number) =>
    tl.fromTo(el, from, { ...to, immediateRender: false }, at);
  // a decaying wobble that starts and ends at 0, so the shake is seek-safe
  const wobble = (p: number) => Math.sin(p * Math.PI * 5) * (1 - p);

  // something always moves: slow push-in per scene
  h.scenes.forEach((sc, i) =>
    ft(drifts[i], { scale: 1 }, { scale: 1.045, duration: q(sc.end) - q(sc.start), ease: "sine.inOut" }, q(sc.start)),
  );

  // words enter on their own timestamp; the spoken word is tinted while it lasts
  words.forEach((w, i) => {
    const el = st.querySelector<HTMLElement>(`.w[data-wi="${i}"]`);
    if (!el) return;
    const inner = el.querySelector(".w-in");
    const tint = el.querySelector(".w-tint");
    const a = anchorOf.get(i);
    const t0 = q(w.s);
    const t1 = q(w.e);
    if (a?.effect === "slam") {
      ft(inner, { scale: 2.4, yPercent: 0, autoAlpha: 0 }, { scale: 1, yPercent: 0, autoAlpha: 1, duration: 0.22, ease: "power4.out" }, t0);
      ft(el, { xPercent: 0 }, { xPercent: 5, duration: 0.32, ease: wobble }, t0 + 0.2);
    } else {
      ft(inner, { yPercent: 108, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: 0.2, ease: "power3.out" }, t0);
    }
    if (a?.effect === "highlight") {
      ft(el.querySelector(".hl"), { scaleX: 0 }, { scaleX: 1, duration: 0.4, ease: "power2.out" }, t0);
      ft(tint, { color: PAPER }, { color: INK, duration: 0.12, ease: "none" }, t0 + 0.06);
    } else {
      ft(tint, { color: PAPER }, { color: AMBER, duration: 0.05, ease: "none" }, t0);
      ft(tint, { color: AMBER }, { color: PAPER, duration: 0.16, ease: "none" }, t1);
    }
  });

  // scene cuts: push up into s2, wipe up into s3
  const c1 = q(h.scenes[1].start);
  const c2 = q(h.scenes[2].start);
  ft(scenes[0], { yPercent: 0, autoAlpha: 1 }, { yPercent: -12, autoAlpha: 0, duration: 0.24, ease: "power2.in" }, c1 - 0.18);
  ft(scenes[1], { yPercent: 12, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: 0.3, ease: "power3.out" }, c1);
  ft(
    scenes[2],
    { clipPath: "inset(100% 0% 0% 0%)", autoAlpha: 1 },
    { clipPath: "inset(0% 0% 0% 0%)", autoAlpha: 1, duration: 0.32, ease: "power3.inOut" },
    c2 - 0.12,
  );
  ft(scenes[1], { autoAlpha: 1 }, { autoAlpha: 0, duration: 0.02, ease: "none" }, c2 + 0.22);

  // emphasis, each on its anchor word's frame
  for (const a of h.anchors) {
    const ta = q(words[a.word].s);
    if (a.effect === "slam") {
      ft(all(".bars i"), { scaleY: 0 }, { scaleY: 1, duration: 0.3, ease: "power3.out", stagger: 0.018 }, ta + 0.04);
    } else if (a.effect === "stagger") {
      ft(all(".tag"), { autoAlpha: 0, yPercent: -40 }, { autoAlpha: 1, yPercent: 0, duration: 0.25, ease: "power3.out", stagger: 0.07 }, ta);
    } else if (a.effect === "punch zoom") {
      const p = punches[2];
      ft(p, { scale: 1 }, { scale: 1.12, duration: 0.25, ease: "power4.out" }, ta);
      ft(p, { scale: 1.12 }, { scale: 1.05, duration: 0.4, ease: "power2.inOut" }, ta + 0.25);
      ft(all(".flash"), { opacity: 0 }, { opacity: 0.32, duration: 0.04, ease: "none" }, ta);
      ft(all(".flash"), { opacity: 0.32 }, { opacity: 0, duration: 0.3, ease: "power2.out" }, ta + 0.04);
      ft(all(".fc"), { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.2, ease: "power3.out" }, ta + 0.06);
      const n = st.querySelector(".fc-n");
      const c = { v: 0 };
      ft(
        c,
        { v: 0 },
        {
          v: punchFrame,
          duration: 0.5,
          ease: "power2.out",
          onUpdate: () => {
            if (n) n.textContent = String(Math.round(c.v)).padStart(3, "0");
          },
        },
        ta + 0.06,
      );
    }
  }
  tl.set({}, {}, D);
  return tl as Tl;
}

onMounted(async () => {
  reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const mod = await import("gsap");
  if (gone) return;
  tl = build(mod.gsap ?? mod.default);
  if (reduced && !touched) seek(D);
  else seek(time.value);
  if (reduced || !stageEl.value) return;
  io = new IntersectionObserver(
    (entries) => {
      if (!entries.some((e) => e.isIntersecting)) return;
      io?.disconnect();
      if (!touched) autoTimer = setTimeout(() => !touched && play(), 350);
    },
    { threshold: 0.6 },
  );
  io.observe(stageEl.value);
});

onBeforeUnmount(() => {
  gone = true;
  cancelAnimationFrame(raf);
  clearTimeout(autoTimer);
  io?.disconnect();
  tl?.kill();
});
</script>

<template>
  <div class="hero">
    <div class="hero-copy">
      <slot />
    </div>

    <!-- program monitor: the vertical frame the timeline drives -->
    <figure class="monitor">
      <div ref="stageEl" class="stage" aria-hidden="true">
        <div class="ui">
          <i v-for="k in 4" :key="k" class="ui-btn" :style="{ top: `${57 + k * 6.6}%` }" />
          <i class="ui-av" />
          <i class="ui-l1" />
          <i class="ui-l2" />
        </div>
        <div v-for="(sc, si) in h.scenes" :key="sc.id" class="scene" :class="`scene-${si}`">
          <div class="punch">
            <div class="drift">
              <div class="safe">
                <div class="block">
                  <div v-for="(line, li) in sc.lines" :key="li" class="line" :class="{ big: line.big }">
                    <span
                      v-for="wi in line.words"
                      :key="wi"
                      class="w"
                      :class="{ 'no-mask': anchorOf.get(wi)?.effect === 'slam' }"
                      :data-wi="wi"
                    >
                      <span v-if="anchorOf.get(wi)?.effect === 'highlight'" class="hl" />
                      <span class="mask"><span class="w-in"><span class="w-tint">{{ words[wi].w }}</span></span></span>
                      <span v-if="si === 1" class="tag">{{ num(words[wi].s) }}</span>
                    </span>
                  </div>
                  <div v-if="si === 0" class="bars">
                    <i v-for="(b, bi) in stageBars" :key="bi" :style="{ height: `${Math.round(b * 100)}%` }" />
                  </div>
                  <div v-if="si === 2" class="fc">{{ h.frameLabel }} <span class="fc-n">000</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="flash" />
      </div>
      <figcaption class="sr-only">{{ h.srStage }}</figcaption>
    </figure>

    <!-- the timeline -->
    <div class="tl-wrap">
      <div class="tl" role="group" :aria-label="h.suiteLabel">
        <div class="transport">
          <button type="button" class="t-play" :aria-label="playing ? h.pause : h.play" @click="togglePlay">
            <svg v-if="!playing" viewBox="0 0 16 16" aria-hidden="true"><path d="M4.5 2.8v10.4L13 8z" /></svg>
            <svg v-else viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3h3v10H4zM9 3h3v10H9z" /></svg>
          </button>
          <span class="t-tc"><span class="tc-now">{{ tcNow }}</span><span class="tc-total">{{ tcTotal }}</span></span>
          <span class="t-json" :class="{ 'is-live': current >= 0 }" aria-hidden="true">
            <span class="j">{"word": </span><span class="v">"{{ inspector.word }}"</span><span class="j">, "start": </span
            ><span class="v">{{ inspector.start }}</span><span class="j">, "end": </span><span class="v">{{ inspector.end }}</span
            ><span class="j">}</span>
          </span>
        </div>

        <div ref="scrollEl" class="tl-scroll">
          <div class="tl-grid">
            <div class="labels" aria-hidden="true">
              <span class="lb lb-ruler" />
              <span class="lb lb-voice">{{ h.tracks.voice }}</span>
              <span class="lb lb-scene">{{ h.tracks.scene }}</span>
              <span class="lb lb-emph">{{ h.tracks.emphasis }}</span>
              <span class="lb lb-sfx">{{ h.tracks.sfx }}</span>
            </div>

            <div ref="lanesEl" class="lanes" @pointerdown="lanesDown" @pointermove="scrubMove" @pointerup="scrubEnd" @pointercancel="scrubEnd">
              <!-- ruler -->
              <div class="row r-ruler" @pointerdown.stop="scrubStart" @pointermove="scrubMove" @pointerup="scrubEnd" @pointercancel="scrubEnd">
                <svg class="ticks" :viewBox="`0 0 ${lastFrame} 26`" preserveAspectRatio="none" aria-hidden="true">
                  <path :d="rulerTicks" />
                </svg>
                <span v-for="s in rulerLabels" :key="s" class="tick-l" :style="{ left: pct(s) }">{{ s }} s</span>
              </div>

              <!-- voice: word clips over the waveform -->
              <div class="row r-voice" role="toolbar" :aria-label="h.wordsLabel">
                <svg class="wave" :viewBox="`0 0 ${waveN} 100`" preserveAspectRatio="none" aria-hidden="true">
                  <defs>
                    <clipPath :id="`${uid}-played`"><rect x="0" y="0" :width="(time / D) * waveN" height="100" /></clipPath>
                  </defs>
                  <path class="wave-base" :d="wavePath" />
                  <path class="wave-played" :d="wavePath" :clip-path="`url(#${uid}-played)`" />
                </svg>
                <button
                  v-for="(w, i) in words"
                  :key="i"
                  ref="wordBtns"
                  type="button"
                  class="clip-w"
                  :class="{ 'is-current': i === current, 'is-past': time >= w.e }"
                  :style="{ left: pct(w.s), width: span(w.s, w.e) }"
                  :tabindex="i === focusIdx ? 0 : -1"
                  :aria-label="`${w.w} ${num(w.s)} s`"
                  @click="jumpTo(i)"
                  @keydown="onWordKey($event, i)"
                >
                  <span>{{ w.w }}</span>
                </button>
              </div>

              <!-- scenes -->
              <div class="row r-scene" aria-hidden="true">
                <span
                  v-for="(sc, si) in h.scenes"
                  :key="sc.id"
                  class="clip-s"
                  :class="{ 'is-active': si === activeScene }"
                  :style="{ left: pct(sc.start), width: span(sc.start, sc.end) }"
                >
                  <b>{{ sc.id }}</b> {{ sceneName(sc.label, sc.id) }}
                </span>
              </div>

              <!-- emphasis markers, pinned to their words -->
              <div class="row r-emph" aria-hidden="true">
                <span
                  v-for="a in h.anchors"
                  :key="a.word"
                  class="mk"
                  :class="anchorState(a.word, a.dur)"
                  :style="{ left: pct(words[a.word].s) }"
                >
                  <i class="pin" />
                  <i class="dia" />
                  <span class="mk-l">{{ a.effect }}</span>
                </span>
              </div>

              <!-- sound effects -->
              <div class="row r-sfx" aria-hidden="true">
                <span
                  v-for="(x, xi) in h.sfx"
                  :key="xi"
                  class="clip-x"
                  :class="[`x-${x.type}`, { 'is-active': sfxActive(x.s, x.e) }]"
                  :style="{ left: pct(x.s), width: span(x.s, x.e) }"
                >
                  <svg v-if="x.type === 'riser'" class="ramp" viewBox="0 0 100 10" preserveAspectRatio="none"><path d="M0 10L100 0V10z" /></svg>
                  <span class="x-l">{{ x.type }}</span>
                </span>
              </div>

              <!-- playhead -->
              <div class="ph" :style="{ left: pct(time) }">
                <i class="ph-line" />
                <span
                  class="ph-handle"
                  role="slider"
                  tabindex="0"
                  :aria-label="h.playhead"
                  aria-valuemin="0"
                  :aria-valuemax="lastFrame"
                  :aria-valuenow="frame"
                  :aria-valuetext="tcNow"
                  @pointerdown.stop="scrubStart"
                  @pointermove="scrubMove"
                  @pointerup="scrubEnd"
                  @pointercancel="scrubEnd"
                  @keydown="onHandleKey"
                ><i /></span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <p class="tl-caption">{{ h.caption }}</p>
    </div>
  </div>
</template>

<style scoped>
.hero {
  --stage-w: clamp(204px, 20vw, 258px);
  --r-ruler: 26px;
  --r-voice: 60px;
  --r-scene: 32px;
  --r-emph: 30px;
  --r-sfx: 30px;
  --label-w: 80px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  grid-template-areas:
    "copy monitor"
    "tl tl";
  column-gap: clamp(28px, 5vw, 80px);
  row-gap: 26px;
}
.hero-copy {
  grid-area: copy;
  align-self: end;
  min-width: 0;
}
.monitor {
  grid-area: monitor;
  margin: 0;
}
.tl-wrap {
  grid-area: tl;
  min-width: 0;
}

/* ------------------------------------------------------------------ stage */
.stage {
  position: relative;
  width: var(--stage-w);
  aspect-ratio: 9 / 16;
  container-type: inline-size;
  overflow: hidden;
  border-radius: var(--mc-radius-frame);
  background: #0a0b0c;
  box-shadow: 0 0 0 1px var(--mc-rule);
  color: var(--mc-paper);
  isolation: isolate;
}
.ui i {
  position: absolute;
  display: block;
  border-color: var(--mc-paper);
  opacity: 0.13;
}
.ui-btn {
  right: 4.6%;
  width: 7.5cqw;
  height: 7.5cqw;
  border: 0.55cqw solid;
  border-radius: 50%;
}
.ui-av {
  left: 5%;
  top: 87.2%;
  width: 7.5cqw;
  height: 7.5cqw;
  border-radius: 50%;
  background: var(--mc-paper);
}
.ui-l1,
.ui-l2 {
  left: 5%;
  height: 1.6cqw;
  border-radius: 1cqw;
  background: var(--mc-paper);
}
.ui-l1 {
  top: 92.6%;
  width: 52cqw;
}
.ui-l2 {
  top: 95.4%;
  width: 34cqw;
}
.scene {
  position: absolute;
  inset: 0;
  visibility: hidden;
}
.scene-0 {
  visibility: visible;
}
.punch,
.drift {
  position: absolute;
  inset: 0;
}
/* the vertical preset's safe area (288 / 672 px of 1920; content centered on x = 540) */
.safe {
  position: absolute;
  top: 15%;
  bottom: 35%;
  left: 17.8%;
  right: 17.8%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.line {
  display: flex;
  gap: 0.22em;
  white-space: nowrap;
  font-family: var(--mc-font-display);
  font-size: 12.8cqw;
  line-height: 1.04;
  letter-spacing: 0.004em;
}
.line.big {
  font-size: 22cqw;
  line-height: 1;
  margin-top: 0.03em;
}
.scene-1 .line {
  margin-bottom: 0.46em;
}
.w {
  position: relative;
  display: inline-block;
}
.mask {
  position: relative;
  z-index: 1;
  display: inline-block;
  overflow: hidden;
  padding: 0.1em 0.03em 0.08em;
  margin: -0.1em -0.03em -0.08em;
  vertical-align: top;
}
.no-mask .mask {
  overflow: visible;
}
.w-in {
  display: inline-block;
  visibility: hidden;
}
.hl {
  position: absolute;
  inset: 0.04em -0.08em 0.02em;
  z-index: 0;
  background: var(--mc-paper);
  visibility: hidden;
}
.tag {
  position: absolute;
  left: 0.03em;
  top: 100%;
  margin-top: 0.12em;
  font: 500 3.3cqw/1 var(--mc-font-mono);
  letter-spacing: 0.02em;
  color: var(--mc-tungsten);
  visibility: hidden;
}
.bars {
  display: flex;
  align-items: center;
  gap: 1.15cqw;
  height: 9cqw;
  margin-top: 5cqw;
}
.bars i {
  display: block;
  width: 1.5cqw;
  border-radius: 0.5cqw;
  background: var(--mc-paper);
  opacity: 0.78;
  visibility: hidden;
}
.fc {
  margin-top: 3.4cqw;
  font: 500 4.1cqw/1 var(--mc-font-mono);
  letter-spacing: 0.02em;
  color: var(--mc-tungsten);
  visibility: hidden;
}
.flash {
  position: absolute;
  inset: 0;
  background: var(--mc-paper);
  opacity: 0;
  pointer-events: none;
}

/* --------------------------------------------------------------- timeline */
.tl {
  border-radius: 6px;
  background: var(--mc-graphite-2);
  box-shadow: 0 0 0 1px var(--mc-rule);
  color: var(--mc-paper);
  overflow: hidden;
}
.transport {
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 48px;
  padding: 6px 14px 6px 8px;
  border-bottom: 1px solid var(--mc-rule);
}
.t-play {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  flex: none;
  border-radius: 4px;
  color: var(--mc-paper);
  transition: background-color 0.15s;
}
.t-play:hover {
  background: var(--mc-graphite-3);
}
.t-play svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}
.t-tc {
  display: flex;
  align-items: baseline;
  gap: 10px;
  font-family: var(--mc-font-mono);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.tc-now {
  font-size: 15px;
  font-weight: 500;
  color: var(--mc-tungsten);
}
.tc-total {
  font-size: 12px;
  color: #6f6b64;
}
.t-json {
  margin-left: auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font: 12px/1.4 var(--mc-font-mono);
  font-variant-numeric: tabular-nums;
  opacity: 0.55;
  transition: opacity 0.12s;
}
.t-json.is-live {
  opacity: 1;
}
.t-json .j {
  color: #6f6b64;
}
.t-json .v {
  color: var(--mc-paper);
}

.tl-scroll {
  overflow-x: auto;
  overscroll-behavior-x: contain;
  scrollbar-width: thin;
  scrollbar-color: var(--mc-rule) transparent;
}
.tl-grid {
  display: grid;
  grid-template-columns: var(--label-w) minmax(calc(var(--hero-dur, 8) * 104px), 1fr);
}
.labels {
  position: sticky;
  left: 0;
  z-index: 6;
  display: grid;
  grid-template-rows: var(--r-ruler) var(--r-voice) var(--r-scene) var(--r-emph) var(--r-sfx);
  background: var(--mc-graphite-2);
  border-right: 1px solid var(--mc-rule);
}
.lb {
  display: flex;
  align-items: center;
  padding-left: 14px;
  font-size: 12.5px;
  color: var(--mc-paper-dim);
  border-bottom: 1px solid #22252a;
}
.lb-sfx {
  border-bottom: 0;
}
.lanes {
  position: relative;
  margin-right: 14px;
  user-select: none;
}
.row {
  position: relative;
  border-bottom: 1px solid #22252a;
}
.r-sfx {
  border-bottom: 0;
}
.r-ruler {
  height: var(--r-ruler);
  cursor: ew-resize;
  touch-action: none;
}
.ticks {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.ticks path {
  stroke: #4a4e55;
  stroke-width: 1;
  vector-effect: non-scaling-stroke;
}
.tick-l {
  position: absolute;
  top: 3px;
  padding-left: 4px;
  font: 10.5px/1 var(--mc-font-mono);
  color: #7d786f;
  pointer-events: none;
}
.r-voice {
  height: var(--r-voice);
}
.r-scene {
  height: var(--r-scene);
}
.r-emph {
  height: var(--r-emph);
}
.r-sfx {
  height: var(--r-sfx);
}

.wave {
  position: absolute;
  left: 0;
  width: 100%;
  top: 24px;
  height: calc(100% - 31px);
  pointer-events: none;
}
.wave-base {
  fill: #4b4f56;
}
.wave-played {
  fill: rgba(242, 179, 61, 0.62);
}
.clip-w {
  position: absolute;
  top: 6px;
  bottom: 7px;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding: 4px 0 0 5px;
  overflow: hidden;
  border-radius: var(--mc-radius-clip);
  box-shadow: inset 0 0 0 1px #363a41;
  background: rgba(34, 37, 42, 0.38);
  text-align: left;
  font: 500 11.5px/1.2 var(--mc-font-body);
  color: var(--mc-paper-dim);
  white-space: nowrap;
  cursor: pointer;
  transition:
    box-shadow 0.12s,
    background-color 0.12s,
    color 0.12s;
}
.clip-w span {
  display: block;
  overflow: hidden;
  text-overflow: clip;
}
.clip-w:hover {
  box-shadow: inset 0 0 0 1px #5a5e66;
  color: var(--mc-paper);
}
.clip-w.is-past {
  color: #cfcac0;
}
.clip-w.is-current {
  box-shadow: inset 0 0 0 1.5px var(--mc-tungsten);
  background: rgba(242, 179, 61, 0.14);
  color: var(--mc-paper);
}
.clip-w:focus-visible {
  outline: 2px solid var(--mc-paper);
  outline-offset: 1px;
  z-index: 3;
}

.clip-s {
  position: absolute;
  top: 5px;
  bottom: 5px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 9px;
  overflow: hidden;
  border-radius: var(--mc-radius-clip);
  background: #1f2226;
  box-shadow: inset 0 0 0 1px #30343a;
  font-size: 12px;
  color: var(--mc-paper-dim);
  white-space: nowrap;
}
.clip-s + .clip-s {
  margin-left: 2px;
}
.clip-s b {
  font: 500 11px var(--mc-font-mono);
  color: #7d786f;
}
.clip-s.is-active {
  box-shadow:
    inset 0 2px 0 var(--mc-tungsten),
    inset 0 0 0 1px #3a3e45;
  background: #24272c;
  color: var(--mc-paper);
}
.clip-s.is-active b {
  color: var(--mc-tungsten);
}

.mk {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 0;
}
.pin {
  position: absolute;
  left: -0.5px;
  bottom: calc(50% + 5px);
  height: calc(var(--r-scene) + 7px + 10px);
  border-left: 1px dashed #5d6168;
}
.dia {
  position: absolute;
  left: -5px;
  top: calc(50% - 5px);
  width: 10px;
  height: 10px;
  transform: rotate(45deg);
  border: 1.5px solid var(--mc-paper-dim);
  background: var(--mc-graphite-2);
}
.mk-l {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: var(--mc-paper-dim);
  white-space: nowrap;
}
.mk.is-firing .dia {
  border-color: var(--mc-tungsten);
  background: var(--mc-tungsten);
}
.mk.is-firing .pin {
  border-left: 1px solid var(--mc-tungsten);
}
.mk.is-firing .mk-l {
  color: var(--mc-paper);
}
.mk.is-done .dia {
  background: var(--mc-paper-dim);
}

.clip-x {
  position: absolute;
  top: 7px;
  bottom: 7px;
  min-width: 3px;
  border-radius: 2px;
  background: #2a2d33;
  box-shadow: inset 0 0 0 1px #393d44;
}
.clip-x.is-active {
  box-shadow: inset 0 0 0 1.5px var(--mc-tungsten);
}
.x-riser {
  background: transparent;
  box-shadow: inset 0 -1px 0 #393d44;
}
.x-riser.is-active {
  box-shadow: inset 0 -1.5px 0 var(--mc-tungsten);
}
.ramp {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.ramp path {
  fill: #2f3238;
}
.x-riser.is-active .ramp path {
  fill: rgba(242, 179, 61, 0.28);
}
.x-l {
  position: absolute;
  left: calc(100% + 6px);
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: var(--mc-paper-dim);
  white-space: nowrap;
}
.x-whoosh .x-l,
.x-riser .x-l {
  left: 7px;
}
.clip-x.is-active .x-l {
  color: var(--mc-paper);
}

.ph {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 0;
  z-index: 5;
  pointer-events: none;
}
.ph-line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: -1px;
  width: 2px;
  background: var(--mc-tungsten);
}
.ph-handle {
  position: absolute;
  top: 0;
  left: -12px;
  width: 24px;
  height: 24px;
  display: grid;
  place-items: start center;
  pointer-events: auto;
  cursor: ew-resize;
  touch-action: none;
  border-radius: 3px;
}
.ph-handle i {
  display: block;
  width: 13px;
  height: 17px;
  margin-top: 2px;
  background: var(--mc-tungsten);
  clip-path: polygon(0 0, 100% 0, 100% 62%, 50% 100%, 0 62%);
}
.ph-handle:focus-visible {
  outline: 2px solid var(--mc-paper);
  outline-offset: 1px;
}

.tl-caption {
  max-width: 76ch;
  margin: 12px 0 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--vp-c-text-2);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 767px) {
  .hero {
    --stage-w: min(56vw, 232px);
    --label-w: 70px;
    grid-template-columns: minmax(0, 1fr);
    grid-template-areas:
      "copy"
      "monitor"
      "tl";
    row-gap: 22px;
  }
  .monitor {
    justify-self: center;
  }
  .lb {
    padding-left: 10px;
    font-size: 12px;
  }
  .transport {
    flex-wrap: wrap;
    row-gap: 2px;
  }
  .t-json {
    flex-basis: 100%;
    margin-left: 0;
    padding: 0 0 4px 8px;
    font-size: 11.5px;
  }
}
</style>
