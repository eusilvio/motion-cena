"""Build index.html for the motion dictionary demo, part 2 (26 effects).

Each scene = header (family, term, params) + a demo block. Timing is laid out
here so the HTML carries static data-start/data-duration values.
"""
from pathlib import Path

INTRO, D = 3.0, 2.6

FRAME_AB = (
    '<div class="frame" data-layout-allow-overlap data-layout-allow-overflow>'
    '<div class="big display A" id="{p}-a">A</div>'
    '<div class="big display B" id="{p}-b">B</div>{extra}</div>'
)
LANDSCAPE = (
    '<div class="sky"></div><div class="sun"></div>'
    '<div class="mtn"></div>'
)

# (family, term, params, demo html)
SCENES = [
    ("texto", "scramble", "embaralha e decodifica · <b>0,8 s</b> · 20 fps",
     '<div class="panel display"><span id="f1" data-text="IDEIA VIRA VÍDEO">IDEIA VIRA VÍDEO</span></div>'),
    ("texto", "line reveal", "linhas sobem da máscara · <b>0,7 s</b> · stagger 0,08 s",
     '<div class="lines display"><div class="line"><span class="f2">PARE DE</span></div>'
     '<div class="line"><span class="f2">PEDIR VÍDEO</span></div>'
     '<div class="line"><span class="f2 accent">BONITO</span></div></div>'),
    ("texto", "highlight", "marca-texto atrás da palavra · <b>0,4 s</b>",
     '<div class="hl-text">isso muda <span class="hlw"><span class="hl" id="f3"></span><span class="hlt">tudo</span></span></div>'),
    ("texto", "slam", "cai grande e bate · <b>0,22 s</b> · power4.out",
     '<div class="slam display" id="f4">AGORA</div>'),
    ("texto", "count-up", "número conta até o valor · <b>1,0 s</b> · power2.out",
     '<div class="count display" id="f5">0</div><div class="count-lb">visualizações</div>'),
    ("ênfase", "pulse", "pulsa uma vez · <b>0,18 s</b> ida e volta",
     '<div class="pill" id="f6">Salvar</div>'),
    ("ênfase", "shake", "treme no lugar · <b>0,35 s</b> · ±14 px",
     '<div class="pill dark" id="f7">senha errada</div>'),
    ("ênfase", "glow", "brilho acende ao redor · <b>0,25 s</b>",
     '<div class="mid sq" id="f8"></div>'),
    ("ênfase", "wiggle", "balança de leve · ±2° · 8× 0,12 s",
     '<div class="mid sq small" id="f9"><span class="badge">1</span></div>'),
    ("física", "anticipation", "recua antes de ir · <b>0,15 s</b> + 0,45 s",
     '<div class="track"></div><div class="ball" id="f10"></div>'),
    ("física", "squash & stretch", "achata no impacto · scale 1,3 × 0,7",
     '<div class="floor"></div><div class="ball" id="f11" style="left: 475px; top: 505px"></div>'),
    ("física", "follow-through", "partes chegam depois · back.out(2)",
     '<div class="card" id="f12"></div>'
     '<div class="part f12p" style="top: 300px; width: 420px"></div>'
     '<div class="part f12p" style="top: 370px; width: 320px"></div>'
     '<div class="part f12p" style="top: 440px; width: 380px"></div>'),
    ("física", "float", "flutua em loop sutil · ±12 px · 1,2 s",
     '<div class="mid sq" id="f13"></div><div class="shadow" id="f13-sh"></div>'),
    ("câmera", "push-in", "aproxima devagar · scale 1 → 1,12",
     '<div class="frame"><div class="world" id="f14">' + LANDSCAPE + '</div></div>'),
    ("câmera", "parallax", "camadas em 3 velocidades · 0,2× 0,5× 1×",
     '<div class="frame" data-layout-allow-overflow><div class="sky"></div>'
     '<div class="layer" id="f15-bg"><div class="sun" style="left: 300px"></div><div class="sun" style="left: 1000px; opacity: .5"></div></div>'
     '<div class="layer" id="f15-mid"><div class="mtn wide"></div></div>'
     '<div class="layer" id="f15-fg">' + "".join(
         f'<div class="tree" style="left: {x}px"></div>' for x in range(40, 1400, 190)) + '</div></div>'),
    ("câmera", "whip pan", "chicote com borrão · <b>0,35 s</b> · blur 30 px",
     FRAME_AB.format(p="f16", extra="")),
    ("câmera", "dolly zoom", "fundo cresce, sujeito fica · <b>1,2 s</b>",
     '<div class="frame"><div class="stripes" id="f17-bg"></div><div class="subject" id="f17"></div></div>'),
    ("transições", "zoom through", "atravessa A e cai em B · <b>0,4 s</b>",
     FRAME_AB.format(p="f18", extra="")),
    ("transições", "iris", "círculo abre revelando B · <b>0,6 s</b>",
     FRAME_AB.format(p="f19", extra="")),
    ("transições", "push", "B empurra A · <b>0,5 s</b> · power3.inOut",
     FRAME_AB.format(p="f20", extra="")),
    ("transições", "glitch", "RGB split e troca · <b>0,3 s</b>",
     FRAME_AB.format(p="f21", extra=(
         '<div class="big display ghost" id="f21-r" style="color: #ff2a3a">A</div>'
         '<div class="big display ghost" id="f21-c" style="color: #19c2ff">A</div>'))),
    ("transições", "flash", "estouro de luz esconde o corte · <b>0,08 s</b>",
     FRAME_AB.format(p="f22", extra='<div class="flash" id="f22-fl"></div>')),
    ("transições", "blinds", "faixas fecham e abrem · stagger 0,04 s",
     FRAME_AB.format(p="f23", extra="".join(
         f'<div class="strip f23s" style="top: {i * 94}px"></div>' for i in range(6)))),
    ("transições", "match cut", "objeto de A vira o de B · <b>0,5 s</b>",
     '<div class="frame" style="background: #e4dbcd">'
     '<div class="mc-b" id="f24-b"><span class="display">B</span></div>'
     '<div class="mc-a" id="f24"></div></div>'),
    ("acabamento", "motion trail", "ecos seguem o movimento · 3 ecos, 0,03 s",
     '<div class="track"></div>'
     '<div class="ball echo f25e" style="opacity: .12"></div>'
     '<div class="ball echo f25e" style="opacity: .25"></div>'
     '<div class="ball echo f25e" style="opacity: .4"></div>'
     '<div class="ball" id="f25"></div>'),
    ("acabamento", "grain", "textura de filme a 12 fps · na demo exagerado (0,6)",
     '<div class="frame">' + LANDSCAPE + '<div class="grain" id="f26"></div></div>'),
]

TOTAL = round(INTRO + D * len(SCENES), 2)

sections = []
for i, (fam, term, par, demo) in enumerate(SCENES, 1):
    start = round(INTRO + D * (i - 1), 2)
    sections.append(
        f'      <section id="e{i}" class="clip" data-start="{start}" data-duration="{D}" data-track-index="1">\n'
        f'        <div class="stage"><div class="hd">{fam}</div><div class="num">{i:02d}/{len(SCENES)}</div>'
        f'<div class="term display"{' style="font-size: 124px"' if len(term) > 11 else ''}>{term}</div><div class="par">{par}</div>\n'
        f'          <div class="demo">{demo}</div></div>\n'
        f'      </section>'
    )

here = Path(__file__).parent
tpl = (here / "index.tpl").read_text(encoding="utf-8")
html = (tpl.replace("{{TOTAL}}", str(TOTAL))
           .replace("{{SECTIONS}}", "\n\n".join(sections))
           .replace("{{COUNT}}", str(len(SCENES))))
assert "{{" not in html
(here / "index.html").write_text(html, encoding="utf-8")
print(f"index.html built ({TOTAL}s, {len(SCENES)} scenes)")
