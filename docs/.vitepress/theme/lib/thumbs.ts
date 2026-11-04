/**
 * Thumbnails of the effects grid. Nothing is built up front: a tile gets a stage when it comes near
 * the viewport (IntersectionObserver), parked on its poster frame with the timeline paused, and
 * loses it (DOM removed, timeline killed) when it scrolls away. Builds run in small batches per
 * animation frame. Hover or keyboard focus plays a tile in a loop; at most MAX_PLAYING play at once,
 * and none play with prefers-reduced-motion.
 */
import { buildStage, posterTime } from "./fixtures.js";
import { ensurePlugins, loadRuntime, missingPlugins } from "./runtime.js";
import { loadFamily, peekEffect } from "./catalog";
import type { EffectIndexEntry } from "./taxonomy";

type Runtime = Awaited<ReturnType<typeof loadRuntime>>;
type Stage = ReturnType<typeof buildStage>;

interface Slot {
  el: HTMLElement;
  host: HTMLElement;
  entry: EffectIndexEntry;
  visible: boolean;
  queued: boolean;
  stage: Stage | null;
  poster: number;
  wantPlay: boolean;
  hold: { kill(): void } | null;
}

const MAX_PLAYING = 3;
const FRAME_BUDGET_MS = 9;
const HOLD_S = 0.5; // pause on the last frame before a hover preview loops

export class ThumbDeck {
  private slots = new Map<HTMLElement, Slot>();
  private queue: Slot[] = [];
  private playing: Slot[] = [];
  private io: IntersectionObserver;
  private rt: Runtime | null = null;
  private raf = 0;
  private dead = false;

  constructor(private reducedMotion: () => boolean) {
    this.io = new IntersectionObserver((entries) => this.onIntersect(entries), { rootMargin: "700px 0px" });
    loadRuntime().then(
      (rt) => {
        this.rt = rt;
        this.pump();
      },
      (err) => console.error("[efeitos] GSAP não carregou:", err),
    );
  }

  bind(el: HTMLElement, entry: EffectIndexEntry) {
    const prev = this.slots.get(el);
    if (prev && prev.entry.id === entry.id) return;
    if (prev) this.unbind(el);
    const host = el.querySelector<HTMLElement>("[data-thumb-host]");
    if (!host) return;
    const slot: Slot = { el, host, entry, visible: false, queued: false, stage: null, poster: 0, wantPlay: false, hold: null };
    this.slots.set(el, slot);
    this.io.observe(el);
  }

  unbind(el: HTMLElement) {
    const slot = this.slots.get(el);
    if (!slot) return;
    this.io.unobserve(el);
    this.teardown(slot);
    this.slots.delete(el);
  }

  play(el: HTMLElement) {
    const slot = this.slots.get(el);
    if (!slot || this.reducedMotion()) return;
    slot.wantPlay = true;
    if (!slot.stage) {
      slot.visible = true;
      this.enqueue(slot, true);
      return;
    }
    this.start(slot);
  }

  stop(el: HTMLElement) {
    const slot = this.slots.get(el);
    if (!slot) return;
    slot.wantPlay = false;
    this.halt(slot);
  }

  destroy() {
    this.dead = true;
    cancelAnimationFrame(this.raf);
    this.io.disconnect();
    for (const slot of this.slots.values()) this.teardown(slot);
    this.slots.clear();
    this.queue = [];
  }

  // ---------------------------------------------------------------- internals

  private onIntersect(entries: IntersectionObserverEntry[]) {
    for (const e of entries) {
      const slot = this.slots.get(e.target as HTMLElement);
      if (!slot) continue;
      slot.visible = e.isIntersecting;
      if (slot.visible) this.enqueue(slot);
      else this.teardown(slot);
    }
  }

  private enqueue(slot: Slot, urgent = false) {
    if (slot.stage || slot.el.dataset.thumb === "error") return;
    if (!slot.queued) {
      slot.queued = true;
      if (urgent) this.queue.unshift(slot);
      else this.queue.push(slot);
    } else if (urgent) {
      this.queue.splice(this.queue.indexOf(slot), 1);
      this.queue.unshift(slot);
    }
    this.pump();
  }

  private pump() {
    if (this.raf || this.dead || !this.rt) return;
    this.raf = requestAnimationFrame(() => {
      this.raf = 0;
      const t0 = performance.now();
      while (this.queue.length && performance.now() - t0 < FRAME_BUDGET_MS) {
        const slot = this.queue.shift()!;
        slot.queued = false;
        if (!slot.visible || slot.stage || !this.slots.has(slot.el)) continue;
        const full = peekEffect(slot.entry.familia, slot.entry.id);
        if (!full) {
          // family chunk not here yet: fetch it, then come back to this tile
          loadFamily(slot.entry.familia).then(
            () => this.enqueue(slot, slot.wantPlay),
            (err) => console.error(`[efeitos] família ${slot.entry.familia} não carregou:`, err),
          );
          continue;
        }
        const need = missingPlugins(this.rt, full.gsap);
        if (need.length) {
          // a GSAP plugin this recipe uses: register it first, then build
          ensurePlugins(this.rt, need).then(
            () => this.enqueue(slot, slot.wantPlay),
            (err) => console.error(`[efeitos] plugin ${need.join(", ")} não carregou:`, err),
          );
          continue;
        }
        this.build(slot, full);
      }
      if (this.queue.length) this.pump();
    });
  }

  private build(slot: Slot, full: Parameters<typeof buildStage>[1]) {
    try {
      const stage = buildStage(slot.host, full, this.rt!);
      slot.poster = posterTime(full.familia, stage.duration);
      stage.tl.totalTime(slot.poster, false);
      slot.stage = stage;
      slot.el.dataset.thumb = "ready";
      if (slot.wantPlay && !this.reducedMotion()) this.start(slot);
    } catch (err) {
      slot.el.dataset.thumb = "error";
      console.error(`[efeitos] prévia de ${slot.entry.id} não montou:`, err);
    }
  }

  private start(slot: Slot) {
    const stage = slot.stage!;
    const gsap = this.rt!.gsap;
    if (!this.playing.includes(slot)) {
      this.playing.push(slot);
      while (this.playing.length > MAX_PLAYING) {
        const old = this.playing[0];
        old.wantPlay = false;
        this.halt(old);
      }
    }
    slot.hold?.kill();
    slot.hold = null;
    const loop = () => {
      slot.hold = gsap.delayedCall(HOLD_S, () => {
        slot.hold = null;
        if (!slot.wantPlay || !slot.stage) return;
        stage.tl.totalTime(0, false);
        stage.tl.play();
      });
    };
    stage.tl.eventCallback("onComplete", loop);
    stage.tl.totalTime(0, false);
    stage.tl.play();
    slot.el.dataset.playing = "";
  }

  private halt(slot: Slot) {
    const i = this.playing.indexOf(slot);
    if (i >= 0) this.playing.splice(i, 1);
    slot.hold?.kill();
    slot.hold = null;
    delete slot.el.dataset.playing;
    if (!slot.stage) return;
    slot.stage.tl.eventCallback("onComplete", null);
    slot.stage.tl.pause();
    slot.stage.tl.totalTime(slot.poster, false);
  }

  private teardown(slot: Slot) {
    this.halt(slot);
    if (slot.stage) {
      slot.stage.destroy();
      slot.stage = null;
    }
    if (slot.el.dataset.thumb === "ready") delete slot.el.dataset.thumb;
  }
}
