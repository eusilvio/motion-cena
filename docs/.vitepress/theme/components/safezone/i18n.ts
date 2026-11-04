/** Strings and number formatting shared by the safe-zone playground and the preset tables. */

export type Locale = "pt" | "en";
export type Kind = "title" | "caption" | "card";

/** English display names; the JSON labels are written in Portuguese. Unknown ids fall back to the JSON label. */
const LABEL_EN: Record<string, string> = {
  vertical: "Universal vertical (Reels + TikTok + Shorts)",
  "ig-feed": "Instagram Feed (in-feed video)",
  "yt-long": "YouTube (horizontal video)",
  "yt-long-4k": "YouTube 4K (horizontal)",
  linkedin: "LinkedIn (feed)",
  square: "Square 1:1 (generic feed, X, LinkedIn)",
  "ig-carousel": "Instagram carousel (4:5)",
  "ig-carousel-square": "Instagram carousel (1:1)",
  "linkedin-carousel": "LinkedIn carousel (4:5 PDF document)",
};

export function presetLabel(id: string, label: string, locale: Locale): string {
  return locale === "en" ? (LABEL_EN[id] ?? label) : label;
}

const nf = (locale: Locale) => new Intl.NumberFormat(locale === "pt" ? "pt-BR" : "en-US");

/** 30 -> "30 s", 180 -> "3 min", 43200 -> "12 h", 90 -> "90 s" */
export function fmtDuration(sec: number, locale: Locale): string {
  if (sec >= 3600 && sec % 3600 === 0) return `${nf(locale).format(sec / 3600)} h`;
  if (sec > 90 && sec % 60 === 0) return `${nf(locale).format(sec / 60)} min`;
  return `${nf(locale).format(sec)} s`;
}

/** [15, 60] -> "15–60 s", [60, 900] -> "1–15 min" */
export function fmtRange([a, b]: [number, number], unit: "s" | "slides", locale: Locale): string {
  if (unit === "s" && a >= 60 && a % 60 === 0 && b % 60 === 0) return `${a / 60}–${b / 60} min`;
  const u = unit === "s" ? " s" : "";
  return `${nf(locale).format(a)}–${nf(locale).format(b)}${u}`;
}

export const STR = {
  pt: {
    preset: "Preset",
    block: "Bloco",
    kinds: { title: "Título", caption: "Legenda", card: "Card" } as Record<Kind, string>,
    sample: {
      title: ["Juros", "compostos"],
      caption: "juro sobre juro",
      cardBig: "R$ 1.791",
      cardSmall: "R$ 1.000 a 6% ao ano, 10 anos",
    },
    ui: "Mostrar a interface do app",
    uiHint: "Silhuetas genéricas de botões, nome, legenda e barra do topo, sem marca de nenhuma rede.",
    center: "Centralizar na horizontal",
    reset: "Voltar à posição inicial",
    edges: { top: "Topo", bottom: "Base", left: "Esquerda", right: "Direita" },
    clear: "de folga",
    inside: "na zona",
    position: "Posição",
    size: "Tamanho",
    ok: "Tudo na área livre",
    okDetail: "Nenhuma parte do bloco entra na zona. Neste quadro, o safe_zone_check.py não aponta nada.",
    hit: { title: "Parte do título está embaixo da interface", caption: "Parte da legenda está embaixo da interface", card: "Parte do card está embaixo da interface" } as Record<Kind, string>,
    hitDetail: "Parado assim por 0,5 s ou mais, o safe_zone_check.py marca ERRO e o vídeo não sai.",
    hitTol: "Até 4 px dentro da zona o medidor ainda tolera (--tol), mas a regra da skill é nenhuma parte na zona.",
    corner: "Encosta num canto ocupado pelo player. O medidor só confere as margens, mas a skill pede para tirar texto importante desses cantos.",
    help: "Arraste o bloco. Pelo teclado, chegue nele com Tab e use as setas (com Shift, 10 px). O canto inferior direito muda o tamanho.",
    blockAria: (k: string) => `${k}. Setas movem 1 px; com Shift, 10 px.`,
    handleAria: "Redimensionar. Setas mudam largura e altura em 1 px; com Shift, 10 px.",
    stageAria: (id: string, w: number, h: number) => `Canvas ${w} por ${h} do preset ${id}`,
    cssTitle: "Variáveis para a composição",
    cssNote: "Igual à saída de",
    copy: "Copiar",
    copied: "Copiado",
    copyFail: "Selecione e copie",
    px: "px",
    zoneLegend: "zona da interface",
    freeLegend: "área livre",
    cornerLegend: "canto do player",
  },
  en: {
    preset: "Preset",
    block: "Block",
    kinds: { title: "Title", caption: "Caption", card: "Card" } as Record<Kind, string>,
    sample: {
      title: ["Compound", "interest"],
      caption: "interest on interest",
      cardBig: "$1,791",
      cardSmall: "$1,000 at 6% a year, 10 years",
    },
    ui: "Show the app interface",
    uiHint: "Generic silhouettes of buttons, name, caption and top bar, with no network's branding.",
    center: "Center horizontally",
    reset: "Back to the starting position",
    edges: { top: "Top", bottom: "Bottom", left: "Left", right: "Right" },
    clear: "clear",
    inside: "in the zone",
    position: "Position",
    size: "Size",
    ok: "Everything in the free area",
    okDetail: "No part of the block enters the zone. On this frame, safe_zone_check.py reports nothing.",
    hit: { title: "Part of the title is under the app's interface", caption: "Part of the caption is under the app's interface", card: "Part of the card is under the app's interface" } as Record<Kind, string>,
    hitDetail: "Held like this for 0.5 s or more, safe_zone_check.py reports an ERRO and the video does not ship.",
    hitTol: "The checker still tolerates up to 4 px inside the zone (--tol), but the skill's rule is no part in the zone.",
    corner: "It touches a corner the player covers. The checker only measures the margins, but the skill asks you to keep important text out of these corners.",
    help: "Drag the block. With the keyboard, Tab to it and use the arrow keys (Shift for 10 px). The bottom-right corner resizes it.",
    blockAria: (k: string) => `${k}. Arrow keys move 1 px; with Shift, 10 px.`,
    handleAria: "Resize. Arrow keys change width and height by 1 px; with Shift, 10 px.",
    stageAria: (id: string, w: number, h: number) => `${w} by ${h} canvas of the ${id} preset`,
    cssTitle: "Variables for the composition",
    cssNote: "Same as the output of",
    copy: "Copy",
    copied: "Copied",
    copyFail: "Select and copy",
    px: "px",
    zoneLegend: "interface zone",
    freeLegend: "free area",
    cornerLegend: "player corner",
  },
};

export const TABLE = {
  pt: {
    preset: "Preset",
    platform: "Plataforma",
    canvas: "Canvas",
    def: "Padrão",
    ideal: "Ideal",
    max: "Máx.",
    zone: "Zona segura",
    zoneSub: "topo / base / esq. / dir.",
    slides: "Slides",
    format: "Saída",
    margin: "Margem segura",
    ads: (n: number) => `${n} em anúncio`,
    fps: (n: number) => `Todos os presets de vídeo rodam a ${n} fps.`,
    caption: "Gerada a partir de assets/platforms.json no build do site.",
  },
  en: {
    preset: "Preset",
    platform: "Platform",
    canvas: "Canvas",
    def: "Default",
    ideal: "Ideal",
    max: "Max",
    zone: "Safe zone",
    zoneSub: "top / bottom / left / right",
    slides: "Slides",
    format: "Output",
    margin: "Safe margin",
    ads: (n: number) => `${n} in ads`,
    fps: (n: number) => `Every video preset runs at ${n} fps.`,
    caption: "Generated from assets/platforms.json when the site is built.",
  },
};
