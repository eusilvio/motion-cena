/**
 * Families, genres and intensities of the effects dictionary, in catalog order.
 * Mirrors schema.json and FAMILY_ORDER in .agents/skills/motion-cena/scripts/motion_lookup.py.
 * Shared by the build-time loader (data/effects.data.ts) and the explorer UI.
 */
export const FAMILY_ORDER = [
  "entradas-suaves",
  "entradas-impacto",
  "saidas",
  "texto",
  "enfase",
  "fisica",
  "loops-ambiente",
  "camera",
  "transicoes",
  "formas-svg",
  "dados-infografico",
  "interface-ui",
  "estilizacao-textura",
  "particulas",
  "3d-perspectiva",
  "mascaras-composicao",
] as const;

export const GENRES = ["historia", "motivacional", "tecnico", "explicativo", "dados", "produto", "opiniao"] as const;
export const INTENSITIES = ["sutil", "media", "forte"] as const;

export type Intensity = (typeof INTENSITIES)[number];

/** One effect in the inline index. The full entry (texts, gsap code) comes from lib/catalog.ts. */
export interface EffectIndexEntry {
  id: string;
  nome: string;
  nome_pt: string;
  aliases: string[];
  familia: string;
  intensidade: Intensity;
  generos: string[];
  /** origem === "dicionario-atual": one of the 44 curated effects, rendered in the demos */
  curado: boolean;
  /** default duration in seconds; null = continuous (loops for the length of the scene) */
  dur: number | null;
  ease: string;
}

/** Full entry, as in the JSON files (fields documented in schema.json). */
export interface EffectFull {
  id: string;
  nome: string;
  nome_pt: string;
  aliases: string[];
  familia: string;
  descricao: string;
  como_funciona: string;
  quando_usar: string;
  evitar: string;
  padrao: { duracao_s: number | null; ease: string; parametros: Record<string, unknown> };
  propriedades: string[];
  intensidade: Intensity;
  generos: string[];
  combina_com: string[];
  gsap: string;
  receita_hyperframes: string | null;
  origem: "dicionario-atual" | "expansao";
}

export interface EffectsData {
  effects: EffectIndexEntry[];
  families: { id: string; count: number; curated: number }[];
  total: number;
  curated: number;
}
