<script setup lang="ts">
/**
 * Generic, unbranded app chrome drawn in canvas pixels, so the reader sees what
 * the zone protects against: side action buttons, name and caption lines at the
 * bottom, a top bar. Shapes only: no logos, glyphs or names of any network.
 */
import { computed } from "vue";
import type { Safe } from "../../../data/platforms.data";

const props = defineProps<{ id: string; width: number; height: number; safe: Safe }>();

type Shape =
  | { t: "rect"; x: number; y: number; w: number; h: number; r?: number; o?: number; stroke?: boolean }
  | { t: "circle"; cx: number; cy: number; r: number; o?: number; stroke?: boolean }
  | { t: "path"; d: string; o?: number; stroke?: boolean };

const family = computed(() => {
  const { id, width: W, height: H } = props;
  if (id === "ig-stories") return "stories";
  if (W > H) return "player";
  if (H / W > 1.5) return "reels";
  return "feed";
});

const shapes = computed<Shape[]>(() => {
  const { width: W, height: H, safe: S } = props;
  const out: Shape[] = [];
  const f = family.value;

  if (f === "reels") {
    const k = W / 1080;
    // right action column: avatar-sized circles with a short count line under each
    const wide = S.right >= 100;
    const colW = Math.max(S.right, 120 * k);
    const cx = W - colW / 2;
    const n = wide ? 5 : 4;
    const y0 = H * (wide ? 0.5 : 0.62);
    const y1 = H * 0.86;
    const step = (y1 - y0) / (n - 1);
    for (let i = 0; i < n; i++) {
      const cy = y0 + i * step;
      out.push({ t: "circle", cx, cy, r: 30 * k, o: 0.62 });
      out.push({ t: "rect", x: cx - 20 * k, y: cy + 42 * k, w: 40 * k, h: 12 * k, r: 6 * k, o: 0.4 });
    }
    // bottom: avatar, handle, follow pill, two caption lines, audio line
    const x0 = Math.max(S.left, 44 * k);
    const textMax = W - colW - x0 - 24 * k;
    const yA = H - S.bottom + Math.min(S.bottom * 0.3, 200 * k);
    out.push({ t: "circle", cx: x0 + 34 * k, cy: yA, r: 34 * k, o: 0.62 });
    out.push({ t: "rect", x: x0 + 84 * k, y: yA - 13 * k, w: Math.min(230 * k, textMax * 0.45), h: 26 * k, r: 13 * k, o: 0.62 });
    out.push({ t: "rect", x: x0 + 84 * k + Math.min(230 * k, textMax * 0.45) + 20 * k, y: yA - 24 * k, w: 130 * k, h: 48 * k, r: 24 * k, o: 0.5, stroke: true });
    out.push({ t: "rect", x: x0, y: yA + 64 * k, w: textMax * 0.92, h: 22 * k, r: 11 * k, o: 0.5 });
    out.push({ t: "rect", x: x0, y: yA + 104 * k, w: textMax * 0.62, h: 22 * k, r: 11 * k, o: 0.5 });
    out.push({ t: "circle", cx: x0 + 14 * k, cy: yA + 172 * k, r: 14 * k, o: 0.42 });
    out.push({ t: "rect", x: x0 + 40 * k, y: yA + 162 * k, w: textMax * 0.45, h: 20 * k, r: 10 * k, o: 0.42 });
    // in-app navigation bar at the very bottom, where the zone is deep enough for it
    if (S.bottom >= 400 * k) {
      const ny = H - 78 * k;
      for (let i = 0; i < 5; i++) {
        const nx = (W / 5) * (i + 0.5);
        out.push({ t: "rect", x: nx - 24 * k, y: ny - 24 * k, w: 48 * k, h: 48 * k, r: 12 * k, o: 0.45, stroke: true });
      }
    }
    // top bar: two tabs in the middle, one icon on each side
    const ty = Math.max(S.top * 0.42, 60 * k);
    out.push({ t: "rect", x: W / 2 - 190 * k, y: ty - 13 * k, w: 160 * k, h: 26 * k, r: 13 * k, o: 0.42 });
    out.push({ t: "rect", x: W / 2 + 20 * k, y: ty - 13 * k, w: 170 * k, h: 26 * k, r: 13 * k, o: 0.62 });
    out.push({ t: "circle", cx: 70 * k, cy: ty, r: 24 * k, o: 0.5, stroke: true });
    out.push({ t: "circle", cx: W - 70 * k, cy: ty, r: 24 * k, o: 0.5, stroke: true });
  } else if (f === "stories") {
    const k = W / 1080;
    // progress segments, account row, menu and close
    const seg = 3;
    const gap = 10 * k;
    const sw = (W - 48 * k - gap * (seg - 1)) / seg;
    for (let i = 0; i < seg; i++) {
      out.push({ t: "rect", x: 24 * k + i * (sw + gap), y: 28 * k, w: sw, h: 7 * k, r: 3.5 * k, o: i === 0 ? 0.8 : 0.35 });
    }
    out.push({ t: "circle", cx: 82 * k, cy: 118 * k, r: 36 * k, o: 0.62 });
    out.push({ t: "rect", x: 136 * k, y: 105 * k, w: 210 * k, h: 26 * k, r: 13 * k, o: 0.62 });
    out.push({ t: "rect", x: 362 * k, y: 105 * k, w: 70 * k, h: 26 * k, r: 13 * k, o: 0.38 });
    for (let i = 0; i < 3; i++) out.push({ t: "circle", cx: W - 170 * k + i * 22 * k, cy: 118 * k, r: 6 * k, o: 0.7 });
    out.push({ t: "path", d: `M${W - 88 * k} ${96 * k} l${44 * k} ${44 * k} M${W - 44 * k} ${96 * k} l${-44 * k} ${44 * k}`, o: 0.7, stroke: true });
    // reply field and two actions at the bottom
    const by = H - 150 * k;
    out.push({ t: "rect", x: 40 * k, y: by, w: W - 300 * k, h: 96 * k, r: 48 * k, o: 0.55, stroke: true });
    out.push({ t: "rect", x: 84 * k, y: by + 37 * k, w: 220 * k, h: 22 * k, r: 11 * k, o: 0.4 });
    out.push({ t: "circle", cx: W - 200 * k, cy: by + 48 * k, r: 32 * k, o: 0.55, stroke: true });
    out.push({ t: "path", d: `M${W - 120 * k} ${by + 18 * k} L${W - 52 * k} ${by + 48 * k} L${W - 120 * k} ${by + 78 * k} L${W - 106 * k} ${by + 48 * k} Z`, o: 0.55, stroke: true });
  } else if (f === "feed") {
    const k = Math.min(W, H) / 1080;
    // feed video: the app chrome sits around the media; only small badges land on it
    const m = Math.min(S.left, S.bottom, S.right, S.top);
    const r = Math.min(22 * k, m * 0.38);
    out.push({ t: "circle", cx: m * 0.75, cy: H - m * 0.75, r, o: 0.62 });
    out.push({ t: "circle", cx: W - m * 0.75, cy: H - m * 0.75, r, o: 0.62 });
    out.push({ t: "rect", x: W - m * 0.4 - 96 * k, y: m * 0.2, w: 96 * k, h: m * 0.6, r: m * 0.3, o: 0.55 });
  } else {
    // horizontal player: title and channel at the top left, icons top right, scrubber and controls at the bottom
    const k = W / 1920;
    out.push({ t: "circle", cx: 74 * k, cy: 78 * k, r: 36 * k, o: 0.62 });
    out.push({ t: "rect", x: 126 * k, y: 58 * k, w: 210 * k, h: 22 * k, r: 11 * k, o: 0.62 });
    out.push({ t: "rect", x: 126 * k, y: 92 * k, w: 140 * k, h: 18 * k, r: 9 * k, o: 0.4 });
    for (let i = 0; i < 3; i++) out.push({ t: "circle", cx: W - 300 * k + i * 100 * k, cy: 66 * k, r: 24 * k, o: 0.55, stroke: true });
    const py = H - 104 * k;
    out.push({ t: "rect", x: 24 * k, y: py, w: W - 48 * k, h: 6 * k, r: 3 * k, o: 0.35 });
    out.push({ t: "rect", x: 24 * k, y: py, w: (W - 48 * k) * 0.38, h: 6 * k, r: 3 * k, o: 0.8 });
    out.push({ t: "circle", cx: 24 * k + (W - 48 * k) * 0.38, cy: py + 3 * k, r: 11 * k, o: 0.9 });
    const cy = H - 52 * k;
    out.push({ t: "path", d: `M${44 * k} ${cy - 18 * k} L${74 * k} ${cy} L${44 * k} ${cy + 18 * k} Z`, o: 0.75 });
    out.push({ t: "circle", cx: 124 * k, cy, r: 16 * k, o: 0.55, stroke: true });
    out.push({ t: "rect", x: 164 * k, y: cy - 4 * k, w: 90 * k, h: 8 * k, r: 4 * k, o: 0.45 });
    out.push({ t: "rect", x: 284 * k, y: cy - 11 * k, w: 150 * k, h: 22 * k, r: 11 * k, o: 0.45 });
    for (let i = 0; i < 4; i++) out.push({ t: "rect", x: W - 300 * k + i * 70 * k, y: cy - 18 * k, w: 36 * k, h: 36 * k, r: 8 * k, o: 0.5, stroke: true });
  }
  return out;
});

const sw = computed(() => (Math.min(props.width, props.height) / 1080) * 4);
</script>

<template>
  <g class="sz-ui" aria-hidden="true">
    <template v-for="(s, i) in shapes" :key="i">
      <rect
        v-if="s.t === 'rect'"
        :x="s.x"
        :y="s.y"
        :width="s.w"
        :height="s.h"
        :rx="s.r ?? 0"
        :fill="s.stroke ? 'none' : 'currentColor'"
        :stroke="s.stroke ? 'currentColor' : 'none'"
        :stroke-width="sw"
        :opacity="s.o ?? 0.6"
      />
      <circle
        v-else-if="s.t === 'circle'"
        :cx="s.cx"
        :cy="s.cy"
        :r="s.r"
        :fill="s.stroke ? 'none' : 'currentColor'"
        :stroke="s.stroke ? 'currentColor' : 'none'"
        :stroke-width="sw"
        :opacity="s.o ?? 0.6"
      />
      <path
        v-else
        :d="s.d"
        :fill="s.stroke ? 'none' : 'currentColor'"
        :stroke="s.stroke ? 'currentColor' : 'none'"
        :stroke-width="sw"
        stroke-linecap="round"
        stroke-linejoin="round"
        :opacity="s.o ?? 0.6"
      />
    </template>
  </g>
</template>
