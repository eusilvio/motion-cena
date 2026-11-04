# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.58.0", "pillow>=10"]
# ///
"""Roda as receitas GSAP do dicionário (references/motion-dictionary/*.json) num Chromium headless.

Cada efeito ganha um fixture novo em harness.html (uma página só, refeita entre efeitos) e passa
pelos checks de harness.js: sem exceção nem aviso do GSAP, timeline com duração, seek
determinístico, algo muda, e o check da família (entrada, saída, transição).

Uso:
  uv run tests/fixtures/dictionary/run_dictionary.py --json relatorio.json [--sheets pasta] [--only id,id] [--family texto]

Saída 0 com o relatório escrito (as falhas ficam no JSON); 77 = pulado (sem Chromium do
Playwright ou sem GSAP no cache e sem rede), com o motivo na primeira linha do stdout.
O GSAP 3.14.2 (mesma versão das demos) vem do cache local; na primeira vez baixa do jsDelivr e
confere o sha256. Nenhuma outra requisição de rede sai da página.
"""
import argparse
import glob
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DICT_DIR = REPO / ".agents" / "skills" / "motion-cena" / "references" / "motion-dictionary"
SKIP = 77

GSAP_VERSION = "3.14.2"
CDN = f"https://cdn.jsdelivr.net/npm/gsap@{GSAP_VERSION}/dist/"
GSAP_FILES = {  # sha256 dos arquivos do pacote npm gsap@3.14.2 (iguais aos do jsDelivr)
    "gsap.min.js": "c174bfce53a729418d57a8ad8625e7247c793a22fef8e2851e3cfa3de9cd8280",
    "DrawSVGPlugin.min.js": "2d2b28b7b1ad56cd5ca0d3032ed0f56503d0aaba6b5467169dc596d96e1125e3",
    "MorphSVGPlugin.min.js": "40e4246c7f898f5204a9d3f02c34672e7da589c297c157cdff714e87a362b045",
    "MotionPathPlugin.min.js": "aa5f955ca4ce3095ebe5726f43a46b72532230edb3501b28fb853f189f023cab",
    "CustomEase.min.js": "2dae8ef6daba66ce7b527b1f46a5695ba325b21ad5b4d73e4a843753c65415f6",
    "SplitText.min.js": "3c38c97c364b3048ed6f7756388d2aa32580b81cf42932ea251b77fc626b3831",
}


def skip(reason: str):
    print(f"SKIP: {reason}")
    sys.exit(SKIP)


def cache_dir() -> Path:
    if os.environ.get("MOTION_CENA_GSAP_DIR"):
        return Path(os.environ["MOTION_CENA_GSAP_DIR"])
    base = os.environ.get("XDG_CACHE_HOME") or (os.environ.get("LOCALAPPDATA") if os.name == "nt" else None) \
        or str(Path.home() / ".cache")
    return Path(base) / "motion-cena" / f"gsap-{GSAP_VERSION}"


def ensure_gsap() -> Path:
    d = cache_dir()
    d.mkdir(parents=True, exist_ok=True)
    for name, digest in GSAP_FILES.items():
        f = d / name
        if f.exists() and hashlib.sha256(f.read_bytes()).hexdigest() == digest:
            continue
        try:
            with urllib.request.urlopen(CDN + name, timeout=30) as r:
                data = r.read()
        except OSError as e:
            skip(f"GSAP {GSAP_VERSION} fora do cache ({d}) e sem rede para baixar {name}: {e}")
        if hashlib.sha256(data).hexdigest() != digest:
            sys.exit(f"sha256 de {name} baixado de {CDN} não confere; nada foi gravado")
        f.write_bytes(data)
    return d


def fallback_chromium() -> str | None:
    """Outro Chromium já baixado pelo Playwright (versão diferente da fixada), se houver."""
    roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH"), str(Path.home() / ".cache" / "ms-playwright"),
             str(Path.home() / "Library" / "Caches" / "ms-playwright"),
             os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright")]
    pats = ["chromium_headless_shell-*/chrome-*/chrome-headless-shell", "chromium_headless_shell-*/chrome-*/chrome-headless-shell.exe",
            "chromium-*/chrome-*/chrome", "chromium-*/chrome-*/chrome.exe",
            "chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium"]
    found = []
    for root in filter(None, roots):
        for pat in pats:
            for p in glob.glob(os.path.join(root, pat)):
                build = Path(p).relative_to(root).parts[0].rsplit("-", 1)[-1]
                if build.isdigit() and os.access(p, os.X_OK):
                    found.append((int(build), p))
    return max(found)[1] if found else None


def load_effects(only: set[str], family: str | None, files: list[Path] | None = None) -> list[dict]:
    effects = []
    for f in files or sorted(DICT_DIR.glob("*.json")):
        if f.name == "schema.json":
            continue
        for e in json.loads(f.read_text(encoding="utf-8")):
            if only and e["id"] not in only:
                continue
            if family and e["familia"] != family:
                continue
            effects.append(e)
    return effects


def launch(p):
    try:
        return p.chromium.launch()
    except Exception as e:  # executável da versão fixada não instalado
        alt = fallback_chromium()
        if not alt:
            skip(f"Chromium do Playwright não instalado ({str(e).splitlines()[0]}); "
                 "instale com: uv run --with playwright==1.58.0 playwright install chromium")
        return p.chromium.launch(executable_path=alt)


def open_page(browser, gsap_dir: Path, scale: float = 1.0):
    ctx = browser.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=scale)

    def route(r):
        url = r.request.url
        if url.startswith(CDN) and url[len(CDN):] in GSAP_FILES:
            return r.fulfill(path=str(gsap_dir / url[len(CDN):]), content_type="application/javascript")
        if url.startswith("file:") or url.startswith("data:"):
            return r.continue_()
        return r.abort()  # o trecho roda isolado: nada sai da página

    ctx.route("**/*", route)
    page = ctx.new_page()
    page.on("pageerror", lambda err: print(f"erro na página: {err}", file=sys.stderr))
    page.goto((HERE / "harness.html").as_uri())
    ready = page.evaluate("dictHarness.ready()")
    if not ready.get("ok"):
        sys.exit(f"harness sem {ready.get('missing')}")
    return page, ready["version"]


def contact_sheets(browser, gsap_dir: Path, effects: list[dict], results: dict, out: Path):
    from io import BytesIO

    from PIL import Image, ImageDraw, ImageFont

    # escala 0.25 (não menos): filtros SVG com detalhe de 1 px, como o pixelate, somem abaixo disso
    page, _ = open_page(browser, gsap_dir, scale=0.25)
    page.evaluate("effects => { window.DICT_EFFECTS = effects; }", effects)
    tw, th, per_row, rows_per_page, lab = 162, 288, 4, 4, 34
    cell_w = tw * 3 + 24
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    out.mkdir(parents=True, exist_ok=True)
    fams = {}
    for e in effects:
        fams.setdefault(e["familia"], []).append(e)
    written = []
    for fam, items in fams.items():
        per_page = per_row * rows_per_page
        for pg in range(0, len(items), per_page):
            chunk = items[pg:pg + per_page]
            nrows = (len(chunk) + per_row - 1) // per_row
            sheet = Image.new("RGB", (cell_w * per_row, nrows * (th + lab)), (24, 24, 28))
            draw = ImageDraw.Draw(sheet)
            for k, e in enumerate(chunk):
                x0, y0 = (k % per_row) * cell_w, (k // per_row) * (th + lab)
                res = results.get(e["id"], {})
                bad = bool(res.get("errors"))
                draw.text((x0 + 6, y0 + 4), ("FALHA " if bad else "") + e["id"], fill=(255, 90, 90) if bad else (230, 230, 230), font=font)
                try:
                    info = page.evaluate("e => dictHarness.prepare(e)", e)
                except Exception as err:  # noqa: BLE001
                    draw.text((x0 + 6, y0 + 20), f"exceção: {str(err)[:60]}", fill=(255, 90, 90), font=font)
                    continue
                d = info["duration"]
                ts = info["times"]
                for j, tt in enumerate([0, ts[len(ts) // 2], d]):
                    page.evaluate("t => dictHarness.seek(t)", tt)
                    png = page.screenshot(clip={"x": 0, "y": 0, "width": 1080, "height": 1920}, type="png")
                    im = Image.open(BytesIO(png)).convert("RGB").resize((tw, th))
                    sheet.paste(im, (x0 + j * (tw + 8), y0 + lab))
                    draw.text((x0 + j * (tw + 8) + 4, y0 + lab + th - 18), f"{tt:.2f}s", fill=(255, 255, 0), font=font)
            name = out / f"{fam}-{pg // per_page + 1:02d}.png"
            sheet.save(name)
            written.append(name)
    page.context.close()
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", required=True, type=Path, help="relatório de saída")
    ap.add_argument("--sheets", type=Path, help="pasta para as folhas de contato (início / meio / fim)")
    ap.add_argument("--only", default="", help="ids separados por vírgula")
    ap.add_argument("--family", help="só uma família")
    ap.add_argument("--effects", type=Path, action="append", help="outro arquivo de efeitos (padrão: o dicionário)")
    args = ap.parse_args()

    effects = load_effects({x for x in args.only.split(",") if x}, args.family, args.effects)
    if not effects:
        sys.exit("nenhum efeito selecionado")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        skip("pacote playwright indisponível")

    with sync_playwright() as p:
        browser = launch(p)  # antes de baixar o GSAP: sem Chromium, pula sem rede
        gsap_dir = ensure_gsap()
        t0 = time.monotonic()
        page, version = open_page(browser, gsap_dir)
        results = []
        for fam in sorted({e["familia"] for e in effects}):
            batch = [e for e in effects if e["familia"] == fam]
            results += page.evaluate("effects => dictHarness.run(effects)", batch)
        page.context.close()
        elapsed = time.monotonic() - t0
        report = {"gsap": version, "chromium": browser.version, "elapsed_s": round(elapsed, 2), "effects": results}
        if args.sheets:
            by_id = {r["id"]: r for r in results}
            report["sheets"] = [str(x) for x in contact_sheets(browser, gsap_dir, effects, by_id, args.sheets)]
        browser.close()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = [r for r in results if r["errors"]]
    print(f"{len(results)} efeitos, {len(bad)} com falha, {elapsed:.1f} s (GSAP {version}, Chromium {report['chromium']})")


if __name__ == "__main__":
    main()
