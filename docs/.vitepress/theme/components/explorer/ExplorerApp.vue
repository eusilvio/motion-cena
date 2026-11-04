<script setup lang="ts">
/**
 * Effects explorer: search + filters over the slim index (data/effects.data.ts), a grid of tiles
 * whose thumbnails are built on demand (lib/thumbs.ts), and the detail panel (EffectDetail.vue).
 * State lives in the URL query (?q=&familia=&genero=&intensidade=&curado=1&efeito=), replaced in
 * place so a filtered view or an open effect can be shared.
 */
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch, type Directive } from "vue";
import { data } from "../../../data/effects.data";
import { prepare, search } from "../../lib/search";
import { GENRES, INTENSITIES, type EffectIndexEntry } from "../../lib/taxonomy";
import type { ThumbDeck } from "../../lib/thumbs";
import EffectDetail from "./EffectDetail.vue";
import { strings, SUGGESTIONS, type Locale } from "./i18n";

const props = defineProps<{ locale: Locale }>();
const t = computed(() => strings(props.locale));

const all = data.effects;
const byId = new Map(all.map((e) => [e.id, e]));
const familyIds = data.families.map((f) => f.id);
const pool = prepare(all);

const state = reactive({ q: "", familia: "", genero: "", intensidade: "", curado: false, efeito: "" });
const opened = ref<"click" | "url">("url");
const reduced = ref(false);
const wide = ref(true); // docked inspector (>= 1280 px) or modal sheet
const filtersOpen = ref(false);
const mounted = ref(false);

// ---------------------------------------------------------------- filtering

const query = computed(() => state.q.trim());
const matched = computed(() => (query.value ? search(pool, query.value) : all));

type Facet = "familia" | "genero" | "intensidade" | "curado";
function pass(e: EffectIndexEntry, skip?: Facet) {
  return (
    (skip === "familia" || !state.familia || e.familia === state.familia) &&
    (skip === "genero" || !state.genero || e.generos.includes(state.genero)) &&
    (skip === "intensidade" || !state.intensidade || e.intensidade === state.intensidade) &&
    (skip === "curado" || !state.curado || e.curado)
  );
}
function tally(list: EffectIndexEntry[], keys: (e: EffectIndexEntry) => string[]) {
  const m = new Map<string, number>();
  for (const e of list) for (const k of keys(e)) m.set(k, (m.get(k) ?? 0) + 1);
  return m;
}

const results = computed(() => matched.value.filter((e) => pass(e)));
const famCounts = computed(() => tally(matched.value.filter((e) => pass(e, "familia")), (e) => [e.familia]));
const genreCounts = computed(() => tally(matched.value.filter((e) => pass(e, "genero")), (e) => e.generos));
const intCounts = computed(() => tally(matched.value.filter((e) => pass(e, "intensidade")), (e) => [e.intensidade]));
const curatedCount = computed(() => matched.value.filter((e) => pass(e, "curado") && e.curado).length);
const famAllCount = computed(() => matched.value.filter((e) => pass(e, "familia")).length);
const activeFilters = computed(
  () => Number(!!state.familia) + Number(!!state.genero) + Number(!!state.intensidade) + Number(state.curado),
);

const sections = computed(() => {
  if (!query.value && !state.familia) {
    return data.families
      .map((f) => ({ id: f.id, items: results.value.filter((e) => e.familia === f.id) }))
      .filter((s) => s.items.length);
  }
  return results.value.length ? [{ id: state.familia, items: results.value }] : [];
});

const emptyAlternatives = computed(() => {
  if (results.value.length) return null;
  const withoutFilters = activeFilters.value ? matched.value.length : 0;
  const suggestions = SUGGESTIONS.filter((s) => search(pool, s).length).slice(0, 6);
  return { withoutFilters, suggestions };
});

function clearFilters() {
  state.familia = state.genero = state.intensidade = "";
  state.curado = false;
}
function toggle<K extends "familia" | "genero" | "intensidade">(key: K, value: string) {
  state[key] = state[key] === value ? "" : value;
}

// ---------------------------------------------------------------- detail

const selected = computed(() => (state.efeito ? byId.get(state.efeito) : undefined));
const navList = computed(() => (selected.value && results.value.includes(selected.value) ? results.value : all));
const selIndex = computed(() => (selected.value ? navList.value.indexOf(selected.value) : -1));

function open(id: string, how: "click" | "url" = "click") {
  if (!byId.has(id)) return;
  opened.value = how;
  state.efeito = id;
}
function onTileClick(ev: MouseEvent, id: string) {
  if (ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return; // new tab/window
  ev.preventDefault();
  open(id);
}
function step(delta: number) {
  const list = navList.value;
  const i = selIndex.value + delta;
  if (i >= 0 && i < list.length) {
    open(list[i].id);
    nextTick(() => tileEl(list[i].id)?.scrollIntoView({ block: "nearest" }));
  }
}
function close() {
  const id = state.efeito;
  state.efeito = "";
  nextTick(() => (tileEl(id) ?? searchInput.value)?.focus({ preventScroll: false }));
}

// ---------------------------------------------------------------- grid keyboard (roving tabindex)

const root = ref<HTMLElement | null>(null);
const searchInput = ref<HTMLInputElement | null>(null);
const focusId = ref("");
const tabbableId = computed(() => {
  const ids = results.value;
  if (focusId.value && ids.some((e) => e.id === focusId.value)) return focusId.value;
  if (selected.value && ids.includes(selected.value)) return selected.value.id;
  return ids[0]?.id ?? "";
});
function tileEl(id: string) {
  return root.value?.querySelector<HTMLElement>(`.mc-tile[data-id="${CSS.escape(id)}"]`) ?? null;
}
function onGridKey(ev: KeyboardEvent) {
  const cur = ev.currentTarget as HTMLElement;
  const tiles = [...(root.value?.querySelectorAll<HTMLElement>(".mc-tile") ?? [])];
  const i = tiles.indexOf(cur);
  let next: HTMLElement | undefined;
  if (ev.key === "ArrowRight") next = tiles[i + 1];
  else if (ev.key === "ArrowLeft") next = tiles[i - 1];
  else if (ev.key === "Home") next = tiles[0];
  else if (ev.key === "End") next = tiles[tiles.length - 1];
  else if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
    const r = cur.getBoundingClientRect();
    const cx = r.left + r.width / 2;
    const down = ev.key === "ArrowDown";
    let best: { el: HTMLElement; dy: number; dx: number } | null = null;
    for (const el of tiles) {
      const q = el.getBoundingClientRect();
      const dy = down ? q.top - r.top : r.top - q.top;
      if (dy < 8) continue;
      const dx = Math.abs(q.left + q.width / 2 - cx);
      if (!best || dy < best.dy - 8 || (Math.abs(dy - best.dy) <= 8 && dx < best.dx)) best = { el, dy, dx };
    }
    next = best?.el;
  } else return;
  ev.preventDefault();
  if (next) {
    focusId.value = next.dataset.id ?? "";
    next.focus();
    next.scrollIntoView({ block: "nearest" });
  }
}

// ---------------------------------------------------------------- thumbnails

let deck: ThumbDeck | null = null;
const vThumb: Directive<HTMLElement, EffectIndexEntry> = {
  mounted: (el, b) => deck?.bind(el, b.value),
  updated: (el, b) => {
    if (b.value !== b.oldValue) deck?.bind(el, b.value);
  },
  beforeUnmount: (el) => deck?.unbind(el),
};
function onEnter(ev: PointerEvent) {
  if (ev.pointerType === "mouse" || ev.pointerType === "pen") deck?.play(ev.currentTarget as HTMLElement);
}
function onLeave(ev: PointerEvent) {
  deck?.stop(ev.currentTarget as HTMLElement);
}
function onTileFocus(ev: FocusEvent, id: string) {
  focusId.value = id;
  const el = ev.currentTarget as HTMLElement;
  if (el.matches(":focus-visible")) deck?.play(el);
}
function onTileBlur(ev: FocusEvent) {
  const el = ev.currentTarget as HTMLElement;
  if (!el.matches(":hover")) deck?.stop(el);
}

let ro: ResizeObserver | null = null;
function measureThumbs() {
  const thumb = root.value?.querySelector<HTMLElement>(".mc-thumb");
  if (thumb && thumb.clientWidth) root.value!.style.setProperty("--mc-thumb-scale", String(thumb.clientWidth / 1080));
}

// ---------------------------------------------------------------- URL state

function readUrl() {
  const p = new URLSearchParams(location.search);
  const pick = (k: string, ok: readonly string[]) => {
    const v = p.get(k) ?? "";
    return ok.includes(v) ? v : "";
  };
  state.q = p.get("q") ?? "";
  state.familia = pick("familia", familyIds);
  state.genero = pick("genero", GENRES);
  state.intensidade = pick("intensidade", INTENSITIES);
  state.curado = p.get("curado") === "1";
  const id = p.get("efeito") ?? "";
  if (byId.has(id)) open(id, "url");
  else state.efeito = "";
}
function writeUrl() {
  const p = new URLSearchParams();
  if (query.value) p.set("q", query.value);
  if (state.familia) p.set("familia", state.familia);
  if (state.genero) p.set("genero", state.genero);
  if (state.intensidade) p.set("intensidade", state.intensidade);
  if (state.curado) p.set("curado", "1");
  if (state.efeito) p.set("efeito", state.efeito);
  const qs = p.toString().replace(/\+/g, "%20");
  const url = location.pathname + (qs ? `?${qs}` : "") + location.hash;
  if (url !== location.pathname + location.search + location.hash) history.replaceState(history.state, "", url);
}

// ---------------------------------------------------------------- lifecycle

let mqReduced: MediaQueryList | null = null;
let mqWide: MediaQueryList | null = null;
const syncReduced = () => (reduced.value = !!mqReduced?.matches);
const syncWide = () => (wide.value = !!mqWide?.matches);

function onDocKey(ev: KeyboardEvent) {
  if (ev.key === "Escape" && state.efeito && !ev.defaultPrevented) {
    ev.preventDefault();
    close();
  }
}

// modal sheet: the page behind does not scroll
watch(
  () => !!state.efeito && !wide.value,
  (lock) => {
    if (!mounted.value) return;
    document.documentElement.classList.toggle("mc-scroll-lock", lock);
  },
);

onMounted(async () => {
  mqReduced = matchMedia("(prefers-reduced-motion: reduce)");
  mqWide = matchMedia("(min-width: 1280px)");
  syncReduced();
  syncWide();
  mqReduced.addEventListener("change", syncReduced);
  mqWide.addEventListener("change", syncWide);
  readUrl();
  mounted.value = true;
  watch(
    () => [query.value, state.familia, state.genero, state.intensidade, state.curado, state.efeito],
    writeUrl,
  );
  document.addEventListener("keydown", onDocKey);

  const { ThumbDeck } = await import("../../lib/thumbs");
  deck = new ThumbDeck(() => reduced.value);
  await nextTick();
  root.value?.querySelectorAll<HTMLElement>(".mc-tile").forEach((el) => {
    const e = byId.get(el.dataset.id ?? "");
    if (e) deck!.bind(el, e);
  });
  ro = new ResizeObserver(measureThumbs);
  if (root.value) ro.observe(root.value.querySelector(".mc-x-results") ?? root.value);
  measureThumbs();
  if (state.efeito) nextTick(() => tileEl(state.efeito)?.scrollIntoView({ block: "center" }));
});

watch(results, () => nextTick(measureThumbs));

onBeforeUnmount(() => {
  deck?.destroy();
  ro?.disconnect();
  document.removeEventListener("keydown", onDocKey);
  mqReduced?.removeEventListener("change", syncReduced);
  mqWide?.removeEventListener("change", syncWide);
  document.documentElement.classList.remove("mc-scroll-lock");
});

function onSearchKey(ev: KeyboardEvent) {
  if (ev.key === "Escape" && state.q) {
    ev.preventDefault();
    ev.stopPropagation();
    state.q = "";
  }
}
function dur(e: EffectIndexEntry) {
  return e.dur === null ? t.value.continuous : t.value.seconds(e.dur);
}
const level = (i: string) => INTENSITIES.indexOf(i as (typeof INTENSITIES)[number]) + 1;
const ptLang = computed(() => (props.locale === "en" ? "pt-BR" : undefined));
</script>

<template>
  <div
    ref="root"
    class="mc-x vp-raw"
    :class="{ 'has-detail': !!selected, 'is-wide': wide, 'is-reduced': reduced }"
  >
    <header class="mc-x-head">
      <h1 class="mc-x-title">{{ t.title }}</h1>
      <p class="mc-x-lede">{{ t.lede(data.total) }}</p>
      <p v-if="t.ptNote" class="mc-x-note">{{ t.ptNote }}</p>
      <figure class="mc-x-formula" :aria-label="`${t.formulaLabel}: ${t.formula}`">
        <figcaption>{{ t.formulaLabel }}</figcaption>
        <ol class="mc-x-clips">
          <li v-for="(part, i) in t.formula.split(' + ')" :key="part">
            <span class="mc-x-clip">{{
              props.locale === "pt"
                ? ["slam", "em 0,22 s", "com power4.out", "no título"][i]
                : ["slam", "in 0.22 s", "with power4.out", "on the title"][i]
            }}</span>
            <span class="mc-x-cliplabel">{{ part }}</span>
          </li>
        </ol>
      </figure>
      <p v-if="reduced" class="mc-x-note">{{ t.reducedNote }}</p>
    </header>

    <div class="mc-x-body">
      <div class="mc-x-search">
        <label class="mc-sr" for="mc-x-q">{{ t.searchLabel }}</label>
        <svg class="mc-x-search-icon" viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="10.5" cy="10.5" r="6.5" />
          <path d="M15.5 15.5 21 21" />
        </svg>
        <input
          id="mc-x-q"
          ref="searchInput"
          v-model="state.q"
          type="search"
          autocomplete="off"
          spellcheck="false"
          :placeholder="t.searchPlaceholder"
          @keydown="onSearchKey"
        />
      </div>

      <button
        class="mc-x-filters-toggle"
        type="button"
        :aria-expanded="filtersOpen"
        aria-controls="mc-x-rail"
        @click="filtersOpen = !filtersOpen"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M7 12h10M10 17h4" /></svg>
        {{ t.filters }}<span v-if="activeFilters" class="mc-x-badge">{{ activeFilters }}</span>
      </button>

      <aside id="mc-x-rail" class="mc-x-rail" :class="{ 'is-open': filtersOpen }" :aria-label="t.filters">
        <div class="mc-x-group">
          <h2 class="mc-x-group-title">{{ t.family }}</h2>
          <ul class="mc-x-fams">
            <li>
              <button
                type="button"
                class="mc-x-fam"
                :aria-pressed="!state.familia"
                @click="state.familia = ''"
              >
                <span>{{ t.allFamilies }}</span><span class="mc-x-count">{{ famAllCount }}</span>
              </button>
            </li>
            <li v-for="f in data.families" :key="f.id">
              <button
                type="button"
                class="mc-x-fam"
                :aria-pressed="state.familia === f.id"
                :disabled="!famCounts.get(f.id) && state.familia !== f.id"
                @click="toggle('familia', f.id)"
              >
                <span>{{ t.families[f.id] ?? f.id }}</span
                ><span class="mc-x-count">{{ famCounts.get(f.id) ?? 0 }}</span>
              </button>
            </li>
          </ul>
        </div>

        <div class="mc-x-group">
          <h2 class="mc-x-group-title">{{ t.genre }}</h2>
          <div class="mc-x-chips">
            <button
              v-for="g in GENRES"
              :key="g"
              type="button"
              class="mc-x-chip"
              :aria-pressed="state.genero === g"
              :disabled="!genreCounts.get(g) && state.genero !== g"
              @click="toggle('genero', g)"
            >
              {{ t.genres[g] }} <span class="mc-x-count">{{ genreCounts.get(g) ?? 0 }}</span>
            </button>
          </div>
        </div>

        <div class="mc-x-group">
          <h2 class="mc-x-group-title">{{ t.intensity }}</h2>
          <div class="mc-x-chips">
            <button
              v-for="i in INTENSITIES"
              :key="i"
              type="button"
              class="mc-x-chip"
              :aria-pressed="state.intensidade === i"
              :disabled="!intCounts.get(i) && state.intensidade !== i"
              @click="toggle('intensidade', i)"
            >
              <span class="mc-meter" :data-level="level(i)" aria-hidden="true"><i /><i /><i /></span>
              {{ t.intensities[i] }} <span class="mc-x-count">{{ intCounts.get(i) ?? 0 }}</span>
            </button>
          </div>
        </div>

        <div class="mc-x-group">
          <button
            type="button"
            role="switch"
            class="mc-x-switch"
            :aria-checked="state.curado"
            :disabled="!curatedCount && !state.curado"
            @click="state.curado = !state.curado"
          >
            <span class="mc-x-switch-track" aria-hidden="true"><span /></span>
            <span class="mc-x-switch-text">
              <span>{{ t.curatedOnly }} <span class="mc-x-count">{{ curatedCount }}</span></span>
              <small>{{ t.curatedHint }}</small>
            </span>
          </button>
        </div>

        <button v-if="activeFilters" type="button" class="mc-x-clear" @click="clearFilters">{{ t.clear }}</button>
      </aside>

      <main class="mc-x-results" :aria-label="t.title">
        <p class="mc-x-status" role="status">
          <strong>{{ t.count(results.length) }}</strong>
          <span>{{ t.ofTotal(data.total) }}</span>
          <span v-if="query && results.length > 1" class="mc-x-ranked">{{ t.rankedFor(query) }}</span>
        </p>

        <section v-for="s in sections" :key="s.id || 'flat'" class="mc-x-section" :aria-label="s.id ? t.families[s.id] : t.title">
          <h2 v-if="s.id" class="mc-x-section-title">
            {{ t.families[s.id] ?? s.id }} <span class="mc-x-count">{{ s.items.length }}</span>
          </h2>
          <div class="mc-x-grid">
            <a
              v-for="e in s.items"
              :key="e.id"
              v-thumb="e"
              class="mc-tile"
              :class="{ 'is-active': e.id === state.efeito }"
              :href="`?efeito=${e.id}`"
              :data-id="e.id"
              :tabindex="e.id === tabbableId ? 0 : -1"
              :aria-current="e.id === state.efeito ? 'true' : undefined"
              @click="onTileClick($event, e.id)"
              @keydown="onGridKey"
              @pointerenter="onEnter"
              @pointerleave="onLeave"
              @focus="onTileFocus($event, e.id)"
              @blur="onTileBlur"
            >
              <span class="mc-thumb">
                <span class="mc-thumb-host" data-thumb-host aria-hidden="true"></span>
                <span v-if="e.curado" class="mc-thumb-tag">{{ t.curatedTag }}</span>
                <span class="mc-thumb-dur">{{ dur(e) }}</span>
              </span>
              <span class="mc-tile-name">{{ e.nome }}</span>
              <span class="mc-tile-pt" :lang="ptLang">{{ e.nome_pt }}</span>
              <span class="mc-tile-meta">
                <code class="mc-tile-ease" :title="e.ease">{{ e.ease }}</code>
                <span class="mc-meter" :data-level="level(e.intensidade)" :title="`${t.intensity}: ${t.intensities[e.intensidade]}`">
                  <i /><i /><i />
                  <span class="mc-sr">{{ t.intensity }}: {{ t.intensities[e.intensidade] }}</span>
                </span>
              </span>
            </a>
          </div>
        </section>

        <div v-if="emptyAlternatives" class="mc-x-empty">
          <p class="mc-x-empty-title">{{ t.emptyTitle(query) }}</p>
          <p>{{ t.emptyHint }}</p>
          <p v-if="emptyAlternatives.withoutFilters">
            <button type="button" class="mc-x-linkbtn" @click="clearFilters">
              {{ t.emptyWithoutFilters(emptyAlternatives.withoutFilters) }}
            </button>
          </p>
          <div v-if="query" class="mc-x-suggest">
            <span>{{ t.suggestions }}</span>
            <button
              v-for="s in emptyAlternatives.suggestions"
              :key="s"
              type="button"
              class="mc-x-chip"
              :lang="ptLang"
              @click="state.q = s"
            >
              {{ s }}
            </button>
          </div>
        </div>
      </main>
    </div>

    <div v-if="selected && !wide" class="mc-x-scrim" aria-hidden="true" @click="close" />
    <EffectDetail
      v-if="selected && mounted"
      :key="'detail'"
      :entry="selected"
      :t="t"
      :by-id="byId"
      :autoplay="opened === 'click' && !reduced"
      :reduced="reduced"
      :modal="!wide"
      :has-prev="selIndex > 0"
      :has-next="selIndex >= 0 && selIndex < navList.length - 1"
      @close="close"
      @open="(id: string) => open(id)"
      @prev="step(-1)"
      @next="step(1)"
    />
  </div>
</template>

<style scoped>
.mc-x {
  --x-bg: var(--vp-c-bg);
  --x-bg-2: var(--vp-c-bg-soft);
  --x-bg-3: var(--vp-c-bg-alt);
  --x-rule: var(--vp-c-divider);
  --x-text: var(--vp-c-text-1);
  --x-text-2: var(--vp-c-text-2);
  --x-text-3: var(--vp-c-text-3);
  --x-active: var(--vp-c-brand-1);
  --x-monitor: #0d0e10;
  --x-panel-w: clamp(700px, 54vw, 880px);
  --x-top: 0px;
  box-sizing: border-box;
  max-width: 1680px;
  margin: 0 auto;
  padding: 28px 16px 96px;
  color: var(--x-text);
  font-family: var(--mc-font-body);
}
.mc-x *,
.mc-x *::before,
.mc-x *::after {
  box-sizing: border-box;
}
@media (min-width: 960px) {
  .mc-x {
    --x-top: var(--vp-nav-height);
    padding: 40px 32px 120px;
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

/* ---------------------------------------------------------------- header */

.mc-x-head {
  display: grid;
  gap: 14px;
  margin-bottom: 32px;
}
@media (min-width: 1100px) {
  .mc-x-head {
    grid-template-columns: minmax(0, 62ch) auto;
    column-gap: 56px;
    align-items: end;
  }
  .mc-x-head > :not(.mc-x-formula) {
    grid-column: 1;
  }
  .mc-x-title {
    grid-column: 1 / -1 !important;
  }
  .mc-x-formula {
    grid-column: 2;
    grid-row: 2 / span 3;
    align-self: end;
  }
}
.mc-x-title {
  margin: 0;
  font-family: var(--mc-font-display);
  font-weight: 400;
  font-size: clamp(2.6rem, 6vw, 4.4rem);
  line-height: 0.98;
  letter-spacing: 0.005em;
  color: var(--x-text);
}
.mc-x-lede {
  margin: 0;
  max-width: 68ch;
  font-size: var(--mc-step-1);
  line-height: 1.5;
  color: var(--x-text-2);
}
.mc-x-note {
  margin: 0;
  max-width: 72ch;
  font-size: 0.92rem;
  line-height: 1.5;
  color: var(--x-text-2);
  padding-left: 12px;
  border-left: 2px solid var(--x-rule);
}

.mc-x-formula {
  margin: 8px 0 0;
  display: grid;
  gap: 8px;
}
.mc-x-formula figcaption {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--x-text-2);
}
.mc-x-clips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.mc-x-clips li {
  display: grid;
  gap: 4px;
}
.mc-x-clip {
  display: block;
  padding: 7px 12px;
  border-radius: var(--mc-radius-clip);
  background: var(--x-bg-2);
  border: 1px solid var(--x-rule);
  font-family: var(--mc-font-mono);
  font-size: 0.86rem;
  line-height: 1.3;
  color: var(--x-text);
}
.mc-x-clips li:first-child .mc-x-clip {
  border-left: 3px solid var(--x-text);
}
.mc-x-cliplabel {
  padding-left: 2px;
  font-size: 0.78rem;
  color: var(--x-text-2);
}

/* ---------------------------------------------------------------- layout */

.mc-x-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  grid-template-areas:
    "search toggle"
    "rail rail"
    "results results";
  gap: 16px 12px;
}
.mc-x-search {
  grid-area: search;
}
.mc-x-filters-toggle {
  grid-area: toggle;
}
.mc-x-rail {
  grid-area: rail;
}
.mc-x-results {
  grid-area: results;
  min-width: 0;
}
@media (min-width: 1024px) {
  .mc-x-body {
    grid-template-columns: 236px minmax(0, 1fr);
    grid-template-rows: auto 1fr;
    grid-template-areas:
      "rail search"
      "rail results";
    gap: 20px 40px;
    align-items: start;
  }
  .mc-x-rail {
    position: sticky;
    top: calc(var(--x-top) + 20px);
    max-height: calc(100vh - var(--x-top) - 40px);
    overflow-y: auto;
    overscroll-behavior: contain;
    scrollbar-width: thin;
    padding-right: 4px;
  }
}
@media (max-width: 1023.98px) {
  .mc-x-rail:not(.is-open) {
    display: none;
  }
  .mc-x-rail {
    padding: 16px;
    border: 1px solid var(--x-rule);
    border-radius: 10px;
    background: var(--x-bg-2);
  }
}
/* docked inspector: the grid gives the panel its room */
@media (min-width: 1280px) {
  .mc-x.has-detail {
    max-width: none;
    margin-right: var(--x-panel-w);
  }
}

/* ---------------------------------------------------------------- search */

.mc-x-search {
  position: relative;
}
.mc-x-search input {
  width: 100%;
  height: 50px;
  padding: 0 16px 0 46px;
  border: 1px solid var(--x-rule);
  border-radius: 10px;
  background: var(--x-bg-2);
  color: var(--x-text);
  font: 500 1rem/1 var(--mc-font-body);
}
.mc-x-search input::placeholder {
  color: var(--x-text-3);
}
.mc-x-search input:hover {
  border-color: var(--x-text-3);
}
.mc-x-search input:focus-visible {
  outline: 2px solid var(--x-active);
  outline-offset: 1px;
}
.mc-x-search-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  width: 20px;
  height: 20px;
  transform: translateY(-50%);
  fill: none;
  stroke: var(--x-text-2);
  stroke-width: 2;
  stroke-linecap: round;
  pointer-events: none;
}

.mc-x-filters-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 50px;
  padding: 0 16px;
  border: 1px solid var(--x-rule);
  border-radius: 10px;
  background: var(--x-bg-2);
  color: var(--x-text);
  font: 600 0.95rem/1 var(--mc-font-body);
  cursor: pointer;
}
.mc-x-filters-toggle svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}
.mc-x-filters-toggle[aria-expanded="true"] {
  border-color: var(--x-text-2);
}
@media (min-width: 1024px) {
  .mc-x-filters-toggle {
    display: none;
  }
}
.mc-x-badge {
  display: inline-grid;
  place-items: center;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  border-radius: 10px;
  background: var(--x-active);
  color: var(--x-bg);
  font: 700 0.75rem/1 var(--mc-font-mono);
}

/* ---------------------------------------------------------------- rail */

.mc-x-group + .mc-x-group {
  margin-top: 22px;
}
.mc-x-group-title {
  margin: 0 0 8px;
  font: 600 0.85rem/1.3 var(--mc-font-body);
  color: var(--x-text-2);
}
.mc-x-count {
  font-family: var(--mc-font-mono);
  font-size: 0.78em;
  font-variant-numeric: tabular-nums;
  color: var(--x-text-3);
}
.mc-x-fams {
  margin: 0;
  padding: 0;
  list-style: none;
}
.mc-x-fam {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  width: 100%;
  padding: 6px 10px;
  border: 0;
  border-left: 2px solid transparent;
  border-radius: 0 4px 4px 0;
  background: none;
  color: var(--x-text-2);
  font: 500 0.92rem/1.3 var(--mc-font-body);
  text-align: left;
  cursor: pointer;
}
.mc-x-fam:hover:not(:disabled) {
  color: var(--x-text);
  background: var(--x-bg-2);
}
.mc-x-fam[aria-pressed="true"] {
  color: var(--x-text);
  font-weight: 650;
  border-left-color: var(--x-active);
  background: var(--x-bg-2);
}
.mc-x-fam:disabled {
  opacity: 0.4;
  cursor: default;
}
@media (max-width: 1023.98px) {
  .mc-x-fams {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0 12px;
  }
}

.mc-x-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.mc-x-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 32px;
  padding: 4px 10px;
  border: 1px solid var(--x-rule);
  border-radius: 6px;
  background: transparent;
  color: var(--x-text-2);
  font: 500 0.86rem/1.2 var(--mc-font-body);
  cursor: pointer;
}
.mc-x-chip:hover:not(:disabled) {
  color: var(--x-text);
  border-color: var(--x-text-3);
}
.mc-x-chip[aria-pressed="true"] {
  color: var(--x-text);
  border-color: var(--x-active);
  box-shadow: inset 0 0 0 1px var(--x-active);
  font-weight: 600;
}
.mc-x-chip:disabled {
  opacity: 0.4;
  cursor: default;
}

.mc-x-switch {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  padding: 4px 0;
  border: 0;
  background: none;
  color: var(--x-text);
  text-align: left;
  font: 600 0.92rem/1.3 var(--mc-font-body);
  cursor: pointer;
}
.mc-x-switch:disabled {
  opacity: 0.4;
  cursor: default;
}
.mc-x-switch small {
  display: block;
  margin-top: 2px;
  font-weight: 400;
  font-size: 0.8rem;
  color: var(--x-text-2);
}
.mc-x-switch-track {
  flex: none;
  position: relative;
  width: 34px;
  height: 20px;
  margin-top: 1px;
  border-radius: 10px;
  border: 1px solid var(--x-text-3);
  background: var(--x-bg-2);
}
.mc-x-switch-track span {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--x-text-2);
  transition: transform 0.15s var(--mc-ease-out);
}
.mc-x-switch[aria-checked="true"] .mc-x-switch-track {
  border-color: var(--x-active);
  background: var(--x-active);
}
.mc-x-switch[aria-checked="true"] .mc-x-switch-track span {
  transform: translateX(14px);
  background: var(--x-bg);
}

.mc-x-clear,
.mc-x-linkbtn {
  margin-top: 20px;
  padding: 0;
  border: 0;
  background: none;
  color: var(--x-active);
  font: 600 0.9rem/1.3 var(--mc-font-body);
  text-decoration: underline;
  text-underline-offset: 3px;
  cursor: pointer;
}
.mc-x-linkbtn {
  margin: 0;
  font-size: 1rem;
}

/* ---------------------------------------------------------------- results */

.mc-x-status {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px 8px;
  margin: 0 0 12px;
  font-size: 0.92rem;
  color: var(--x-text-2);
}
.mc-x-status strong {
  color: var(--x-text);
  font-weight: 650;
}
.mc-x-ranked {
  flex-basis: 100%;
}
@media (min-width: 640px) {
  .mc-x-ranked {
    flex-basis: auto;
    margin-left: auto;
  }
}

.mc-x-section + .mc-x-section {
  margin-top: 36px;
}
.mc-x-section-title {
  position: sticky;
  top: var(--x-top);
  z-index: 2;
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin: 0 0 12px;
  padding: 10px 0 8px;
  background: var(--x-bg);
  border-bottom: 1px solid var(--x-rule);
  font-family: var(--mc-font-display);
  font-weight: 400;
  font-size: var(--mc-step-2);
  line-height: 1.1;
  letter-spacing: 0.005em;
  color: var(--x-text);
}
.mc-x-section-title .mc-x-count {
  font-size: 0.85rem;
}

.mc-x-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(104px, 1fr));
  gap: 18px 12px;
}
@media (min-width: 640px) {
  .mc-x-grid {
    grid-template-columns: repeat(auto-fill, minmax(124px, 1fr));
    gap: 22px 14px;
  }
}

.mc-tile {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  padding: 0 0 4px;
  border-radius: 6px;
  color: inherit;
  text-decoration: none;
  outline-offset: 4px;
}
.mc-thumb {
  position: relative;
  display: block;
  aspect-ratio: 9 / 16;
  margin-bottom: 6px;
  border-radius: 8px;
  overflow: hidden;
  background:
    linear-gradient(rgba(243, 237, 226, 0.04) 1px, transparent 1px) 0 0 / 11.11% 6.25%,
    linear-gradient(90deg, rgba(243, 237, 226, 0.04) 1px, transparent 1px) 0 0 / 11.11% 6.25%,
    var(--x-monitor);
  box-shadow: 0 0 0 1px var(--x-rule);
  isolation: isolate;
}
.mc-thumb-host {
  position: absolute;
  inset: 0;
  overflow: hidden;
}
.mc-thumb-host :deep(.mc-stage-root) {
  transform: scale(var(--mc-thumb-scale, 0.12));
  transform-origin: 0 0;
}
.mc-tile:hover .mc-thumb {
  box-shadow: 0 0 0 1px var(--x-text-3);
}
.mc-tile.is-active .mc-thumb {
  box-shadow: 0 0 0 2px var(--x-active);
}
.mc-tile[data-thumb="error"] .mc-thumb-host::after {
  content: "";
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(135deg, transparent 0 8px, rgba(229, 72, 77, 0.18) 8px 10px);
}
.mc-thumb-tag,
.mc-thumb-dur {
  position: absolute;
  z-index: 1;
  padding: 2px 5px;
  border-radius: 3px;
  font: 600 10.5px/1.3 var(--mc-font-mono);
  pointer-events: none;
}
.mc-thumb-tag {
  top: 6px;
  left: 6px;
  background: #f2efe8;
  color: #16171a;
  font-family: var(--mc-font-body);
  font-weight: 650;
}
.mc-thumb-dur {
  right: 6px;
  bottom: 6px;
  background: rgba(8, 9, 10, 0.72);
  color: #f2efe8;
  font-variant-numeric: tabular-nums;
}
.mc-tile[data-playing] .mc-thumb-dur {
  background: var(--mc-tungsten);
  color: #16171a;
}
.mc-tile-name {
  font: 650 0.92rem/1.25 var(--mc-font-body);
  color: var(--x-text);
  overflow-wrap: anywhere;
}
.mc-tile.is-active .mc-tile-name {
  color: var(--x-active);
}
.mc-tile-pt {
  font-size: 0.8rem;
  line-height: 1.3;
  color: var(--x-text-2);
  overflow-wrap: anywhere;
}
.mc-tile-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 3px;
  min-width: 0;
}
.mc-tile-ease {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0;
  background: none;
  font: 500 0.72rem/1.3 var(--mc-font-mono);
  color: var(--x-text-2);
}

/* intensity as a three-step level meter */
.mc-meter {
  flex: none;
  display: inline-flex;
  align-items: flex-end;
  gap: 2px;
  height: 12px;
}
.mc-meter i {
  display: block;
  width: 3px;
  border-radius: 1px;
  background: var(--x-rule);
}
.mc-meter i:nth-child(1) {
  height: 5px;
}
.mc-meter i:nth-child(2) {
  height: 8px;
}
.mc-meter i:nth-child(3) {
  height: 12px;
}
.mc-meter[data-level="1"] i:nth-child(-n + 1),
.mc-meter[data-level="2"] i:nth-child(-n + 2),
.mc-meter[data-level="3"] i:nth-child(-n + 3) {
  background: var(--x-text-2);
}

/* ---------------------------------------------------------------- empty */

.mc-x-empty {
  display: grid;
  gap: 10px;
  max-width: 60ch;
  padding: 32px 0;
  color: var(--x-text-2);
}
.mc-x-empty p {
  margin: 0;
}
.mc-x-empty-title {
  font-family: var(--mc-font-display);
  font-size: var(--mc-step-3);
  line-height: 1.1;
  color: var(--x-text);
  overflow-wrap: anywhere;
}
.mc-x-suggest {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
}
.mc-x-suggest > span {
  margin-right: 4px;
  font-weight: 600;
  color: var(--x-text);
}

/* docked inspector (>= 1280 px): the bin narrows and the filters fold into the toggle */
@media (min-width: 1280px) {
  .mc-x.has-detail .mc-x-body {
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas:
      "search toggle"
      "rail rail"
      "results results";
    gap: 16px 12px;
  }
  .mc-x.has-detail .mc-x-filters-toggle {
    display: inline-flex;
  }
  .mc-x.has-detail .mc-x-rail {
    position: static;
    max-height: none;
    overflow: visible;
    padding: 16px;
    border: 1px solid var(--x-rule);
    border-radius: 10px;
    background: var(--x-bg-2);
  }
  .mc-x.has-detail .mc-x-rail:not(.is-open) {
    display: none;
  }
  .mc-x.has-detail .mc-x-fams {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0 12px;
  }
}

.mc-x-scrim {
  position: fixed;
  inset: 0;
  z-index: 70;
  background: rgba(8, 9, 10, 0.55);
}
</style>

<style>
/* page-level: the explorer page owns its width; the modal sheet locks the page scroll */
.mc-explorer .VPPage {
  padding: 0;
}
html.mc-scroll-lock {
  overflow: hidden;
}
</style>
