<script setup lang="ts">
import { computed } from "vue";
import { data } from "../../../data/platforms.data";
import { TABLE, fmtDuration, fmtRange, presetLabel, type Locale } from "./i18n";

const props = withDefaults(defineProps<{ locale?: Locale; kind?: "video" | "carousel" }>(), {
  locale: "pt",
  kind: "video",
});

const t = computed(() => TABLE[props.locale]);
const sameFps = computed(() => {
  const all = new Set(data.video.map((p) => p.fps));
  return all.size === 1 ? [...all][0] : null;
});
const n = (v: number) => new Intl.NumberFormat(props.locale === "pt" ? "pt-BR" : "en-US").format(v);
</script>

<template>
  <div class="sz-table">
    <table v-if="kind === 'video'">
      <thead>
        <tr>
          <th scope="col">{{ t.preset }}</th>
          <th scope="col">{{ t.platform }}</th>
          <th scope="col">{{ t.canvas }}</th>
          <th v-if="!sameFps" scope="col">fps</th>
          <th scope="col">{{ t.def }}</th>
          <th scope="col">{{ t.ideal }}</th>
          <th scope="col">{{ t.max }}</th>
          <th scope="col">
            {{ t.zone }}<span class="sz-table-sub">{{ t.zoneSub }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in data.video" :key="p.id">
          <td><code>{{ p.id }}</code></td>
          <td>{{ presetLabel(p.id, p.label, locale) }}</td>
          <td class="sz-num">{{ p.width }}×{{ p.height }}</td>
          <td v-if="!sameFps" class="sz-num">{{ p.fps }}</td>
          <td class="sz-num">{{ p.defaultDuration ? fmtDuration(p.defaultDuration, locale) : "" }}</td>
          <td class="sz-num">{{ fmtRange(p.idealDuration, "s", locale) }}</td>
          <td class="sz-num">{{ fmtDuration(p.maxDuration, locale) }}</td>
          <td class="sz-num sz-zone">
            {{ p.safe.top }} / {{ p.safe.bottom }} / {{ p.safe.left }} / {{ p.safe.right }}
          </td>
        </tr>
      </tbody>
    </table>

    <table v-else>
      <thead>
        <tr>
          <th scope="col">{{ t.preset }}</th>
          <th scope="col">{{ t.platform }}</th>
          <th scope="col">{{ t.canvas }}</th>
          <th scope="col">{{ t.slides }}</th>
          <th scope="col">{{ t.ideal }}</th>
          <th scope="col">{{ t.margin }}</th>
          <th scope="col">{{ t.format }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in data.carousel" :key="p.id">
          <td><code>{{ p.id }}</code></td>
          <td>{{ presetLabel(p.id, p.label, locale) }}</td>
          <td class="sz-num">{{ p.width }}×{{ p.height }}</td>
          <td class="sz-num">
            {{ n(p.maxSlides) }}<template v-if="p.adsMaxSlides"> ({{ t.ads(p.adsMaxSlides) }})</template>
          </td>
          <td class="sz-num">{{ fmtRange(p.idealSlides, "slides", locale) }}</td>
          <td class="sz-num sz-zone">
            {{ p.safe.top }} / {{ p.safe.bottom }} / {{ p.safe.left }} / {{ p.safe.right }}
          </td>
          <td class="sz-num">{{ p.format.toUpperCase() }}</td>
        </tr>
      </tbody>
    </table>

    <p class="sz-table-caption">
      <template v-if="kind === 'video' && sameFps">{{ t.fps(sameFps) }} </template>{{ t.caption }}
    </p>
  </div>
</template>

<style scoped>
.sz-table table {
  margin: 16px 0 8px;
}
.sz-table th {
  vertical-align: bottom;
  white-space: nowrap;
}
.sz-table-sub {
  display: block;
  font-weight: 400;
  font-size: 0.78rem;
  color: var(--vp-c-text-2);
}
.sz-num {
  font-family: var(--mc-font-mono);
  font-size: 0.84rem;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.sz-table code {
  white-space: nowrap;
}
.sz-table-caption {
  margin: 0 0 16px;
  font-size: 0.84rem;
  color: var(--vp-c-text-2);
}
</style>
