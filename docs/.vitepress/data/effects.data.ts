/**
 * Build-time index of the effects dictionary.
 *
 * Source of truth: .agents/skills/motion-cena/references/motion-dictionary/*.json (16 family files,
 * fields in schema.json there). Nothing is copied into docs/: this loader reads the skill folder at
 * build time and inlines only a slim index (names, aliases, filters, default duration and ease), so
 * the explorer can search, filter and list all effects without shipping the GSAP code and the long
 * texts. Full entries are loaded per family, on demand, by theme/lib/catalog.ts (import.meta.glob
 * over the same folder: one lazy chunk per family file).
 *
 * Order follows load() in scripts/motion_lookup.py: family order, curated first inside a family,
 * then file order.
 */
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { defineLoader } from "vitepress";
import { FAMILY_ORDER, type EffectFull, type EffectIndexEntry, type EffectsData } from "../theme/lib/taxonomy";

declare const data: EffectsData;
export { data };

export default defineLoader({
  // relative to this file: docs/.vitepress/data -> repo root
  watch: ["../../../.agents/skills/motion-cena/references/motion-dictionary/*.json"],
  load(files: string[]): EffectsData {
    const raw: EffectFull[] = [];
    for (const file of [...files].sort()) {
      if (basename(file) === "schema.json") continue;
      raw.push(...(JSON.parse(readFileSync(file, "utf-8")) as EffectFull[]));
    }
    const order = new Map<string, number>(FAMILY_ORDER.map((f, i) => [f, i]));
    const curated = (e: EffectFull) => e.origem === "dicionario-atual";
    // Array.prototype.sort is stable: ties keep file order, as in motion_lookup.py
    raw.sort(
      (p, q) =>
        (order.get(p.familia) ?? 99) - (order.get(q.familia) ?? 99) || Number(!curated(p)) - Number(!curated(q)),
    );
    const effects: EffectIndexEntry[] = raw.map((e) => ({
      id: e.id,
      nome: e.nome,
      nome_pt: e.nome_pt,
      aliases: e.aliases,
      familia: e.familia,
      intensidade: e.intensidade,
      generos: e.generos,
      curado: curated(e),
      dur: e.padrao.duracao_s,
      ease: e.padrao.ease,
    }));
    const families = [...new Set(effects.map((e) => e.familia))]
      .sort((p, q) => (order.get(p) ?? 99) - (order.get(q) ?? 99))
      .map((id) => {
        const list = effects.filter((e) => e.familia === id);
        return { id, count: list.length, curated: list.filter((e) => e.curado).length };
      });
    return { effects, families, total: effects.length, curated: effects.filter((e) => e.curado).length };
  },
});
