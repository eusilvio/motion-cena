<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Dicionário de efeitos motion — parte 2</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Inter"; src: url("assets/fonts/Inter.ttf") format("truetype"); font-weight: 100 900; }
      @font-face { font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf") format("truetype"); font-weight: 400; }
      @font-face { font-family: "JetBrains Mono"; src: url("assets/fonts/JetBrainsMono.ttf") format("truetype"); font-weight: 100 800; }

      :root {
        --bg: #f3ede2;
        --ink: #141414;
        --muted: #6b645b;
        --accent: #d0592c;
        --panel: #161616;
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--bg); }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; color: var(--ink); font-family: "Inter", sans-serif; background: var(--bg); }

      .clip { position: absolute; inset: 0; }
      .stage { position: absolute; inset: 0; }
      .display { font-family: "Anton", "Inter", sans-serif; font-weight: 400; letter-spacing: -0.01em; }
      .accent { color: var(--accent); }

      .hd { position: absolute; left: 80px; top: 290px; font-family: "JetBrains Mono", monospace; font-size: 34px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--accent); }
      .num { position: absolute; right: 80px; top: 290px; font-family: "JetBrains Mono", monospace; font-size: 34px; color: var(--muted); }
      .term { position: absolute; left: 76px; top: 345px; font-size: 170px; line-height: 1; white-space: nowrap; }
      .par { position: absolute; left: 80px; top: 570px; right: 80px; font-size: 42px; line-height: 1.3; color: var(--muted); }
      .par b { color: var(--ink); font-weight: 700; }
      .demo { position: absolute; left: 0; right: 0; top: 760px; height: 760px; }
      .mid { position: absolute; left: 50%; top: 50%; }

      .sq { width: 340px; height: 340px; margin: -170px 0 0 -170px; background: var(--accent); border-radius: 18px; }
      .sq.small { width: 240px; height: 240px; margin: -120px 0 0 -120px; }
      .badge { position: absolute; right: -26px; top: -26px; width: 80px; height: 80px; border-radius: 50%; background: var(--ink); color: #fff; font-weight: 800; font-size: 44px; display: flex; align-items: center; justify-content: center; }
      .shadow { position: absolute; left: 50%; top: 600px; width: 300px; height: 30px; margin-left: -150px; border-radius: 50%; background: #d9cfc0; }

      .panel { position: absolute; left: 70px; right: 70px; top: 50%; height: 300px; margin-top: -150px; background: var(--panel); border-radius: 22px; display: flex; align-items: center; justify-content: center; color: #f6f1e8; font-size: 118px; line-height: 1; white-space: nowrap; font-variant-numeric: tabular-nums; }
      .lines { position: absolute; left: 80px; top: 120px; font-size: 150px; line-height: 1.05; }
      .line { overflow: hidden; }
      .line span { display: inline-block; }
      .hl-text { position: absolute; left: 80px; right: 80px; top: 300px; font-size: 100px; font-weight: 800; letter-spacing: -0.02em; }
      .hlw { position: relative; display: inline-block; }
      .hl { position: absolute; left: -12px; right: -12px; top: 18%; bottom: 4%; background: var(--accent); border-radius: 6px; }
      .hlt { position: relative; color: var(--ink); }
      .slam { position: absolute; left: 0; right: 0; top: 200px; text-align: center; font-size: 300px; line-height: 1; color: var(--accent); }
      .count { position: absolute; left: 0; right: 0; top: 160px; text-align: center; font-size: 280px; line-height: 1; font-variant-numeric: tabular-nums; }
      .count-lb { position: absolute; left: 0; right: 0; top: 470px; text-align: center; font-size: 48px; color: var(--muted); }
      .pill { position: absolute; left: 50%; top: 50%; width: 560px; height: 170px; margin: -85px 0 0 -280px; border-radius: 85px; background: var(--accent); color: #fff; font-size: 64px; font-weight: 800; display: flex; align-items: center; justify-content: center; }
      .pill.dark { background: var(--ink); }

      .track { position: absolute; left: 140px; right: 140px; top: 50%; border-top: 4px dashed #c9bfb1; }
      .ball { position: absolute; left: 140px; top: 50%; width: 130px; height: 130px; margin-top: -65px; border-radius: 50%; background: var(--accent); border: 6px solid var(--ink); }
      .ball.echo { border-color: transparent; }
      .floor { position: absolute; left: 120px; right: 120px; top: 640px; border-top: 6px solid var(--ink); }
      .card { position: absolute; left: 200px; top: 220px; width: 680px; height: 340px; border-radius: 26px; background: var(--ink); }
      .part { position: absolute; left: 260px; height: 36px; border-radius: 18px; background: var(--accent); }

      .frame { position: absolute; left: 100px; right: 100px; top: 100px; height: 560px; overflow: hidden; border-radius: 20px; background: #e4dbcd; }
      .big { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 320px; line-height: 1; color: #f3ede2; }
      .A { background: #8a837a; }
      .B { background: var(--accent); }
      .ghost { background: transparent; opacity: 0; }
      .flash { position: absolute; inset: 0; background: #fffaf2; opacity: 0; }
      .strip { position: absolute; left: 0; right: 0; height: 94px; background: var(--ink); }
      .world, .layer { position: absolute; inset: 0; }
      .sky { position: absolute; inset: 0; background: linear-gradient(#f0d3c4, #e9b39b); }
      .sun { position: absolute; left: 480px; top: 120px; width: 190px; height: 190px; border-radius: 50%; background: var(--accent); }
      .mtn { position: absolute; left: 0; right: 0; bottom: 0; height: 330px; background: #3a3530; clip-path: polygon(0 60%, 18% 20%, 32% 55%, 50% 0, 68% 50%, 82% 25%, 100% 55%, 100% 100%, 0 100%); }
      .mtn.wide { right: -500px; opacity: 0.75; }
      .tree { position: absolute; bottom: 0; width: 90px; height: 230px; background: #1d1b19; clip-path: polygon(50% 0, 100% 100%, 0 100%); }
      .stripes { position: absolute; inset: -40px; background: repeating-linear-gradient(90deg, #d8cdbd 0 40px, #efe8dc 40px 80px); }
      .subject { position: absolute; left: 50%; top: 50%; width: 240px; height: 240px; margin: -120px 0 0 -120px; border-radius: 50%; background: var(--accent); border: 8px solid var(--ink); }
      .mc-a { position: absolute; left: 60px; top: 60px; width: 140px; height: 140px; border-radius: 50%; background: var(--accent); }
      .mc-b { position: absolute; left: 190px; top: 80px; width: 500px; height: 400px; border-radius: 36px; background: var(--accent); opacity: 0; display: flex; align-items: center; justify-content: center; font-size: 220px; color: #f3ede2; }
      .grain {
        position: absolute; left: -10%; top: -10%; width: 120%; height: 120%; opacity: 0.6; mix-blend-mode: multiply;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
      }

      .title { position: absolute; left: 76px; right: 76px; top: 420px; font-size: 200px; line-height: 0.95; }
      .sub { position: absolute; left: 80px; right: 80px; top: 1130px; font-size: 52px; line-height: 1.25; font-weight: 600; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{TOTAL}}" data-width="1080" data-height="1920">

      <section id="e0" class="clip" data-start="0" data-duration="3" data-track-index="1">
        <div class="stage">
          <div class="hd">motion dictionary · parte 2</div>
          <div class="title display"><span class="t0">Mais</span><br /><span class="t0">efeitos</span><br /><span class="t0 accent">Motion</span></div>
          <div class="sub" id="e0-sub">{{COUNT}} efeitos novos · texto, ênfase, física, câmera, transições e acabamento.</div>
        </div>
      </section>

{{SECTIONS}}
    </div>

    <script>
      window.__timelines = window.__timelines || {};

      function rng(seed) {
        return () => {
          seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
          let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
          t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
          return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
      }

      document.fonts.ready.then(() => {
        const tl = gsap.timeline({ paused: true });
        const E = "power3.out";
        const N = {{COUNT}};
        const $ = (id) => document.getElementById(id);
        const start = (i) => parseFloat($("e" + i).dataset.start);
        const dur = (i) => parseFloat($("e" + i).dataset.duration);
        const fx = (i, off = 0) => start(i) + 0.55 + off;
        const W = 880;

        // headers slide in; every scene fades out at its end
        for (let i = 0; i <= N; i++) {
          const sec = $("e" + i), stage = sec.querySelector(".stage");
          const head = ["hd", "num", "term", "par"].map((c) => sec.getElementsByClassName(c)[0]).filter(Boolean);
          if (i > 0) tl.fromTo(head, { x: -80, opacity: 0 }, { x: 0, opacity: 1, duration: 0.4, ease: E, stagger: 0.06 }, start(i) + 0.05);
          if (i < N) tl.to(stage, { opacity: 0, duration: 0.15, ease: "power2.in" }, start(i) + dur(i) - 0.15);
        }
        tl.fromTo("#e0 .t0", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: E, stagger: 0.15 }, 0.1);
        tl.fromTo("#e0-sub", { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power2.out" }, 0.8);

        let t;
        // 1 scramble
        t = fx(1);
        const GL = "!<>-_/[]{}=+*^?#ABCDEFGHJKMNPRSTUVWXYZ0123456789", sEl = $("f1"), word = sEl.dataset.text, sc = { p: 0 };
        tl.fromTo(sc, { p: 0 }, { p: 1, duration: 0.8, ease: "none", onUpdate: () => {
          const shown = Math.floor(sc.p * word.length), step = Math.floor(tl.time() * 20);
          sEl.textContent = [...word].map((ch, i) => (i < shown || ch === " " ? ch : GL[(i * 31 + step * 17) % GL.length])).join("");
        } }, t);
        tl.set(sEl, { textContent: word }, t + 0.81);
        // 2 line reveal
        tl.fromTo(".f2", { yPercent: 110 }, { yPercent: 0, duration: 0.7, ease: "power4.out", stagger: 0.08 }, fx(2, -0.2));
        // 3 highlight
        tl.fromTo("#f3", { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.4, ease: "power2.out" }, fx(3));
        // 4 slam
        t = fx(4);
        tl.fromTo("#f4", { scale: 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.22, ease: "power4.out" }, t);
        tl.fromTo("#e4 .demo", { y: 0 }, { keyframes: { y: [0, 14, -9, 5, 0] }, duration: 0.3, ease: "none" }, t + 0.2);
        // 5 count-up
        const n = { v: 0 }, numEl = $("f5");
        tl.fromTo(n, { v: 0 }, { v: 1000, duration: 1.0, ease: "power2.out", onUpdate: () => { numEl.textContent = Math.round(n.v).toLocaleString("pt-BR"); } }, fx(5));
        // 6 pulse (twice so it reads in the demo)
        tl.fromTo("#f6", { scale: 1 }, { scale: 1.08, duration: 0.18, ease: "sine.inOut", yoyo: true, repeat: 1 }, fx(6));
        tl.fromTo("#f6", { scale: 1 }, { scale: 1.08, duration: 0.18, ease: "sine.inOut", yoyo: true, repeat: 1, immediateRender: false }, fx(6, 0.8));
        // 7 shake
        tl.fromTo("#f7", { x: 0 }, { keyframes: { x: [0, -14, 12, -8, 6, -3, 0] }, duration: 0.35, ease: "none" }, fx(7));
        // 8 glow
        t = fx(8);
        tl.fromTo("#f8", { filter: "drop-shadow(0 0 0px rgba(208,89,44,0))" }, { filter: "drop-shadow(0 0 40px rgba(208,89,44,0.9))", duration: 0.25, ease: "power2.out" }, t);
        tl.to("#f8", { filter: "drop-shadow(0 0 0px rgba(208,89,44,0))", duration: 0.5, ease: "power2.in" }, t + 0.6);
        // 9 wiggle
        t = fx(9);
        tl.fromTo("#f9", { rotation: -2 }, { rotation: 2, duration: 0.12, ease: "sine.inOut", yoyo: true, repeat: 7 }, t);
        tl.to("#f9", { rotation: 0, duration: 0.1 }, t + 0.96);

        // 10 anticipation
        t = fx(10);
        tl.fromTo("#f10", { x: 0 }, { x: -50, duration: 0.15, ease: "power2.inOut" }, t);
        tl.to("#f10", { x: 670, duration: 0.45, ease: "power3.out" }, t + 0.15);
        // 11 squash & stretch
        t = fx(11, -0.2);
        tl.fromTo("#f11", { y: -450, scaleX: 0.85, scaleY: 1.2 }, { y: 0, duration: 0.45, ease: "power2.in", transformOrigin: "50% 100%" }, t);
        tl.to("#f11", { scaleX: 1.3, scaleY: 0.7, duration: 0.08, ease: "power2.out" }, t + 0.45);
        tl.to("#f11", { scaleX: 1, scaleY: 1, duration: 0.5, ease: "elastic.out(1, 0.4)" }, t + 0.53);
        // 12 follow-through
        t = fx(12, -0.2);
        tl.fromTo("#f12", { x: -800 }, { x: 0, duration: 0.5, ease: "power3.out" }, t);
        tl.fromTo(".f12p", { x: -800 }, { x: 0, duration: 0.6, ease: "back.out(2)", stagger: 0.06 }, t + 0.06);
        // 13 float
        t = fx(13, -0.4);
        tl.fromTo("#f13", { y: 0 }, { y: -24, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: 2 }, t);
        tl.fromTo("#f13-sh", { scaleX: 1 }, { scaleX: 0.85, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: 2 }, t);

        // 14 push-in
        tl.fromTo("#f14", { scale: 1, x: 0 }, { scale: 1.12, x: -30, duration: dur(14), ease: "sine.inOut" }, start(14));
        // 15 parallax
        t = fx(15, -0.3);
        [["#f15-bg", 0.2], ["#f15-mid", 0.5], ["#f15-fg", 1]].forEach(([el, k]) =>
          tl.fromTo(el, { x: 0 }, { x: -400 * k, duration: 1.6, ease: "power1.inOut" }, t));
        // 16 whip pan
        t = fx(16, 0.2);
        tl.set("#f16-b", { x: W }, start(16));
        tl.fromTo("#f16-a", { x: 0 }, { x: -W, duration: 0.35, ease: "power4.inOut" }, t);
        tl.fromTo("#f16-b", { x: W }, { x: 0, duration: 0.35, ease: "power4.inOut", immediateRender: false }, t);
        tl.fromTo(["#f16-a", "#f16-b"], { filter: "blur(0px)" }, { keyframes: { filter: ["blur(0px)", "blur(30px)", "blur(0px)"] }, duration: 0.35, ease: "none" }, t);
        // 17 dolly zoom
        t = fx(17, -0.2);
        tl.fromTo("#f17-bg", { scale: 1 }, { scale: 1.6, duration: 1.2, ease: "power1.inOut" }, t);
        tl.fromTo("#f17", { scale: 1 }, { scale: 0.9, duration: 1.2, ease: "power1.inOut" }, t);

        // 18 zoom through
        t = fx(18, 0.2);
        tl.set("#f18-b", { opacity: 0 }, start(18));
        tl.fromTo("#f18-a", { scale: 1, opacity: 1 }, { scale: 4, opacity: 0, duration: 0.4, ease: "power3.in" }, t);
        tl.fromTo("#f18-b", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: "power3.out", immediateRender: false }, t + 0.25);
        // 19 iris
        tl.fromTo("#f19-b", { clipPath: "circle(0% at 50% 50%)" }, { clipPath: "circle(75% at 50% 50%)", duration: 0.6, ease: "power3.inOut" }, fx(19, 0.2));
        // 20 push
        t = fx(20, 0.2);
        tl.fromTo("#f20-a", { x: 0 }, { x: -W, duration: 0.5, ease: "power3.inOut" }, t);
        tl.fromTo("#f20-b", { x: W }, { x: 0, duration: 0.5, ease: "power3.inOut" }, t);
        // 21 glitch
        t = fx(21, 0.2);
        tl.set("#f21-b", { opacity: 0 }, start(21));
        [18, -26, 12, -8, 22, 0].forEach((o, k) => {
          tl.set("#f21-r", { x: o, opacity: o ? 0.8 : 0 }, t + k * 0.05);
          tl.set("#f21-c", { x: -o, opacity: o ? 0.8 : 0 }, t + k * 0.05);
        });
        tl.set("#f21-a", { opacity: 0 }, t + 0.15);
        tl.set("#f21-b", { opacity: 1 }, t + 0.15);
        // 22 flash
        t = fx(22, 0.2);
        tl.set("#f22-b", { opacity: 0 }, start(22));
        tl.fromTo("#f22-fl", { opacity: 0 }, { opacity: 1, duration: 0.08, ease: "power2.in" }, t);
        tl.set("#f22-a", { opacity: 0 }, t + 0.08);
        tl.set("#f22-b", { opacity: 1 }, t + 0.08);
        tl.to("#f22-fl", { opacity: 0, duration: 0.25, ease: "power2.out" }, t + 0.08);
        // 23 blinds
        t = fx(23);
        tl.set("#f23-b", { opacity: 0 }, start(23));
        tl.fromTo(".f23s", { scaleY: 0, transformOrigin: "50% 0%" }, { scaleY: 1, duration: 0.25, ease: "power3.in", stagger: 0.04 }, t);
        tl.set("#f23-a", { opacity: 0 }, t + 0.45);
        tl.set("#f23-b", { opacity: 1 }, t + 0.45);
        tl.fromTo(".f23s", { scaleY: 1, transformOrigin: "50% 100%" }, { scaleY: 0, duration: 0.25, ease: "power3.out", stagger: 0.04, immediateRender: false }, t + 0.45);
        // 24 match cut: circle travels to B's slot, grows, then B takes over
        t = fx(24);
        tl.fromTo("#f24", { x: 0, y: 0, scaleX: 1, scaleY: 1, borderRadius: "50%" },
          { x: 310, y: 150, scaleX: 3.57, scaleY: 2.86, borderRadius: "10%", duration: 0.5, ease: "power3.inOut" }, t);
        tl.set("#f24", { opacity: 0 }, t + 0.5);
        tl.set("#f24-b", { opacity: 1 }, t + 0.5);
        tl.fromTo("#f24-b span", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.7)" }, t + 0.5);
        // 25 motion trail
        t = fx(25);
        ["#f25", ...document.querySelectorAll(".f25e")].forEach((el, i) => {
          const lag = i === 0 ? 0 : (4 - i) * 0.03;
          tl.fromTo(el, { x: 0 }, { x: 670, duration: 0.5, ease: "power3.out" }, t + lag);
        });
        tl.to(".f25e", { opacity: 0, duration: 0.15 }, t + 0.65);
        // 26 grain at 12 fps, deterministic
        const r = rng(99);
        for (let k = 0; k < dur(26) * 12; k++) tl.set("#f26", { x: (r() - 0.5) * 80, y: (r() - 0.5) * 80 }, start(26) + k / 12);

        window.__timelines["main"] = tl;
      });
    </script>
  </body>
</html>
