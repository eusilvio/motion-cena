# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.45"]
# ///
"""Check that text, numbers, logos and images stay out of the platform UI zones.

Opens the HyperFrames composition in Chrome, seeks every GSAP timeline in
window.__timelines to evenly spaced times, measures the real on-screen box of
every visible text run and image, and reports what enters the danger zone
(the margins in assets/platforms.json `safe`).

Usage:
  uv run safe_zone_check.py projects/<slug>/video [--preset vertical] [--step 0.25] [--json out.json]

- Preset `vertical` = union of Reels, TikTok and Shorts zones: one render serves all three.
- A breach that lasts < --min-hold seconds (entrance/exit motion) is a warning; longer is an error.
- Boxes with a background or border (cards, phone frames, labels, chips) count as content.
  Decorative bleed (background shapes, full-bleed photos) is skipped automatically when the element
  covers > 45% of the canvas or is blurred > 20px; mark anything else intentional with `data-safe-ignore`.
Exit code 1 when an error is found.
"""
import argparse
import functools
import http.server
import json
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

PRESETS = Path(__file__).resolve().parent.parent / "assets" / "platforms.json"

MEASURE_JS = r"""
({t, safe, W, H, tol}) => {
  for (const tl of Object.values(window.__timelines || {})) { try { tl.seek(t, false); } catch (e) {} }
  const root = document.querySelector('[data-composition-id]') || document.body;
  const o = root.getBoundingClientRect();
  const sx = o.width ? W / o.width : 1, sy = o.height ? H / o.height : 1;
  const inClip = (el) => {
    for (let n = el; n && n !== document; n = n.parentElement) {
      if (n === root) break;
      const s = n.getAttribute && n.getAttribute('data-start');
      if (s !== null && s !== undefined && s !== '' && !isNaN(+s)) {
        const d = n.getAttribute('data-duration');
        if (t < +s || (d && !isNaN(+d) && t >= +s + +d)) return false;
      }
    }
    return true;
  };
  const shown = (el) => {
    let a = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      a *= parseFloat(cs.opacity);
      if (n.hasAttribute('data-safe-ignore')) return 0;
    }
    return a;
  };
  const name = (el) => {
    if (el.id) return '#' + el.id;
    let p = el, path = [];
    while (p && p !== root && path.length < 3) {
      path.unshift(p.id ? '#' + p.id : p.tagName.toLowerCase() + (p.classList[0] ? '.' + p.classList[0] : ''));
      if (p.id) break;
      p = p.parentElement;
    }
    return path.join(' > ');
  };
  const out = [];
  const check = (el, r, label, kind) => {
    const x0 = (r.left - o.left) * sx, y0 = (r.top - o.top) * sy;
    const x1 = (r.right - o.left) * sx, y1 = (r.bottom - o.top) * sy;
    if (x1 <= 0 || y1 <= 0 || x0 >= W || y0 >= H || x1 - x0 < 2 || y1 - y0 < 2) return;
    if ((x1 - x0) * (y1 - y0) > 0.45 * W * H) return;
    if (kind === 'caixa' && x1 - x0 >= 0.98 * W) return;  // full-width band = background
    const cx0 = Math.max(0, x0), cy0 = Math.max(0, y0), cx1 = Math.min(W, x1), cy1 = Math.min(H, y1);
    const over = {
      top: safe.top - cy0, bottom: cy1 - (H - safe.bottom),
      left: safe.left - cx0, right: cx1 - (W - safe.right),
    };
    const hit = Object.entries(over).filter(([, v]) => v > tol).map(([k, v]) => [k, Math.round(v)]);
    if (hit.length) out.push({el: name(el), kind, text: label, box: [cx0, cy0, cx1, cy1].map(Math.round), hit});
  };
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const seen = new Map();
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const txt = n.textContent.trim();
    if (!txt) continue;
    const el = n.parentElement;
    if (!el || el.closest('script,style,svg title') || !inClip(el) || shown(el) < 0.15) continue;
    const range = document.createRange(); range.selectNodeContents(n);
    const rects = [...range.getClientRects()];
    if (!rects.length) continue;
    const r = rects.reduce((a, b) => ({left: Math.min(a.left, b.left), top: Math.min(a.top, b.top),
      right: Math.max(a.right, b.right), bottom: Math.max(a.bottom, b.bottom)}));
    check(el, r, txt.slice(0, 40), 'texto');
  }
  for (const el of root.querySelectorAll('div, span, b, i, li, section')) {
    const cs = getComputedStyle(el);
    const bg = cs.backgroundColor, bgi = cs.backgroundImage;
    const filled = (bg && !/rgba\(.*,\s*0\)$/.test(bg) && bg !== 'transparent') || (bgi && bgi !== 'none');
    const bordered = parseFloat(cs.borderTopWidth) > 0 && !/rgba\(.*,\s*0\)$/.test(cs.borderTopColor);
    if (!(filled || bordered) || !inClip(el) || shown(el) < 0.15) continue;
    if (parseFloat(cs.filter.replace(/.*blur\((\d+).*/, '$1')) > 20) continue;  // glow blobs
    check(el, el.getBoundingClientRect(), '', 'caixa');
  }
  for (const el of root.querySelectorAll('img, video, canvas, svg')) {
    if (el.tagName.toLowerCase() === 'svg' && el.parentElement.closest('svg')) continue;
    if (!inClip(el) || shown(el) < 0.15) continue;
    check(el, el.getBoundingClientRect(), el.getAttribute('alt') || el.getAttribute('src') || '', el.tagName.toLowerCase());
  }
  return out;
}
"""


def serve(directory: Path) -> tuple[http.server.ThreadingHTTPServer, int]:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    handler = functools.partial(Quiet, directory=str(directory))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    srv.handle_error = lambda *a: None  # browser closing sockets mid-transfer is not our problem
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def main() -> int:
    for stream in (sys.stdout, sys.stderr):  # Windows consoles and pipes default to cp1252
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("composition", type=Path, help="folder with index.html")
    ap.add_argument("--preset", default="vertical")
    ap.add_argument("--html", default="index.html")
    ap.add_argument("--step", type=float, default=0.25, help="seconds between samples")
    ap.add_argument("--min-hold", type=float, default=0.5, help="breach shorter than this = warning")
    ap.add_argument("--tol", type=float, default=4, help="px allowed inside the zone")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    preset = json.loads(PRESETS.read_text(encoding="utf-8"))["presets"].get(a.preset)
    if not preset:
        print(f"unknown preset {a.preset}", file=sys.stderr)
        return 2
    W, H, safe = preset["width"], preset["height"], preset["safe"]
    srv, port = serve(a.composition.resolve())
    hits: dict[tuple, list] = {}
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": W, "height": H})
        page.add_init_script("window.__timelines = window.__timelines || {};")
        page.goto(f"http://127.0.0.1:{port}/{a.html}", wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(800)
        dur = page.evaluate("""() => {
          const r = document.querySelector('[data-composition-id]');
          const d = r && parseFloat(r.getAttribute('data-duration'));
          if (d) return d;
          return Math.max(0, ...Object.values(window.__timelines || {}).map(t => t.duration()));
        }""")
        if not page.evaluate("Object.keys(window.__timelines || {}).length"):
            print("aviso: nenhuma timeline em window.__timelines; medindo só o quadro inicial", file=sys.stderr)
        n = int(dur / a.step) + 1
        for i in range(n):
            t = round(min(i * a.step, max(dur - 0.01, 0)), 3)
            for h in page.evaluate(MEASURE_JS, {"t": t, "safe": safe, "W": W, "H": H, "tol": a.tol}):
                key = (h["el"], h["text"], tuple(k for k, _ in h["hit"]))
                hits.setdefault(key, []).append((t, h))
        browser.close()
    srv.shutdown()

    report, errors, warns = [], 0, 0
    for (el, text, edges), occ in hits.items():
        spans, start, prev = [], occ[0][0], occ[0][0]
        for t, _ in occ[1:]:
            if t - prev > a.step * 1.5:
                spans.append((start, prev)); start = t
            prev = t
        spans.append((start, prev))
        longest = max(e - s + a.step for s, e in spans)
        worst = {}
        for _, h in occ:
            for k, v in h["hit"]:
                worst[k] = max(worst.get(k, 0), v)
        level = "ERRO" if longest >= a.min_hold else "aviso"
        errors += level == "ERRO"; warns += level == "aviso"
        report.append({"level": level, "el": el, "text": text, "kind": occ[0][1]["kind"], "edges": worst,
                       "spans": [[s, e] for s, e in spans], "box": occ[0][1]["box"]})
    report.sort(key=lambda r: (r["level"] != "ERRO", r["spans"][0][0]))
    print(f"== {a.composition} vs {a.preset} (zona: topo {safe['top']} · base {safe['bottom']} · "
          f"esq {safe['left']} · dir {safe['right']} px) · {dur:.1f}s a cada {a.step}s")
    for r in report:
        when = ", ".join(f"{s:.2f}" if s == e else f"{s:.2f}–{e:.2f}" for s, e in r["spans"][:4])
        if len(r["spans"]) > 4:
            when += f" (+{len(r['spans']) - 4})"
        edges = " ".join(f"{k} +{v}px" for k, v in r["edges"].items())
        print(f"  {r['level']:5} {when}s  {r['kind']} {r['el']} \"{r['text']}\"  {edges}")
    print(f"{errors} erro(s), {warns} aviso(s)")
    if a.json:
        a.json.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
