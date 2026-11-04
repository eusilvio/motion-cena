import type { HeroWord } from "./i18n";

/** small seeded PRNG: same seed, same waveform on the server and in the browser */
function mulberry32(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function syllables(word: string) {
  const groups = word.toLowerCase().match(/[aeiouyáàâãéêíóôõú]+/g);
  return Math.max(1, groups ? groups.length : 1);
}

/**
 * A deterministic pseudo-waveform built only from the word timings: a hump per word,
 * one bump per syllable, a noise floor in the pauses. `sps` = samples per second.
 */
export function envelope(words: HeroWord[], duration: number, sps = 40, seed = 11): number[] {
  const rnd = mulberry32(seed);
  const n = Math.round(duration * sps);
  const out: number[] = [];
  for (let i = 0; i < n; i++) {
    const t = (i + 0.5) / sps;
    const r = rnd();
    const w = words.find((x) => t >= x.s && t < x.e);
    if (!w) {
      out.push(0.03 + 0.03 * r);
      continue;
    }
    const u = (t - w.s) / (w.e - w.s);
    const hump = Math.pow(Math.sin(Math.PI * u), 0.45);
    const syl = 0.5 + 0.5 * Math.abs(Math.sin(Math.PI * syllables(w.w) * u));
    out.push(Math.min(1, 0.12 + hump * syl * (0.6 + 0.4 * r)));
  }
  return out;
}

/** mirrored bars in a viewBox of `0 0 n 100` */
export function barsPath(env: number[], barWidth = 0.58): string {
  let d = "";
  for (let i = 0; i < env.length; i++) {
    const a = +(env[i] * 46).toFixed(1);
    if (a <= 0) continue;
    d += `M${i} ${+(50 - a).toFixed(1)}h${barWidth}v${+(2 * a).toFixed(1)}h-${barWidth}z`;
  }
  return d;
}

/** `count` bar heights (0.18..1) sampled from one word's slice of the envelope */
export function wordBars(env: number[], word: HeroWord, sps: number, count: number): number[] {
  const a = Math.floor(word.s * sps);
  const b = Math.max(a + 1, Math.ceil(word.e * sps));
  const out: number[] = [];
  for (let i = 0; i < count; i++) {
    const k = a + Math.floor(((b - a) * i) / count);
    out.push(Math.max(0.18, Math.min(1, env[k] ?? 0.2)));
  }
  return out;
}
