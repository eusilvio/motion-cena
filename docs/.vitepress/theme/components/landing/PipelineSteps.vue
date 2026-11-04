<script setup lang="ts">
import { computed, ref } from "vue";
import type { LandingCopy, PipelineStep } from "./i18n";

const props = defineProps<{ p: LandingCopy["pipeline"]; uid: string }>();
const sel = ref(0);
const tabs = ref<HTMLButtonElement[]>([]);
const step = computed(() => props.p.steps[sel.value]);
const pad = (n: number) => String(n).padStart(2, "0");
/** first step of each phase shows the phase name above it */
const phaseStart = (i: number) => i === 0 || props.p.steps[i - 1].phase !== props.p.steps[i].phase;

function choose(i: number, focus = false) {
  sel.value = i;
  if (focus) {
    const el = tabs.value[i];
    el?.focus();
    el?.scrollIntoView({ block: "nearest", inline: "nearest" });
  }
}
function onKey(e: KeyboardEvent, i: number) {
  const n = props.p.steps.length;
  let k = -1;
  if (e.key === "ArrowDown" || e.key === "ArrowRight") k = (i + 1) % n;
  else if (e.key === "ArrowUp" || e.key === "ArrowLeft") k = (i - 1 + n) % n;
  else if (e.key === "Home") k = 0;
  else if (e.key === "End") k = n - 1;
  if (k < 0) return;
  e.preventDefault();
  choose(k, true);
}

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const keys = (s: string) => s.replace(/("[^"\n]*")(\s*:)/g, '<span class="c-k">$1</span>$2');

/** a tiny, calm highlighter: prompts, output, JSON keys, comments, markdown headings */
function highlight(s: PipelineStep): string {
  let cont = false;
  return s.code
    .split("\n")
    .map((line) => {
      if (s.lang === "chat") {
        const m = line.match(/^(\S+)(\s+)(.*)$/);
        return m ? `<span class="c-who">${esc(m[1])}</span>${m[2]}${esc(m[3])}` : esc(line);
      }
      if (s.lang === "md") {
        if (/^#{1,3} /.test(line)) return `<span class="c-h">${esc(line)}</span>`;
        return esc(line).replace(/\*\*(.+?)\*\*/g, '<span class="c-h">$1</span>');
      }
      if (s.lang === "html") {
        if (/^\s*\/\//.test(line)) return `<span class="c-c">${esc(line)}</span>`;
        return keys(esc(line));
      }
      if (s.lang === "sh") {
        const isCmd = line.startsWith("$ ") || cont;
        cont = isCmd && line.trimEnd().endsWith("\\");
        if (line.startsWith("$ ")) return `<span class="c-p">$</span> ${esc(line.slice(2))}`;
        if (isCmd) return esc(line);
        const ok = line.match(/^(\s*)(OK|RESULT: PASS)(.*)$/);
        if (ok) return `${ok[1]}<span class="c-ok">${ok[2]}</span><span class="c-out">${esc(ok[3])}</span>`;
        if (/^\s*[[\]{}"]/.test(line)) return keys(esc(line));
        return `<span class="c-out">${esc(line)}</span>`;
      }
      return keys(esc(line));
    })
    .map((l, i) => `<span class="ln" aria-hidden="true">${i + 1}</span>${l}`)
    .join("\n");
}
const html = computed(() => highlight(step.value));
</script>

<template>
  <section class="mcl-sec" :aria-labelledby="`${uid}-pipe`">
    <header class="mcl-sec-head">
      <h2 :id="`${uid}-pipe`" class="mcl-h2">{{ p.title }}</h2>
      <p class="mcl-sec-lead">{{ p.lead }}</p>
    </header>

    <div class="pipe">
      <div class="steps" role="tablist" aria-orientation="vertical" :aria-label="p.listLabel">
        <button
          v-for="(s, i) in p.steps"
          :id="`${uid}-tab-${i}`"
          :key="i"
          ref="tabs"
          type="button"
          role="tab"
          class="step"
          :class="{ 'is-sel': i === sel, 'has-phase': phaseStart(i) }"
          :data-phase="phaseStart(i) ? p.phases[s.phase] : null"
          :aria-selected="i === sel"
          :aria-controls="`${uid}-panel`"
          :tabindex="i === sel ? 0 : -1"
          @click="choose(i)"
          @keydown="onKey($event, i)"
        >
          <span class="n mcl-mono">{{ pad(i + 1) }}</span>
          <span class="nm">{{ s.name }}</span>
        </button>
      </div>

      <div :id="`${uid}-panel`" class="viewer" role="tabpanel" :aria-labelledby="`${uid}-tab-${sel}`">
        <div class="v-head">
          <span class="v-file mcl-mono" :class="{ 'is-none': !step.file }">{{ step.file ?? p.noFile }}</span>
          <span class="v-phase">{{ p.phases[step.phase] }}</span>
        </div>
        <p class="v-note">{{ step.note }}</p>
        <pre class="v-code" tabindex="0"><code v-html="html" /></pre>
      </div>
    </div>
  </section>
</template>

<style scoped>
.pipe {
  display: grid;
  grid-template-columns: minmax(220px, 290px) minmax(0, 1fr);
  gap: 0 clamp(28px, 4vw, 56px);
  align-items: stretch;
}
.steps {
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--vp-c-divider);
}
.step {
  position: relative;
  display: flex;
  align-items: baseline;
  gap: 14px;
  min-height: 32px;
  padding: 5px 12px 5px 18px;
  text-align: left;
  font-size: 0.98rem;
  color: var(--vp-c-text-2);
  transition: color 0.12s;
}
.step.has-phase:not(:first-child) {
  margin-top: 26px;
}
.step.has-phase::before {
  content: attr(data-phase);
  position: absolute;
  left: 18px;
  bottom: calc(100% + 2px);
  font-size: 0.8rem;
  color: var(--vp-c-text-3);
}
.step:first-child {
  margin-top: 26px;
}
.step::after {
  content: "";
  position: absolute;
  left: -1px;
  top: 4px;
  bottom: 4px;
  width: 2px;
  background: transparent;
  transition: background-color 0.12s;
}
.step:hover {
  color: var(--vp-c-text-1);
}
.step .n {
  font-size: 0.78rem;
  color: var(--vp-c-text-3);
}
.step.is-sel {
  color: var(--vp-c-text-1);
  font-weight: 600;
}
.step.is-sel::after {
  background: var(--mc-tungsten);
}
.step.is-sel .n {
  color: var(--vp-c-brand-1);
}
.step:focus-visible {
  outline: 2px solid var(--vp-c-brand-1);
  outline-offset: -2px;
}

.viewer {
  display: flex;
  flex-direction: column;
  min-width: 0;
  margin-top: 22px;
  border-radius: 6px;
  box-shadow: 0 0 0 1px var(--vp-c-divider);
  background: var(--vp-code-block-bg);
  overflow: hidden;
}
.v-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 18px 0;
}
.v-file {
  min-width: 0;
  overflow-wrap: anywhere;
  font-size: 0.86rem;
  font-weight: 500;
  color: var(--vp-c-text-1);
}
.v-file.is-none {
  color: var(--vp-c-text-3);
  font-style: italic;
}
.v-phase {
  flex: none;
  font-size: 0.8rem;
  color: var(--vp-c-text-3);
}
.v-note {
  max-width: none;
  min-height: 3.2em;
  padding: 6px 18px 14px;
  border-bottom: 1px solid var(--vp-c-divider);
  font-size: 0.92rem;
  line-height: 1.6;
  color: var(--vp-c-text-2);
}
.v-code {
  flex: 1;
  min-height: 300px;
  height: 0;
  overflow: auto;
  padding: 16px 18px 20px 8px;
  font: 12.8px/1.65 var(--mc-font-mono);
  color: var(--vp-c-text-1);
  white-space: pre;
  tab-size: 2;
  background: transparent;
}
.v-code :deep(.ln) {
  display: inline-block;
  width: 2.2em;
  margin-right: 1.1em;
  text-align: right;
  color: var(--vp-c-text-3);
  opacity: 0.6;
  user-select: none;
}
.v-code code {
  font: inherit;
  color: inherit;
  background: none;
  padding: 0;
}
.v-code:focus-visible {
  outline: 2px solid var(--vp-c-brand-1);
  outline-offset: -2px;
}

@media (max-width: 767px) {
  .pipe {
    grid-template-columns: minmax(0, 1fr);
    gap: 18px;
  }
  /* a filmstrip of steps that scrolls sideways */
  .steps {
    flex-direction: row;
    overflow-x: auto;
    scroll-snap-type: x proximity;
    scrollbar-width: none;
    border-left: 0;
    border-bottom: 1px solid var(--vp-c-divider);
    margin: 0 -24px;
    padding: 0 24px;
  }
  .steps::-webkit-scrollbar {
    display: none;
  }
  .step,
  .step:first-child,
  .step.has-phase:not(:first-child) {
    flex: none;
    flex-direction: column;
    gap: 2px;
    margin: 0;
    padding: 10px 14px 12px 0;
    scroll-snap-align: start;
  }
  .step.has-phase::before {
    display: none;
  }
  .step::after {
    left: 0;
    right: 14px;
    top: auto;
    bottom: -1px;
    width: auto;
    height: 2px;
  }
  .nm {
    white-space: nowrap;
  }
  .viewer {
    margin-top: 0;
  }
  .v-code {
    flex: none;
    height: 320px;
    font-size: 12px;
  }
}
</style>
