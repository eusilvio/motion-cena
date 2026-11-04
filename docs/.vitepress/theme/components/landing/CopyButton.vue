<script setup lang="ts">
import { onBeforeUnmount, ref } from "vue";

const props = defineProps<{ text: string; label: string; done: string; context?: string; variant?: "primary" | "quiet" }>();
const copied = ref(false);
let timer: ReturnType<typeof setTimeout> | undefined;

async function copy() {
  try {
    await navigator.clipboard.writeText(props.text);
  } catch {
    // http or an old browser: fall back to a hidden textarea
    const ta = document.createElement("textarea");
    ta.value = props.text;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;top:0;left:0;opacity:0";
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand("copy");
    } finally {
      ta.remove();
    }
  }
  copied.value = true;
  clearTimeout(timer);
  timer = setTimeout(() => (copied.value = false), 1800);
}
onBeforeUnmount(() => clearTimeout(timer));
</script>

<template>
  <button type="button" class="cb" :class="[`cb-${variant ?? 'quiet'}`, { 'is-done': copied }]" @click="copy">
    <span class="cb-g" aria-live="polite">
      <span :class="{ off: copied }">{{ label }}</span>
      <span :class="{ off: !copied }">{{ done }}</span>
    </span>
    <span v-if="context" class="cb-sr">{{ context }}</span>
  </button>
</template>

<style scoped>
.cb {
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  min-height: 40px;
  font: 600 0.9rem/1 var(--mc-font-body);
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s, box-shadow 0.15s;
}
.cb-g {
  display: grid;
}
.cb-g > span {
  grid-area: 1 / 1;
  text-align: center;
}
.cb-g > .off {
  visibility: hidden;
}
.cb-primary {
  background: var(--mc-tungsten);
  color: var(--mc-graphite);
}
.cb-primary:hover {
  background: #f5c463;
}
.cb-quiet {
  min-height: 32px;
  padding: 0 12px;
  border-radius: 4px;
  font-size: 0.82rem;
  color: var(--vp-c-text-2);
  box-shadow: inset 0 0 0 1px var(--vp-c-divider);
}
.cb-quiet:hover {
  color: var(--vp-c-text-1);
  box-shadow: inset 0 0 0 1px var(--vp-c-text-2);
}
.cb-quiet.is-done {
  color: var(--vp-c-text-1);
}
.cb:focus-visible {
  outline: 2px solid var(--vp-c-brand-1);
  outline-offset: 2px;
}
.cb-sr {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
</style>
