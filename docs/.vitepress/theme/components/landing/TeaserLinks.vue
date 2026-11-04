<script setup lang="ts">
import { ref } from "vue";
import { withBase } from "vitepress";
import type { LandingCopy } from "./i18n";
// Vite copies the demo next to the build; it only downloads when the visitor presses play
import demoUrl from "../../../../../creatives/demos/dicionario-demo-2.mp4?url";
import posterUrl from "./assets/demo-poster.jpg";

const props = defineProps<{ t: LandingCopy["teaser"]; links: LandingCopy["links"]; uid: string }>();
const video = ref<HTMLVideoElement>();
const started = ref(false);

/* the vertical preset (assets/platforms.json): 1080×1920, safe 288 / 672 / 65 / 192 px */
const Z = { w: 1080, h: 1920, top: 288, bottom: 672, left: 65, right: 192 };
const zp = (v: number, of: number) => `${((v / of) * 100).toFixed(3)}%`;

function start() {
  const v = video.value;
  if (!v) return;
  started.value = true;
  v.controls = true;
  void v.play().catch(() => {
    /* autoplay policy: controls stay visible, the visitor can press play */
  });
  v.focus();
}
void props;
</script>

<template>
  <section class="mcl-sec tz">
    <!-- effects dictionary -->
    <article class="tz-item tz-fx" :aria-labelledby="`${uid}-fx`">
      <div class="vid">
        <video
          ref="video"
          :src="demoUrl"
          :poster="posterUrl"
          preload="none"
          muted
          playsinline
          width="1080"
          height="1920"
          :aria-label="t.videoNote"
        />
        <button v-if="!started" type="button" class="vid-play" @click="start">
          <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4.5 2.8v10.4L13 8z" /></svg>
          <span>{{ t.videoPlay }}</span>
        </button>
      </div>
      <div class="tz-text">
        <h2 :id="`${uid}-fx`" class="mcl-h3">{{ t.effectsTitle }}</h2>
        <p class="mcl-body">{{ t.effectsBody }}</p>
        <p class="vid-note">{{ t.videoNote }}</p>
        <a class="mcl-link" :href="withBase(links.effects)">{{ t.effectsLink }}</a>
      </div>
    </article>

    <!-- safe zone -->
    <article class="tz-item tz-zone" :aria-labelledby="`${uid}-zone`">
      <div class="zone" aria-hidden="true">
        <i class="z z-top" :style="{ height: zp(Z.top, Z.h) }" />
        <i class="z z-bottom" :style="{ height: zp(Z.bottom, Z.h) }" />
        <i class="z z-left" :style="{ top: zp(Z.top, Z.h), bottom: zp(Z.bottom, Z.h), width: zp(Z.left, Z.w) }" />
        <i class="z z-right" :style="{ top: zp(Z.top, Z.h), bottom: zp(Z.bottom, Z.h), width: zp(Z.right, Z.w) }" />
        <i
          class="free"
          :style="{ top: zp(Z.top, Z.h), bottom: zp(Z.bottom, Z.h), left: zp(Z.left, Z.w), right: zp(Z.right, Z.w) }"
        />
        <span class="zl zl-top">{{ t.zoneEdges.top }} {{ Z.top }}</span>
        <span class="zl zl-bottom">{{ t.zoneEdges.bottom }} {{ Z.bottom }}</span>
        <span class="zl zl-right">{{ Z.right }}</span>
        <span class="card"><b>{{ t.zoneCard }}</b><em>{{ t.zoneError }}</em></span>
      </div>
      <div class="tz-text">
        <h2 :id="`${uid}-zone`" class="mcl-h3">{{ t.zoneTitle }}</h2>
        <p class="mcl-body">{{ t.zoneBody }}</p>
        <a class="mcl-link" :href="withBase(links.platforms)">{{ t.zoneLink }}</a>
      </div>
    </article>
  </section>
</template>

<style scoped>
.tz {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  padding-top: 0;
}
.tz-item {
  display: grid;
  grid-template-columns: clamp(150px, 15vw, 196px) minmax(0, 1fr);
  gap: 28px;
  align-items: start;
  padding: 36px 0 8px;
}
.tz-fx {
  padding-right: clamp(24px, 4vw, 56px);
  border-right: 1px solid var(--vp-c-divider);
}
.tz-zone {
  padding-left: clamp(24px, 4vw, 56px);
}
.tz-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14px;
  padding-top: 4px;
}
.tz-text .mcl-link {
  margin-top: 6px;
}

/* demo video */
.vid {
  position: relative;
  aspect-ratio: 9 / 16;
  border-radius: 10px;
  overflow: hidden;
  background: #f2eee4;
  box-shadow: 0 0 0 1px var(--vp-c-divider);
}
.vid video {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.vid-play {
  position: absolute;
  left: 10px;
  bottom: 10px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 36px;
  padding: 0 14px 0 11px;
  border-radius: 4px;
  background: var(--mc-graphite);
  color: var(--mc-paper);
  font-size: 0.85rem;
  font-weight: 600;
  transition: background-color 0.15s;
}
.vid-play:hover {
  background: #26292e;
}
.vid-play svg {
  width: 13px;
  height: 13px;
  fill: var(--mc-tungsten);
}
.vid-play:focus-visible {
  outline: 2px solid var(--vp-c-brand-1);
  outline-offset: 2px;
}
.vid-note {
  font: 0.8rem/1.4 var(--mc-font-body);
  color: var(--vp-c-text-3);
}

/* safe-zone diagram, in the proportions of the vertical preset */
.zone {
  position: relative;
  aspect-ratio: 9 / 16;
  border-radius: 10px;
  overflow: hidden;
  background: #121417;
  box-shadow: 0 0 0 1px var(--vp-c-divider);
  container-type: inline-size;
}
.z {
  position: absolute;
  display: block;
  background: rgba(229, 72, 77, 0.2);
}
.z-top {
  top: 0;
  left: 0;
  right: 0;
}
.z-bottom {
  bottom: 0;
  left: 0;
  right: 0;
}
.z-left {
  left: 0;
}
.z-right {
  right: 0;
}
.free {
  position: absolute;
  display: block;
  box-shadow: inset 0 0 0 1.5px rgba(229, 72, 77, 0.85);
}
.zl {
  position: absolute;
  font: 500 6.2cqw/1 var(--mc-font-mono);
  color: #f0a6a8;
  white-space: nowrap;
}
.zl-top {
  left: 7cqw;
  top: 6.4%;
}
.zl-bottom {
  left: 7cqw;
  bottom: 6%;
}
.zl-right {
  right: 2.2cqw;
  top: 56%;
  writing-mode: vertical-rl;
}
.card {
  position: absolute;
  left: 50%;
  top: 34%;
  display: flex;
  align-items: center;
  gap: 4cqw;
  padding: 4cqw 6cqw;
  border-radius: 2.5cqw;
  background: var(--mc-paper);
  color: var(--mc-graphite);
  transform: translate(-50%, 0);
  transition: top 0.6s var(--mc-ease-out);
}
.card b {
  font: 400 12cqw/1 var(--mc-font-display);
  white-space: nowrap;
}
.card em {
  position: absolute;
  left: 50%;
  top: calc(100% + 3cqw);
  transform: translateX(-50%);
  padding: 1.6cqw 3cqw;
  border-radius: 1.5cqw;
  background: var(--mc-zone);
  color: #fff;
  font: 600 5.6cqw/1 var(--mc-font-mono);
  font-style: normal;
  opacity: 0;
  transition: opacity 0.2s 0.35s;
}
/* hover or focus the panel: the card drifts under the buttons and fails */
.tz-zone:hover .card,
.tz-zone:focus-within .card {
  top: 70%;
}
.tz-zone:hover .card em,
.tz-zone:focus-within .card em {
  opacity: 1;
}

@media (max-width: 959px) {
  .tz {
    grid-template-columns: minmax(0, 1fr);
  }
  .tz-fx {
    padding-right: 0;
    border-right: 0;
    border-bottom: 1px solid var(--vp-c-divider);
    padding-bottom: 36px;
  }
  .tz-zone {
    padding-left: 0;
  }
}
@media (max-width: 479px) {
  .tz-item {
    grid-template-columns: 124px minmax(0, 1fr);
    gap: 18px;
  }
  .tz-text {
    gap: 10px;
  }
  .vid-play {
    left: 6px;
    right: 6px;
    bottom: 6px;
    justify-content: center;
    padding: 0 8px;
    font-size: 0.78rem;
    white-space: nowrap;
  }
}
</style>
