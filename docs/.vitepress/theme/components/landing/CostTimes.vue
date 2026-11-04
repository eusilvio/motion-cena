<script setup lang="ts">
import { withBase } from "vitepress";
import type { LandingCopy } from "./i18n";

const props = defineProps<{ c: LandingCopy["cost"]; link: string; uid: string }>();
const MAX = 45; // minutes on the scale
const w = (min: number) => `${((min / MAX) * 100).toFixed(3)}%`;
const scale = [0, 15, 30, 45];
void props;
</script>

<template>
  <section class="mcl-sec" :aria-labelledby="`${uid}-cost`">
    <header class="mcl-sec-head">
      <h2 :id="`${uid}-cost`" class="mcl-h2">{{ c.title }}</h2>
      <p class="mcl-sec-lead">{{ c.lead }}</p>
    </header>

    <div class="ct" role="table" :aria-labelledby="`${uid}-cost`">
      <div class="ct-row ct-head" role="row">
        <span role="columnheader">{{ c.colPiece }}</span>
        <span role="columnheader" class="h-time">
          {{ c.colTime }}
          <span class="scale" aria-hidden="true">
            <span v-for="s in scale" :key="s" :style="{ left: w(s) }" class="mcl-mono">{{ s }}{{ s === MAX ? ` ${c.unit}` : "" }}</span>
          </span>
        </span>
        <span role="columnheader">{{ c.colTokens }}</span>
        <span role="columnheader">{{ c.colCost }}</span>
        <span role="columnheader">{{ c.colRender }}</span>
      </div>

      <div v-for="(r, i) in c.rows" :key="i" class="ct-row" role="row">
        <div role="cell" class="c-piece">
          <span class="piece">{{ r.piece }}</span>
          <span class="voice">{{ r.voice }}</span>
        </div>
        <div role="cell" class="c-time">
          <span class="bar" aria-hidden="true">
            <i class="b-first" :style="{ width: w(r.first) }" />
            <i class="b-rev" :style="{ left: w(r.first), width: w(r.total - r.first) }" />
          </span>
          <span class="t-labels">
            <span><i class="sw sw-first" aria-hidden="true" /><span class="mcl-mono">{{ r.firstLabel }}</span> <span class="lg">{{ c.legendFirst }}</span></span>
            <span><i class="sw sw-rev" aria-hidden="true" /><span class="mcl-mono">{{ r.totalLabel }}</span> <span class="lg">{{ c.legendTotal }}</span></span>
          </span>
        </div>
        <div role="cell" class="c-num">
          <span class="m-l">{{ c.colTokens }}</span>
          <span class="mcl-mono">{{ r.tokens }}</span>
        </div>
        <div role="cell" class="c-num">
          <span class="m-l">{{ c.colCost }}</span>
          <span class="mcl-mono">{{ r.cost }}</span>
          <span class="sub">{{ r.costFirst }}</span>
        </div>
        <div role="cell" class="c-num">
          <span class="m-l">{{ c.colRender }}</span>
          <span class="mcl-mono">{{ r.render }}</span>
        </div>
      </div>
    </div>

    <div class="ct-foot">
      <p class="mcl-body">{{ c.notes }}</p>
      <p class="mcl-body">{{ c.tip }}</p>
      <a class="mcl-link" :href="withBase(link)">{{ c.link }}</a>
    </div>
  </section>
</template>

<style scoped>
.ct {
  --cols: minmax(0, 2.3fr) minmax(0, 3fr) minmax(0, 0.9fr) minmax(0, 1.35fr) minmax(0, 1.2fr);
}
.ct-row {
  display: grid;
  grid-template-columns: var(--cols);
  gap: 0 28px;
  align-items: start;
  padding: 20px 0;
  border-top: 1px solid var(--vp-c-divider);
}
.ct-head {
  padding: 0 0 12px;
  border-top: 0;
  font-size: 0.82rem;
  color: var(--vp-c-text-3);
}
.h-time {
  position: relative;
}
.scale {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(100% + 1px);
  height: 0;
}
.scale span {
  position: absolute;
  top: 0;
  transform: translateX(-50%);
  font-size: 0.7rem;
  color: var(--vp-c-text-3);
  white-space: nowrap;
}
.scale span:first-child {
  transform: none;
}
.scale span:last-child {
  transform: translateX(-100%);
}
.piece {
  display: block;
  font-weight: 600;
  line-height: 1.4;
}
.voice {
  display: block;
  margin-top: 4px;
  font-size: 0.88rem;
  color: var(--vp-c-text-2);
}
.c-time {
  padding-top: 6px;
}
.bar {
  position: relative;
  display: block;
  height: 14px;
  border-radius: 2px;
  background: var(--vp-c-bg-soft);
}
.bar i {
  position: absolute;
  top: 0;
  bottom: 0;
  display: block;
}
.b-first {
  left: 0;
  background: var(--mc-tungsten);
  border-radius: 2px 0 0 2px;
}
.b-rev {
  box-shadow: inset 0 0 0 1.5px var(--mc-tungsten);
  background: rgba(242, 179, 61, 0.14);
  border-radius: 0 2px 2px 0;
}
.t-labels {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 18px;
  margin-top: 10px;
  font-size: 0.86rem;
}
.t-labels > span {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}
.lg {
  color: var(--vp-c-text-3);
}
.sw {
  display: inline-block;
  width: 9px;
  height: 9px;
  border-radius: 1px;
}
.sw-first {
  background: var(--mc-tungsten);
}
.sw-rev {
  box-shadow: inset 0 0 0 1.5px var(--mc-tungsten);
}
.c-num {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.95rem;
  text-wrap: balance;
}
.sub {
  font-size: 0.8rem;
  line-height: 1.4;
  color: var(--vp-c-text-3);
}
.m-l {
  display: none;
}
.ct-foot {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px 48px;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid var(--vp-c-divider);
}
.ct-foot .mcl-link {
  grid-column: 1 / -1;
  justify-self: start;
}

@media (max-width: 899px) {
  .ct-head {
    display: none;
  }
  .ct-row {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px 16px;
  }
  .c-piece,
  .c-time {
    grid-column: 1 / -1;
  }
  .c-time {
    padding-top: 0;
  }
  .m-l {
    display: block;
    font-size: 0.75rem;
    color: var(--vp-c-text-3);
  }
  .ct-foot {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
