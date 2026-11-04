<script setup lang="ts">
/**
 * Detail of one effect: a large stage (the effect running on its fixture), transport (play/pause,
 * loop, scrubber bound to the timeline: the recipes are seek-safe, so dragging is the demo), the
 * request phrase in the dictionary's formula, the texts, defaults and the GSAP code.
 * Docked as an inspector on wide screens, a modal sheet below 1280 px (full screen on phones).
 */
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from "vue";
import { loadEffect, peekEffect } from "../../lib/catalog";
import type { EffectFull, EffectIndexEntry } from "../../lib/taxonomy";
import { INTENSITIES } from "../../lib/taxonomy";
import type { Strings } from "./i18n";

const props = defineProps<{
  entry: EffectIndexEntry;
  t: Strings;
  byId: Map<string, EffectIndexEntry>;
  autoplay: boolean;
  reduced: boolean;
  modal: boolean;
  hasPrev: boolean;
  hasNext: boolean;
}>();
const emit = defineEmits<{ close: []; open: [id: string]; prev: []; next: [] }>();

const FPS = 30;
const T0 = 0.25; // effect start in the stage (same t as lib/fixtures.js and the harness)
const HOLD_S = 0.6;

const panel = ref<HTMLElement | null>(null);
const heading = ref<HTMLElement | null>(null);
const monitor = ref<HTMLElement | null>(null);
const host = ref<HTMLElement | null>(null);
const full = shallowRef<EffectFull | null>(peekEffect(props.entry.familia, props.entry.id) ?? null);
const status = ref<"loading" | "ready" | "error">("loading");
const playing = ref(false);
const loop = ref(false);
const time = ref(0);
const duration = ref(0);
const live = ref(""); // aria-live feedback (copy)

type Stage = { root: HTMLElement; tl: any; duration: number; destroy: () => void };
let stage: Stage | null = null;
let rt: { gsap: any; plugins: Record<string, any> } | null = null;
let hold: { kill(): void } | null = null;
let posterTime: ((familia: string, d: number) => number) | null = null;
let token = 0;

const ptLang = computed(() => (props.t.locale === "en" ? "pt-BR" : undefined));
const level = computed(() => INTENSITIES.indexOf(props.entry.intensidade) + 1);
const titleId = computed(() => `mc-d-title-${props.entry.id}`);
const request = computed(() =>
  props.t.request_phrase(props.entry.nome, props.entry.dur, props.entry.ease, props.t.targets[props.entry.familia] ?? ""),
);
const params = computed(() =>
  Object.entries(full.value?.padrao.parametros ?? {}).map(([k, v]) => [k, typeof v === "string" ? v : JSON.stringify(v)]),
);
const combos = computed(() =>
  (full.value?.combina_com ?? []).map((id) => props.byId.get(id)).filter((e): e is EffectIndexEntry => !!e),
);

// ---------------------------------------------------------------- timeline ruler

const ticks = computed(() => {
  const d = duration.value;
  if (!d) return [];
  const step = [0.05, 0.1, 0.25, 0.5, 1, 2].find((s) => d / s <= 26) ?? 2;
  const major = step < 0.25 ? (step === 0.05 ? 0.25 : 0.5) : step < 1 ? 1 : step * 2;
  const out: { at: number; label: string | null }[] = [];
  for (let k = 0; k * step <= d + 1e-6; k++) {
    const at = Math.round(k * step * 1000) / 1000;
    const isMajor = Math.abs(at / major - Math.round(at / major)) < 1e-6;
    out.push({ at: at / d, label: isMajor ? props.t.n(at) : null });
  }
  return out;
});
const clipStart = computed(() => (duration.value ? Math.min(T0 / duration.value, 1) : 0));

// ---------------------------------------------------------------- stage

function destroyStage() {
  hold?.kill();
  hold = null;
  stage?.destroy();
  stage = null;
  playing.value = false;
}

async function load() {
  const my = ++token;
  const entry = props.entry;
  destroyStage();
  status.value = "loading";
  full.value = peekEffect(entry.familia, entry.id) ?? null;
  try {
    const [runtime, fixtures, eff] = await Promise.all([
      import("../../lib/runtime.js"),
      import("../../lib/fixtures.js"),
      loadEffect(entry.familia, entry.id),
    ]);
    const r = await runtime.loadRuntime();
    if (!eff) throw new Error(`efeito ${entry.id} não está em ${entry.familia}.json`);
    await runtime.ensurePlugins(r, runtime.missingPlugins(r, eff.gsap));
    rt = r;
    if (my !== token) return;
    full.value = eff;
    posterTime = fixtures.posterTime;
    await nextTick();
    if (my !== token || !host.value) return;
    const s = fixtures.buildStage(host.value, eff, rt) as Stage;
    stage = s;
    duration.value = s.duration;
    s.tl.eventCallback("onUpdate", () => {
      time.value = s.tl.totalTime();
    });
    s.tl.eventCallback("onComplete", onComplete);
    status.value = "ready";
    if (props.reduced) seek(s.duration);
    else if (props.autoplay) play();
    else seek(posterTime(eff.familia, s.duration));
  } catch (err) {
    if (my !== token) return;
    status.value = "error";
    console.error(`[efeitos] ${entry.id}:`, err);
  }
}

function seek(v: number) {
  if (!stage) return;
  const d = stage.duration;
  const x = Math.min(Math.max(v, 0), d);
  stage.tl.totalTime(x, false);
  time.value = x;
}
function play() {
  if (!stage) return;
  hold?.kill();
  hold = null;
  if (stage.tl.totalTime() >= stage.duration - 1e-3) seek(0);
  stage.tl.play();
  playing.value = true;
}
function pause() {
  hold?.kill();
  hold = null;
  stage?.tl.pause();
  playing.value = false;
}
function togglePlay() {
  if (playing.value) pause();
  else play();
}
function onComplete() {
  if (loop.value && rt && stage) {
    const s = stage;
    hold = rt.gsap.delayedCall(HOLD_S, () => {
      hold = null;
      if (stage !== s || !loop.value) {
        playing.value = false;
        return;
      }
      s.tl.totalTime(0, false);
      s.tl.play();
    });
  } else playing.value = false;
}
function onScrub(ev: Event) {
  pause();
  seek(Number((ev.target as HTMLInputElement).value));
}
// keyboard on the scrubber: one frame (30 fps) per arrow, ten with Page keys; Space or K plays.
// Done by hand because the native step would snap the end of the timeline to a frame boundary.
function onScrubKey(ev: KeyboardEvent) {
  const frame = 1 / FPS;
  const d = duration.value;
  const now = Math.round(time.value / frame) * frame;
  const to: Record<string, number> = {
    ArrowRight: now + frame,
    ArrowUp: now + frame,
    ArrowLeft: now - frame,
    ArrowDown: now - frame,
    PageUp: now + 10 * frame,
    PageDown: now - 10 * frame,
    Home: 0,
    End: d,
  };
  if (ev.key === " " || ev.key === "k" || ev.key === "K") {
    ev.preventDefault();
    togglePlay();
  } else if (ev.key in to) {
    ev.preventDefault();
    pause();
    seek(to[ev.key]);
  }
}

function onLink(ev: MouseEvent, id: string) {
  if (ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return; // new tab/window
  ev.preventDefault();
  emit("open", id);
}

// ---------------------------------------------------------------- monitor scale

let ro: ResizeObserver | null = null;
function measure() {
  if (monitor.value && monitor.value.clientWidth)
    monitor.value.style.setProperty("--mc-stage-scale", String(monitor.value.clientWidth / 1080));
}

// ---------------------------------------------------------------- copy

const copiedKey = ref("");
let copyTimer = 0;
async function copy(text: string, key: string) {
  let ok = false;
  try {
    await navigator.clipboard.writeText(text);
    ok = true;
  } catch {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;left:-9999px;top:0;";
    document.body.appendChild(ta);
    ta.select();
    try {
      ok = document.execCommand("copy");
    } catch {
      ok = false;
    }
    ta.remove();
  }
  copiedKey.value = ok ? key : "";
  live.value = ok ? props.t.copied : props.t.copyFailed;
  window.clearTimeout(copyTimer);
  copyTimer = window.setTimeout(() => {
    copiedKey.value = "";
    live.value = "";
  }, 1800);
}

// ---------------------------------------------------------------- code

const KEYWORDS = /^(const|let|var|for|of|in|if|else|return|function|new|true|false|null|undefined)$/;
function esc(s: string) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
const codeHtml = computed(() => {
  const code = full.value?.gsap ?? "";
  const re =
    /(\/\/[^\n]*)|(`(?:[^`\\]|\\.)*`|"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')|\b(\d+(?:\.\d+)?)\b|\b([A-Za-z_$][\w$]*)\b/g;
  let out = "";
  let last = 0;
  for (const m of code.matchAll(re)) {
    const i = m.index ?? 0;
    out += esc(code.slice(last, i));
    let cls = "";
    if (m[1]) cls = "c";
    else if (m[2]) cls = "s";
    else if (m[3]) cls = "n";
    else if (m[4] && KEYWORDS.test(m[4])) cls = "k";
    out += cls ? `<span class="tk-${cls}">${esc(m[0])}</span>` : esc(m[0]);
    last = i + m[0].length;
  }
  return out + esc(code.slice(last));
});

// ---------------------------------------------------------------- focus

function focusables(): HTMLElement[] {
  return [
    ...(panel.value?.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ) ?? []),
  ].filter((el) => el.offsetParent !== null || el === document.activeElement);
}
function onPanelKey(ev: KeyboardEvent) {
  if (!props.modal || ev.key !== "Tab") return;
  const list = focusables();
  if (!list.length) return;
  const first = list[0];
  const lastEl = list[list.length - 1];
  if (ev.shiftKey && (document.activeElement === first || document.activeElement === panel.value)) {
    ev.preventDefault();
    lastEl.focus();
  } else if (!ev.shiftKey && document.activeElement === lastEl) {
    ev.preventDefault();
    first.focus();
  }
}

const fmt = (x: number) => props.t.f(x);
const durText = computed(() =>
  props.entry.dur === null ? props.t.continuous : props.t.seconds(props.entry.dur),
);

onMounted(() => {
  ro = new ResizeObserver(measure);
  if (monitor.value) ro.observe(monitor.value);
  measure();
  watch(
    () => props.entry.id,
    () => {
      load();
      nextTick(() => heading.value?.focus({ preventScroll: true }));
      panel.value?.querySelector(".mc-d-scroll")?.scrollTo({ top: 0 });
    },
    { immediate: true },
  );
});
onBeforeUnmount(() => {
  token++;
  destroyStage();
  ro?.disconnect();
  window.clearTimeout(copyTimer);
});
</script>

<template>
  <section
    ref="panel"
    class="mc-d"
    :class="{ 'is-modal': modal }"
    role="dialog"
    :aria-modal="modal ? 'true' : 'false'"
    :aria-labelledby="titleId"
    @keydown="onPanelKey"
  >
    <div class="mc-d-bar">
      <div class="mc-d-steps">
        <button type="button" class="mc-d-icon" :disabled="!hasPrev" :aria-label="t.prev" :title="t.prev" @click="emit('prev')">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5 8 12l7 7" /></svg>
        </button>
        <button type="button" class="mc-d-icon" :disabled="!hasNext" :aria-label="t.next" :title="t.next" @click="emit('next')">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7" /></svg>
        </button>
      </div>
      <code class="mc-d-id">{{ entry.id }}</code>
      <button type="button" class="mc-d-icon" :aria-label="t.close" :title="t.close" @click="emit('close')">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" /></svg>
      </button>
    </div>

    <div class="mc-d-scroll">
      <div class="mc-d-layout">
        <header class="mc-d-head">
          <h2 :id="titleId" ref="heading" class="mc-d-title" tabindex="-1">{{ entry.nome }}</h2>
          <p class="mc-d-pt" :lang="ptLang">{{ entry.nome_pt }}</p>
        </header>
        <div class="mc-d-left">
          <div ref="monitor" class="mc-d-monitor" :data-status="status">
            <div ref="host" class="mc-d-host" aria-hidden="true"></div>
            <p v-if="status === 'loading'" class="mc-d-msg">{{ t.loading }}</p>
            <p v-else-if="status === 'error'" class="mc-d-msg is-error">{{ t.stageError }}</p>
          </div>

          <div class="mc-d-transport">
            <button
              type="button"
              class="mc-d-play"
              :disabled="status !== 'ready'"
              :aria-label="playing ? t.pause : t.play"
              :title="playing ? t.pause : t.play"
              @click="togglePlay"
            >
              <svg v-if="playing" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14M16 5v14" /></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path class="fill" d="M8 5.5v13l10.5-6.5z" /></svg>
            </button>
            <div class="mc-d-track">
              <div class="mc-d-ruler" aria-hidden="true">
                <span
                  v-for="(k, i) in ticks"
                  :key="i"
                  class="mc-d-tick"
                  :class="{ 'is-major': k.label !== null }"
                  :style="{ left: `${k.at * 100}%` }"
                  ><span v-if="k.label !== null && k.at < 0.97">{{ k.label }}</span></span
                >
              </div>
              <div class="mc-d-clip" aria-hidden="true" :style="{ left: `${clipStart * 100}%` }" :title="t.effectStart"></div>
              <input
                class="mc-d-range"
                type="range"
                min="0"
                :max="duration || 1"
                step="any"
                :value="time"
                :disabled="status !== 'ready'"
                :aria-label="t.timeline"
                :aria-valuetext="t.timeText(time, duration)"
                @input="onScrub"
                @keydown="onScrubKey"
              />
            </div>
            <span class="mc-d-time"
              ><span>{{ fmt(time) }}</span><span class="mc-d-time-total">/ {{ fmt(duration) }} s</span></span
            >
            <button
              type="button"
              class="mc-d-icon mc-d-loop"
              :aria-pressed="loop"
              :aria-label="t.loop"
              :title="t.loop"
              @click="loop = !loop"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M4 11V9a3 3 0 0 1 3-3h11M15 3l3 3-3 3M20 13v2a3 3 0 0 1-3 3H6M9 21l-3-3 3-3" />
              </svg>
            </button>
          </div>

          <div class="mc-d-request">
            <p class="mc-d-label">{{ t.request }}</p>
            <div class="mc-d-request-row">
              <code class="mc-d-phrase">{{ request }}</code>
              <button type="button" class="mc-d-copy" @click="copy(request, 'request')">
                {{ copiedKey === "request" ? t.copied : t.copy }}
              </button>
            </div>
            <p class="mc-d-hint">{{ t.requestHint }}</p>
          </div>
        </div>

        <div class="mc-d-info">
          <dl class="mc-d-facts">
            <div>
              <dt>{{ t.family }}</dt>
              <dd>{{ t.families[entry.familia] ?? entry.familia }}</dd>
            </div>
            <div>
              <dt>{{ t.duration }}</dt>
              <dd class="mono">{{ durText }}</dd>
            </div>
            <div>
              <dt>{{ t.ease }}</dt>
              <dd class="mono">{{ entry.ease }}</dd>
            </div>
            <div>
              <dt>{{ t.intensity }}</dt>
              <dd>
                <span class="mc-d-meter" :data-level="level" aria-hidden="true"><i /><i /><i /></span>
                {{ t.intensities[entry.intensidade] }}
              </dd>
            </div>
          </dl>

          <p class="mc-d-status" :class="{ 'is-curated': entry.curado }">
            {{ entry.curado ? t.statusCurated : t.statusCatalog }}
          </p>

          <template v-if="full">
            <p v-if="t.ptOnly" class="mc-d-hint mc-d-ptnote">{{ t.ptOnly }}</p>
            <dl class="mc-d-texts" :lang="ptLang">
              <div>
                <dt>{{ t.whatItIs }}</dt>
                <dd>{{ full.descricao }}</dd>
              </div>
              <div>
                <dt>{{ t.howItWorks }}</dt>
                <dd>{{ full.como_funciona }}</dd>
              </div>
              <div>
                <dt>{{ t.whenToUse }}</dt>
                <dd>{{ full.quando_usar }}</dd>
              </div>
              <div>
                <dt>{{ t.avoid }}</dt>
                <dd>{{ full.evitar }}</dd>
              </div>
            </dl>

            <div v-if="params.length" class="mc-d-block">
              <h3 class="mc-d-label">{{ t.params }}</h3>
              <table class="mc-d-params">
                <tbody>
                  <tr v-for="[k, v] in params" :key="k">
                    <th scope="row">{{ k }}</th>
                    <td>{{ v }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="mc-d-block">
              <h3 class="mc-d-label">{{ t.properties }}</h3>
              <ul class="mc-d-tags mono">
                <li v-for="p in full.propriedades" :key="p">{{ p }}</li>
              </ul>
            </div>

            <div v-if="full.generos.length" class="mc-d-block">
              <h3 class="mc-d-label">{{ t.genresLabel }}</h3>
              <ul class="mc-d-tags">
                <li v-for="g in full.generos" :key="g">{{ t.genres[g] ?? g }}</li>
              </ul>
            </div>

            <div v-if="full.aliases.length" class="mc-d-block">
              <h3 class="mc-d-label">{{ t.aliases }}</h3>
              <ul class="mc-d-tags" :lang="ptLang">
                <li v-for="a in full.aliases" :key="a">{{ a }}</li>
              </ul>
            </div>

            <div v-if="combos.length" class="mc-d-block">
              <h3 class="mc-d-label">{{ t.combines }}</h3>
              <ul class="mc-d-combos">
                <li v-for="c in combos" :key="c.id">
                  <a :href="`?efeito=${c.id}`" @click="onLink($event, c.id)">
                    <span class="mc-d-combo-name">{{ c.nome }}</span>
                    <span class="mc-d-combo-pt" :lang="ptLang">{{ c.nome_pt }}</span>
                  </a>
                </li>
              </ul>
            </div>

            <div class="mc-d-block">
              <h3 class="mc-d-label">{{ t.recipe }}</h3>
              <p class="mc-d-recipe">
                <code v-if="full.receita_hyperframes">{{ full.receita_hyperframes }}</code>
                <span v-else>{{ t.none }}</span>
              </p>
            </div>

            <div class="mc-d-block mc-d-codeblock">
              <div class="mc-d-code-head">
                <h3 class="mc-d-label">{{ t.code }}</h3>
                <button type="button" class="mc-d-copy" @click="copy(full.gsap, 'code')">
                  {{ copiedKey === "code" ? t.copied : t.copy }}
                </button>
              </div>
              <pre class="mc-d-code" tabindex="0" :aria-label="t.code"><code v-html="codeHtml"></code></pre>
              <p class="mc-d-hint">{{ t.codeScope }}</p>
            </div>
          </template>
        </div>
      </div>
    </div>
    <p class="mc-sr" role="status" aria-live="polite">{{ live }}</p>
  </section>
</template>

<style scoped>
.mc-d {
  position: fixed;
  z-index: 80;
  inset: 0;
  display: flex;
  flex-direction: column;
  background: var(--x-bg);
  color: var(--x-text);
  font-family: var(--mc-font-body);
}
@media (min-width: 720px) {
  .mc-d {
    left: auto;
    width: min(720px, 100vw);
    border-left: 1px solid var(--x-rule);
  }
}
@media (min-width: 1280px) {
  .mc-d:not(.is-modal) {
    z-index: 20;
    top: var(--vp-nav-height);
    width: var(--x-panel-w);
  }
}
.mc-sr {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
.mono {
  font-family: var(--mc-font-mono);
}

/* ---------------------------------------------------------------- bar */

.mc-d-bar {
  flex: none;
  display: flex;
  align-items: center;
  gap: 12px;
  height: 52px;
  padding: 0 10px;
  border-bottom: 1px solid var(--x-rule);
}
.mc-d-steps {
  display: flex;
  gap: 2px;
}
.mc-d-id {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font: 500 0.8rem/1 var(--mc-font-mono);
  color: var(--x-text-2);
  background: none;
  padding: 0;
}
.mc-d-icon {
  display: inline-grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border: 0;
  border-radius: 8px;
  background: none;
  color: var(--x-text);
  cursor: pointer;
}
.mc-d-icon:hover:not(:disabled) {
  background: var(--x-bg-2);
}
.mc-d-icon:disabled {
  opacity: 0.35;
  cursor: default;
}
.mc-d-icon svg,
.mc-d-play svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.mc-d-play svg .fill {
  fill: currentColor;
}

.mc-d-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
}
.mc-d-layout {
  display: grid;
  gap: 24px;
  padding: 20px 16px 48px;
}
.mc-d-head {
  min-width: 0;
}
@media (min-width: 720px) {
  .mc-d-layout {
    grid-template-columns: minmax(0, 300px) minmax(0, 1fr);
    grid-template-rows: auto 1fr;
    grid-template-areas:
      "left head"
      "left info";
    gap: 0 28px;
    padding: 24px 24px 56px;
    align-items: start;
  }
  .mc-d-head {
    grid-area: head;
  }
  .mc-d-info {
    grid-area: info;
  }
  .mc-d-left {
    grid-area: left;
    position: sticky;
    top: 24px;
  }
}

/* ---------------------------------------------------------------- monitor */

.mc-d-left {
  display: grid;
  gap: 14px;
  min-width: 0;
}
.mc-d-monitor {
  position: relative;
  width: 100%;
  max-width: min(300px, max(200px, calc((100vh - 380px) * 0.5625)));
  aspect-ratio: 9 / 16;
  margin: 0 auto;
  border-radius: var(--mc-radius-frame);
  overflow: hidden;
  background: #121417;
  box-shadow: 0 0 0 1px var(--x-rule);
  isolation: isolate;
}
@media (max-width: 719.98px) {
  .mc-d-monitor {
    max-width: calc(52vh * 9 / 16);
  }
}
.mc-d-host {
  position: absolute;
  inset: 0;
  overflow: hidden;
}
.mc-d-host :deep(.mc-stage-root) {
  transform: scale(var(--mc-stage-scale, 0.27));
  transform-origin: 0 0;
}
.mc-d-msg {
  position: absolute;
  inset: auto 0 45% 0;
  margin: 0;
  padding: 0 16px;
  text-align: center;
  font-size: 0.9rem;
  color: #a9a49a;
}
.mc-d-msg.is-error {
  color: #f2efe8;
}

/* ---------------------------------------------------------------- transport */

.mc-d-transport {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  grid-template-areas:
    "track track track"
    "play time loop";
  align-items: center;
  gap: 6px 8px;
}
.mc-d-play {
  grid-area: play;
  display: inline-grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border: 1px solid var(--x-rule);
  border-radius: 50%;
  background: var(--x-bg-2);
  color: var(--x-text);
  cursor: pointer;
}
.mc-d-play:hover:not(:disabled) {
  border-color: var(--x-active);
  color: var(--x-active);
}
.mc-d-play:disabled {
  opacity: 0.4;
  cursor: default;
}
.mc-d-time {
  grid-area: time;
  display: flex;
  gap: 6px;
  align-items: baseline;
  font: 600 0.92rem/1 var(--mc-font-mono);
  font-variant-numeric: tabular-nums;
  color: var(--x-active);
}
.mc-d-time-total {
  font-weight: 400;
  color: var(--x-text-2);
}
.mc-d-loop {
  grid-area: loop;
}
.mc-d-loop[aria-pressed="true"] {
  color: var(--x-active);
  background: var(--x-bg-2);
  box-shadow: inset 0 0 0 1px var(--x-active);
}

.mc-d-track {
  grid-area: track;
  position: relative;
  height: 52px;
  border-radius: 4px;
  background: var(--x-bg-2);
  box-shadow: inset 0 0 0 1px var(--x-rule);
}
.mc-d-ruler {
  position: absolute;
  left: 7px;
  right: 7px;
  top: 0;
  height: 18px;
}
.mc-d-tick {
  position: absolute;
  top: 0;
  width: 1px;
  height: 5px;
  background: var(--x-text-3);
}
.mc-d-tick.is-major {
  height: 9px;
  background: var(--x-text-2);
}
.mc-d-tick span {
  position: absolute;
  left: 4px;
  top: 0;
  font: 500 9.5px/1 var(--mc-font-mono);
  color: var(--x-text-2);
  white-space: nowrap;
}
.mc-d-clip {
  position: absolute;
  right: 7px;
  top: 22px;
  bottom: 8px;
  margin-left: 7px;
  border-radius: var(--mc-radius-clip);
  background: var(--x-bg-3);
  box-shadow: inset 0 0 0 1px var(--x-text-3);
}
.dark .mc-d-clip {
  background: #2a2d33;
}
.mc-d-range {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  margin: 0;
  background: transparent;
  -webkit-appearance: none;
  appearance: none;
  cursor: ew-resize;
}
.mc-d-range:disabled {
  cursor: default;
}
.mc-d-range:focus-visible {
  outline: 2px solid var(--x-active);
  outline-offset: 2px;
  border-radius: 4px;
}
.mc-d-range::-webkit-slider-runnable-track {
  height: 52px;
  background: transparent;
  border: 0;
}
.mc-d-range::-moz-range-track {
  height: 52px;
  background: transparent;
  border: 0;
}
/* playhead: a 2 px line with a head, the only amber on the track */
.mc-d-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 52px;
  border: 0;
  border-radius: 0;
  background:
    linear-gradient(var(--x-active), var(--x-active)) center top / 12px 10px no-repeat,
    linear-gradient(var(--x-active), var(--x-active)) center / 2px 100% no-repeat;
}
.mc-d-range::-moz-range-thumb {
  width: 14px;
  height: 52px;
  border: 0;
  border-radius: 0;
  background:
    linear-gradient(var(--x-active), var(--x-active)) center top / 12px 10px no-repeat,
    linear-gradient(var(--x-active), var(--x-active)) center / 2px 100% no-repeat;
}
.mc-d-range:disabled::-webkit-slider-thumb {
  opacity: 0.3;
}

/* ---------------------------------------------------------------- request */

.mc-d-label {
  margin: 0 0 6px;
  font: 600 0.85rem/1.3 var(--mc-font-body);
  color: var(--x-text-2);
}
.mc-d-request {
  padding-top: 4px;
}
.mc-d-request-row {
  display: flex;
  align-items: stretch;
  border: 1px solid var(--x-rule);
  border-radius: 8px;
  background: var(--x-bg-2);
  overflow: hidden;
}
.mc-d-phrase {
  flex: 1;
  min-width: 0;
  padding: 10px 12px;
  background: none;
  font: 500 0.86rem/1.45 var(--mc-font-mono);
  color: var(--x-text);
  overflow-wrap: anywhere;
}
.mc-d-copy {
  flex: none;
  padding: 0 12px;
  border: 0;
  border-left: 1px solid var(--x-rule);
  background: none;
  color: var(--x-active);
  font: 600 0.85rem/1 var(--mc-font-body);
  cursor: pointer;
}
.mc-d-copy:hover {
  background: var(--x-bg-3);
}
.mc-d-hint {
  margin: 6px 0 0;
  font-size: 0.8rem;
  line-height: 1.45;
  color: var(--x-text-2);
}

/* ---------------------------------------------------------------- info */

.mc-d-info {
  min-width: 0;
}
.mc-d-title {
  margin: 0;
  font-family: var(--mc-font-display);
  font-weight: 400;
  font-size: clamp(2.2rem, 5vw, 3.2rem);
  line-height: 1;
  letter-spacing: 0.005em;
  color: var(--x-text);
  overflow-wrap: anywhere;
}
.mc-d-title:focus {
  outline: none;
}
.mc-d-title:focus-visible {
  outline: none; /* focused only so screen readers announce the effect */
}
.mc-d-pt {
  margin: 6px 0 0;
  font-size: var(--mc-step-1);
  line-height: 1.35;
  color: var(--x-text-2);
}
.mc-d-facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 16px;
  margin: 20px 0 0;
  padding: 14px 0;
  border-top: 1px solid var(--x-rule);
  border-bottom: 1px solid var(--x-rule);
}
.mc-d-facts dt {
  font-size: 0.78rem;
  color: var(--x-text-2);
}
.mc-d-facts dd {
  margin: 2px 0 0;
  font-size: 0.95rem;
  font-weight: 550;
  overflow-wrap: anywhere;
}
.mc-d-facts dd.mono {
  font-size: 0.88rem;
}
.mc-d-meter {
  display: inline-flex;
  align-items: flex-end;
  gap: 2px;
  height: 12px;
  margin-right: 4px;
}
.mc-d-meter i {
  display: block;
  width: 3px;
  border-radius: 1px;
  background: var(--x-rule);
}
.mc-d-meter i:nth-child(1) {
  height: 5px;
}
.mc-d-meter i:nth-child(2) {
  height: 8px;
}
.mc-d-meter i:nth-child(3) {
  height: 12px;
}
.mc-d-meter[data-level="1"] i:nth-child(-n + 1),
.mc-d-meter[data-level="2"] i:nth-child(-n + 2),
.mc-d-meter[data-level="3"] i:nth-child(-n + 3) {
  background: var(--x-text);
}
.mc-d-status {
  margin: 14px 0 0;
  padding-left: 12px;
  border-left: 3px solid var(--x-rule);
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--x-text-2);
}
.mc-d-status.is-curated {
  border-left-color: var(--x-text);
  color: var(--x-text);
}

.mc-d-texts {
  display: grid;
  gap: 16px;
  margin: 24px 0 0;
}
.mc-d-ptnote {
  margin: 20px 0 -8px;
}
.mc-d-texts dt {
  font: 600 0.85rem/1.3 var(--mc-font-body);
  color: var(--x-text-2);
}
.mc-d-texts dd {
  margin: 4px 0 0;
  font-size: 0.98rem;
  line-height: 1.55;
  max-width: 62ch;
}

.mc-d-block {
  margin-top: 24px;
}
.mc-d-params {
  display: table;
  width: 100%;
  margin: 0;
  border-collapse: collapse;
  font: 500 0.82rem/1.4 var(--mc-font-mono);
}
.mc-d-params tr {
  border: 0;
  border-top: 1px solid var(--x-rule);
  background: none;
}
.mc-d-params tr:last-child {
  border-bottom: 1px solid var(--x-rule);
}
.mc-d-params th,
.mc-d-params td {
  padding: 6px 8px 6px 0;
  border: 0;
  text-align: left;
  vertical-align: top;
  background: none;
  overflow-wrap: anywhere;
}
.mc-d-params th {
  width: 45%;
  font-weight: 500;
  color: var(--x-text-2);
}
.mc-d-params td {
  color: var(--x-text);
}
.mc-d-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.mc-d-tags li {
  padding: 3px 9px;
  border: 1px solid var(--x-rule);
  border-radius: 4px;
  font-size: 0.84rem;
  line-height: 1.35;
}
.mc-d-tags.mono li {
  font-size: 0.78rem;
}
.mc-d-combos {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.mc-d-combos a {
  display: grid;
  gap: 1px;
  height: 100%;
  padding: 8px 10px;
  border: 1px solid var(--x-rule);
  border-radius: 6px;
  text-decoration: none;
  color: var(--x-text);
}
.mc-d-combos a:hover {
  border-color: var(--x-active);
}
.mc-d-combo-name {
  font-weight: 650;
  font-size: 0.9rem;
  color: var(--x-active);
  text-decoration: underline;
  text-decoration-color: transparent;
  text-underline-offset: 3px;
}
.mc-d-combos a:hover .mc-d-combo-name {
  text-decoration-color: currentColor;
}
.mc-d-combo-pt {
  font-size: 0.8rem;
  color: var(--x-text-2);
}
.mc-d-recipe {
  margin: 0;
  font-size: 0.92rem;
  color: var(--x-text-2);
}
.mc-d-recipe code {
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--x-bg-2);
  font: 500 0.86rem/1.4 var(--mc-font-mono);
  color: var(--x-text);
}

.mc-d-code-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}
.mc-d-code-head .mc-d-label {
  margin: 0;
}
.mc-d-code-head .mc-d-copy {
  height: 30px;
  border: 1px solid var(--x-rule);
  border-radius: 6px;
}
.mc-d-code {
  margin: 0;
  padding: 14px 16px;
  border-radius: 8px;
  background: #121417;
  color: #e9e5dc;
  font: 450 0.8rem/1.6 var(--mc-font-mono);
  overflow-x: auto;
  tab-size: 2;
  scrollbar-width: thin;
}
.mc-d-code code {
  font: inherit;
  color: inherit;
  background: none;
  padding: 0;
}
.mc-d-code:focus-visible {
  outline: 2px solid var(--x-active);
  outline-offset: 2px;
}
.mc-d-code :deep(.tk-c) {
  color: #8a8579;
  font-style: italic;
}
.mc-d-code :deep(.tk-s) {
  color: #b9d7a8;
}
.mc-d-code :deep(.tk-n) {
  color: #9ec5e8;
}
.mc-d-code :deep(.tk-k) {
  color: #d9a7e8;
}
</style>
