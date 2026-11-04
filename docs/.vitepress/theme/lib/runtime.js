/* GSAP for the effects explorer, loaded on the client only (call from onMounted).
 * Same version as the demos and the dictionary test (gsap 3.14.2, pinned in docs/package.json).
 *
 * The core loads once; the plugins (free since 3.13) load only when an effect's code uses one,
 * so the first screen of the grid does not pay for MorphSVG and friends. Recipes reach a plugin by
 * name (CustomEase.create...) through each stage's scope (lib/fixtures.js reads rt.plugins), and the
 * plugin must be registered before the timeline is built, so callers await ensurePlugins() first. */
let promise = null;

const LOADERS = {
  DrawSVGPlugin: () => import("gsap/DrawSVGPlugin").then((m) => m.DrawSVGPlugin),
  MorphSVGPlugin: () => import("gsap/MorphSVGPlugin").then((m) => m.MorphSVGPlugin),
  MotionPathPlugin: () => import("gsap/MotionPathPlugin").then((m) => m.MotionPathPlugin),
  CustomEase: () => import("gsap/CustomEase").then((m) => m.CustomEase),
  SplitText: () => import("gsap/SplitText").then((m) => m.SplitText),
};
// what in a snippet means it needs the plugin (comments are stripped first)
const USES = {
  DrawSVGPlugin: /\bdrawSVG\b/,
  MorphSVGPlugin: /\bmorphSVG\b/,
  MotionPathPlugin: /\bmotionPath\b/,
  CustomEase: /\bCustomEase\b/,
  SplitText: /\bSplitText\b/,
};
const pending = new Map();

/** @returns {Promise<{gsap: any, plugins: Record<string, any>}>} */
export function loadRuntime() {
  if (!promise) {
    promise = import("gsap").then((core) => ({ gsap: core.gsap || core.default, plugins: {} }));
    promise.catch(() => { promise = null; });
  }
  return promise;
}

/** Plugins this snippet needs that are not registered yet. */
export function missingPlugins(rt, code) {
  const bare = code.replace(/\/\/[^\n]*/g, "");
  return Object.keys(USES).filter((name) => !rt.plugins[name] && USES[name].test(bare));
}

/** Loads and registers the named plugins (each once). */
export function ensurePlugins(rt, names) {
  return Promise.all(names.map((name) => {
    if (rt.plugins[name]) return rt.plugins[name];
    if (!pending.has(name)) {
      const p = LOADERS[name]().then((plugin) => {
        rt.gsap.registerPlugin(plugin);
        rt.plugins[name] = plugin;
        return plugin;
      });
      p.catch(() => pending.delete(name));
      pending.set(name, p);
    }
    return pending.get(name);
  }));
}
