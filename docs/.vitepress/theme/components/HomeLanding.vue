<script setup lang="ts">
import { computed } from "vue";
import { withBase } from "vitepress";
import { COPY, REPO_URL, type Locale } from "./landing/i18n";
import HeroSuite from "./landing/HeroSuite.vue";
import PipelineSteps from "./landing/PipelineSteps.vue";
import TeaserLinks from "./landing/TeaserLinks.vue";
import CostTimes from "./landing/CostTimes.vue";
import CopyButton from "./landing/CopyButton.vue";
import "./landing/landing.css";

const props = defineProps<{ locale?: Locale }>();
const loc = computed<Locale>(() => (props.locale === "en" ? "en" : "pt"));
const c = computed(() => COPY[loc.value]);
const uid = computed(() => `mcl-${loc.value}`);
/** break the clone URL only after its slashes */
const cloneParts = computed(() => c.value.hero.clone.split(/(?<= )|(?<=github\.com\/)|(?<=eusilvio\/)/));
</script>

<template>
  <div class="mcl" :lang="c.lang">
    <HeroSuite :hero="c.hero" :decimal="c.decimal" :uid="uid">
      <h1 class="mcl-h1">
        <span>{{ c.hero.title[0] }}</span>
        <span>{{ c.hero.title[1] }}</span>
      </h1>
      <p class="mcl-lead">{{ c.hero.lead }}</p>
      <div class="mcl-actions">
        <div class="mcl-clone">
          <span class="mcl-clone-cmd">
            <span class="mcl-prompt" aria-hidden="true">$</span>
            <span><template v-for="(part, i) in cloneParts" :key="i"><span class="mcl-nw">{{ part }}</span><wbr /></template></span>
          </span>
          <CopyButton :text="c.hero.clone" :label="c.hero.copy" :done="c.hero.copied" :context="c.hero.copyLabel" variant="primary" />
        </div>
        <a class="mcl-link" :href="withBase(c.links.guide)">{{ c.hero.guide }}</a>
      </div>
    </HeroSuite>

    <!-- what you can ask -->
    <section class="mcl-sec" :aria-labelledby="`${uid}-ask`">
      <header class="mcl-sec-head">
        <h2 :id="`${uid}-ask`" class="mcl-h2">{{ c.ask.title }}</h2>
        <p class="mcl-sec-lead">{{ c.ask.lead }}</p>
      </header>
      <div class="ask">
        <div class="ask-row ask-head" aria-hidden="true">
          <span>{{ c.ask.colAsk }}</span>
          <span>{{ c.ask.colGet }}</span>
        </div>
        <dl>
          <div v-for="(r, i) in c.ask.rows" :key="i" class="ask-row">
            <dt class="ask-q">“{{ r[0] }}”</dt>
            <dd class="ask-a">{{ r[1] }}</dd>
          </div>
        </dl>
        <p class="ask-iter">
          {{ c.ask.iterate }}
          <template v-for="(it, i) in c.ask.iterations" :key="i">
            <q>{{ it }}</q>{{ c.ask.iterations.length - 1 > i ? ", " : "." }}
          </template>
        </p>
      </div>
    </section>

    <PipelineSteps :p="c.pipeline" :uid="uid" />

    <TeaserLinks :t="c.teaser" :links="c.links" :uid="uid" />

    <!-- quick start -->
    <section class="mcl-sec" :aria-labelledby="`${uid}-start`">
      <header class="mcl-sec-head">
        <h2 :id="`${uid}-start`" class="mcl-h2">{{ c.start.title }}</h2>
        <p class="mcl-sec-lead">{{ c.start.lead }}</p>
      </header>
      <div class="qs">
        <ol class="qs-steps">
          <li v-for="(s, i) in c.start.steps" :key="i" class="qs-step">
            <span class="qs-n mcl-mono" aria-hidden="true">{{ i + 1 }}</span>
            <div class="qs-body">
              <p class="qs-label">{{ s.label }}</p>
              <div class="term">
                <pre class="term-code"><code><template v-for="(l, li) in s.lines" :key="li"><span class="c-p">$ </span>{{ l }}{{ s.lines.length - 1 > li ? "\n" : "" }}</template></code></pre>
                <CopyButton :text="s.lines.join('\n')" :label="c.start.copy" :done="c.start.copied" :context="`${c.start.copyStep} ${i + 1}`" />
              </div>
              <p v-if="s.note" class="qs-note">{{ s.note }}</p>
            </div>
          </li>
        </ol>
        <div class="qs-side">
          <p class="mcl-body">{{ c.start.keys }}</p>
          <div class="qs-block">
            <h3 class="qs-h">{{ c.start.windowsTitle }}</h3>
            <p class="mcl-body">{{ c.start.windows }}</p>
            <a class="mcl-link" :href="withBase(c.links.windows)">{{ c.start.windowsLink }}</a>
          </div>
          <div class="qs-block">
            <h3 class="qs-h">{{ c.start.firstTitle }}</h3>
            <p class="qs-first">“{{ c.start.first }}”</p>
            <a class="mcl-link" :href="withBase(c.links.firstVideo)">{{ c.start.firstLink }}</a>
          </div>
        </div>
      </div>
    </section>

    <CostTimes :c="c.cost" :link="c.links.cost" :uid="uid" />

    <!-- any agent -->
    <section class="mcl-sec" :aria-labelledby="`${uid}-agents`">
      <header class="mcl-sec-head">
        <h2 :id="`${uid}-agents`" class="mcl-h2">{{ c.agents.title }}</h2>
        <p class="mcl-sec-lead">{{ c.agents.lead }}</p>
      </header>
      <dl class="credits">
        <div v-for="r in c.agents.rows" :key="r.file" class="cr">
          <dt>
            <span class="mcl-mono">{{ r.file }}</span>
            <span v-if="r.note" class="cr-note">{{ r.note }}</span>
          </dt>
          <dd>
            <span v-for="n in r.names" :key="n" class="cr-name">{{ n }}</span>
          </dd>
        </div>
      </dl>
      <div class="agents-foot">
        <p class="mcl-body">{{ c.agents.note }}</p>
        <a class="mcl-link" :href="withBase(c.links.agents)">{{ c.agents.link }}</a>
      </div>
    </section>

    <!-- closing -->
    <section class="mcl-sec cta" :aria-labelledby="`${uid}-cta`">
      <h2 :id="`${uid}-cta`" class="cta-title">{{ c.cta.title }}</h2>
      <div class="cta-side">
        <p class="mcl-body cta-body">{{ c.cta.body }}</p>
        <div class="cta-actions">
          <a class="mcl-btn mcl-btn-primary" :href="REPO_URL">{{ c.cta.github }}</a>
          <a class="mcl-btn mcl-btn-quiet" :href="withBase(c.links.contribute)">{{ c.cta.contribute }}</a>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* --- what you can ask: a spoken request beside what comes out --------- */
.ask-row {
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 5fr);
  gap: 8px 48px;
  padding: 18px 0;
  border-top: 1px solid var(--vp-c-divider);
}
.ask-head {
  padding: 0 0 10px;
  border-top: 0;
  font-size: 0.82rem;
  color: var(--vp-c-text-3);
}
.ask-q {
  font-size: clamp(1.08rem, 1rem + 0.35vw, 1.28rem);
  line-height: 1.45;
  font-style: italic;
  color: var(--vp-c-text-1);
}
.ask-a {
  margin: 0;
  padding-top: 3px;
  font-size: 0.98rem;
  line-height: 1.55;
  color: var(--vp-c-text-2);
}
.ask-iter {
  padding-top: 18px;
  border-top: 1px solid var(--vp-c-divider);
  font-size: 1rem;
  color: var(--vp-c-text-2);
}
.ask-iter q {
  font-style: italic;
  color: var(--vp-c-text-1);
}
.ask-iter q::before {
  content: "“";
}
.ask-iter q::after {
  content: "”";
}

/* --- quick start ------------------------------------------------------- */
.qs {
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 5fr);
  gap: 40px clamp(32px, 5vw, 72px);
  align-items: start;
}
.qs-step {
  position: relative;
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 0 16px;
  padding-bottom: 30px;
}
.qs-step:last-child {
  padding-bottom: 0;
}
/* the steps are a sequence: a rule ties each number to the next */
.qs-step:not(:last-child)::before {
  content: "";
  position: absolute;
  left: 16px;
  top: 32px;
  bottom: 4px;
  border-left: 1px solid var(--vp-c-divider);
}
.qs-n {
  display: grid;
  place-items: center;
  width: 33px;
  height: 33px;
  border-radius: 50%;
  box-shadow: inset 0 0 0 1px var(--vp-c-divider);
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}
.qs-label {
  padding-top: 5px;
  font-weight: 600;
}
.term {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  padding: 10px 10px 10px 16px;
  border-radius: 6px;
  background: var(--vp-code-block-bg);
  box-shadow: 0 0 0 1px var(--vp-c-divider);
}
.term-code {
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: thin;
  font: 13px/1.7 var(--mc-font-mono);
  color: var(--vp-c-text-1);
  background: none;
}
.term-code code {
  font: inherit;
  color: inherit;
  background: none;
  padding: 0;
}
.qs-note {
  margin-top: 10px;
  font-size: 0.92rem;
  line-height: 1.55;
  color: var(--vp-c-text-2);
}
.qs-side {
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.qs-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  padding-top: 22px;
  border-top: 1px solid var(--vp-c-divider);
}
.qs-h {
  margin: 0;
  padding: 0;
  border: 0;
  font-size: 1rem;
  font-weight: 650;
  line-height: 1.4;
  letter-spacing: 0;
  color: var(--vp-c-text-1);
}
.qs-first {
  font-size: 1.08rem;
  font-style: italic;
  line-height: 1.5;
  color: var(--vp-c-text-1);
}

/* --- any agent: set like a credit roll -------------------------------- */
.cr {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  gap: 8px 48px;
  padding: 22px 0;
  border-top: 1px solid var(--vp-c-divider);
}
.cr dt {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 6px;
  font-size: 0.95rem;
  color: var(--vp-c-text-1);
}
.cr-note {
  font-size: 0.85rem;
  color: var(--vp-c-text-3);
}
.cr dd {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 1.1em;
  margin: 0;
}
.cr-name {
  font-size: clamp(1.35rem, 1.1rem + 0.8vw, 1.85rem);
  font-weight: 500;
  line-height: 1.3;
  letter-spacing: -0.01em;
  color: var(--vp-c-text-1);
}
.agents-foot {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  gap: 12px 48px;
  padding-top: 22px;
  border-top: 1px solid var(--vp-c-divider);
}
.agents-foot .mcl-body {
  grid-column: 2;
  max-width: 62ch;
}
.agents-foot .mcl-link {
  grid-column: 2;
  justify-self: start;
}

/* --- closing ----------------------------------------------------------- */
.cta {
  display: grid;
  grid-template-columns: minmax(0, 6fr) minmax(0, 5fr);
  gap: 28px 48px;
  align-items: end;
  padding-top: clamp(40px, 6vw, 72px);
}
.cta-title {
  margin: 0;
  padding: 0;
  border: 0;
  font: 400 clamp(3rem, 1.4rem + 5vw, 6rem) / 0.96 var(--mc-font-display);
  letter-spacing: 0.002em;
  color: var(--vp-c-text-1);
  text-wrap: balance;
}
.cta-body {
  max-width: 48ch;
}
.cta-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 22px;
}

@media (max-width: 767px) {
  .ask-row,
  .qs,
  .cr,
  .agents-foot,
  .cta {
    grid-template-columns: minmax(0, 1fr);
  }
  .ask-head {
    display: none;
  }
  .ask-row {
    gap: 6px;
  }
  .agents-foot .mcl-body,
  .agents-foot .mcl-link {
    grid-column: 1;
  }
}
</style>
