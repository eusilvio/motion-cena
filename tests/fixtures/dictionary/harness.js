/* Harness de runtime do dicionário de efeitos (references/motion-dictionary/*.json).
 *
 * Para cada efeito: monta um fixture novo (cena 1080x1920 com o DOM que o comentário da receita
 * descreve), roda o trecho `gsap` como corpo de função numa timeline pausada e confere:
 *   - sem exceção e sem aviso do GSAP (propriedade inválida, alvo não encontrado, plugin faltando);
 *   - a timeline dura algo depois de t;
 *   - seek determinístico: o mesmo instante dá o mesmo estado vindo de qualquer direção, inclusive
 *     num build novo que pula direto para o fim (worker de render que começa no meio);
 *   - algo muda entre o início e o fim;
 *   - por família: entrada termina visível e no quadro, saída termina escondida,
 *     transição começa em A e termina com B visível e nada cobrindo.
 *
 * Escopo do trecho: tl, t, el, items, a, b, scene, gsap (parâmetros) e, como globais preguiçosas
 * (o `const` do próprio trecho tem prioridade), path, mask, cursor, words, bar, num, grid, stage,
 * layers, lines, chars, svg, paths.
 *
 * Usado por run_dictionary.py (tests/test_dictionary_runtime.py). Também abre direto no navegador:
 * no console, dictHarness.show("slide-in", 0.4) monta um efeito e posiciona a timeline.
 */
(() => {
  "use strict";

  const W = 1080, H = 1920, T0 = 0.25, NS = "http://www.w3.org/2000/svg";
  const FONT = '"DejaVu Sans", Arial, sans-serif';
  const COL = {
    ink: "#f3ede2", dark: "#14181f", accent: "#d0592c", blue: "#1f6feb", green: "#2da44e",
    gold: "#e3b341", muted: "#56606e", red: "#e5484d", cyan: "#3cc8e6", violet: "#8957e5",
  };
  const PALETTE = [COL.accent, COL.blue, COL.green, COL.gold, COL.violet, COL.cyan, COL.red, COL.ink];
  const GLOBALS = ["path", "mask", "cursor", "words", "bar", "num", "grid", "stage", "layers", "lines", "chars", "svg", "paths"];
  const PLUGINS = ["DrawSVGPlugin", "MorphSVGPlugin", "MotionPathPlugin", "CustomEase", "SplitText"];

  // ---------------------------------------------------------------- DOM helpers

  const box = (x, y, w, h) => `position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;`;
  const ctr = "display:flex;align-items:center;justify-content:center;text-align:center;";
  const font = (px, weight = 700) => `font:${weight} ${px}px/1 ${FONT};`;

  function node(tag, parent, style = "", text = null, cls = "") {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (style) e.style.cssText = style;
    if (text !== null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  const div = (parent, style, text, cls) => node("div", parent, style, text, cls);
  const span = (parent, style, text, cls) => node("span", parent, style, text, cls);

  function sv(parent, tag, attrs = {}) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
    if (parent) parent.appendChild(e);
    return e;
  }

  function svgLayer(parent, z = 5) {
    const s = sv(parent, "svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H });
    s.style.cssText = `position:absolute;left:0;top:0;overflow:visible;z-index:${z};`;
    return s;
  }

  // Imagem "foto": gradiente com formas, para efeitos de cor, filtro e recorte.
  const PHOTO = `background:radial-gradient(circle at 30% 30%, ${COL.gold} 0 12%, transparent 13%),`
    + `radial-gradient(circle at 70% 60%, ${COL.cyan} 0 18%, transparent 19%),`
    + `linear-gradient(160deg, ${COL.blue}, ${COL.violet} 45%, ${COL.accent});`;

  // ---------------------------------------------------------------- fixture kinds

  // Posição padrão de cada papel quando o tipo é um objeto pequeno.
  const SPOT = { el: [140, 760, 400, 240], a: [140, 380, 360, 180], b: [600, 380, 360, 180] };
  const ROLE_COLOR = { el: COL.accent, a: COL.blue, b: COL.green };
  const ROLE_TEXT = { el: "Texto", a: "A", b: "B" };

  function card(c, role, style = "") {
    const [x, y, w, h] = SPOT[role] || SPOT.el;
    return div(c.scene, box(x, y, w, h) + ctr + font(72) + `background:${ROLE_COLOR[role] || COL.accent};`
      + "border-radius:28px;z-index:3;" + style, ROLE_TEXT[role] || "Texto", "card");
  }

  const KINDS = {
    card,
    // objeto pequeno numa posição livre (bola, peça)
    ball: (c, role) => {
      const y = role === "b" ? 1300 : role === "a" ? 1000 : 900;
      return div(c.scene, box(140, y, 160, 160) + `border-radius:50%;background:${ROLE_COLOR[role]};z-index:3;`, null, "ball");
    },
    text: (c, role) => {
      const y = { el: 840, a: 560, b: 1120 }[role] || 840;
      const words = { el: "MOVIMENTO", a: "antes", b: "depois" };
      return div(c.scene, box(90, y, 900, 200) + ctr + font(110) + "z-index:3;", words[role] || "MOVIMENTO", "title");
    },
    layer: (c, role) => {
      const isA = role === "a";
      const bg = isA ? `linear-gradient(160deg, ${COL.blue}, #0b2a5c)` : `linear-gradient(200deg, ${COL.accent}, #6b230b)`;
      const e = div(c.scene, box(0, 0, W, H) + `background:${bg};overflow:hidden;z-index:${isA ? 1 : 2};`, null, `layer layer-${role}`);
      div(e, box(140, 520, 800, 800) + ctr + font(640) + `color:rgba(243,237,226,0.9);`, isA ? "A" : "B");
      div(e, box(isA ? 120 : 760, 160, 200, 200) + `border-radius:50%;background:${COL.ink};opacity:0.7;`);
      div(e, box(isA ? 700 : 120, 1500, 260, 260) + `border-radius:40px;background:${isA ? COL.gold : COL.cyan};`);
      span(e, "position:absolute;left:40px;bottom:40px;" + font(56) + "color:rgba(243,237,226,0.85);", isA ? "cena A" : "cena B");
      return e;
    },
    num: (c, role) => {
      if (role === "el") return div(c.scene, box(140, 700, 800, 240) + ctr + font(180) + "font-variant-numeric:tabular-nums;z-index:3;", "0", "num");
      const [x, y, w, h] = SPOT[role];
      return div(c.scene, box(x, y, w, h) + ctr + font(110) + "font-variant-numeric:tabular-nums;z-index:3;", "0", "num");
    },
    bar: (c, role) => div(c.scene, box(140, 1040, 800, 80) + `background:${COL.accent};border-radius:16px;z-index:3;`, null, "bar"),
    dot: (c, role) => {
      const [x, y] = { el: [516, 936], a: [300, 600], b: [760, 600] }[role];
      return div(c.scene, box(x, y, 48, 48) + `border-radius:50%;background:${ROLE_COLOR[role]};z-index:4;`, null, "dot");
    },
    label: (c, role) => {
      const [x, y] = { el: [600, 700], a: [600, 700], b: [600, 820] }[role];
      return div(c.scene, box(x, y, 320, 100) + ctr + font(48) + `background:${COL.ink};color:${COL.dark};border-radius:20px;z-index:4;`, "48%", "label");
    },
    ring: (c, role) => div(c.scene, box(390, 810, 300, 300) + `border:12px solid ${ROLE_COLOR[role]};border-radius:50%;z-index:4;`, null, "ring"),
    // camada de cor no lugar exato do el (cópia tingida, máscara, sombra)
    overlay: (c, role) => {
      const [x, y, w, h] = SPOT.el;
      return div(c.scene, box(x, y, w, h) + ctr + font(72) + `background:${COL.gold};color:${COL.dark};border-radius:28px;z-index:4;`, "Texto", "overlay");
    },
    shadow: (c, role) => {
      const [x, y, w, h] = SPOT.el;
      return div(c.scene, box(x + 10, y + h - 10, w - 20, 50) + "border-radius:50%;background:rgba(0,0,0,0.6);filter:blur(10px);z-index:2;", null, "shadow");
    },
    path: (c, role) => {
      const d = {
        el: "M140 1100 C 340 760, 540 1420, 740 1000 S 940 860, 980 980",
        a: "M160 640 C 360 520, 560 760, 920 600",
        b: "M540 960 L 760 760 L 940 760",
      }[role];
      return sv(c.svg(), "path", { d, fill: "none", stroke: ROLE_COLOR[role], "stroke-width": 16, "stroke-linecap": "round", class: "path" });
    },
    circle: (c, role) => sv(c.svg(), "circle", {
      cx: 540, cy: 960, r: role === "el" ? 240 : 160, fill: "none", stroke: ROLE_COLOR[role],
      "stroke-width": 36, "stroke-linecap": "round", class: "circle",
    }),
    // contorno aberto em volta da palavra (circle-word, circle-draw)
    ellipse: (c, role) => sv(c.svg(), "path", {
      d: "M880 900 C 880 780, 200 770, 170 920 C 150 1060, 860 1090, 900 950 C 910 910, 880 880, 820 870",
      fill: "none", stroke: COL.gold, "stroke-width": 12, "stroke-linecap": "round", class: "ellipse",
    }),
    photo: (c, role) => div(c.scene, box(140, 460, 800, 1000) + PHOTO + "border-radius:24px;z-index:3;", null, "photo"),
    fullphoto: (c, role) => div(c.scene, box(0, 0, W, H) + PHOTO + "z-index:3;", null, "photo"),
    // camada de textura maior que o quadro (grain, papel, scanlines, ruído)
    texture: (c, role) => div(c.scene, box(-120, -120, W + 240, H + 240) + "z-index:8;opacity:0.5;mix-blend-mode:overlay;"
      + "background:repeating-linear-gradient(0deg, rgba(255,255,255,0.25) 0 3px, transparent 3px 7px),"
      + "repeating-linear-gradient(90deg, rgba(0,0,0,0.25) 0 2px, transparent 2px 9px);", null, "texture"),
  };

  // Listas (items). Cada uma devolve um array de elementos.
  function grid(c, sp, n, opts = {}) {
    const cols = opts.cols || sp.cols || Math.min(n, 4), rows = Math.ceil(n / cols), gap = opts.gap ?? 32;
    const areaW = opts.w || 800;
    const size = opts.size || Math.min(160, (areaW - (cols - 1) * gap) / cols);
    const x0 = (W - (cols * size + (cols - 1) * gap)) / 2, y0 = opts.y ?? 1180;
    const gw = cols * size + (cols - 1) * gap, gh = rows * size + (rows - 1) * gap;
    const out = [];
    for (let i = 0; i < n; i++) {
      const col = i % cols, row = Math.floor(i / cols);
      const x = x0 + col * (size + gap), y = y0 + row * (size + gap);
      const e = div(c.scene, box(x, y, size, size) + ctr + font(Math.round(size * 0.45))
        + `background:${PALETTE[i % PALETTE.length]};color:${COL.dark};border-radius:${Math.round(size * 0.18)}px;z-index:3;`,
        opts.noText ? null : String.fromCharCode(65 + (i % 26)), opts.cls || "item");
      e.dataset.char = String.fromCharCode(65 + (i % 26));
      e.dataset.dx = String(Math.round(x0 + gw / 2 - (x + size / 2)));
      e.dataset.dy = String(Math.round(y0 + gh / 2 - (y + size / 2)));
      e.dataset.at = String(n > 1 ? i / (n - 1) : 0);
      out.push(e);
    }
    return out;
  }

  function letters(c, sp, word = "MOVIMENTO", opts = {}) {
    const wrap = div(c.scene, box(40, opts.y ?? 840, 1000, 200) + ctr + "perspective:800px;z-index:3;", null, "word");
    return [...word].map((ch) => {
      const holder = opts.mask ? span(wrap, "display:inline-block;overflow:hidden;") : wrap;
      const e = span(holder, "display:inline-block;" + font(opts.size || 120) + (opts.style || ""), ch, "ch");
      e.dataset.char = ch;
      return e;
    });
  }

  function words(c, sp, list = ["cada", "palavra", "no", "tempo"], opts = {}) {
    const wrap = div(c.scene, box(90, opts.y ?? 760, 900, 420) + "display:flex;flex-wrap:wrap;align-content:center;"
      + "justify-content:center;gap:24px 32px;z-index:3;", null, "words");
    return list.map((w) => span(wrap, "display:inline-block;position:relative;" + font(96), w, "w"));
  }

  function maskedLines(c, list, y0 = 720, size = 104) {
    return list.map((txt, i) => {
      const line = div(c.scene, box(90, y0 + i * (size + 30), 900, size + 16) + "overflow:hidden;z-index:3;", null, "line");
      return span(line, "display:block;" + font(size), txt, "line-span");
    });
  }

  function stacked(c, list, y = 860) {
    return list.map((w) => div(c.scene, box(90, y, 900, 200) + ctr + font(120) + "z-index:3;", w, "stacked"));
  }

  function copiesOfEl(c, n, opts = {}) {
    const [x, y, w, h] = opts.rect || SPOT.el;
    return Array.from({ length: n }, (_, i) => div(c.scene, box(x, y, w, h) + ctr + font(72)
      + `background:${opts.colors ? opts.colors[i % opts.colors.length] : PALETTE[(i + 1) % PALETTE.length]};border-radius:28px;`
      + `z-index:${opts.above ? 6 + i : 2 - Math.min(i, 1)};opacity:${opts.opacity ?? 1};` + (opts.style || ""),
      opts.text ?? "Texto", "copy"));
  }

  function centered(c, n, size = 24, opts = {}) {
    return Array.from({ length: n }, (_, i) => div(c.scene, box(540 - size / 2, (opts.cy ?? 960) - size / 2, size, opts.h || size)
      + `border-radius:${opts.round === false ? 4 : size}px;background:${opts.color || PALETTE[i % PALETTE.length]};z-index:6;` + (opts.style || ""),
      null, opts.cls || "particle"));
  }

  function rings(c, n, size = 320) {
    return Array.from({ length: n }, () => div(c.scene, box(540 - size / 2, 960 - size / 2, size, size)
      + `border:10px solid ${COL.accent};border-radius:50%;z-index:4;`, null, "ring"));
  }

  function fullCells(c, rows, cols, cls = "cell") {
    const out = [], cw = W / cols, ch = H / rows;
    for (let r = 0; r < rows; r++) for (let k = 0; k < cols; k++) {
      out.push(div(c.scene, box(k * cw, r * ch, Math.ceil(cw) + 1, Math.ceil(ch) + 1)
        + `background:${(r * cols + k) % 5 === 0 ? COL.gold : COL.accent};z-index:10;`, null, cls));
    }
    return out;
  }

  const ITEMS = {
    boxes: (c, sp) => grid(c, sp, sp.n),
    letters: (c, sp) => letters(c, sp, sp.word),
    words: (c, sp) => words(c, sp),
    lines: (c, sp) => maskedLines(c, ["cada linha", "sobe por trás", "da máscara"]),
    particles: (c, sp) => centered(c, sp.n, sp.size || 24),
    rings: (c, sp) => rings(c, sp.n),
    copies: (c, sp) => copiesOfEl(c, sp.n, sp.copies || {}),
    strips: (c, sp) => Array.from({ length: sp.n }, (_, i) => div(c.scene, box(0, i * H / sp.n, W, H / sp.n + 1)
      + `background:${i % 2 ? COL.accent : COL.gold};z-index:10;`, null, "strip")),
    cells: (c, sp) => fullCells(c, sp.rows, sp.cols),
    blocks: (c, sp) => Array.from({ length: sp.n }, (_, i) => div(c.scene, box(0, 0, W, H)
      + `background:${[COL.gold, COL.accent, COL.violet, COL.cyan, COL.green][i % 5]};z-index:${10 + i};`, null, "block")),
    dots: (c, sp) => Array.from({ length: sp.n }, (_, i) => div(c.scene, box(150 + i * (760 / Math.max(sp.n - 1, 1)) - 20,
      1100 - ((i * 37) % 7) * 60 - 20, 40, 40) + `border-radius:50%;background:${COL.ink};z-index:4;`, null, "dot")),
  };

  // ---------------------------------------------------------------- helpers by selector
  // Criados só quando o trecho cita o seletor (querySelector ou string "#id").

  const HELPERS = {
    ".bg": (c) => div(c.scene, box(-60, -60, W + 120, H + 120) + "z-index:1;background:"
      + `radial-gradient(circle at 50% 35%, ${COL.gold} 0 6%, transparent 7%), linear-gradient(180deg, #2b4a7a, #0e1b33 60%, #1c3326);`, null, "bg"),
    ".mid": (c) => {
      const e = div(c.scene, box(-200, 1100, W + 600, 500) + "z-index:2;", null, "mid");
      for (let i = 0; i < 5; i++) div(e, box(i * 300, 100 + (i % 2) * 80, 360, 360) + `border-radius:50%;background:${i % 2 ? "#2f5d46" : "#3d7358"};`);
      return e;
    },
    ".fg": (c) => {
      const e = div(c.scene, box(-200, 1500, W + 600, 420) + "z-index:3;", null, "fg");
      for (let i = 0; i < 6; i++) div(e, box(i * 260, 0, 120, 420) + `background:${COL.dark};border-radius:60px 60px 0 0;`);
      return e;
    },
    ".subject": (c) => {
      const e = div(c.scene, box(390, 760, 300, 520) + "z-index:5;", null, "subject");
      div(e, box(80, 0, 140, 140) + `border-radius:50%;background:${COL.ink};`);
      div(e, box(30, 160, 240, 360) + `border-radius:120px 120px 20px 20px;background:${COL.accent};`);
      return e;
    },
    ".world": (c) => {
      const st = div(c.scene, box(0, 0, W, H) + "perspective:1200px;z-index:4;", null, "stage");
      const world = div(st, box(0, 0, W, H) + "transform-style:preserve-3d;", null, "world");
      for (let i = 0; i < 6; i++) {
        const z = -i * 500;
        div(world, box(240 + (i % 2) * 300, 700 + (i % 3) * 120, 300, 400) + ctr + font(120)
          + `background:${PALETTE[i]};border-radius:24px;transform:translateZ(${z}px);color:${COL.dark};`, String(i + 1));
      }
      return world;
    },
    ".stage": (c) => {
      const e = div(c.scene, box(0, 0, W * 1.6, H) + "z-index:2;", null, "stage");
      for (let i = 0; i < 5; i++) div(e, box(80 + i * 340, 760, 280, 400) + `background:${PALETTE[i]};border-radius:24px;`);
      return e;
    },
    ".flash": (c) => div(c.scene, box(0, 0, W, H) + "background:#fffaf2;opacity:0;z-index:40;", null, "flash"),
    ".glitch-r": (c) => div(c.scene, box(0, 0, W, H) + "background:rgba(255,40,60,0.55);mix-blend-mode:screen;opacity:0;z-index:40;", null, "glitch-r"),
    ".glitch-b": (c) => div(c.scene, box(0, 0, W, H) + "background:rgba(40,200,255,0.55);mix-blend-mode:screen;opacity:0;z-index:40;", null, "glitch-b"),
    ".wipe-bar": (c) => div(c.scene, box(-80, 0, 160, H) + `background:${COL.gold};z-index:30;`, null, "wipe-bar"),
    ".cursor": (c) => div(c.scene, box(990, 860, 12, 160) + `background:${COL.ink};z-index:6;`, null, "cursor"),
    ".occluder": (c) => div(c.scene, box(0, 0, 1600, H) + "background:linear-gradient(90deg, #0b0d11, #1e2633 50%, #0b0d11);z-index:30;", null, "occluder"),
    ".base": (c) => div(c.scene, box(0, 0, W, H) + PHOTO + "z-index:3;", null, "base"),
    ".sharp-top": (c) => div(c.scene, box(0, 0, W, H) + PHOTO + "z-index:4;", null, "sharp-top"),
    ".sharp-bottom": (c) => div(c.scene, box(0, 0, W, H) + PHOTO + "z-index:4;", null, "sharp-bottom"),
    ".app": (c) => {
      const e = div(c.scene, box(0, 0, W, H) + "z-index:2;background:#1b2230;", null, "app");
      for (let i = 0; i < 5; i++) div(e, box(80, 200 + i * 300, 920, 240) + `background:${PALETTE[i]};border-radius:28px;opacity:0.8;`);
      return e;
    },
    ".focus-ring": (c) => div(c.scene, box(110, 880, 860, 180) + `border:6px solid ${COL.cyan};border-radius:36px;z-index:4;`, null, "focus-ring"),
    ".gridline": (c) => Array.from({ length: 4 }, (_, i) => div(c.scene, box(180, 600 + i * 150, 760, 4) + `background:${COL.ink};z-index:2;`, null, "gridline")),
    ".tick": (c) => Array.from({ length: 5 }, (_, i) => div(c.scene, box(170 + i * 180, 1230, 60, 50) + ctr + font(36), String(i * 25), "tick")),
    ".seg-label": (c) => Array.from({ length: 4 }, (_, i) => div(c.scene, box(140 + i * 200, 900, 200, 60) + ctr + font(40) + "z-index:4;", `${[40, 25, 20, 15][i]}%`, "seg-label")),
    ".step": (c) => {
      for (let i = 0; i < 3; i++) {
        const s = div(c.scene, box(160 + i * 320, 900, 120, 120) + `border-radius:50%;border:8px solid ${COL.muted};z-index:4;`, null, "step");
        div(s, box(-8, -8, 120, 120) + `border-radius:50%;background:${COL.green};`, null, "done");
        if (i < 2) {
          const ln = div(c.scene, box(280 + i * 320, 954, 200, 12) + `background:${COL.muted};z-index:3;`, null, "step-line");
          div(ln, box(0, 0, 200, 12) + `background:${COL.green};`, null, "fill");
        }
      }
    },
    ".step-line": () => {},  // criado junto com .step
    ".track": (c) => {
      const tr = div(c.scene, box(0, 0, W, H * 2 + 60) + "z-index:2;", null, "track");
      const { a, b } = c.refs;
      if (a) { tr.appendChild(a); a.style.top = "0px"; }
      if (b) { tr.appendChild(b); b.style.top = `${H}px`; }
      return tr;
    },
    ".burn-a": (c) => burn(c, "burn-a", 0), ".burn-b": (c) => burn(c, "burn-b", 1), ".burn-c": (c) => burn(c, "burn-c", 2),
    ".leak-warm": (c) => div(c.scene, box(0, 0, W, H) + "background:linear-gradient(120deg, #ffb347, #ff6a3d);mix-blend-mode:screen;opacity:0;z-index:30;", null, "leak-warm"),
    ".leak-1": (c) => div(c.scene, box(200, 300, 900, 1300) + "background:radial-gradient(closest-side, #fff2c4, transparent);mix-blend-mode:screen;opacity:0;z-index:31;", null, "leak-1"),
    ".leak-2": (c) => div(c.scene, box(-100, 600, 900, 1100) + "background:radial-gradient(closest-side, #ff9a5a, transparent);mix-blend-mode:screen;opacity:0;z-index:31;", null, "leak-2"),
    ".shutter-top": (c) => div(c.scene, box(0, 0, W, H / 2) + "background:#0b0d11;z-index:30;", null, "shutter-top"),
    ".shutter-bot": (c) => div(c.scene, box(0, H / 2, W, H / 2) + "background:#0b0d11;z-index:30;", null, "shutter-bot"),
    ".split-l": (c) => splitCopy(c, "split-l"), ".split-r": (c) => splitCopy(c, "split-r"),
    "#rota": (c) => sv(c.svg(), "path", { id: "rota", d: "M140 1500 C 300 900, 800 1300, 900 700 S 600 300, 300 420", fill: "none", stroke: COL.muted, "stroke-width": 8, "stroke-dasharray": "18 14" }),
    "#ink-mask": (c) => {
      const s = c.svg();
      const f = sv(c.defs(), "filter", { id: "ink-rough" });
      sv(f, "feTurbulence", { type: "fractalNoise", baseFrequency: 0.02, numOctaves: 2, seed: 4 });
      sv(f, "feDisplacementMap", { in: "SourceGraphic", scale: 60 });
      const m = sv(c.defs(), "mask", { id: "ink-mask", maskUnits: "userSpaceOnUse", x: 0, y: 0, width: W, height: H });
      const g = sv(m, "g", { filter: "url(#ink-rough)" });
      [[300, 500], [780, 900], [420, 1400], [700, 1700]].forEach(([cx, cy]) => sv(g, "circle", { cx, cy, r: 0, fill: "#fff" }));
      if (c.refs.b) { c.refs.b.style.mask = "url(#ink-mask)"; c.refs.b.style.webkitMask = "url(#ink-mask)"; }
      return s;
    },
    "#px": (c) => {
      const f = sv(c.defs(), "filter", { id: "px", x: 0, y: 0, width: "100%", height: "100%" });
      sv(f, "feFlood", { x: 0.5, y: 0.5, height: 1, width: 1 });
      sv(f, "feComposite", { width: 1, height: 1 });
      sv(f, "feTile", { result: "a" });
      sv(f, "feComposite", { in: "SourceGraphic", in2: "a", operator: "in" });
      sv(f, "feMorphology", { operator: "dilate", radius: 0.5 });
      return f;
    },
    "#warp": (c) => fxDisplacement(c, "warp"),
    "#dissolve": (c) => {
      const f = fxDisplacement(c, "dissolve");
      if (c.refs.el) c.refs.el.style.filter = "url(#dissolve)";
      return f;
    },
    "#blob1": (c) => defsPath(c, "blob1", "M540 700 C 700 700 800 820 790 960 C 780 1120 660 1220 540 1210 C 400 1200 290 1100 300 950 C 310 800 400 700 540 700Z"),
    "#blob2": (c) => defsPath(c, "blob2", "M560 680 C 760 720 830 880 780 1010 C 730 1160 600 1250 480 1190 C 330 1120 270 980 330 860 C 390 740 450 670 560 680Z"),
    "#blob3": (c) => defsPath(c, "blob3", "M520 720 C 650 650 840 760 810 930 C 790 1080 700 1230 560 1220 C 420 1210 300 1140 290 990 C 280 850 400 780 520 720Z"),
    "#quad": (c) => defsPath(c, "quad", "M390 810 L 690 810 L 690 1110 L 390 1110 Z"),
    "#hex": (c) => defsPath(c, "hex", "M540 790 L 687 875 L 687 1045 L 540 1130 L 393 1045 L 393 875 Z"),
    "#tri": (c) => defsPath(c, "tri", "M540 790 L 710 1090 L 370 1090 Z"),
    "#forma": (c) => defsPath(c, "forma", "M540 760 L 600 900 L 750 910 L 635 1005 L 675 1150 L 540 1070 L 405 1150 L 445 1005 L 330 910 L 480 900 Z"),
  };

  function burn(c, cls, i) {
    return div(c.scene, box(700 + i * 60, 300 + i * 450, 900, 900) + "z-index:30;opacity:0;mix-blend-mode:screen;"
      + `background:radial-gradient(closest-side, ${["#ffcf6b", "#ff8a3d", "#e5484d"][i]}, transparent);`, null, cls);
  }
  function splitCopy(c, cls) {
    const e = KINDS.layer(c, "a");
    e.className = cls;
    e.style.zIndex = "20";
    e.style.opacity = "0";
    return e;
  }
  function fxDisplacement(c, id) {
    const f = sv(c.defs(), "filter", { id, x: "-10%", y: "-10%", width: "120%", height: "120%" });
    sv(f, "feTurbulence", { type: "fractalNoise", baseFrequency: 0.012, numOctaves: 2, seed: 3, result: "n" });
    sv(f, "feDisplacementMap", { in: "SourceGraphic", in2: "n", scale: 0, xChannelSelector: "R", yChannelSelector: "G" });
    return f;
  }
  function defsPath(c, id, d) {
    return sv(c.defs(), "path", { id, d });
  }

  // ---------------------------------------------------------------- per-effect fixtures
  // Só o que foge do padrão. Os comentários de cada receita descrevem esse DOM.

  const FAMILY = {
    texto: { el: "text", items: "letters" },
    transicoes: { a: "layer", b: "layer", items: "strips", n: 8, always: ["a", "b"] },  // A e B existem mesmo quando o trecho só mexe em um
    camera: { a: "layer", b: "layer" },
    particulas: { items: "particles", n: 24 },
  };

  const S = {
    // 3d-perspectiva
    "extrude": { items: "copies", n: 4, copies: { colors: ["#7a3418", "#5e2812", "#431c0d", "#2b1208"] } },
    "page-curl": { custom: (c) => {
      const el = div(c.scene, box(240, 460, 600, 900) + `background:${COL.ink};border-radius:8px;z-index:3;`, null, "page");
      const flap = div(c.scene, box(240, 460, 600, 900) + "background:linear-gradient(135deg, #ffffff, #c9c2b6);box-shadow:-20px -20px 40px rgba(0,0,0,0.4);z-index:4;", null, "flap");
      return { el, items: [flap] };
    } },
    "isometric-rise": { n: 9, cols: 3, preserve3d: true },
    "layered-depth": { n: 4, cols: 2, preserve3d: true },
    "scatter-3d-assemble": { items: "letters" },
    // camera
    "pan": { custom: (c) => wideWorld(c, 2400, H) },
    "tilt": { custom: (c) => wideWorld(c, W, 3200) },
    "follow-cam": { custom: (c) => {
      const world = HELPERS[".world"](c);
      const subject = HELPERS[".subject"](c);
      world.appendChild(subject);  // o sujeito anda dentro do mundo; a câmera é o mundo andando ao contrário
      return {};
    }, noHelpers: true },
    "word-cube": { custom: (c) => {
      const el = div(c.scene, box(240, 860, 600, 200) + "transform-style:preserve-3d;z-index:3;", null, "cube");
      ["UM", "DOIS", "TRÊS", "QUATRO"].forEach((w, i) => div(el, box(0, 0, 600, 200) + ctr + font(110)
        + `background:${PALETTE[i]};color:${COL.dark};backface-visibility:hidden;transform:rotateX(${i * 90}deg) translateZ(100px);`, w, "face"));
      return { el };
    } },
    // dados-infografico
    "bar-grow": { el: "bar", a: "num" },
    "count-up": { el: "num" },
    "area-fill": { custom: (c) => ({ a: sv(c.svg(), "path", { d: "M140 1300 L 140 1000 C 340 760, 540 1180, 740 900 S 940 820, 980 860 L 980 1300 Z", fill: COL.cyan, class: "area" }) }) },
    "bar-race": { custom: (c) => ({ items: [0, 1, 2, 3].map((i) => {
      const row = div(c.scene, box(140, 700, 800, 110) + "z-index:3;", null, "row");
      div(row, box(0, 0, 160, 110) + ctr + font(48), ["Ana", "Bia", "Caio", "Davi"][i]);
      div(row, box(180, 10, 620, 90) + `background:${PALETTE[i]};border-radius:12px;`, null, "bar");
      return row;
    }) }) },
    "before-after-slider": { custom: (c) => ({
      el: div(c.scene, box(0, 0, W, H) + "background:linear-gradient(200deg, #e3b341, #d0592c);z-index:3;", null, "after"),
      a: div(c.scene, box(-6, 0, 12, H) + `background:${COL.ink};z-index:4;`, null, "handle"),
    }) },
    "chart-axes-build": { custom: (c) => ({ items: [
      div(c.scene, box(180, 1200, 760, 8) + `background:${COL.ink};z-index:3;`, null, "x-axis"),
      div(c.scene, box(180, 560, 8, 648) + `background:${COL.ink};z-index:3;`, null, "y-axis"),
    ] }) },
    "chart-scrub-readout": { custom: (c) => {
      const ox = 90, oy = 500;
      sv(c.svg(), "polyline", { points: "90,1100 270,1020 450,1060 630,880 810,800 990,680", transform: `translate(0 ${oy - 500})`, fill: "none", stroke: COL.cyan, "stroke-width": 10 });
      return {
        el: div(c.scene, box(ox - 3, oy, 6, 760) + `background:${COL.ink};z-index:4;`, null, "vline"),
        a: div(c.scene, box(ox - 20, oy - 20, 40, 40) + `border-radius:50%;background:${COL.accent};z-index:5;`, null, "dot"),
        b: div(c.scene, box(700, 360, 280, 110) + ctr + font(64) + "z-index:5;", "0%", "readout"),
      };
    } },
    "comparison-bars": { custom: (c) => ({
      a: div(c.scene, box(140, 900, 400, 120) + `background:${COL.accent};z-index:3;`, null, "bar-left"),
      b: div(c.scene, box(540, 900, 400, 120) + `background:${COL.blue};z-index:3;`, null, "bar-right"),
    }) },
    "data-point-highlight": { items: "dots", n: 8, el: "dot", a: "label", b: "path" },
    "donut-fill": { custom: (c) => ({ items: [0, 1, 2].map((i) => sv(c.svg(), "circle", {
      cx: 540, cy: 960, r: 260, fill: "none", stroke: PALETTE[i], "stroke-width": 90, transform: "rotate(-90 540 960)", class: "slice" })) }) },
    "funnel-reveal": { custom: (c) => ({ items: [0, 1, 2, 3, 4].map((i) => div(c.scene, box(140 + i * 70, 600 + i * 150, 800 - i * 140, 120)
      + `background:${PALETTE[i]};border-radius:16px;z-index:3;`, null, "band")) }) },
    "gauge-needle": { custom: (c) => ({
      a: sv(c.svg(), "path", { d: "M240 1100 A 300 300 0 0 1 840 1100", fill: "none", stroke: COL.green, "stroke-width": 40, "stroke-linecap": "round", class: "arc" }),
      el: div(c.scene, box(530, 830, 20, 300) + `background:${COL.ink};border-radius:10px;z-index:4;`, null, "needle"),
    }) },
    "heatmap-fade": { n: 12, cols: 4, gridOpts: { gap: 8, noText: true } },
    "line-chart-draw": { custom: (c) => {
      const pts = [[140, 1200], [300, 1000], [460, 1080], [620, 820], [780, 900], [940, 640]];
      const el = sv(c.svg(), "path", { d: "M" + pts.map((p) => p.join(" ")).join(" L "), fill: "none", stroke: COL.cyan, "stroke-width": 12, class: "line" });
      return { el, items: pts.map(([x, y]) => div(c.scene, box(x - 20, y - 20, 40, 40) + `border-radius:50%;background:${COL.ink};z-index:6;`, null, "pt")) };
    } },
    "map-pin-drop": { custom: (c) => ({
      el: div(c.scene, box(480, 760, 120, 180) + `background:${COL.red};border-radius:60px 60px 60px 0;transform:rotate(-45deg);z-index:5;`, null, "pin"),
      a: div(c.scene, box(470, 940, 140, 40) + "background:rgba(0,0,0,0.6);border-radius:50%;z-index:4;", null, "pin-shadow"),
      b: div(c.scene, box(440, 860, 200, 200) + `border:8px solid ${COL.red};border-radius:50%;z-index:4;`, null, "impact"),
    }) },
    "map-route-draw": { custom: (c) => ({
      el: sv(c.svg(), "path", { d: "M180 1500 C 300 1100, 700 1300, 760 900 S 900 500, 880 420", fill: "none", stroke: COL.gold, "stroke-width": 12, "stroke-linecap": "round", class: "route" }),
      a: div(c.scene, box(0, 0, 48, 48) + `border-radius:50%;background:${COL.accent};z-index:6;`, null, "marker"),
      b: div(c.scene, box(840, 340, 80, 80) + `border-radius:50%;background:${COL.red};z-index:6;`, null, "dest"),
    }) },
    "odometer": { custom: (c) => ({ items: [0, 1, 2, 3].map((i) => {
      const win = div(c.scene, box(220 + i * 170, 860, 150, 160) + "overflow:hidden;z-index:3;background:#0b0d11;border-radius:12px;", null, "digit-window");
      const col = div(win, box(0, 0, 150, 160 * 40), null, "digit-col");
      for (let k = 0; k < 40; k++) div(col, box(0, k * 160, 150, 160) + ctr + font(120) + "font-variant-numeric:tabular-nums;", String(k % 10));
      return col;
    }) }) },
    "percent-ring": { el: "circle", a: "num" },
    "pictogram-fill": { n: 100, cols: 10, gridOpts: { gap: 12, noText: true, y: 760 } },
    "progress-bar": { custom: (c) => {
      div(c.scene, box(140, 1000, 800, 60) + "background:#2a313d;border-radius:30px;z-index:2;", null, "track");
      const tag = div(c.scene, box(80, 880, 120, 90) + ctr + `background:${COL.ink};color:${COL.dark};border-radius:16px;z-index:4;`, null, "tag");
      return {
        el: div(c.scene, box(140, 1000, 800, 60) + `background:${COL.green};border-radius:30px;z-index:3;`, null, "fill"),
        a: tag, b: span(tag, font(44), "0%", "num"),
      };
    } },
    "scatter-pop": { items: "dots", n: 10, el: "path" },
    "stacked-bar": { custom: (c) => {
      let x = 140;
      return { items: [320, 200, 160, 120].map((w, i) => { const e = div(c.scene, box(x, 980, w, 120) + `background:${PALETTE[i]};z-index:3;`, null, "seg"); x += w; return e; }) };
    } },
    "timeline-scrub": { custom: (c) => {
      div(c.scene, box(90, 1000, 900, 12) + "background:#2a313d;z-index:2;");
      return {
        el: div(c.scene, box(90, 1000, 900, 12) + `background:${COL.accent};z-index:3;`, null, "progress"),
        a: div(c.scene, box(66, 982, 48, 48) + `border-radius:50%;background:${COL.ink};z-index:5;`, null, "head"),
        items: [0, 0.25, 0.5, 0.75, 1].map((at) => {
          const m = div(c.scene, box(90 + at * 900 - 30, 920, 60, 60) + `border-radius:50%;background:${COL.gold};z-index:4;`, null, "milestone");
          m.dataset.at = String(at);
          return m;
        }),
      };
    } },
    // enfase
    "color-pop": { a: "overlay" },
    "outline-pulse": { custom: (c) => {
      const [x, y, w, h] = SPOT.el;
      return { a: div(c.scene, box(x, y, w, h) + `border:10px solid ${COL.gold};border-radius:28px;z-index:2;`, null, "outline") };
    } },
    "ripple": { items: "rings", n: 3 },
    "shockwave-ring": { a: "circle" },
    // entradas: padrão
    // estilizacao-textura
    "grain": { el: "texture" },
    "motion-trail": { items: "copies", n: 4, copies: { colors: [COL.accent, COL.accent, COL.accent, COL.accent] } },
    "bloom": { el: "overlay" },
    "boiling-line": { custom: (c) => {
      const f = sv(c.defs(), "filter", { id: "boil" });
      const turb = sv(f, "feTurbulence", { type: "fractalNoise", baseFrequency: 0.03, numOctaves: 2, seed: 1, result: "n" });
      sv(f, "feDisplacementMap", { in: "SourceGraphic", in2: "n", scale: 6 });
      const g = sv(c.svg(), "g", { filter: "url(#boil)" });
      sv(g, "path", { d: "M240 1200 C 300 700, 780 700, 840 1200 Z", fill: "none", stroke: COL.ink, "stroke-width": 14 });
      return { el: turb };
    } },
    "bw-to-color": { el: "photo" },
    "color-grade-shift": { el: "photo" },
    "crt-turn-on": { el: "fullphoto" },
    "datamosh": { custom: (c) => ({ items: [0, 1, 2, 3, 4, 5].map((i) => div(c.scene, box(140, 460, 800, 1000) + PHOTO
      + `clip-path:inset(${i * 16.66}% 0% ${100 - (i + 1) * 16.66}% 0%);z-index:3;`, null, "block")) }) },
    "duotone": { custom: (c) => ({ items: [KINDS.photo(c, "el"),
      div(c.scene, box(140, 460, 800, 1000) + "background:linear-gradient(160deg, #1f6feb, #e3b341);mix-blend-mode:color;opacity:0;z-index:4;border-radius:24px;", null, "tint")] }) },
    "dust-scratches": { items: "particles", n: 10, size: 14 },
    "echo-ghost": { items: "copies", n: 3, copies: { opacity: 0.5 } },
    "film-burn": { custom: (c) => ({ items: [0, 1, 2].map((i) => burn(c, "burn", i)) }) },
    "frosted-glass": { custom: (c) => {
      KINDS.fullphoto(c, "el").style.zIndex = "1";
      const el = div(c.scene, box(0, 0, W, H) + PHOTO + "z-index:2;", null, "frost");
      const items = ["Título", "linha de texto", "outra linha"].map((t, i) => div(c.scene, box(180, 700 + i * 140, 720, 110) + ctr + font(i ? 56 : 80) + "z-index:3;", t, "card-line"));
      return { el, items };
    } },
    "halftone": { custom: (c) => {
      const el = KINDS.photo(c, "el");
      el.style.cssText += "-webkit-mask-image:radial-gradient(circle, #000 var(--dot), transparent calc(var(--dot) + 0.5px));"
        + "mask-image:radial-gradient(circle, #000 var(--dot), transparent calc(var(--dot) + 0.5px));-webkit-mask-size:12px 12px;mask-size:12px 12px;";
      return { el };
    } },
    "lens-flare": { items: "particles", n: 4, size: 160 },
    "light-leak": { custom: (c) => ({ items: [0, 1, 2].map((i) => div(c.scene, box(-200 + i * 200, 200 + i * 400, 1400, 1400)
      + `background:radial-gradient(closest-side, ${["#ffcf6b", "#ff8a3d", "#ff5f6d"][i]}, transparent);mix-blend-mode:screen;z-index:20;`, null, "leak")) }) },
    "liquid-glass": { custom: (c) => {
      const f = sv(c.defs(), "filter", { id: "lg" });
      sv(f, "feTurbulence", { type: "fractalNoise", baseFrequency: 0.01, numOctaves: 1, seed: 2, result: "n" });
      const disp = sv(f, "feDisplacementMap", { in: "SourceGraphic", in2: "n", scale: 18 });
      KINDS.fullphoto(c, "el").style.filter = "url(#lg)";
      const card = div(c.scene, box(180, 700, 720, 520) + "background:rgba(255,255,255,0.18);border:2px solid rgba(255,255,255,0.5);border-radius:48px;z-index:4;overflow:hidden;", null, "glass");
      const shine = div(card, box(0, 0, 240, 520) + "background:linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent);", null, "shine");
      return { items: [card, disp, shine] };
    } },
    "motion-blur": { custom: (c) => {
      const f = sv(c.defs(), "filter", { id: "mb", x: "-50%", width: "200%" });
      const blur = sv(f, "feGaussianBlur", { stdDeviation: "0 0" });
      const n = card(c, "el", "filter:url(#mb);");
      return { items: [n, blur] };
    } },
    "neon-flicker": { custom: (c) => ({ el: div(c.scene, box(90, 840, 900, 200) + ctr + font(130) + "color:transparent;-webkit-text-stroke:4px #ff2fd1;filter:drop-shadow(0 0 18px #ff2fd1);z-index:3;", "NEON", "neon") }) },
    "paper-texture": { el: "texture" },
    "pixel-sort": { custom: (c) => ({ items: Array.from({ length: 8 }, (_, i) => div(c.scene, box(140, 460, 800, 1000) + PHOTO
      + `clip-path:inset(0% ${100 - (i + 1) * 12.5}% 0% ${i * 12.5}%);z-index:3;`, null, "col")) }) },
    "posterize": { custom: (c) => {
      const f = sv(c.defs(), "filter", { id: "poster" });
      const ct = sv(f, "feComponentTransfer");
      const items = ["feFuncR", "feFuncG", "feFuncB"].map((t) => sv(ct, t, { type: "discrete", tableValues: "0 0.25 0.5 0.75 1" }));
      return { el: KINDS.photo(c, "el"), items };
    } },
    "rgb-split": { custom: (c) => ({ items: [
      copiesOfEl(c, 1, { colors: ["rgba(255,40,60,0.8)"], above: true, opacity: 0, style: "mix-blend-mode:screen;" })[0],
      copiesOfEl(c, 1, { colors: ["rgba(40,200,255,0.8)"], above: true, opacity: 0, style: "mix-blend-mode:screen;" })[0],
    ] }) },
    "scanlines": { el: "texture" },
    "tv-static": { el: "texture" },
    "vhs": { custom: (c) => ({
      items: Array.from({ length: 6 }, (_, i) => div(c.scene, box(0, 0, W, H) + PHOTO + `clip-path:inset(${i * 16.66}% 0% ${100 - (i + 1) * 16.66}% 0%);z-index:3;`, null, "band")),
      el: div(c.scene, box(0, 0, W, 100) + "background:linear-gradient(transparent, rgba(255,255,255,0.35), transparent);z-index:6;", null, "tracking"),
    }) },
    "vignette-pulse": { custom: (c) => ({ el: div(c.scene, box(0, 0, W, H) + "background:radial-gradient(transparent 50%, rgba(0,0,0,0.85));z-index:20;", null, "vignette") }) },
    // fisica
    "domino-fall": { custom: (c) => ({ items: Array.from({ length: 6 }, (_, i) => div(c.scene, box(160 + i * 140, 900, 50, 300) + `background:${PALETTE[i]};border-radius:8px;z-index:3;`, null, "domino")) }) },
    "drag": { custom: (c) => {
      const el = card(c, "el");
      const [x, y, , h] = SPOT.el;
      return { el, a: div(c.scene, box(x - 160, y + 40, 160, h - 80) + `background:${COL.gold};z-index:2;`, null, "flag") };
    } },
    "secondary-action": { custom: (c) => {
      const el = card(c, "el");
      return { el, a: div(c.scene, box(470, 700, 30, 100) + `background:${COL.gold};border-radius:15px;z-index:4;`, null, "antenna") };
    } },
    "timing-spacing": { a: "ball", b: "ball" },
    // formas-svg
    "draw-on": { el: "path" },
    "arrow-draw": { custom: (c) => ({
      a: sv(c.svg(), "path", { d: "M200 1200 C 400 1000, 600 1000, 820 820", fill: "none", stroke: COL.ink, "stroke-width": 14, "stroke-linecap": "round", class: "shaft" }),
      b: sv(c.svg(), "path", { d: "M770 790 L 840 805 L 820 870 Z", fill: COL.ink, class: "head" }),
    }) },
    "blob": { custom: (c) => ({ el: sv(c.svg(), "path", { d: "M540 700 C 700 700 800 820 790 960 C 780 1120 660 1220 540 1210 C 400 1200 290 1100 300 950 C 310 800 400 700 540 700Z", fill: COL.violet, class: "blob" }) }) },
    "check-mark-draw": { custom: (c) => {
      const g = sv(c.svg(), "g", { class: "seal" });
      return {
        el: g,
        a: sv(g, "circle", { cx: 540, cy: 960, r: 200, fill: "none", stroke: COL.green, "stroke-width": 24 }),
        b: sv(g, "path", { d: "M450 965 L 520 1035 L 650 885", fill: "none", stroke: COL.green, "stroke-width": 28, "stroke-linecap": "round", "stroke-linejoin": "round" }),
      };
    } },
    "circle-draw": { el: "ellipse" },
    "corner-brackets": { custom: (c) => {
      const s = (x, y, b) => div(c.scene, box(x, y, 90, 90) + `border:${b};z-index:4;`, null, "bracket");
      const L = `14px solid ${COL.gold}`;
      return { items: [
        s(240, 660, `${L};border-right:0;border-bottom:0`), s(750, 660, `${L};border-left:0;border-bottom:0`),
        s(240, 1170, `${L};border-right:0;border-top:0`), s(750, 1170, `${L};border-left:0;border-top:0`),
      ] };
    } },
    "dash-march": { custom: (c) => ({ el: sv(c.svg(), "path", { d: "M140 1100 C 340 760, 540 1420, 740 1000 S 940 860, 980 980", fill: "none", stroke: COL.ink, "stroke-width": 10, "stroke-dasharray": "16 12", class: "dash" }) }) },
    "dot-to-line": { custom: (c) => ({ el: div(c.scene, box(180, 954, 720, 12) + `background:${COL.accent};border-radius:6px;z-index:3;`, null, "line") }) },
    "line-connect": { custom: (c) => {
      // linha de A (240,1200) até B (840,720): comprimento 768, ângulo -38,66°
      const line = div(c.scene, box(240, 1194, 768, 12) + `background:${COL.ink};transform-origin:0% 50%;transform:rotate(-38.66deg);z-index:2;`, null, "connector");
      const n = (x, y) => div(c.scene, box(x - 50, y - 50, 100, 100) + `border-radius:50%;background:${COL.accent};z-index:3;`, null, "node");
      return { el: line, items: [n(240, 1200), n(840, 720)] };
    } },
    "line-to-shape": { custom: (c) => ({ el: sv(c.svg(), "path", { d: "M330 960 L 750 960", fill: "none", stroke: COL.gold, "stroke-width": 14, class: "line" }) }) },
    "liquid-fill": { custom: (c) => {
      const glass = div(c.scene, box(340, 560, 400, 800) + `border:10px solid ${COL.ink};border-radius:0 0 80px 80px;overflow:hidden;z-index:3;`, null, "glass");
      const el = div(glass, box(0, 0, 400, 800) + `background:${COL.blue};`, null, "liquid");
      const a = div(el, box(0, -40, 1080 * 2, 60) + `background:repeating-radial-gradient(circle at 135px 60px, ${COL.blue} 0 70px, transparent 71px 270px);`, null, "wave");
      return { el, a };
    } },
    "loading-spinner": { el: "circle" },
    "path-follow": { custom: (c) => ({ el: div(c.scene, box(0, 0, 80, 50) + `background:${COL.accent};border-radius:10px 40px 40px 10px;z-index:6;`, null, "arrow") }) },
    "polygon-morph": { custom: (c) => ({ el: sv(c.svg(), "path", { d: "M540 790 L 710 1090 L 370 1090 Z", fill: COL.cyan, class: "poly" }) }) },
    "shape-burst": { items: "particles", n: 8, size: 60 },
    "shape-grid-stagger": { n: 24, cols: 6, gridOpts: { gap: 20, noText: true, y: 760 } },
    "star-burst": { custom: (c) => ({
      el: div(c.scene, box(440, 860, 200, 200) + `border-radius:50%;background:${COL.gold};z-index:4;`, null, "core"),
      items: Array.from({ length: 12 }, (_, i) => {
        const ang = (i / 12) * Math.PI * 2;
        return sv(c.svg(), "line", { x1: 540 + Math.cos(ang) * 140, y1: 960 + Math.sin(ang) * 140, x2: 540 + Math.cos(ang) * 340, y2: 960 + Math.sin(ang) * 340, stroke: COL.gold, "stroke-width": 14, "stroke-linecap": "round" });
      }),
    }) },
    "stroke-to-fill": { custom: (c) => ({ el: sv(c.svg(), "path", { d: "M540 760 L 600 900 L 750 910 L 635 1005 L 675 1150 L 540 1070 L 405 1150 L 445 1005 L 330 910 L 480 900 Z", fill: COL.gold, stroke: COL.gold, "stroke-width": 10, class: "star" }) }) },
    "underline-sweep": { custom: (c) => {
      KINDS.text(c, "el");
      return { el: div(c.scene, box(240, 1050, 600, 16) + `background:${COL.accent};z-index:3;`, null, "underline") };
    } },
    "x-mark-draw": { custom: (c) => {
      const g = sv(c.svg(), "g", { class: "x" });
      const ln = (x1, y1, x2, y2) => sv(g, "line", { x1, y1, x2, y2, stroke: COL.red, "stroke-width": 40, "stroke-linecap": "round" });
      return { el: g, items: [ln(380, 800, 700, 1120), ln(700, 800, 380, 1120)] };
    } },
    // interface-ui
    "button-press": { custom: (c) => ({
      el: div(c.scene, box(240, 880, 600, 160) + ctr + font(64) + `background:${COL.accent};border-radius:80px;z-index:3;`, "Comprar", "btn"),
      a: div(c.scene, box(260, 1010, 560, 60) + "background:rgba(0,0,0,0.7);border-radius:50%;filter:blur(12px);z-index:2;", null, "btn-shadow"),
    }) },
    "card-stack-swipe": { custom: (c) => ({ items: [0, 1, 2, 3].map((i) => div(c.scene, box(240, 600, 600, 800) + ctr + font(90)
      + `background:${PALETTE[i]};border-radius:40px;z-index:${10 - i};transform:translateY(${i * 30}px) scale(${1 - i * 0.05});`, String(i + 1), "card")) }) },
    "chat-bubbles": { custom: (c) => {
      const list = div(c.scene, box(80, 400, 920, 700) + "z-index:2;", null, "list");
      ["Oi!", "Tudo bem?", "Viu o vídeo?"].forEach((t, i) => div(list, box(i % 2 ? 420 : 0, i * 140 + 160, 500, 110) + ctr + font(48) + `background:${i % 2 ? COL.blue : "#2a313d"};border-radius:40px;`, t));
      const typing = div(c.scene, box(80, 1000, 220, 110) + ctr + "gap:16px;background:#2a313d;border-radius:40px;z-index:3;", null, "typing");
      const dots = [0, 1, 2].map(() => span(typing, `display:inline-block;width:24px;height:24px;border-radius:50%;background:${COL.ink};`, null, "dot"));
      const bubble = div(c.scene, box(80, 1000, 560, 110) + ctr + font(48) + "background:#2a313d;border-radius:40px;z-index:3;", "Vi sim, ficou ótimo", "bubble");
      return { el: bubble, a: typing, b: list, items: dots };
    } },
    "cursor-click": { custom: (c) => {
      const target = div(c.scene, box(290, 880, 500, 160) + ctr + font(60) + `background:${COL.accent};border-radius:80px;z-index:3;`, "Enviar", "btn");
      return {
        a: target,
        b: div(c.scene, box(440, 860, 200, 200) + `border:8px solid ${COL.ink};border-radius:50%;opacity:0;z-index:4;`, null, "click-ring"),
        el: div(c.scene, box(540, 960, 60, 80) + `background:${COL.ink};clip-path:polygon(0 0, 100% 70%, 45% 70%, 30% 100%);z-index:6;`, null, "cursor"),
      };
    } },
    "cursor-drag": { custom: (c) => ({
      a: div(c.scene, box(200, 1100, 300, 120) + ctr + font(48) + `background:${COL.gold};color:${COL.dark};border-radius:24px;z-index:4;`, "arquivo", "chip"),
      el: div(c.scene, box(420, 1170, 60, 80) + `background:${COL.ink};clip-path:polygon(0 0, 100% 70%, 45% 70%, 30% 100%);z-index:6;`, null, "cursor"),
    }) },
    "dropdown-open": { custom: (c) => {
      const field = div(c.scene, box(190, 600, 700, 140) + `background:#2a313d;border-radius:24px;z-index:3;` + ctr + font(52), "Escolha", "field");
      const chevron = div(field, box(600, 50, 40, 40) + `border-right:8px solid ${COL.ink};border-bottom:8px solid ${COL.ink};transform:rotate(45deg);`, null, "chevron");
      const menu = div(c.scene, box(190, 760, 700, 520) + "background:#2a313d;border-radius:24px;z-index:3;", null, "menu");
      const items = ["Reels", "Stories", "Shorts", "Feed"].map((t, i) => div(menu, box(40, 30 + i * 120, 620, 100) + font(52) + "display:flex;align-items:center;", t, "option"));
      return { el: menu, a: chevron, items };
    } },
    "input-typing": { custom: (c) => {
      const field = div(c.scene, box(130, 900, 820, 140) + "background:#2a313d;border-radius:30px;z-index:3;", null, "field");
      const ph = div(field, box(40, 0, 740, 140) + font(52) + "display:flex;align-items:center;color:rgba(243,237,226,0.5);", "Digite aqui", "placeholder");
      const txt = span(field, "position:absolute;left:40px;top:44px;" + font(52), "", "typed");
      txt.dataset.text = "motion design";
      const caret = div(field, box(420, 35, 6, 70) + `background:${COL.ink};`, null, "caret");
      return { el: caret, a: ph, b: txt };
    } },
    "like-burst": { custom: (c) => ({
      el: div(c.scene, box(440, 860, 200, 200) + ctr + font(170) + `color:${COL.red};z-index:5;`, "♥", "heart"),
      a: sv(c.svg(), "circle", { cx: 540, cy: 960, r: 150, fill: "none", stroke: COL.red, "stroke-width": 30, class: "ring" }),
      items: centered(c, 6, 28, { color: COL.gold }),
    }) },
    "modal-pop": { custom: (c) => ({
      a: div(c.scene, box(0, 0, W, H) + "background:#000;opacity:0;z-index:5;", null, "backdrop"),
      el: div(c.scene, box(140, 660, 800, 600) + ctr + font(64) + `background:${COL.ink};color:${COL.dark};border-radius:40px;z-index:6;`, "Confirmar?", "modal"),
    }) },
    "notification-slide": { custom: (c) => {
      const el = div(c.scene, box(60, 80, 960, 200) + "background:rgba(42,49,61,0.95);border-radius:40px;z-index:6;", null, "banner");
      const items = [
        div(el, box(30, 40, 120, 120) + `background:${COL.green};border-radius:28px;`, null, "icon"),
        div(el, box(180, 40, 740, 56) + font(48), "Novo vídeo", "title"),
        div(el, box(180, 110, 740, 50) + font(36, 400), "Seu render terminou", "text"),
      ];
      return { el, items };
    } },
    "phone-mockup-reveal": { custom: (c) => {
      const phone = div(c.scene, box(290, 460, 500, 1000) + "background:#0b0d11;border:16px solid #2a313d;border-radius:80px;z-index:4;overflow:hidden;", null, "phone");
      return { el: phone, a: div(phone, box(0, 0, 468, 968) + PHOTO, null, "screen") };
    } },
    "scroll-screen": { custom: (c) => {
      const screen = div(c.scene, box(290, 460, 500, 1000) + "background:#0b0d11;border:16px solid #2a313d;border-radius:60px;overflow:hidden;z-index:4;", null, "screen");
      const el = div(screen, box(0, 0, 468, 3400), null, "content");
      for (let i = 0; i < 14; i++) div(el, box(24, 24 + i * 240, 420, 210) + ctr + font(60) + `background:${PALETTE[i % PALETTE.length]};border-radius:24px;color:${COL.dark};`, String(i + 1));
      return { el };
    } },
    "skeleton-shimmer": { custom: (c) => {
      const real = div(c.scene, box(140, 700, 800, 520) + "z-index:3;opacity:0;", null, "real");
      div(real, box(0, 0, 800, 300) + PHOTO + "border-radius:24px;");
      div(real, box(0, 340, 800, 70) + font(56), "Conteúdo carregado");
      const skel = div(c.scene, box(140, 700, 800, 520) + "z-index:4;overflow:hidden;", null, "skeleton");
      div(skel, box(0, 0, 800, 300) + "background:#2a313d;border-radius:24px;");
      div(skel, box(0, 340, 600, 70) + "background:#2a313d;border-radius:16px;");
      const shine = div(skel, box(0, 0, 800, 520) + "background:linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);", null, "shine");
      return { el: shine, a: real, b: skel };
    } },
    "slider-scrub": { custom: (c) => {
      div(c.scene, box(190, 1000, 700, 20) + "background:#2a313d;border-radius:10px;z-index:2;");
      return {
        a: div(c.scene, box(190, 1000, 700, 20) + `background:${COL.cyan};border-radius:10px;z-index:3;`, null, "fill"),
        el: div(c.scene, box(160, 980, 60, 60) + `border-radius:50%;background:${COL.ink};z-index:4;`, null, "knob"),
        b: div(c.scene, box(390, 780, 300, 160) + ctr + font(120) + "z-index:4;", "20", "readout"),
      };
    } },
    "tab-switch": { custom: (c) => {
      div(c.scene, box(180, 520, 720, 120) + "background:#2a313d;border-radius:60px;z-index:2;");
      const pill = div(c.scene, box(180, 520, 360, 120) + `background:${COL.accent};border-radius:60px;z-index:3;`, null, "pill");
      return {
        el: pill,
        a: div(c.scene, box(140, 760, 800, 700) + ctr + font(72) + `background:${COL.blue};border-radius:40px;z-index:3;`, "Aba 1", "panel-old"),
        b: div(c.scene, box(140, 760, 800, 700) + ctr + font(72) + `background:${COL.green};border-radius:40px;z-index:3;opacity:0;`, "Aba 2", "panel-new"),
      };
    } },
    "tap-ripple": { custom: (c) => {
      const btn = div(c.scene, box(240, 880, 600, 160) + ctr + font(60) + `background:${COL.blue};border-radius:80px;overflow:hidden;z-index:3;`, null, "btn");
      return {
        el: div(btn, box(-100, -220, 600, 600) + "border-radius:50%;background:#fff;", null, "ripple"),
        a: div(c.scene, box(470, 890, 140, 140) + "border-radius:50%;background:rgba(255,255,255,0.6);z-index:4;", null, "finger"),
      };
    } },
    "toast": { custom: (c) => {
      const el = div(c.scene, box(240, 1500, 600, 130) + "background:#2a313d;border-radius:65px;z-index:5;" + font(48) + "display:flex;align-items:center;padding-left:130px;", "Salvo", "toast");
      return { el, a: div(el, box(30, 25, 80, 80) + `border-radius:50%;background:${COL.green};`, null, "icon") };
    } },
    "toggle-switch": { custom: (c) => {
      div(c.scene, box(420, 920, 240, 120) + "background:#2a313d;border-radius:60px;z-index:2;");
      return {
        a: div(c.scene, box(420, 920, 240, 120) + `background:${COL.green};border-radius:60px;opacity:0;z-index:3;`, null, "on"),
        el: div(c.scene, box(436, 936, 88, 88) + `background:${COL.ink};border-radius:50%;z-index:4;`, null, "knob"),
      };
    } },
    // loops-ambiente
    "blob-morph": { custom: (c) => ({ el: sv(c.svg(), "path", { d: "M200,60 C280,60 340,140 320,220 C300,300 200,340 130,300 C60,260 60,140 200,60Z", fill: COL.violet, transform: "translate(340 700) scale(1.6)", class: "blob" }) }) },
    "bubble-rise": { custom: (c) => ({ items: Array.from({ length: 6 }, (_, i) => div(c.scene, box(140 + i * 150, 1800, 60, 60)
      + "border:4px solid rgba(243,237,226,0.8);border-radius:50%;z-index:4;", null, "bubble")) }) },
    "gradient-shift": { custom: (c) => ({ el: div(c.scene, box(-W, -H, W * 3, H * 3) + "background:linear-gradient(135deg, #1f6feb, #8957e5 30%, #d0592c 60%, #e3b341);z-index:1;", null, "gradient") }) },
    "light-sheen": { custom: (c) => {
      const el = card(c, "el", "overflow:hidden;");
      return { el, a: div(el, box(0, -40, 120, 320) + "background:rgba(255,255,255,0.6);", null, "sheen") };
    } },
    "marquee": { custom: (c) => marquee(c) },
    "marquee-type": { custom: (c) => marquee(c) },
    "orbit": { custom: (c) => {
      div(c.scene, box(490, 910, 100, 100) + `border-radius:50%;background:${COL.gold};z-index:3;`);
      return { items: [0, 1, 2].map((i) => {
        const arm = div(c.scene, box(540, 960 - 200 - i * 80, 0, 0) + `transform-origin:0px ${200 + i * 80}px;z-index:4;`, null, "arm");
        div(arm, box(-30, -30, 60, 60) + `border-radius:50%;background:${PALETTE[i + 1]};`, null, "satellite");
        return arm;
      }) };
    } },
    "pulse-ring-loop": { items: "rings", n: 2 },
    "sparkle-loop": { custom: (c) => ({ items: [[200, 500], [800, 640], [420, 1100], [760, 1400], [300, 1600]].map(([x, y]) => div(c.scene,
      box(x, y, 80, 80) + `background:${COL.gold};clip-path:polygon(50% 0, 60% 40%, 100% 50%, 60% 60%, 50% 100%, 40% 60%, 0 50%, 40% 40%);z-index:4;`, null, "sparkle")) }) },
    // mascaras-composicao
    "alpha-cutout": { custom: (c) => ({ items: [
      div(c.scene, box(190, 560, 700, 800) + `background:${COL.blue};border-radius:40px;z-index:3;`, null, "frame"),
      div(c.scene, box(290, 460, 500, 900) + `background:linear-gradient(${COL.gold}, ${COL.accent});border-radius:250px 250px 40px 40px;z-index:4;`, null, "cutout"),
    ] }) },
    "collage-stagger": { custom: (c) => ({ items: [[100, 300], [560, 380], [160, 800], [600, 900], [120, 1300], [560, 1360]].map(([x, y], i) => div(c.scene,
      box(x, y, 420, 380) + PHOTO + `border:14px solid ${COL.ink};z-index:${3 + i};`, null, "photo")) }) },
    "frame-in-frame": { custom: (c) => {
      const el = div(c.scene, box(0, 0, W, H) + "z-index:3;", null, "nest");
      for (let i = 0; i < 6; i++) div(el, box(0, 0, W, H) + `border:30px solid ${PALETTE[i]};transform:scale(${Math.pow(0.7, i)});`);
      return { el };
    } },
    "grid-reveal": { custom: (c) => {
      const out = [], cols = 5, rows = 8, cw = 160, ch = 160, x0 = 140, y0 = 320;
      for (let r = 0; r < rows; r++) for (let k = 0; k < cols; k++) out.push(div(c.scene, box(x0 + k * cw, y0 + r * ch, cw, ch)
        + PHOTO + `background-size:${cols * cw}px ${rows * ch}px;background-position:${-k * cw}px ${-r * ch}px;z-index:3;`, null, "tile"));
      return { items: out };
    } },
    "kaleidoscope": { custom: (c) => {
      const el = div(c.scene, box(0, 0, W, H) + "z-index:3;", null, "kaleido");
      const items = Array.from({ length: 8 }, (_, i) => {
        const slice = div(el, box(0, 0, W, H) + `transform:rotate(${i * 45}deg)${i % 2 ? " scaleX(-1)" : ""};clip-path:polygon(50% 50%, 30% 0%, 70% 0%);`, null, "slice");
        return div(slice, box(0, 0, W, H) + PHOTO, null, "img");
      });
      return { el, items };
    } },
    "luma-matte": { custom: (c) => {
      const f = sv(c.defs(), "filter", { id: "luma" });
      const ct = sv(f, "feComponentTransfer");
      const items = ["feFuncR", "feFuncG", "feFuncB"].map((t) => sv(ct, t, { type: "linear", slope: 4, intercept: -1 }));
      const m = sv(c.defs(), "mask", { id: "luma-mask", maskUnits: "userSpaceOnUse", x: 0, y: 0, width: W, height: H });
      const lg = sv(c.defs(), "linearGradient", { id: "luma-grad", x1: 0, y1: 0, x2: 0, y2: 1 });
      sv(lg, "stop", { offset: 0, "stop-color": "#fff" });
      sv(lg, "stop", { offset: 1, "stop-color": "#000" });
      sv(m, "rect", { x: 0, y: 0, width: W, height: H, fill: "url(#luma-grad)", filter: "url(#luma)" });
      const img = KINDS.fullphoto(c, "el");
      img.style.mask = "url(#luma-mask)";
      img.style.webkitMask = "url(#luma-mask)";
      return { items };
    } },
    "mask-wipe-local": { el: "photo" },
    "mirror": { custom: (c) => ({ items: [
      div(c.scene, box(140, 560, 800, 800) + PHOTO + "z-index:3;", null, "orig"),
      div(c.scene, box(140, 560, 800, 800) + PHOTO + "z-index:3;", null, "copy"),
    ] }) },
    "picture-in-picture": { el: "fullphoto" },
    "polaroid-drop": { custom: (c) => {
      const frame = div(c.scene, box(240, 560, 600, 720) + `background:${COL.ink};z-index:3;`, null, "polaroid");
      return { items: [frame, div(frame, box(40, 40, 520, 520) + PHOTO, null, "photo")] };
    } },
    "shape-mask": { el: "fullphoto" },
    "split-screen": { custom: (c) => ({ items: [
      div(c.scene, box(0, 0, W, H / 2) + `background:linear-gradient(160deg, ${COL.blue}, #0b2a5c);z-index:3;`, null, "upper"),
      div(c.scene, box(0, H / 2, W, H / 2) + `background:linear-gradient(200deg, ${COL.accent}, #6b230b);z-index:3;`, null, "lower"),
      div(c.scene, box(0, H / 2 - 6, W, 12) + `background:${COL.ink};z-index:4;`, null, "divider"),
    ] }) },
    "spotlight": { custom: (c) => {
      KINDS.fullphoto(c, "el").style.zIndex = "2";
      return { el: div(c.scene, box(340, 760, 400, 400) + "border-radius:50%;box-shadow:0 0 0 4000px rgba(0,0,0,0.72);z-index:5;", null, "spot") };
    } },
    "sticker-slap": { custom: (c) => ({ items: [
      div(c.scene, box(290, 760, 500, 400) + ctr + font(90) + `background:${COL.gold};color:${COL.dark};border-radius:40px;z-index:4;`, "UAU", "sticker"),
      div(c.scene, box(310, 790, 500, 400) + "background:rgba(0,0,0,0.6);border-radius:40px;filter:blur(14px);z-index:3;", null, "sticker-shadow"),
    ] }) },
    "text-mask": { custom: (c) => {
      const word = div(c.scene, box(40, 760, 1000, 400) + "overflow:hidden;z-index:3;"
        + "-webkit-mask-image:linear-gradient(#000, #000);", null, "word");
      const video = div(word, box(0, -200, 1000, 800) + PHOTO, null, "video");
      return { items: [word, video] };
    } },
    // saidas
    "tuck-out": { custom: (c) => {
      const wrap = div(c.scene, box(140, 760, 800, 200) + "overflow:hidden;z-index:3;", null, "mask");
      return { el: div(wrap, box(0, 0, 800, 200) + ctr + font(110), "TCHAU", "word") };
    } },
    // texto
    "highlight": { custom: (c) => {
      const el = div(c.scene, box(220, 860, 640, 150) + `background:${COL.gold};z-index:2;`, null, "hl");
      div(c.scene, box(90, 840, 900, 200) + ctr + font(110) + "z-index:3;", "destaque", "title");
      return { el };
    } },
    "line-reveal": { items: "lines" },
    "word-reveal": { items: "words" },
    "text-swap": { custom: (c) => {
      const slot = div(c.scene, box(140, 840, 800, 160) + "overflow:hidden;z-index:3;", null, "slot");
      return {
        a: div(slot, box(0, 0, 800, 160) + ctr + font(120), "ideia", "old"),
        b: div(slot, box(0, 0, 800, 160) + ctr + font(120) + `color:${COL.gold};`, "vídeo", "new"),
      };
    } },
    "blur-focus-words": { items: "words" },
    "caption-chunks": { custom: (c) => ({ items: [0, 1, 2, 3].map((i) => {
      const e = div(c.scene, box(90, 1400, 900, 160) + ctr + font(80) + "opacity:0;z-index:4;", ["a voz", "marca", "o tempo", "de cada cena"][i], "chunk");
      e.dataset.start = String(T0 + i * 0.6);
      e.dataset.end = String(T0 + i * 0.6 + 0.55);
      return e;
    }) }) },
    "caption-pop": { custom: (c) => ({ items: [0, 1, 2].map((i) => {
      const chunk = div(c.scene, box(90, 1400, 900, 160) + ctr + "gap:28px;opacity:0;z-index:4;", null, "chunk");
      const c0 = T0 + i * 0.8;
      chunk.dataset.start = String(c0);
      chunk.dataset.end = String(c0 + 0.75);
      [["a", "voz"], ["marca", "o"], ["tempo", "certo"]][i].forEach((w, k) => {
        const ws = span(chunk, "display:inline-block;position:relative;" + font(90), w, "w");
        ws.dataset.start = String(c0 + k * 0.35);
        ws.dataset.end = String(c0 + k * 0.35 + 0.35);
        span(ws, `position:absolute;left:0;top:0;color:${COL.gold};opacity:0;`, w, "hot");
      });
      return chunk;
    }) }) },
    "chat-bubble-typing": { custom: (c) => {
      const typing = div(c.scene, box(80, 900, 240, 120) + ctr + "gap:18px;background:#2a313d;border-radius:44px;z-index:3;", null, "typing");
      const dots = [0, 1, 2].map(() => span(typing, `display:inline-block;width:26px;height:26px;border-radius:50%;background:${COL.ink};`, null, "dot"));
      return { a: typing, items: dots, b: div(c.scene, box(80, 900, 640, 120) + ctr + font(52) + "background:#2a313d;border-radius:44px;z-index:3;", "Chegou a resposta", "msg") };
    } },
    "circle-word": { custom: (c) => { KINDS.text(c, "el"); return { el: KINDS.ellipse(c, "el") }; } },
    "glitch-text": { custom: (c) => {
      const el = KINDS.text(c, "el");
      const cp = (col) => div(c.scene, box(90, 840, 900, 200) + ctr + font(110) + `color:${col};mix-blend-mode:screen;opacity:0;z-index:4;`, "MOVIMENTO", "glitch-copy");
      return { el, a: cp("#ff2840"), b: cp("#28c8ff") };
    } },
    "handwriting": { custom: (c) => ({ items: [
      "M160 1000 C 200 860, 260 860, 260 1000 C 260 1080, 200 1080, 200 1000",
      "M300 1000 C 320 900, 380 900, 380 1000 L 380 1060",
      "M440 900 L 440 1060 M 440 980 C 500 940, 560 960, 560 1060",
      "M620 1000 C 660 900, 760 920, 720 1000 C 690 1060, 780 1080, 900 960",
    ].map((d) => sv(c.svg(), "path", { d, fill: "none", stroke: COL.ink, "stroke-width": 14, "stroke-linecap": "round", class: "stroke" })) }) },
    "highlight-follow": { custom: (c) => {
      const row = div(c.scene, box(90, 860, 900, 160) + "z-index:3;", null, "row");
      const el = div(row, box(0, 10, 100, 140) + `background:${COL.accent};border-radius:16px;`, null, "hl-box");
      const items = ["voz", "cena", "efeito"].map((w, i) => span(row, `position:absolute;left:${40 + i * 300}px;top:20px;` + font(96), w, "w"));
      return { el, items };
    } },
    "ink-bleed": { custom: (c) => {
      const wrap = div(c.scene, box(40, 740, 1000, 400) + `background:${COL.ink};filter:contrast(18);z-index:3;`, null, "ink-wrap");
      return { el: div(wrap, box(0, 100, 1000, 200) + ctr + font(130) + `color:${COL.dark};`, "TINTA", "word") };
    } },
    "karaoke": { custom: (c) => ({ items: words(c, {}).map((w) => {
      span(w, `position:absolute;left:0;top:0;color:${COL.gold};clip-path:inset(0% 100% 0% 0%);`, w.textContent, "fill");
      return w;
    }) }) },
    "keyword-color-swap": { custom: (c) => ({
      a: div(c.scene, box(90, 840, 900, 200) + ctr + font(110) + "z-index:3;", "palavra", "word"),
      el: div(c.scene, box(90, 840, 900, 200) + ctr + font(110) + `color:${COL.gold};opacity:0;z-index:4;`, "palavra", "word-accent"),
    }) },
    "kinetic-stack": { custom: (c) => {
      const el = div(c.scene, box(90, 700, 900, 1000) + "z-index:3;", null, "column");
      const items = ["CADA", "LINHA", "EMPURRA", "A COLUNA"].map((t, i) => div(el, box(0, i * 110, 900, 110) + ctr + font([90, 120, 80, 100][i]), t, "line"));
      return { el, items };
    } },
    "letter-cascade": { custom: (c) => ({ items: letters(c, {}, "CASCATA", { mask: true }) }) },
    "lower-third": { custom: (c) => ({
      el: div(c.scene, box(60, 1440, 760, 200) + `background:${COL.accent};z-index:3;`, null, "lt-bar"),
      a: div(c.scene, box(100, 1460, 700, 90) + font(68) + "display:flex;align-items:center;z-index:4;", "Silvio Campos", "lt-name"),
      b: div(c.scene, box(100, 1560, 700, 60) + font(44, 400) + "display:flex;align-items:center;z-index:4;", "motion designer", "lt-role"),
    }) },
    "marker-scribble": { custom: (c) => ({
      a: div(c.scene, box(90, 840, 900, 200) + ctr + font(110) + "z-index:3;", "errado", "word"),
      el: sv(c.svg(), "path", { d: "M260 900 L 360 1000 L 420 880 L 520 1010 L 580 880 L 680 1010 L 740 880 L 820 990", fill: "none", stroke: COL.red, "stroke-width": 18, "stroke-linecap": "round", class: "scribble" }),
    }) },
    "matrix-rain-text": { custom: (c) => ({ items: letters(c, {}, "CODIGO") }) },
    "mirror-text": { custom: (c) => ({
      a: div(c.scene, box(90, 760, 900, 200) + ctr + font(120) + "z-index:3;", "REFLEXO", "word"),
      b: div(c.scene, box(90, 960, 900, 200) + ctr + font(120) + "-webkit-mask-image:linear-gradient(transparent, #000);opacity:0.35;z-index:3;transform:scaleY(-1);", "REFLEXO", "mirror"),
    }) },
    "one-word-flash": { custom: (c) => ({ items: stacked(c, ["UMA", "PALAVRA", "POR", "VEZ"]) }) },
    "outline-to-fill": { custom: (c) => ({ items: [
      "M180 1100 L 180 820 L 330 820 L 330 1100 Z", "M380 1100 L 460 820 L 540 1100 Z",
      "M590 1100 L 590 820 L 700 1000 L 700 820", "M760 820 C 960 820, 960 1100, 760 1100 Z",
    ].map((d) => sv(c.svg(), "path", { d, fill: COL.gold, stroke: COL.gold, "stroke-width": 8, "fill-opacity": 0, class: "glyph" })) }) },
    "quote-reveal": { custom: (c) => ({
      a: div(c.scene, box(90, 440, 300, 260) + font(320) + `color:${COL.accent};z-index:3;`, "“", "quote-mark"),
      items: maskedLines(c, ["Não peça um vídeo", "bonito: peça", "o efeito certo."], 720, 84),
      b: div(c.scene, box(90, 1180, 900, 80) + font(48, 400) + "z-index:3;", "Matheus", "author"),
    }) },
    "ransom-note": { custom: (c) => ({ items: letters(c, {}, "RECADO", { size: 110, style: `padding:8px 14px;margin:0 6px;background:${COL.ink};color:${COL.dark};` }) }) },
    "reaction-word": { custom: (c) => ({ el: div(c.scene, box(240, 820, 600, 260) + ctr + font(120) + `background:${COL.gold};color:${COL.dark};border-radius:40px;z-index:4;`, "UAU!", "reaction") }) },
    "redaction-reveal": { custom: (c) => {
      const ws = words(c, {});
      return { items: ws.map((w) => { const bar = span(w, "position:absolute;left:-6px;top:-4px;right:-6px;bottom:-4px;background:#000;", null, "redact"); return bar; }) };
    } },
    "rolling-letters": { custom: (c) => {
      const AB = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", word = "ROLA";
      return { items: [...word].map((ch, i) => {
        const win = div(c.scene, box(240 + i * 160, 860, 140, 180) + "overflow:hidden;z-index:3;", null, "reel-window");
        const reel = div(win, box(0, 0, 140, 180 * AB.length), null, "reel");
        for (const L of AB) div(reel, "width:140px;height:180px;" + ctr + font(140), L);
        reel.dataset.index = String(AB.indexOf(ch));
        reel.dataset.rows = String(AB.length);
        return reel;
      }) };
    } },
    "rotating-words": { custom: (c) => ({ items: stacked(c, ["RÁPIDO", "SIMPLES", "BONITO"]) }) },
    "split-flap": { custom: (c) => ({ items: letters(c, {}, "PARTIDA", { style: `background:#2a313d;margin:0 6px;padding:10px 12px;` }) }) },
    "split-halves": { custom: (c) => ({
      a: div(c.scene, box(90, 840, 900, 200) + ctr + font(140) + "clip-path:inset(0 0 50% 0);z-index:3;", "CORTE", "half-top"),
      b: div(c.scene, box(90, 840, 900, 200) + ctr + font(140) + "clip-path:inset(50% 0 0 0);z-index:3;", "CORTE", "half-bottom"),
    }) },
    "spotlight-word": { custom: (c) => {
      div(c.scene, box(90, 840, 900, 200) + ctr + font(110) + "color:#3a404a;z-index:3;", "ILUMINA", "dim");
      return { el: div(c.scene, box(90, 840, 900, 200) + ctr + font(110) + `color:${COL.gold};z-index:4;`, "ILUMINA", "lit") };
    } },
    "stencil-cut": { custom: (c) => {
      KINDS.fullphoto(c, "el").style.zIndex = "1";
      const panel = sv(c.svg(), "svg", { x: 0, y: 0, width: W, height: H, class: "stencil" });
      const m = sv(panel, "mask", { id: "stencil-m" });
      sv(m, "rect", { x: 0, y: 0, width: W, height: H, fill: "#fff" });
      sv(m, "text", { x: 540, y: 1010, "text-anchor": "middle", "font-size": 220, "font-weight": 700, "font-family": "DejaVu Sans", fill: "#000" }).textContent = "VAZA";
      sv(panel, "rect", { x: 0, y: 0, width: W, height: H, fill: COL.dark, mask: "url(#stencil-m)" });
      return { el: panel };
    } },
    "strike-through": { custom: (c) => ({
      a: div(c.scene, box(90, 760, 900, 200) + ctr + font(110) + "z-index:3;", "caro", "word"),
      el: div(c.scene, box(330, 852, 420, 16) + `background:${COL.red};z-index:4;`, null, "strike"),
      b: div(c.scene, box(90, 1000, 900, 200) + ctr + font(110) + `color:${COL.gold};z-index:3;`, "barato", "fix"),
    }) },
    "text-echo": { custom: (c) => ({ el: KINDS.text(c, "el"), items: Array.from({ length: 4 }, () => div(c.scene, box(90, 840, 900, 200) + ctr + font(110)
      + `color:transparent;-webkit-text-stroke:2px ${COL.gold};z-index:2;`, "MOVIMENTO", "echo")) }) },
    "text-mask-fill": { custom: (c) => {
      div(c.scene, box(90, 840, 900, 200) + ctr + font(130) + `color:transparent;-webkit-text-stroke:3px ${COL.ink};z-index:3;`, "ENCHE", "outline");
      return { el: div(c.scene, box(90, 840, 900, 200) + ctr + font(130) + `color:${COL.gold};z-index:4;`, "ENCHE", "filled") };
    } },
    "text-on-path": { custom: (c) => {
      sv(c.defs(), "path", { id: "curva", d: "M80 1100 C 300 700, 780 700, 1000 1100" });
      const tx = sv(c.svg(), "text", { "font-size": 90, "font-weight": 700, "font-family": "DejaVu Sans", fill: COL.ink });
      const tp = sv(tx, "textPath", { href: "#curva", startOffset: "0%" });
      tp.textContent = "texto que anda na curva";
      return { el: tp };
    } },
    "text-shine": { custom: (c) => ({ el: div(c.scene, box(90, 840, 900, 200) + ctr + font(130)
      + "background:linear-gradient(100deg, #8a8f99 40%, #ffffff 50%, #8a8f99 60%);background-size:200% 100%;"
      + "background-position:var(--shine) 50%;-webkit-background-clip:text;background-clip:text;color:transparent;z-index:3;", "BRILHO", "shine-text") }) },
    "title-card": { custom: (c) => ({
      el: div(c.scene, box(90, 800, 900, 220) + `background:${COL.accent};z-index:4;`, null, "band"),
      a: div(c.scene, box(90, 800, 900, 220) + ctr + font(120) + "z-index:3;", "CAPÍTULO 1", "title"),
      b: div(c.scene, box(90, 1050, 900, 90) + ctr + font(56, 400) + "z-index:3;", "o começo", "subtitle"),
    }) },
    "underline-draw": { custom: (c) => {
      KINDS.text(c, "el");
      return { el: sv(c.svg(), "path", { d: "M200 1060 C 400 1040, 640 1080, 880 1040", fill: "none", stroke: COL.accent, "stroke-width": 16, "stroke-linecap": "round", class: "underline" }) };
    } },
    "vertical-ticker": { custom: (c) => {
      const win = div(c.scene, box(90, 820, 900, 140) + "overflow:hidden;z-index:3;", null, "ticker-window");
      const el = div(win, box(0, 0, 900, 140 * 4), null, "ticker");
      const items = ["vídeo", "carrossel", "reels", "story"].map((t, i) => div(el, box(0, i * 140, 900, 140) + ctr + font(110), t, "row"));
      return { el, items };
    } },
    "weight-morph": { custom: (c) => ({ el: div(c.scene, box(90, 840, 900, 200) + ctr + `font:120px/1 ${FONT};font-variation-settings:"wght" var(--wght);z-index:3;`, "PESO", "var-font") }) },
    "word-zoom-through": { b: "layer" },
    "feather-in": { custom: (c) => ({ el: card(c, "el", "-webkit-mask-image:linear-gradient(90deg, #000 var(--p), transparent calc(var(--p) + 20%));"
      + "mask-image:linear-gradient(90deg, #000 var(--p), transparent calc(var(--p) + 20%));") }) },
    // transicoes
    "blinds": { items: "strips", n: 8 },
    "grid-tiles": { items: "cells", rows: 7, cols: 4 },
    "slice": { custom: (c) => ({ items: Array.from({ length: 6 }, (_, i) => {
      const e = KINDS.layer(c, "a");
      e.className = "slice";
      e.style.zIndex = "5";
      e.style.clipPath = `inset(${i * 16.666}% 0% ${100 - (i + 1) * 16.666}% 0%)`;
      return e;
    }) }) },
    "staggered-blocks": { items: "blocks", n: 3 },
    "luma-fade": { bStyle: "-webkit-mask-image:linear-gradient(to bottom, #000 calc(var(--p) * 1% - 20%), transparent calc(var(--p) * 1%));"
      + "mask-image:linear-gradient(to bottom, #000 calc(var(--p) * 1% - 20%), transparent calc(var(--p) * 1%));" },
    "shape-reveal": { bStyle: "-webkit-mask-image:url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='50'/%3E%3C/svg%3E\");"
      + "-webkit-mask-repeat:no-repeat;-webkit-mask-position:center;-webkit-mask-size:var(--m);"
      + "mask-image:url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='50'/%3E%3C/svg%3E\");"
      + "mask-repeat:no-repeat;mask-position:center;mask-size:var(--m);" },
    "flip-3d": { abStyle: "backface-visibility:hidden;", rootStyle: "perspective:1200px;" },
    "j-cut": { el: "caption" },
  };

  KINDS.caption = (c) => div(c.scene, box(90, 1500, 900, 140) + ctr + font(64) + "background:rgba(0,0,0,0.6);border-radius:24px;z-index:20;opacity:0;", "a fala de B já começou", "caption");

  // cena maior que o quadro (pan, tilt): a câmera anda pelo mundo inteiro
  function wideWorld(c, w, h) {
    c.scene.style.width = w + "px";
    c.scene.style.height = h + "px";
    for (let x = 0; x < w; x += 600) for (let y = 300; y < h; y += 700) {
      const i = (x / 600 + y / 700) | 0;
      div(c.scene, box(x + 120, y, 360, 360) + ctr + font(140) + `background:${PALETTE[i % PALETTE.length]};color:${COL.dark};border-radius:40px;z-index:3;`, String(i + 1), "deco");
    }
    return {};
  }

  function marquee(c) {
    const el = div(c.scene, box(0, 860, W * 4, 200) + "display:flex;z-index:3;", null, "marquee");
    for (let k = 0; k < 2; k++) div(el, `width:${W * 2}px;height:200px;` + font(130) + "display:flex;align-items:center;white-space:nowrap;", "SIGA O FLUXO • SIGA O FLUXO • ");
    return { el };
  }

  // ---------------------------------------------------------------- code inspection

  const stripCode = (code) => code
    .replace(/\/\/[^\n]*/g, "")
    .replace(/`(?:[^`\\]|\\.)*`|"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'/g, '""');

  function selectorsIn(code) {
    const out = new Set();
    for (const m of code.matchAll(/querySelector(?:All)?\(\s*(["'])(.+?)\1/g)) out.add(m[2].trim().split(/\s+/)[0]);
    for (const m of code.matchAll(/["'](#[A-Za-z][\w-]*)["']/g)) out.add(m[1]);
    return [...out];
  }

  // ---------------------------------------------------------------- build

  let current = null;

  function build(effect) {
    const root = document.getElementById("root");
    root.innerHTML = "";
    root.style.cssText = "";
    const code = effect.gsap, bare = stripCode(code);
    // nome do escopo usado pelo trecho (e não só um parâmetro de arrow ou variável com o mesmo nome)
    const shadowed = (name) => new RegExp(`\\(([^()]*\\b${name}\\b[^()]*)\\)\\s*=>|\\b(?:let|const|var)\\s+${name}\\b`).test(bare);
    const uses = (name) => new RegExp(`\\b${name}\\b`).test(bare) && !shadowed(name);
    const sp = Object.assign({ el: "card", items: "boxes", n: 8, a: "card", b: "card" }, FAMILY[effect.familia] || {}, S[effect.id] || {});
    const used = { el: uses("el"), items: uses("items"), a: uses("a"), b: uses("b"), scene: uses("scene") };
    const scene = div(root, "", null, "scene");
    if (sp.preserve3d) scene.style.transformStyle = "preserve-3d";
    if (sp.rootStyle) root.style.cssText = sp.rootStyle;
    div(scene, "", null, "backdrop");
    const c = { effect, scene, sp, refs: {} };
    c.svg = () => c._svg || (c._svg = svgLayer(scene));
    c.defs = () => c._defs || (c._defs = sv(c.svg(), "defs"));

    let refs = sp.custom ? sp.custom(c) || {} : {};
    const aOnTop = /A acima de B/.test(code);
    const bHidden = sp.bHidden ?? /\bset\(\s*b\s*,\s*\{[^}]*\bopacity:\s*1\b/.test(bare);
    const wantsAB = used.a || used.b || /["']\.track["']/.test(code);
    for (const role of ["a", "b", "el"]) {
      if (refs[role] || !(used[role] || (wantsAB && (sp.always || []).includes(role)))) continue;
      refs[role] = KINDS[sp[role]](c, role);
    }
    if (!refs.items && used.items) {
      refs.items = sp.gridOpts ? grid(c, sp, sp.n, sp.gridOpts) : ITEMS[sp.items](c, sp);
    }
    if (sp.a === "layer" && refs.a && refs.a.classList.contains("layer")) {
      if (aOnTop) refs.a.style.zIndex = "3";
      if (sp.abStyle) refs.a.style.cssText += sp.abStyle;
    }
    if (sp.b === "layer" && refs.b && refs.b.classList.contains("layer")) {
      if (bHidden) refs.b.style.opacity = "0";
      if (sp.bStyle) refs.b.style.cssText += sp.bStyle;
      if (sp.abStyle) refs.b.style.cssText += sp.abStyle;
    }
    if (refs.el instanceof HTMLElement) {
      refs.el.dataset.text = refs.el.dataset.text || "Do texto ao MP4";
      refs.el.dataset.char = refs.el.dataset.char || "A";
    }
    c.refs = refs;
    for (const sel of sp.noHelpers ? [] : selectorsIn(code)) {
      if (!HELPERS[sel]) continue;
      HELPERS[sel](c);
    }
    // cena só com a câmera: dá conteúdo para o movimento aparecer
    if (!used.el && !used.items && !used.a && !used.b && effect.familia !== "transicoes" && !sp.custom) {
      div(scene, box(90, 700, 900, 300) + ctr + font(150) + "z-index:3;", "CENA", "deco");
      [[160, 300, COL.gold], [780, 1300, COL.cyan], [300, 1500, COL.accent]].forEach(([x, y, col]) =>
        div(scene, box(x, y, 160, 160) + `border-radius:50%;background:${col};z-index:3;`, null, "deco"));
    }
    for (const [role, e] of Object.entries(refs)) {
      if (Array.isArray(e)) e.forEach((x, i) => x && x.setAttribute && x.setAttribute("data-role", `${role}[${i}]`));
      else if (e && e.setAttribute) e.setAttribute("data-role", role);
    }

    // escopo do trecho
    const usedGlobals = [];
    const lazy = {};
    for (const g of GLOBALS) {
      Object.defineProperty(window, g, {
        configurable: true,
        get() {
          if (!usedGlobals.includes(g)) usedGlobals.push(g);
          if (!(g in lazy)) lazy[g] = g === "path" || g === "paths" ? KINDS.path(c, "el") : g === "words" ? [] : card(c, "el");
          return g === "paths" ? [lazy[g]] : lazy[g];
        },
      });
    }
    const tl = gsap.timeline({ paused: true });
    current = { tl };
    const fn = new Function("tl", "t", "el", "items", "a", "b", "scene", "gsap", `"use strict";\n${code}`);
    fn(tl, T0, refs.el || null, refs.items || [], refs.a || null, refs.b || null, scene, gsap);
    return { tl, c, refs, used, usedGlobals, aOnTop, bHidden, root };
  }

  function teardown() {
    if (current && current.tl) current.tl.kill();
    for (const g of GLOBALS) delete window[g];
    current = null;
  }

  // ---------------------------------------------------------------- state

  const PROPS = ["opacity", "transform", "filter", "clipPath", "visibility", "display", "strokeDashoffset", "strokeDasharray",
    "fillOpacity", "strokeOpacity", "strokeWidth", "maskImage", "maskSize", "webkitMaskSize", "backgroundPosition",
    "backgroundColor", "borderRadius", "fontVariationSettings"];
  const IDENT = new Set(["matrix(1, 0, 0, 1, 0, 0)", "matrix3d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)"]);
  const round = (s) => String(s).replace(/-?\d*\.?\d+(?:e-?\d+)?/g, (m) => {
    const v = Math.round(parseFloat(m) * 100) / 100;
    return Object.is(v, -0) ? "0" : String(v);
  });

  // filtro que não muda nada (blur 0, brilho 1, sombra transparente) conta como "none"
  const FILTER_IDENT = /^(blur\(0px\)|brightness\(1\)|contrast\(1\)|saturate\(1\)|grayscale\(0\)|sepia\(0\)|invert\(0\)|opacity\(1\)|hue-rotate\(0deg\)|drop-shadow\(rgba\([^)]*, 0\)[^)]*\))$/;
  function normFilter(v) {
    if (!v || v === "none") return "none";
    const fns = v.match(/[a-z-]+\((?:[^()]|\([^()]*\))*\)|url\([^)]*\)/g) || [v];
    const keep = fns.filter((f) => !FILTER_IDENT.test(f));
    return keep.length ? keep.join(" ") : "none";
  }

  function describe(e) {
    if (!e) return "?";
    const role = e.getAttribute && e.getAttribute("data-role");
    const cls = typeof e.className === "string" ? e.className : (e.className && e.className.baseVal) || "";
    return (role ? role + " " : "") + "<" + e.tagName.toLowerCase() + (cls ? "." + cls.trim().split(/\s+/).join(".") : "") + ">";
  }

  function snapshot(root) {
    const out = [];
    for (const e of root.querySelectorAll("*")) {
      const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
      const parts = [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)];
      for (const p of PROPS) {
        let v = cs[p];
        if (p === "transform" && IDENT.has(v)) v = "none";
        if (p === "filter") v = normFilter(v);
        parts.push(v);
      }
      if (e instanceof SVGElement) {
        for (const n of e.getAttributeNames()) {
          if (n === "style" || n === "class" || n.startsWith("data-")) continue;  // data-*: cache dos plugins
          // forma do path, não o texto do d: o MorphSVG reescreve o mesmo desenho em cúbicas
          if (n === "d" && e.getBBox) {
            const bb = e.getBBox();
            parts.push(`d~${Math.round(bb.x)},${Math.round(bb.y)},${Math.round(bb.width)},${Math.round(bb.height)},${Math.round(e.getTotalLength())}`);
          } else if (n === "transform" && /^matrix\(1[ ,]+0[ ,]+0[ ,]+1[ ,]+0[ ,]+0\)$/.test(e.getAttribute(n).trim())) {
            continue;  // identidade escrita pelo GSAP ao voltar: igual a não ter transform
          } else parts.push(n + "=" + e.getAttribute(n));
        }
      }
      let txt = "";
      for (const ch of e.childNodes) if (ch.nodeType === 3) txt += ch.data;
      if (txt) parts.push("T:" + txt);
      for (let i = 0; i < e.style.length; i++) {
        const n = e.style[i];
        if (n.startsWith("--")) parts.push(n + ":" + e.style.getPropertyValue(n).trim());
      }
      out.push({ e, key: round(parts.join("|")) });
    }
    return out;
  }

  function diffSnap(s1, s2) {
    if (s1.length !== s2.length) return `número de elementos mudou (${s1.length} vs ${s2.length})`;
    for (let i = 0; i < s1.length; i++) {
      if (s1[i].key === s2[i].key) continue;
      const p1 = s1[i].key.split("|"), p2 = s2[i].key.split("|");
      let k = p1.findIndex((v, j) => v !== p2[j]);
      if (k < 0) k = p1.length;
      const name = k < 4 ? "posição" : k < 4 + PROPS.length ? PROPS[k - 4] : "atributo/texto";
      return `${describe(s1[i].e)} ${name}: ${(p1[k] || "").slice(0, 80)} vs ${(p2[k] || "").slice(0, 80)}`;
    }
    return null;
  }

  // Área visível (px) depois de recortes: quadro, overflow dos ancestrais e clip-path
  // (inset, circle e polygon), medida por amostragem numa grade sobre o retângulo do elemento.
  function parseLen(v, ref) {
    if (v.endsWith("%")) return parseFloat(v) / 100 * ref;
    return parseFloat(v) || 0;
  }
  function clipTest(cp, r) {
    let m = cp.match(/^inset\(([^)]*)\)/);
    if (m) {
      const v = m[1].split(/\s+round\s+/)[0].trim().split(/\s+/);
      const [t, rt, b, l] = [v[0], v[1] ?? v[0], v[2] ?? v[0], v[3] ?? v[1] ?? v[0]];
      const x0 = r.left + parseLen(l, r.width), y0 = r.top + parseLen(t, r.height);
      const x1 = r.right - parseLen(rt, r.width), y1 = r.bottom - parseLen(b, r.height);
      return (x, y) => x >= x0 && x <= x1 && y >= y0 && y <= y1;
    }
    m = cp.match(/^circle\(([^)]*)\)/);
    if (m) {
      const [rad, at] = m[1].split(/\s+at\s+/);
      const ref = Math.hypot(r.width, r.height) / Math.SQRT2;
      const R = /side/.test(rad) ? ref : parseLen(rad.trim(), ref);
      const [cx, cy] = (at || "50% 50%").trim().split(/\s+/);
      const X = r.left + parseLen(cx, r.width), Y = r.top + parseLen(cy || "50%", r.height);
      return (x, y) => (x - X) ** 2 + (y - Y) ** 2 <= R * R;
    }
    m = cp.match(/^polygon\(([^)]*)\)/);
    if (m) {
      const pts = m[1].split(",").map((q) => q.trim().split(/\s+/)).filter((q) => q.length === 2)
        .map(([x, y]) => [r.left + parseLen(x, r.width), r.top + parseLen(y, r.height)]);
      return (x, y) => {
        let inside = false;
        for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
          const [xi, yi] = pts[i], [xj, yj] = pts[j];
          if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
        }
        return inside;
      };
    }
    return null;
  }
  function vis(e, root) {
    const fr = root.getBoundingClientRect(), r = e.getBoundingClientRect();
    const tests = [(x, y) => x >= fr.left && x <= fr.right && y >= fr.top && y <= fr.bottom];
    let op = 1, masked = false;
    for (let n = e; n instanceof Element; n = n.parentNode) {
      const cs = getComputedStyle(n);
      op *= parseFloat(cs.opacity);
      if ((cs.maskImage && cs.maskImage !== "none") || (cs.webkitMaskImage && cs.webkitMaskImage !== "none")) masked = true;
      if (cs.visibility === "hidden" || cs.display === "none") op = 0;
      const nr = n.getBoundingClientRect();
      if (cs.clipPath && cs.clipPath !== "none") { const ct = clipTest(cs.clipPath, nr); if (ct) tests.push(ct); }
      if (n !== e && cs.overflow !== "visible") tests.push((x, y) => x >= nr.left && x <= nr.right && y >= nr.top && y <= nr.bottom);
      if (n === root) break;
    }
    const own = r.width * r.height, N = 24;
    let hit = 0;
    if (own >= 1) {
      for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
        const x = r.left + (i + 0.5) * r.width / N, y = r.top + (j + 0.5) * r.height / N;
        if (tests.every((f) => f(x, y))) hit++;
      }
    }
    const area = own * hit / (N * N);
    return { op, area, own, masked, cover: area / (fr.width * fr.height) };
  }

  function domTargets(tl) {
    const set = new Set();
    for (const tw of tl.getChildren(true, true, false)) {
      const ts = typeof tw.targets === "function" ? tw.targets() : null;
      for (const x of ts || []) if (x instanceof Element) set.add(x);
    }
    return [...set];
  }

  const pct = (v) => Math.round(v * 100) + "%";

  // ---------------------------------------------------------------- run one effect

  // Instantes conferidos: 0, quatro pontos depois de t e o fim. Os do meio levam um deslocamento
  // pequeno (EPS) para não cair em cima do início exato de um tween: um tl.set exatamente no
  // instante do seek depende da direção de chegada, por definição do GSAP.
  const EPS = 0.0071;
  const r3 = (x) => Math.round(x * 1000) / 1000;
  function sampleTimes(D) {
    const span = Math.max(D - T0, 0);
    const ts = [0, ...[0, 0.25, 0.5, 0.75].map((f) => Math.min(T0 + span * f + EPS, D)), D];
    return [...new Set(ts.map(r3))].sort((p, q) => p - q);
  }
  // Varredura densa só para saber se algo muda (pisca-pisca curto escapa dos pontos acima).
  function denseTimes(D) {
    const n = 48;
    return Array.from({ length: n + 1 }, (_, i) => r3(Math.min(D, (D * i) / n + (i && i < n ? EPS : 0))));
  }

  function runEffect(effect) {
    const res = { id: effect.id, familia: effect.familia, origem: effect.origem, errors: [], warnings: [], notes: [], duration: null };
    const capture = (kind) => (...args) => {  // não devolve nada: o GSAP usa o retorno de console.warn
      res.warnings.push(`console.${kind}: ` + args.map((x) => (x instanceof Element ? describe(x) : String(x))).join(" "));
    };
    const orig = { warn: console.warn, error: console.error };
    console.warn = capture("warn");
    console.error = capture("error");
    try {
      let b1;
      try {
        b1 = build(effect);
        current = b1;
      } catch (err) {
        res.errors.push("exceção ao montar a timeline: " + (err && err.message ? err.message : String(err)));
        return res;
      }
      if (b1.usedGlobals.length) res.notes.push("usa nome não declarado no trecho: " + b1.usedGlobals.join(", "));
      const tl = b1.tl, root = b1.root, D = tl.duration();
      res.duration = Math.round(D * 1000) / 1000;
      if (!(D > T0 + 1e-6) && effect.padrao.duracao_s !== 0) res.errors.push(`timeline não passa de t (duração ${res.duration} s)`);
      // loop do tamanho da cena: com const sceneDur no trecho, nada passa de t + sceneDur
      const sd = effect.gsap.match(/\bsceneDur\s*=\s*(\d+(?:\.\d+)?)/);
      if (sd && D > T0 + parseFloat(sd[1]) + 0.05) res.errors.push(`passa do fim da cena: termina em ${r3(D - T0)} s depois de t, a cena tem ${sd[1]} s`);
      const times = sampleTimes(D), mid = times[Math.floor(times.length / 2)];
      const seekErr = (time) => {
        try { tl.totalTime(time, false); return true; } catch (err) {
          res.errors.push(`exceção no seek ${time}s: ${err && err.message ? err.message : err}`);
          return false;
        }
      };
      // estado inicial (o que a montagem renderiza) e passadas para frente e para trás
      const canon = new Map();
      canon.set(0, snapshot(root));
      const check = (time, from) => {
        if (!seekErr(time)) return false;
        const s = snapshot(root), ref = canon.get(time);
        if (!ref) { canon.set(time, s); return true; }
        const d = diffSnap(ref, s);
        if (d) { res.errors.push(`não determinístico em ${time}s (vindo de ${from}): ${d}`); return false; }
        return true;
      };
      let ok = true, prev = "montagem";
      const dense = [...new Set([...denseTimes(D), ...times])].sort((p, q) => p - q);
      const seq1 = [...dense, ...times.slice().reverse(), mid, D, 0];
      for (const time of seq1) { if (!ok) break; ok = check(time, prev + "s"); prev = String(time); }
      // fim: estado final para os checks de família
      let endInfo = null, startInfo = null;
      if (ok) {
        seekErr(0);
        startInfo = familyState(b1, effect);
        seekErr(D);
        endInfo = familyState(b1, effect);
      }
      // nada muda?
      if (ok) {
        const keys = new Set(dense.map((time) => canon.get(time).map((x) => x.key).join("\n")));
        if (keys.size < 2) res.errors.push("nada muda entre o início e o fim");
      }
      if (ok && startInfo && endInfo) familyChecks(effect, b1, startInfo, endInfo, res);
      // build novo que pula direto para o fim (worker de render começando no meio)
      if (ok) {
        teardown();
        let b2;
        try { b2 = build(effect); current = b2; } catch (err) { res.errors.push("exceção no segundo build: " + err.message); return res; }
        const seq2 = [D, mid, 0, ...times.slice(1).reverse().filter((_, i) => i % 2 === 0), ...times];
        let p2 = "montagem nova";
        for (const time of seq2) {
          try { b2.tl.totalTime(time, false); } catch (err) { res.errors.push(`exceção no seek ${time}s (build novo): ${err.message}`); break; }
          const d = diffSnap(canon.get(time), snapshot(b2.root));
          if (d) { res.errors.push(`não determinístico em ${time}s (build novo, vindo de ${p2}): ${d}`); break; }
          p2 = time + "s";
        }
      }
    } finally {
      teardown();
      console.warn = orig.warn;
      console.error = orig.error;
    }
    if (res.warnings.length) res.errors.push(...[...new Set(res.warnings)].map((w) => "aviso: " + w));
    return res;
  }

  function familyState(b, effect) {
    const { refs, used, root, tl } = b;
    const pick = [];
    if (used.el && refs.el) pick.push(refs.el);
    if (used.items && refs.items) pick.push(...refs.items.filter((x) => x instanceof Element));
    const main = pick.length ? pick : [b.c.scene];
    const st = { main: main.map((e) => ({ e, v: vis(e, root) })) };
    if (refs.a && refs.a instanceof Element) st.a = vis(refs.a, root);
    if (refs.b && refs.b instanceof Element) st.b = vis(refs.b, root);
    const skip = new Set([refs.a, refs.b, b.c.scene, root].filter(Boolean));
    st.overlays = domTargets(tl).filter((e) => !skip.has(e) && !(refs.b && (e.contains(refs.b) || refs.b.contains(e))) && !(refs.a && refs.a.contains(e)))
      .map((e) => ({ e, v: vis(e, root) }));
    return st;
  }

  // Camadas extras (faixas, flash, blocos) que somadas cobrem 25% ou mais do quadro.
  function covering(overlays) {
    const on = overlays.filter(({ v }) => v.op >= 0.05 && v.cover > 0.002);
    const total = on.reduce((acc, { v }) => acc + v.cover * Math.min(v.op, 1), 0);
    if (total < 0.25) return null;
    const names = [...new Set(on.map(({ e }) => describe(e).replace(/\[\d+\]/, "[]")))].slice(0, 3).join(", ");
    return `${names} (${pct(Math.min(total, 1))})`;
  }

  // entradas de ritmo (ease): movem algo que já está na tela
  const MOVES_VISIBLE = new Set(["ease-in-out", "overshoot", "bounce"]);

  function familyChecks(effect, b, s0, s1, res) {
    const fam = effect.familia;
    const visible = (v) => v.op >= 0.3 && v.own > 1 && v.area >= 0.5 * v.own;
    if (fam === "entradas-suaves" || fam === "entradas-impacto") {
      for (const { e, v } of s1.main) if (!visible(v)) res.errors.push(`entrada termina invisível ou fora do quadro: ${describe(e)} (opacidade ${v.op.toFixed(2)}, área visível ${v.own > 1 ? pct(v.area / v.own) : "0"})`);
      // antes de t a entrada não aparece (exceto ritmo, que move algo já na tela; máscara não dá para medir)
      if (!MOVES_VISIBLE.has(effect.id)) s0.main.forEach(({ e, v }, i) => {
        const end = s1.main[i].v;
        if (!v.masked && v.op >= 0.05 && v.area >= 0.05 * Math.max(end.area, 1)) res.errors.push(`entrada já aparece antes de t: ${describe(e)} (opacidade ${v.op.toFixed(2)}, área visível ${pct(v.area / Math.max(end.area, 1))} da final)`);
      });
    } else if (fam === "saidas") {
      s1.main.forEach(({ e, v }, i) => {
        const v0 = s0.main[i].v;
        if (!visible(v0)) res.errors.push(`saída começa invisível: ${describe(e)}`);
        const hidden = v.op < 0.05 || v.area < 0.05 * Math.max(v0.area, 1);
        if (!hidden) res.errors.push(`saída não termina escondida: ${describe(e)} (opacidade ${v.op.toFixed(2)}, área visível ${pct(v.area / Math.max(v0.area, 1))} da inicial)`);
      });
    } else if (fam === "transicoes") {
      if (!s0.a || !s1.b) { res.notes.push("transição sem a e b: sem o check de A para B"); return; }
      if (s0.a.op < 0.9 || s0.a.cover < 0.9) res.errors.push(`transição não começa com A na tela (opacidade ${s0.a.op.toFixed(2)}, cobre ${pct(s0.a.cover)})`);
      if (!b.aOnTop && s0.b.op >= 0.05 && s0.b.cover >= 0.1) res.errors.push(`B já aparece antes da transição (opacidade ${s0.b.op.toFixed(2)}, cobre ${pct(s0.b.cover)})`);
      if (s1.b.op < 0.9 || s1.b.cover < 0.9) res.errors.push(`transição não termina com B na tela (opacidade ${s1.b.op.toFixed(2)}, cobre ${pct(s1.b.cover)})`);
      if (b.aOnTop && s1.a && s1.a.op >= 0.05 && s1.a.cover >= 0.02) res.errors.push(`A (por cima de B) continua visível no fim (opacidade ${s1.a.op.toFixed(2)}, cobre ${pct(s1.a.cover)})`);
      const c1 = covering(s1.overlays);
      if (c1) res.errors.push(`${c1} ainda cobre o quadro no fim`);
    }
  }

  // ---------------------------------------------------------------- API

  window.dictHarness = {
    T0,
    ready() {
      const missing = ["gsap", ...PLUGINS].filter((n) => !window[n]);
      if (missing.length) return { ok: false, missing };
      gsap.registerPlugin(...PLUGINS.map((n) => window[n]));
      return { ok: true, version: gsap.version };
    },
    run(effects) { return effects.map(runEffect); },
    // para folhas de contato e inspeção manual
    prepare(effect) {
      teardown();
      current = build(effect);
      return { duration: current.tl.duration(), times: sampleTimes(current.tl.duration()) };
    },
    seek(time) { current.tl.totalTime(time, false); },
    show(id, time = 0) {
      const e = (window.DICT_EFFECTS || []).find((x) => x.id === id);
      if (!e) throw new Error("efeito não carregado: " + id);
      const info = this.prepare(e);
      this.seek(time);
      return info;
    },
  };
})();
