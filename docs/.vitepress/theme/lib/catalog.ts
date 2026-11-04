/**
 * Full dictionary entries, loaded per family on demand.
 *
 * import.meta.glob makes Vite emit one lazy chunk per family file of the skill
 * (.agents/skills/motion-cena/references/motion-dictionary/<familia>.json), read straight from the
 * skill folder at build time: the JSON stays the single source and nothing is copied into docs/.
 * The page only fetches a family when one of its effects is previewed or opened.
 */
import type { EffectFull } from "./taxonomy";

const files = import.meta.glob<EffectFull[]>(
  [
    "../../../../.agents/skills/motion-cena/references/motion-dictionary/*.json",
    "!../../../../.agents/skills/motion-cena/references/motion-dictionary/schema.json",
  ],
  { import: "default" },
);

const byFamily = new Map<string, () => Promise<EffectFull[]>>();
for (const [path, load] of Object.entries(files)) {
  const name = path.split("/").pop()!.replace(/\.json$/, "");
  byFamily.set(name, load);
}

const cache = new Map<string, Promise<Map<string, EffectFull>>>();
const ready = new Map<string, Map<string, EffectFull>>();

/** Loads one family file (cached). */
export function loadFamily(familia: string): Promise<Map<string, EffectFull>> {
  let p = cache.get(familia);
  if (!p) {
    const load = byFamily.get(familia);
    if (!load) return Promise.reject(new Error(`família desconhecida: ${familia}`));
    p = load().then((list) => {
      const m = new Map(list.map((e) => [e.id, e]));
      ready.set(familia, m);
      return m;
    });
    p.catch(() => cache.delete(familia)); // allow a retry after a failed fetch
    cache.set(familia, p);
  }
  return p;
}

/** Full entry if its family is already loaded (no fetch). */
export function peekEffect(familia: string, id: string): EffectFull | undefined {
  return ready.get(familia)?.get(id);
}

export async function loadEffect(familia: string, id: string): Promise<EffectFull | undefined> {
  return (await loadFamily(familia)).get(id);
}
