import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineLoader } from "vitepress";

/**
 * Platform presets for the docs, read at build time from the skill's own file.
 * The JSON is never copied into the site: change assets/platforms.json and the
 * table, the playground and the CSS block follow on the next build.
 */
const SOURCE = "../../../.agents/skills/motion-cena/assets/platforms.json";

export interface Safe {
  top: number;
  bottom: number;
  left: number;
  right: number;
}

/** [x, y, w, h] in canvas pixels */
export type Rect = [number, number, number, number];

export interface VideoPreset {
  id: string;
  label: string;
  width: number;
  height: number;
  fps: number;
  maxDuration: number;
  idealDuration: [number, number];
  defaultDuration: number | null;
  safe: Safe;
  note: string | null;
  /** player overlays outside the plain margins (only presets that list them with numbers) */
  corners: { name: string; rect: Rect }[];
}

export interface CarouselPreset {
  id: string;
  label: string;
  width: number;
  height: number;
  maxSlides: number;
  adsMaxSlides: number | null;
  idealSlides: [number, number];
  safe: Safe;
  format: string;
}

export interface PlatformData {
  video: VideoPreset[];
  carousel: CarouselPreset[];
}

declare const data: PlatformData;
export { data };

type Json = Record<string, any>;

const isRect = (v: unknown): v is Rect =>
  Array.isArray(v) && v.length === 4 && v.every((n) => typeof n === "number");

export default defineLoader({
  watch: [SOURCE],
  load(files: string[]): PlatformData {
    const file = files[0] ?? fileURLToPath(new URL(SOURCE, import.meta.url));
    let presets: Record<string, Json>;
    try {
      presets = JSON.parse(readFileSync(file, "utf-8")).presets;
    } catch (err) {
      throw new Error(`platforms.data.ts: could not read ${file}: ${(err as Error).message}`);
    }

    const video: VideoPreset[] = [];
    const carousel: CarouselPreset[] = [];
    for (const [id, p] of Object.entries(presets)) {
      if (p.type === "carousel") {
        carousel.push({
          id,
          label: p.label,
          width: p.width,
          height: p.height,
          maxSlides: p.max_slides,
          adsMaxSlides: p.ads_max_slides ?? null,
          idealSlides: p.ideal_slides,
          safe: p.safe,
          format: p.format,
        });
      } else {
        const corners = Object.entries((p.safe_corners ?? {}) as Json)
          .filter(([, v]) => isRect(v))
          .map(([name, rect]) => ({ name, rect: rect as Rect }));
        video.push({
          id,
          label: p.label,
          width: p.width,
          height: p.height,
          fps: p.fps,
          maxDuration: p.max_duration,
          idealDuration: p.ideal_duration,
          defaultDuration: p.default_duration ?? null,
          safe: p.safe,
          note: p.note ?? null,
          corners,
        });
      }
    }
    return { video, carousel };
  },
});
