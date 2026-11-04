/**
 * Effect search: a port of search() in .agents/skills/motion-cena/scripts/motion_lookup.py, so the
 * site ranks a term the same way the agent's lookup does. Keep the two in sync.
 *
 * Rank: exact id/term > exact pt-BR name > exact alias > all words inside one name > shared word
 * stems > fuzzy spelling (difflib ratio >= 0.75). Ties keep catalog order (curated first in a family).
 */
import type { EffectIndexEntry } from "./taxonomy";

/** Lowercase, accents stripped, anything not a-z0-9 becomes a single space (norm() in Python). */
export function norm(s: string): string {
  return s
    .toLowerCase()
    .normalize("NFKD")
    .replace(/\p{M}/gu, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

/** Same word, or same 5-letter stem for longer words (revelando ~ revelacao). */
function wordHit(w: string, tokens: string[]): boolean {
  return tokens.some((tok) => w === tok || (w.length >= 5 && tok.length >= 5 && w.slice(0, 5) === tok.slice(0, 5)));
}

/**
 * difflib.SequenceMatcher(None, a, b).ratio(): Ratcliff/Obershelp, 2*M/T, where M counts the
 * characters of the longest common block plus, recursively, the blocks left and right of it.
 * (No junk heuristic: difflib only turns it on for strings of 200+ characters.)
 */
export function ratio(a: string, b: string): number {
  const total = a.length + b.length;
  if (!total) return 1;
  return (2 * matched(a, 0, a.length, b, 0, b.length)) / total;
}

function matched(a: string, alo: number, ahi: number, b: string, blo: number, bhi: number): number {
  if (alo >= ahi || blo >= bhi) return 0;
  // longest common substring, earliest in a, then earliest in b (find_longest_match tie rule)
  let besti = alo,
    bestj = blo,
    bestsize = 0;
  let prev = new Map<number, number>();
  for (let i = alo; i < ahi; i++) {
    const next = new Map<number, number>();
    for (let j = blo; j < bhi; j++) {
      if (a[i] !== b[j]) continue;
      const k = (prev.get(j - 1) ?? 0) + 1;
      next.set(j, k);
      if (k > bestsize) {
        besti = i - k + 1;
        bestj = j - k + 1;
        bestsize = k;
      }
    }
    prev = next;
  }
  if (!bestsize) return 0;
  return (
    bestsize +
    matched(a, alo, besti, b, blo, bestj) +
    matched(a, besti + bestsize, ahi, b, bestj + bestsize, bhi)
  );
}

export interface Searchable {
  e: EffectIndexEntry;
  idN: string;
  nomeN: string;
  ptN: string;
  names: string[];
  tokens: string[][];
}

export function prepare(effects: EffectIndexEntry[]): Searchable[] {
  return effects.map((e) => {
    const names = [e.id, e.nome, e.nome_pt, ...e.aliases].map(norm);
    return { e, idN: names[0], nomeN: names[1], ptN: names[2], names, tokens: names.map((n) => n.split(" ")) };
  });
}

export function score(s: Searchable, q: string, words: string[]): number {
  if (q === s.idN || q === s.nomeN) return 3;
  if (q === s.ptN) return 2.8;
  if (s.names.includes(q)) return 2.5;
  if (s.names.some((n) => words.every((w) => n.includes(w)))) return 2;
  let stems = 0;
  for (const toks of s.tokens) {
    const hit = words.filter((w) => wordHit(w, toks)).length / words.length;
    if (hit > stems) stems = hit;
  }
  if (stems >= 0.5) return 1 + stems * 0.9;
  let best = 0;
  for (const n of s.names) {
    // upper bound of the ratio is 2*min/total: skip names that cannot reach 0.75
    if ((2 * Math.min(n.length, q.length)) / (n.length + q.length) < 0.75) continue;
    const r = ratio(q, n);
    if (r > best) best = r;
  }
  return best >= 0.75 ? best : 0;
}

/** Ranked matches for a query (all of them; the UI shows the list). Empty query: []. */
export function search(pool: Searchable[], query: string): EffectIndexEntry[] {
  const q = norm(query);
  if (!q) return [];
  const words = q.split(" ");
  const scored: { sc: number; i: number; e: EffectIndexEntry }[] = [];
  pool.forEach((s, i) => {
    const sc = score(s, q, words);
    if (sc) scored.push({ sc, i, e: s.e });
  });
  scored.sort((p, r) => r.sc - p.sc || p.i - r.i);
  return scored.map((x) => x.e);
}
