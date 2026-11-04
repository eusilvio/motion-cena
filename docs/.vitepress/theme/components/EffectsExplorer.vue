<script setup lang="ts">
/**
 * Registered globally by the theme, so it stays tiny: the explorer itself (slim index of the
 * dictionary, search, grid, detail) is an async chunk that only the effects pages load. SSR awaits
 * it, so the pre-rendered page has the full list.
 */
import { defineAsyncComponent } from "vue";

const props = defineProps<{ locale?: "pt" | "en" }>();
const ExplorerApp = defineAsyncComponent(() => import("./explorer/ExplorerApp.vue"));
</script>

<template>
  <ExplorerApp :locale="props.locale === 'en' ? 'en' : 'pt'" />
</template>
