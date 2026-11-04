import { defineAsyncComponent } from "vue";
import DefaultTheme from "vitepress/theme";
import type { Theme } from "vitepress";
import "./custom.css";

// Each interactive component lives on one or two pages: load it on demand so the theme
// chunk that every page downloads stays small. SSR still pre-renders them.
const HomeLanding = defineAsyncComponent(() => import("./components/HomeLanding.vue"));
const EffectsExplorer = defineAsyncComponent(() => import("./components/EffectsExplorer.vue"));
const SafeZonePlayground = defineAsyncComponent(() => import("./components/SafeZonePlayground.vue"));

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component("HomeLanding", HomeLanding);
    app.component("EffectsExplorer", EffectsExplorer);
    app.component("SafeZonePlayground", SafeZonePlayground);
  },
} satisfies Theme;
