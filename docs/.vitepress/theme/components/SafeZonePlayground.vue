<script setup lang="ts">
/**
 * Safe-zone playground. Pick a platform preset, drag a block over the canvas and
 * see, in logical canvas pixels, how far it is from each safe edge. The rule is
 * the one safe_zone_check.py applies: nothing that matters may sit in the zone,
 * not even partly. Presets come from the skill's platforms.json at build time.
 * DOM is only touched inside event handlers, so it renders the same on the server.
 */
import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import { data } from "../../data/platforms.data";
import UiSilhouettes from "./safezone/UiSilhouettes.vue";
import { STR, presetLabel, type Kind, type Locale } from "./safezone/i18n";

const props = withDefaults(defineProps<{ locale?: Locale }>(), { locale: "pt" });
const s = computed(() => STR[props.locale]);

const presets = data.video;
const presetId = ref(presets.some((p) => p.id === "vertical") ? "vertical" : presets[0].id);
const preset = computed(() => presets.find((p) => p.id === presetId.value) ?? presets[0]);
const W = computed(() => preset.value.width);
const H = computed(() => preset.value.height);
const S = computed(() => preset.value.safe);
const landscape = computed(() => W.value > H.value);

const kind = ref<Kind>("title");
const showUi = ref(true);
const box = reactive({ x: 0, y: 0, w: 0, h: 0 });

const kinds: Kind[] = ["title", "caption", "card"];

/** starting size and place of each block, in canvas pixels, centered on the canvas's horizontal center */
function place(k: Kind) {
  const { width: w0, height: h0, safe } = preset.value;
  const u = Math.min(w0, h0);
  const freeTop = safe.top;
  const freeH = h0 - safe.top - safe.bottom;
  let w: number, h: number, y: number;
  if (k === "title") {
    w = u * 0.6;
    h = u * 0.27;
    y = freeTop + (freeH - h) * 0.28;
  } else if (k === "caption") {
    w = u * 0.6;
    h = u * 0.13;
    y = h0 - safe.bottom - h - u * 0.03;
  } else {
    w = u * 0.52;
    h = u * 0.4;
    y = freeTop + (freeH - h) * 0.5;
  }
  box.w = Math.round(w);
  box.h = Math.round(h);
  box.x = Math.round(w0 / 2 - w / 2);
  box.y = Math.round(y);
}
place(kind.value);

const clamp = (v: number, lo: number, hi: number) => Math.min(Math.max(v, lo), hi);
const minW = computed(() => Math.round(Math.min(W.value, H.value) * 0.12));
const minH = computed(() => Math.round(Math.min(W.value, H.value) * 0.06));

function moveTo(x: number, y: number) {
  box.x = Math.round(clamp(x, 0, W.value - box.w));
  box.y = Math.round(clamp(y, 0, H.value - box.h));
}
function resizeTo(w: number, h: number) {
  box.w = Math.round(clamp(w, minW.value, W.value - box.x));
  box.h = Math.round(clamp(h, minH.value, H.value - box.y));
}

// same canvas size (every 9:16 preset is 1080x1920): keep the block where it is, so switching
// ig-reels -> tiktok shows what the wider right zone does to the same layout
watch(presetId, (_id, oldId) => {
  const old = presets.find((p) => p.id === oldId);
  if (old && old.width === W.value && old.height === H.value) return;
  place(kind.value);
});
watch(kind, (k) => place(k));

function center() {
  moveTo(W.value / 2 - box.w / 2, box.y);
}

// ---- pointer drag ---------------------------------------------------------
const canvasEl = ref<HTMLElement | null>(null);
let drag: { mode: "move" | "resize"; sx: number; sy: number; b: typeof box; scale: number; id: number } | null = null;
const dragging = ref(false);

function onPointerDown(e: PointerEvent, mode: "move" | "resize") {
  if (e.button !== 0 || !canvasEl.value) return;
  const rect = canvasEl.value.getBoundingClientRect();
  drag = { mode, sx: e.clientX, sy: e.clientY, b: { ...box }, scale: rect.width / W.value, id: e.pointerId };
  (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  (e.currentTarget as HTMLElement).focus({ preventScroll: true });
  dragging.value = true;
  e.preventDefault();
  e.stopPropagation();
}
function onPointerMove(e: PointerEvent) {
  if (!drag || e.pointerId !== drag.id) return;
  const dx = (e.clientX - drag.sx) / drag.scale;
  const dy = (e.clientY - drag.sy) / drag.scale;
  if (drag.mode === "move") moveTo(drag.b.x + dx, drag.b.y + dy);
  else resizeTo(drag.b.w + dx, drag.b.h + dy);
}
function onPointerUp(e: PointerEvent) {
  if (!drag || e.pointerId !== drag.id) return;
  drag = null;
  dragging.value = false;
}

function onKey(e: KeyboardEvent, mode: "move" | "resize") {
  const step = e.shiftKey ? 10 : 1;
  let dx = 0;
  let dy = 0;
  if (e.key === "ArrowLeft") dx = -step;
  else if (e.key === "ArrowRight") dx = step;
  else if (e.key === "ArrowUp") dy = -step;
  else if (e.key === "ArrowDown") dy = step;
  else return;
  e.preventDefault();
  e.stopPropagation();
  if (mode === "move") moveTo(box.x + dx, box.y + dy);
  else resizeTo(box.w + dx, box.h + dy);
}

// ---- measurement: same edges as safe_zone_check.py ------------------------
type Edge = "top" | "bottom" | "left" | "right";
const edges: Edge[] = ["top", "bottom", "left", "right"];

/** distance from the block to each safe edge; negative = that many px inside the zone */
const dist = computed<Record<Edge, number>>(() => ({
  top: box.y - S.value.top,
  bottom: H.value - S.value.bottom - (box.y + box.h),
  left: box.x - S.value.left,
  right: W.value - S.value.right - (box.x + box.w),
}));
const worst = computed(() => Math.max(0, ...edges.map((e) => -dist.value[e])));
const inZone = computed(() => worst.value > 0);

type R = { x: number; y: number; w: number; h: number };
const bands = computed<R[]>(() => {
  const { top, bottom, left, right } = S.value;
  return [
    { x: 0, y: 0, w: W.value, h: top },
    { x: 0, y: H.value - bottom, w: W.value, h: bottom },
    { x: 0, y: top, w: left, h: H.value - top - bottom },
    { x: W.value - right, y: top, w: right, h: H.value - top - bottom },
  ];
});
const cornerRects = computed<R[]>(() => preset.value.corners.map(({ rect: [x, y, w, h] }) => ({ x, y, w, h })));

function intersect(a: R, b: R): R | null {
  const x0 = Math.max(a.x, b.x);
  const y0 = Math.max(a.y, b.y);
  const x1 = Math.min(a.x + a.w, b.x + b.w);
  const y1 = Math.min(a.y + a.h, b.y + b.h);
  return x1 > x0 && y1 > y0 ? { x: x0, y: y0, w: x1 - x0, h: y1 - y0 } : null;
}
const overlaps = computed(() => bands.value.map((b) => intersect(box, b)).filter((r): r is R => !!r));
const cornerHits = computed(() => cornerRects.value.map((c) => intersect(box, c)).filter((r): r is R => !!r));

const fmt = (v: number) => (v < 0 ? `−${Math.abs(v)}` : String(v));

// ---- text inside the block, sized in canvas px --------------------------
const titleFont = computed(() => Math.min(box.h / 2.3, box.w / 5.3));
const captionFont = computed(() => Math.min(box.h * 0.5, box.w / 8.6));
const cardFont = computed(() => Math.min(box.h * 0.3, box.w / 5.4));

// ---- labels in the zone bands ---------------------------------------------
const u = computed(() => Math.min(W.value, H.value) / 1080);
const labelSize = computed(() => 40 * u.value);
/** side labels sit in the upper part of the free height, away from the action buttons lower down */
const sideLabelY = computed(() => S.value.top + (H.value - S.value.top - S.value.bottom) * 0.22);

/** each zone label with its approximate box; a label under the block is skipped so it never sits on the text */
const zoneLabels = computed(() => {
  const z = labelSize.value;
  const tw = (n: number) => (String(n).length + 3) * z * 0.62;
  const list = [
    { key: "top", text: S.value.top, x: W.value / 2, y: S.value.top - z * 0.45, rot: 0, fits: S.value.top >= z * 1.4 },
    { key: "bottom", text: S.value.bottom, x: W.value / 2, y: H.value - S.value.bottom + z * 1.15, rot: 0, fits: S.value.bottom >= z * 1.4 },
    { key: "left", text: S.value.left, x: S.value.left / 2, y: sideLabelY.value, rot: -90, fits: S.value.left >= z * 1.2 },
    { key: "right", text: S.value.right, x: W.value - S.value.right / 2, y: sideLabelY.value, rot: 90, fits: S.value.right >= z * 1.2 },
  ];
  return list.filter((l) => {
    if (!l.fits) return false;
    const w = l.rot ? z : tw(l.text);
    const h = l.rot ? tw(l.text) : z;
    const cy = l.rot ? l.y : l.y - z * 0.35;
    return !intersect(box, { x: l.x - w / 2, y: cy - h / 2, w, h });
  });
});

// ---- CSS block: exactly what `platform_preset.py <id> --css` prints -------
const css = computed(
  () =>
    `:root {\n  --canvas-w: ${W.value}px; --canvas-h: ${H.value}px;\n` +
    `  --safe-top: ${S.value.top}px; --safe-bottom: ${S.value.bottom}px; --safe-left: ${S.value.left}px; --safe-right: ${S.value.right}px;\n}`,
);
const copyState = ref<"" | "ok" | "fail">("");
let copyTimer: ReturnType<typeof setTimeout> | undefined;
async function copyCss() {
  try {
    await navigator.clipboard.writeText(css.value);
    copyState.value = "ok";
  } catch {
    copyState.value = "fail";
  }
  clearTimeout(copyTimer);
  copyTimer = setTimeout(() => (copyState.value = ""), 2200);
}
onBeforeUnmount(() => clearTimeout(copyTimer));

const stageStyle = computed(() => ({ "--ar": `${W.value / H.value}`, "--u": `calc(100cqw / ${W.value})` }));
const boxStyle = computed(() => ({
  left: `${(box.x / W.value) * 100}%`,
  top: `${(box.y / H.value) * 100}%`,
  width: `${(box.w / W.value) * 100}%`,
  height: `${(box.h / H.value) * 100}%`,
}));
const fs = (px: number) => `calc(var(--u) * ${px.toFixed(2)})`;
</script>

<template>
  <div class="sz" :class="{ 'is-landscape': landscape }">
    <div class="sz-grid">
      <fieldset class="sz-picker">
        <legend class="sz-label">{{ s.preset }}</legend>
        <label v-for="p in presets" :key="p.id" class="sz-preset" :class="{ 'is-on': p.id === presetId }">
          <input v-model="presetId" type="radio" :name="`sz-preset-${locale}`" :value="p.id" />
          <span class="sz-preset-id">{{ p.id }}</span>
          <span class="sz-preset-meta">{{ presetLabel(p.id, p.label, locale) }}</span>
        </label>
      </fieldset>

      <div class="sz-main">
        <div class="sz-stage" :style="stageStyle">
          <div class="sz-slate">
            <span class="sz-mono">{{ preset.id }}</span>
            <span class="sz-mono sz-dim">{{ W }} × {{ H }}</span>
          </div>
          <div class="sz-frame">
            <div ref="canvasEl" class="sz-canvas" role="group" :aria-label="s.stageAria(preset.id, W, H)">
              <svg class="sz-layer" :viewBox="`0 0 ${W} ${H}`" aria-hidden="true">
                <defs>
                  <pattern :id="`sz-hatch-${locale}`" patternUnits="userSpaceOnUse" :width="18 * u" :height="18 * u" patternTransform="rotate(45)">
                    <rect :width="7 * u" :height="18 * u" class="sz-hatch-line" />
                  </pattern>
                </defs>
                <g class="sz-thirds">
                  <line :x1="W / 3" y1="0" :x2="W / 3" :y2="H" />
                  <line :x1="(2 * W) / 3" y1="0" :x2="(2 * W) / 3" :y2="H" />
                  <line x1="0" :y1="H / 3" :x2="W" :y2="H / 3" />
                  <line x1="0" :y1="(2 * H) / 3" :x2="W" :y2="(2 * H) / 3" />
                </g>
                <rect v-for="(b, i) in bands" :key="`b${i}`" class="sz-band" :x="b.x" :y="b.y" :width="b.w" :height="b.h" />
                <rect
                  v-for="(c, i) in cornerRects"
                  :key="`c${i}`"
                  class="sz-corner"
                  :x="c.x"
                  :y="c.y"
                  :width="c.w"
                  :height="c.h"
                  :fill="`url(#sz-hatch-${locale})`"
                />
                <rect class="sz-free" :x="S.left" :y="S.top" :width="W - S.left - S.right" :height="H - S.top - S.bottom" />
              </svg>

              <div
                class="sz-box"
                :class="[`is-${kind}`, { 'is-hit': inZone, 'is-dragging': dragging }]"
                :style="boxStyle"
                tabindex="0"
                :aria-label="s.blockAria(s.kinds[kind])"
                aria-describedby="sz-readout"
                @pointerdown="onPointerDown($event, 'move')"
                @pointermove="onPointerMove"
                @pointerup="onPointerUp"
                @pointercancel="onPointerUp"
                @keydown="onKey($event, 'move')"
              >
                <div v-if="kind === 'title'" class="sz-title" :style="{ fontSize: fs(titleFont) }">
                  <span>{{ s.sample.title[0] }}</span><span>{{ s.sample.title[1] }}</span>
                </div>
                <div v-else-if="kind === 'caption'" class="sz-caption" :style="{ fontSize: fs(captionFont) }">
                  {{ s.sample.caption }}
                </div>
                <div v-else class="sz-card">
                  <span class="sz-card-big" :style="{ fontSize: fs(cardFont) }">{{ s.sample.cardBig }}</span>
                  <span class="sz-card-small" :style="{ fontSize: fs(cardFont * 0.3) }">{{ s.sample.cardSmall }}</span>
                </div>
                <button
                  type="button"
                  class="sz-handle"
                  :aria-label="s.handleAria"
                  @pointerdown="onPointerDown($event, 'resize')"
                  @pointermove="onPointerMove"
                  @pointerup="onPointerUp"
                  @pointercancel="onPointerUp"
                  @keydown="onKey($event, 'resize')"
                />
              </div>

              <svg class="sz-layer sz-over" :viewBox="`0 0 ${W} ${H}`" aria-hidden="true">
                <rect v-for="(o, i) in overlaps" :key="`o${i}`" class="sz-overlap" :x="o.x" :y="o.y" :width="o.w" :height="o.h" />
                <rect v-for="(o, i) in cornerHits" :key="`h${i}`" class="sz-corner-hit" :x="o.x" :y="o.y" :width="o.w" :height="o.h" />
                <UiSilhouettes v-if="showUi" :id="preset.id" :width="W" :height="H" :safe="S" />
                <g class="sz-zone-labels" :font-size="labelSize" :stroke-width="labelSize * 0.28">
                  <text
                    v-for="l in zoneLabels"
                    :key="l.key"
                    :transform="`translate(${l.x} ${l.y}) rotate(${l.rot})`"
                    text-anchor="middle"
                    :dominant-baseline="l.rot ? 'central' : 'auto'"
                  >{{ l.text }} px</text>
                </g>
              </svg>
            </div>
            <p class="sz-status" :class="inZone ? 'is-hit' : 'is-ok'" role="status">
              <span class="sz-dot" aria-hidden="true" />{{ inZone ? s.hit[kind] : s.ok }}
            </p>
          </div>
          <ul class="sz-legend">
            <li><span class="sz-swatch is-zone" aria-hidden="true" />{{ s.zoneLegend }}</li>
            <li><span class="sz-swatch is-free" aria-hidden="true" />{{ s.freeLegend }}</li>
            <li v-if="cornerRects.length"><span class="sz-swatch is-corner" aria-hidden="true" />{{ s.cornerLegend }}</li>
          </ul>
        </div>

        <div class="sz-panel">
          <div class="sz-panel-a">
          <div class="sz-kinds" role="radiogroup" :aria-label="s.block">
            <span class="sz-label" aria-hidden="true">{{ s.block }}</span>
            <div class="sz-seg">
              <label v-for="k in kinds" :key="k" :class="{ 'is-on': k === kind }">
                <input v-model="kind" type="radio" :name="`sz-kind-${locale}`" :value="k" />{{ s.kinds[k] }}
              </label>
            </div>
          </div>

          <dl id="sz-readout" class="sz-readout">
            <div v-for="e in edges" :key="e" :class="{ 'is-hit': dist[e] < 0 }">
              <dt>{{ s.edges[e] }}</dt>
              <dd>
                <span class="sz-mono">{{ fmt(dist[e]) }} px</span>
                <span class="sz-dim">{{ dist[e] < 0 ? s.inside : s.clear }}</span>
              </dd>
            </div>
            <div class="sz-readout-meta">
              <dt>{{ s.position }}</dt>
              <dd><span class="sz-mono">x {{ box.x }}, y {{ box.y }}</span></dd>
            </div>
            <div class="sz-readout-meta">
              <dt>{{ s.size }}</dt>
              <dd><span class="sz-mono">{{ box.w }} × {{ box.h }} px</span></dd>
            </div>
          </dl>

          </div>
          <div class="sz-panel-b">
          <div class="sz-notes">
            <p v-if="inZone">{{ s.hitDetail }}</p>
            <p v-if="inZone && worst <= 4">{{ s.hitTol }}</p>
            <p v-if="!inZone">{{ s.okDetail }}</p>
            <p v-if="cornerHits.length">{{ s.corner }}</p>
          </div>

          <div class="sz-actions">
            <button type="button" class="sz-btn" @click="center">{{ s.center }}</button>
            <button type="button" class="sz-btn" @click="place(kind)">{{ s.reset }}</button>
          </div>

          <label class="sz-toggle">
            <input v-model="showUi" type="checkbox" />
            <span class="sz-switch" aria-hidden="true" />
            <span>
              {{ s.ui }}
              <span class="sz-hint">{{ s.uiHint }}</span>
            </span>
          </label>

          <p class="sz-help">{{ s.help }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="sz-css">
      <div class="sz-css-head">
        <span class="sz-css-title">{{ s.cssTitle }}</span>
        <button type="button" class="sz-btn" @click="copyCss">
          {{ copyState === "ok" ? s.copied : copyState === "fail" ? s.copyFail : s.copy }}
        </button>
      </div>
      <pre class="sz-code"><code>{{ css }}</code></pre>
      <p class="sz-css-note">{{ s.cssNote }}</p>
      <code class="sz-cmd">uv run .agents/skills/motion-cena/scripts/platform_preset.py {{ preset.id }} --css</code>
      <span class="sz-sr" aria-live="polite">{{ copyState === "ok" ? s.copied : "" }}</span>
    </div>
  </div>
</template>

<style scoped>
.sz {
  --sz-zone-text: #ff8a8d;
  --sz-ok-text: var(--mc-ok);
  --sz-panel-rule: var(--vp-c-divider);
  container-type: inline-size;
  margin: 28px 0 40px;
  font-family: var(--mc-font-body);
}
html:not(.dark) .sz {
  --sz-zone-text: #b42a30;
  --sz-ok-text: #2c7a31;
}

.sz-mono {
  font-family: var(--mc-font-mono);
  font-variant-numeric: tabular-nums;
}
.sz-dim {
  color: var(--vp-c-text-2);
}
.sz-label {
  display: block;
  margin-bottom: 8px;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--vp-c-text-2);
}
.sz-sr {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

/* ---- layout ------------------------------------------------------------- */
.sz-grid {
  display: grid;
  gap: 20px;
}
.sz-main {
  display: grid;
  gap: 20px;
  min-width: 0;
}
@container (min-width: 600px) {
  .sz:not(.is-landscape) .sz-main {
    grid-template-columns: auto minmax(0, 1fr);
    align-items: start;
  }
  /* a percentage width inside an auto track collapses: size the portrait stage from its height */
  .sz:not(.is-landscape) .sz-stage {
    width: calc(var(--stage-h) * var(--ar) + 14px);
  }
}
@container (min-width: 860px) {
  .sz-grid {
    grid-template-columns: 196px minmax(0, 1fr);
    align-items: start;
  }
  .sz.is-landscape .sz-main {
    grid-template-columns: minmax(0, 1fr);
  }
  .sz.is-landscape .sz-panel {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    column-gap: 32px;
  }
}

/* ---- preset picker: a bin list, chips on narrow screens -------------------- */
.sz-picker {
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.sz-picker legend {
  float: left;
  width: 100%;
  padding: 0;
}
.sz-preset {
  position: relative;
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--mc-radius-clip);
  cursor: pointer;
  color: var(--vp-c-text-2);
  transition: border-color 0.15s, color 0.15s, background-color 0.15s;
}
.sz-preset input {
  position: absolute;
  opacity: 0;
  inset: 0;
  margin: 0;
  cursor: pointer;
}
.sz-preset-id {
  font-family: var(--mc-font-mono);
  font-size: 0.8rem;
}
.sz-preset-meta {
  display: none;
}
.sz-preset:hover {
  color: var(--vp-c-text-1);
  border-color: var(--vp-c-text-3, #6f6b64);
}
.sz-preset.is-on {
  color: var(--vp-c-text-1);
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
}
.sz-preset:has(input:focus-visible) {
  outline: 2px solid var(--vp-c-brand-1);
  outline-offset: 2px;
}
@container (min-width: 860px) {
  .sz-picker {
    display: block;
    border-top: 1px solid var(--sz-panel-rule);
  }
  .sz-picker legend {
    float: none;
    margin-bottom: 0;
    padding: 0 0 8px;
  }
  .sz-preset {
    display: grid;
    gap: 1px;
    width: 100%;
    padding: 8px 10px 8px 12px;
    border: 0;
    border-bottom: 1px solid var(--sz-panel-rule);
    border-left: 2px solid transparent;
    border-radius: 0;
  }
  .sz-preset.is-on {
    border-color: var(--sz-panel-rule);
    border-left-color: var(--vp-c-brand-1);
  }
  .sz-preset-meta {
    display: block;
    font-size: 0.76rem;
    line-height: 1.3;
    color: var(--vp-c-text-2);
  }
  .sz-preset.is-on .sz-preset-id {
    color: var(--vp-c-brand-1);
  }
}

/* ---- stage ---------------------------------------------------------------- */
.sz-stage {
  --stage-h: min(64vh, 620px);
  justify-self: center;
  width: min(100%, calc(var(--stage-h) * var(--ar) + 14px));
  min-width: 0;
}
.sz.is-landscape .sz-stage {
  width: 100%;
}
.sz-slate {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
  font-size: 0.8rem;
  color: var(--vp-c-text-1);
}
.sz-frame {
  padding: 6px;
  border: 1px solid #2e3238;
  border-radius: var(--mc-radius-frame);
  background: #08090a;
}
.sz-canvas {
  container-type: inline-size;
  position: relative;
  aspect-ratio: var(--ar);
  overflow: hidden;
  border-radius: calc(var(--mc-radius-frame) - 6px);
  background: #131518;
  color: #f2efe8;
  user-select: none;
  -webkit-user-select: none;
}
.sz-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}
.sz-over {
  pointer-events: none;
  color: #f2efe8;
}
.sz-thirds line {
  stroke: rgba(242, 239, 232, 0.06);
  stroke-width: 1;
  vector-effect: non-scaling-stroke;
}
.sz-band {
  fill: var(--mc-zone);
  fill-opacity: 0.2;
}
.sz-corner {
  stroke: var(--mc-zone);
  stroke-opacity: 0.55;
  stroke-width: 1;
  vector-effect: non-scaling-stroke;
}
.sz-hatch-line {
  fill: var(--mc-zone);
  fill-opacity: 0.32;
}
.sz-free {
  fill: none;
  stroke: rgba(242, 239, 232, 0.55);
  stroke-width: 1;
  stroke-dasharray: 5 4;
  vector-effect: non-scaling-stroke;
}
.sz-zone-labels text {
  font-family: var(--mc-font-mono);
  fill: rgba(242, 239, 232, 0.82);
  stroke: #131518;
  stroke-opacity: 0.85;
  paint-order: stroke;
  stroke-linejoin: round;
}
.sz-overlap {
  fill: var(--mc-zone);
  fill-opacity: 0.55;
  stroke: var(--mc-zone);
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
}
.sz-corner-hit {
  fill: var(--mc-zone);
  fill-opacity: 0.3;
}

/* ---- the draggable block ---------------------------------------------------- */
.sz-box {
  position: absolute;
  display: grid;
  place-items: center;
  touch-action: none;
  cursor: grab;
  outline: 1px solid rgba(242, 239, 232, 0.35);
  outline-offset: 0;
  transition: outline-color 0.15s;
}
.sz-box:hover {
  outline-color: rgba(242, 239, 232, 0.7);
}
.sz-box:focus-visible,
.sz-box.is-dragging {
  outline: 2px solid var(--mc-tungsten);
  outline-offset: 0;
}
.sz-box.is-dragging {
  cursor: grabbing;
}
.sz-box.is-hit {
  outline: 2px solid var(--mc-zone);
}
.sz-title {
  display: grid;
  justify-items: center;
  font-family: var(--mc-font-display);
  line-height: 0.98;
  letter-spacing: 0.005em;
  color: #f2efe8;
  text-align: center;
  overflow: hidden;
  white-space: nowrap;
}
.sz-caption {
  padding: 0 0.3em;
  border-radius: 0.18em;
  background: rgba(15, 16, 18, 0.72);
  font-weight: 650;
  line-height: 1.15;
  white-space: nowrap;
  overflow: hidden;
}
.sz-card {
  width: 100%;
  height: 100%;
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 0.4em;
  padding: 6%;
  box-sizing: border-box;
  border-radius: 6%;
  background: #22252a;
  border: 1px solid #3a3f46;
  overflow: hidden;
  text-align: center;
}
.sz-card-big {
  font-family: var(--mc-font-display);
  line-height: 1;
  white-space: nowrap;
}
.sz-card-small {
  color: #c9c4ba;
  line-height: 1.25;
}
.sz-handle {
  position: absolute;
  right: -9px;
  bottom: -9px;
  width: 18px;
  height: 18px;
  padding: 0;
  border: 2px solid #0f1012;
  border-radius: 3px;
  background: #f2efe8;
  cursor: nwse-resize;
  touch-action: none;
}
.sz-box.is-hit .sz-handle {
  background: var(--mc-zone);
}
.sz-handle:focus-visible {
  outline: 2px solid var(--mc-tungsten);
  outline-offset: 2px;
}

/* ---- status line under the canvas ------------------------------------------ */
.sz-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 6px 4px 0;
  min-height: 1.6em;
  font-size: 0.86rem;
  font-weight: 600;
  line-height: 1.35;
}
.sz-status.is-ok {
  color: #9fd6a2;
}
.sz-status.is-hit {
  color: #ff8a8d;
}
.sz-dot {
  flex: none;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}
.sz-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 16px;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
}
.sz-legend li {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
}
.sz-swatch {
  width: 14px;
  height: 10px;
  border-radius: 2px;
}
.sz-swatch.is-zone {
  background: color-mix(in srgb, var(--mc-zone) 45%, transparent);
}
.sz-swatch.is-free {
  border: 1px dashed var(--vp-c-text-2);
}
.sz-swatch.is-corner {
  background: repeating-linear-gradient(45deg, color-mix(in srgb, var(--mc-zone) 55%, transparent) 0 3px, transparent 3px 6px);
}

/* ---- panel -------------------------------------------------------------------- */
.sz-panel {
  display: grid;
  gap: 18px;
  align-content: start;
  min-width: 0;
}
.sz-panel-a,
.sz-panel-b {
  display: grid;
  gap: 18px;
  align-content: start;
  min-width: 0;
}
.sz-seg {
  display: inline-flex;
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--mc-radius-clip);
  overflow: hidden;
}
.sz-seg label {
  position: relative;
  padding: 6px 14px;
  font-size: 0.88rem;
  cursor: pointer;
  color: var(--vp-c-text-2);
  border-right: 1px solid var(--vp-c-divider);
}
.sz-seg label:last-child {
  border-right: 0;
}
.sz-seg label.is-on {
  color: var(--vp-c-text-1);
  background: var(--vp-c-brand-soft);
  box-shadow: inset 0 -2px 0 var(--vp-c-brand-1);
}
.sz-seg input {
  position: absolute;
  inset: 0;
  opacity: 0;
  margin: 0;
  cursor: pointer;
}
.sz-seg label:has(input:focus-visible) {
  outline: 2px solid var(--vp-c-brand-1);
  outline-offset: -2px;
}

.sz-readout {
  margin: 0;
  border-top: 1px solid var(--sz-panel-rule);
}
.sz-readout > div {
  display: grid;
  grid-template-columns: 6.5em minmax(0, 1fr);
  align-items: baseline;
  gap: 12px;
  padding: 7px 0;
  border-bottom: 1px solid var(--sz-panel-rule);
}
.sz-readout dt {
  font-size: 0.88rem;
  color: var(--vp-c-text-2);
}
.sz-readout dd {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 10px;
  margin: 0;
  font-size: 0.9rem;
}
.sz-readout .is-hit dt,
.sz-readout .is-hit dd,
.sz-readout .is-hit .sz-dim {
  color: var(--sz-zone-text);
}
.sz-readout .is-hit {
  box-shadow: inset 2px 0 0 var(--mc-zone);
  padding-left: 10px;
}
.sz-readout-meta dd {
  color: var(--vp-c-text-2);
}

.sz-notes p {
  margin: 0 0 8px;
  font-size: 0.86rem;
  line-height: 1.5;
  color: var(--vp-c-text-2);
}
.sz-notes p:last-child {
  margin-bottom: 0;
}

.sz-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.sz-btn {
  padding: 6px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--mc-radius-clip);
  font-size: 0.86rem;
  color: var(--vp-c-text-1);
  background: transparent;
  cursor: pointer;
  transition: border-color 0.15s;
}
.sz-btn:hover {
  border-color: var(--vp-c-text-2);
}

.sz-toggle {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  font-size: 0.9rem;
  cursor: pointer;
  position: relative;
}
.sz-toggle input {
  position: absolute;
  opacity: 0;
  width: 34px;
  height: 20px;
  margin: 0;
}
.sz-switch {
  position: relative;
  width: 34px;
  height: 20px;
  margin-top: 1px;
  border-radius: 10px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-soft);
  transition: background-color 0.15s, border-color 0.15s;
}
.sz-switch::after {
  content: "";
  position: absolute;
  top: 3px;
  left: 3px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--vp-c-text-2);
  transition: transform 0.15s var(--mc-ease-out), background-color 0.15s;
}
.sz-toggle input:checked + .sz-switch {
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
}
.sz-toggle input:checked + .sz-switch::after {
  transform: translateX(14px);
  background: var(--vp-c-brand-1);
}
.sz-toggle input:focus-visible + .sz-switch {
  outline: 2px solid var(--vp-c-brand-1);
  outline-offset: 2px;
}
.sz-hint {
  display: block;
  margin-top: 2px;
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
}
.sz-help {
  margin: 0;
  font-size: 0.8rem;
  line-height: 1.5;
  color: var(--vp-c-text-2);
}

/* ---- CSS block ---------------------------------------------------------------- */
.sz-css {
  margin-top: 28px;
}
.sz-css-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}
.sz-css-title {
  font-weight: 600;
  font-size: 0.95rem;
}
.sz-code {
  margin: 0;
  padding: 16px 20px;
  overflow-x: auto;
  border-radius: 8px;
  background: var(--vp-code-block-bg);
  font-family: var(--mc-font-mono);
  font-size: 0.84rem;
  line-height: 1.7;
}
.sz-code code {
  font-family: inherit;
  color: var(--vp-c-text-1);
  white-space: pre;
}
.sz-css-note {
  margin: 8px 0 0;
  font-size: 0.82rem;
  color: var(--vp-c-text-2);
}
.sz-cmd {
  display: block;
  width: fit-content;
  max-width: 100%;
  margin-top: 6px;
  padding: 6px 10px;
  overflow-x: auto;
  white-space: nowrap;
  border-radius: 4px;
  background: var(--vp-c-bg-soft);
  font-family: var(--mc-font-mono);
  font-size: 0.8rem;
  color: var(--vp-c-text-1);
}

@media (prefers-reduced-motion: reduce) {
  .sz *,
  .sz *::after {
    transition: none !important;
  }
}
</style>
