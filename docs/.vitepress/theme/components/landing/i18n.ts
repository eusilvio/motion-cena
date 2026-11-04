/**
 * Every string the landing shows, one dictionary per locale.
 * Facts and numbers come from README.md / README.en.md; the hero sentence and the
 * pipeline excerpts are synthetic examples written for this page.
 */
export type Locale = "pt" | "en";

/** a spoken word with its timestamps in seconds, as in audio/words.json */
export interface HeroWord {
  w: string;
  s: number;
  e: number;
}
export interface HeroScene {
  id: string;
  label: string;
  start: number;
  end: number;
  /** word indices per line; `big` = the oversized last line */
  lines: { words: number[]; big?: boolean }[];
}
export type HeroEffect = "slam" | "stagger" | "highlight" | "punch zoom";
export interface HeroAnchor {
  word: number;
  effect: HeroEffect;
  /** how long the effect runs, for the marker's "firing" state */
  dur: number;
}
export interface HeroSfx {
  type: "pop" | "whoosh" | "tick" | "riser" | "impact";
  s: number;
  e: number;
}

export interface PipelineStep {
  name: string;
  phase: 0 | 1 | 2 | 3;
  /** path relative to the repo root; null when the step writes no file */
  file: string | null;
  note: string;
  lang: "md" | "json" | "html" | "sh" | "chat";
  code: string;
}

export interface CostRow {
  piece: string;
  voice: string;
  first: number;
  total: number;
  firstLabel: string;
  totalLabel: string;
  tokens: string;
  cost: string;
  costFirst: string;
  render: string;
}

const CLONE = "git clone https://github.com/eusilvio/motion-cena.git";

const pt = {
  lang: "pt-BR",
  decimal: ",",
  hero: {
    title: ["Você manda a ideia.", "A fala manda no tempo."],
    lead: "Um agente de código escreve o roteiro, grava a locução, anima cada cena no quadro em que a palavra é dita e entrega o MP4 pronto pra postar.",
    clone: CLONE,
    copy: "Copiar",
    copied: "Copiado",
    copyLabel: "Copiar o comando git clone",
    guide: "Ler o guia",
    suiteLabel: "Demonstração: timeline ancorada na fala",
    tracks: { voice: "voz", scene: "cena", emphasis: "ênfase", sfx: "efeito" },
    play: "Reproduzir",
    pause: "Pausar",
    playhead: "Cursor de tempo",
    wordsLabel: "Palavras da locução",
    frameLabel: "quadro",
    caption:
      "Cada ênfase está presa a uma palavra da locução. Arraste o cursor de tempo ou clique numa palavra: o mesmo instante mostra sempre o mesmo quadro, como no render.",
    srStage:
      "Demonstração sem som. A frase aparece palavra por palavra no tempo da locução, e cada efeito dispara na palavra a que está preso.",
    duration: 8,
    words: [
      { w: "A", s: 0.24, e: 0.34 },
      { w: "locução", s: 0.36, e: 0.92 },
      { w: "sai", s: 0.96, e: 1.18 },
      { w: "antes", s: 1.2, e: 1.52 },
      { w: "da", s: 1.54, e: 1.64 },
      { w: "animação.", s: 1.66, e: 2.3 },
      { w: "Cada", s: 2.64, e: 2.9 },
      { w: "palavra", s: 2.92, e: 3.36 },
      { w: "ganha", s: 3.38, e: 3.7 },
      { w: "um", s: 3.72, e: 3.82 },
      { w: "timestamp.", s: 3.84, e: 4.56 },
      { w: "A", s: 4.9, e: 4.98 },
      { w: "ênfase", s: 5.0, e: 5.46 },
      { w: "dispara", s: 5.48, e: 5.94 },
      { w: "no", s: 5.96, e: 6.06 },
      { w: "quadro", s: 6.08, e: 6.44 },
      { w: "exato.", s: 6.46, e: 7.1 },
    ] as HeroWord[],
    scenes: [
      { id: "s1", label: "s1 locução", start: 0, end: 2.5, lines: [{ words: [0, 1] }, { words: [2, 3, 4] }, { words: [5] }] },
      { id: "s2", label: "s2 timestamp", start: 2.5, end: 4.74, lines: [{ words: [6, 7] }, { words: [8, 9] }, { words: [10] }] },
      {
        id: "s3",
        label: "s3 quadro exato",
        start: 4.74,
        end: 8,
        lines: [{ words: [11, 12] }, { words: [13, 14] }, { words: [15] }, { words: [16], big: true }],
      },
    ] as HeroScene[],
    anchors: [
      { word: 1, effect: "slam", dur: 0.5 },
      { word: 10, effect: "stagger", dur: 0.55 },
      { word: 12, effect: "highlight", dur: 0.4 },
      { word: 16, effect: "punch zoom", dur: 0.65 },
    ] as HeroAnchor[],
    sfx: [
      { type: "pop", s: 0.36, e: 0.5 },
      { type: "whoosh", s: 2.25, e: 2.75 },
      { type: "tick", s: 3.84, e: 3.94 },
      { type: "riser", s: 4.89, e: 6.46 },
      { type: "impact", s: 6.46, e: 6.8 },
    ] as HeroSfx[],
  },

  ask: {
    title: "Faz o pedido",
    lead: "Fala com o agente como falaria com um editor. Pode escrever em qualquer idioma: o vídeo sai no idioma do pedido.",
    colAsk: "Você pede",
    colGet: "Sai",
    rows: [
      [
        "Faz um reels de 30 s explicando juros compostos. Pesquisa os fatos.",
        "pesquisa com fonte, roteiro com 3 hooks, locução, animação e o MP4 de Reels e TikTok",
      ],
      [
        "Transforma esse PDF num vídeo de dados no estilo do meu site.",
        "os melhores números do relatório, com a página de origem, nas cores e fontes do site",
      ],
      [
        "Analisa o app em ../loja e faz um vídeo de 40 s do produto.",
        "fatos, telas e marca tirados do próprio código, sem ler .env nem dado de produção",
      ],
      [
        "Anima em cima desse vídeo em que eu falo, com legenda palavra por palavra.",
        "a sua gravação como base, com legenda, palavra-chave e cards no ritmo da fala",
      ],
      ["Faz em carrossel de 7 slides.", "capa com gancho, um slide por ideia, PNG por slide, legenda e texto alternativo"],
      [
        "Título entra com slide in em 0,4 s ease out, benefícios com stagger de 0,15 s.",
        "exatamente isso: o dicionário traduz cada termo em código",
      ],
    ] as [string, string][],
    iterate: "Depois é iterar:",
    iterations: ["troca pelo hook B", "tira a música", "divide em 3 stories", "faz a versão pro YouTube"],
  },

  pipeline: {
    title: "Do pedido ao MP4",
    lead: "Cada etapa grava um arquivo em projects/<slug>/. Dá para parar, revisar e pedir só o pedaço que mudou. Abaixo, o pedido de juros compostos etapa por etapa.",
    phases: ["direção", "revisão", "produção", "entrega"],
    listLabel: "Etapas do pipeline",
    noFile: "nenhum arquivo novo",
    steps: [
      {
        name: "Brief",
        phase: 0,
        file: "projects/juros-compostos/brief.md",
        note: "Modo de entrada, gênero, plataforma, duração e de onde vêm marca e voz.",
        lang: "md",
        code: `# Juros compostos em 30 s

- Modo de entrada: tema (pesquisa na web, fontes em source/research.md)
- Gênero: explicativo
- Plataforma: vertical (Reels + TikTok), 1080×1920, 30 fps
- Duração-alvo: 30 s (pedido)
- Público e tom: quem guarda dinheiro parado; tom direto
- Marca: nenhuma no pedido, a direção visual vem da ideia central
- Voz: edge-tts, pt-BR-FranciscaNeural`,
      },
      {
        name: "Formato narrativo",
        phase: 0,
        file: "projects/juros-compostos/plan.md",
        note: "Testa o mesmo conteúdo em quatro formatos ou mais e escolhe um, com o motivo.",
        lang: "md",
        code: `## Análise de formato
### Comparação
Ângulo: R$ 1.000 parados contra R$ 1.000 a 1% ao mês.
Tensão: a diferença começa em R$ 10 e cresce sozinha.
### Experimento
### Explicação por analogia
### Listicle

**Escolhido:** comparação. Dois saldos lado a lado mostram
a diferença sem precisar de fórmula.`,
      },
      {
        name: "Roteiro + 3 hooks",
        phase: 0,
        file: "projects/juros-compostos/plan.md",
        note: "Três ganchos com nota no teste de lacuna e a narração dentro do orçamento de palavras da duração.",
        lang: "md",
        code: `## Roteiro
**Hook recomendado:** A

- Hook A (contra a crença, nota 9): Mil reais parados
  continuam mil reais. A 1% ao mês, em cinco anos, viram 1.817.
- Hook B (lacuna, nota 8): No primeiro mês você ganha
  10 reais. No mês 60, ganha 18.
- Hook C (informa demais, nota 4): Juro composto é juro
  em cima de juro.

Palavras: 74, orçamento para 30 s: 75
Duração estimada: 29 s`,
      },
      {
        name: "Ideia central",
        phase: 0,
        file: "projects/juros-compostos/plan.md",
        note: "Três ideias com dispositivos diferentes. O registro de vídeos anteriores veta a que repete.",
        lang: "md",
        code: `## Ideia central
Ideia A: o vídeo inteiro é um extrato bancário que ganha
  uma linha por mês.
Ideia B: um cofre de vidro enchendo de moedas.
  Vetada: repete um vídeo do registro.
Ideia C: uma régua de 60 meses que vira gráfico.

**Escolhida:** A. Abre no extrato com R$ 1.000, cada mês
soma uma linha e o saldo faz count-up até R$ 1.817.`,
      },
      {
        name: "Storyboard",
        phase: 0,
        file: "projects/juros-compostos/storyboard.json",
        note: "O contrato entre história e animação: trecho da fala, visual, movimento e a palavra que dispara cada ênfase.",
        lang: "json",
        code: `{
  "id": "s5",
  "narration": "Em cinco anos, viram mil oitocentos e dezessete.",
  "visual": "Linha 60 do extrato, saldo em destaque.",
  "motion": "saldo: count-up 0,8 s power2.out",
  "anchors": [
    { "id": "saldo", "phrase": "mil oitocentos e dezessete", "effect": "count-up" }
  ],
  "sfx": [
    { "type": "riser", "at": "anchor:saldo", "offset": -1.6 },
    { "type": "impact", "at": "anchor:saldo" }
  ]
}`,
      },
      {
        name: "Revisão",
        phase: 1,
        file: null,
        note: "O agente mostra o plan.md e espera você aprovar antes de gastar crédito de voz e render. Se você pediu “faz tudo direto”, ele segue e anota que pulou a revisão.",
        lang: "chat",
        code: `agente  O plano está em projects/juros-compostos/plan.md:
        hook A, ideia do extrato, 74 palavras, 29 s.
        Posso gravar a locução?
você    pode, mas usa o hook B`,
      },
      {
        name: "Marca",
        phase: 2,
        file: "projects/juros-compostos/brand.json",
        note: "Cores, fontes e tokens de movimento. Sem marca no pedido, tudo sai da ideia central.",
        lang: "json",
        code: `{
  "source": "ideia central: extrato bancário",
  "colors": {
    "bg": "#F4F1EA",
    "text": "#1B1D21",
    "primary": "#1F7A4D",
    "negative": "#C2413B"
  },
  "fonts": {
    "display": { "family": "IBM Plex Mono", "weights": [500, 700], "source": "google" },
    "body": { "family": "Inter", "weights": [400, 600], "source": "google" }
  },
  "motion": { "ease_in": "power3.out", "ease_out": "power2.in", "base_duration": 0.45 }
}`,
      },
      {
        name: "Locução com timestamps",
        phase: 2,
        file: "projects/juros-compostos/audio/words.json",
        note: "A voz sai antes da animação, e cada palavra ganha início e fim em segundos.",
        lang: "sh",
        code: `$ uv run scripts/tts_edge.py --text-file projects/juros-compostos/narration.txt \\
    --voice pt-BR-FranciscaNeural --out projects/juros-compostos/audio
voice.mp3 + words.json (75 words, ~28.9s) -> projects/juros-compostos/audio

[
  {"word": "No", "start": 0.12, "end": 0.24},
  {"word": "primeiro", "start": 0.25, "end": 0.66},
  {"word": "mês", "start": 0.67, "end": 0.95},
  {"word": "você", "start": 0.98, "end": 1.21},
  {"word": "ganha", "start": 1.22, "end": 1.53},`,
      },
      {
        name: "Timeline",
        phase: 2,
        file: "projects/juros-compostos/timeline.json",
        note: "Cada cena e cada ênfase presas às palavras ditas, em segundos e em quadros.",
        lang: "sh",
        code: `$ uv run scripts/build_timeline.py projects/juros-compostos/storyboard.json \\
    projects/juros-compostos/audio/words.json --fps 30 \\
    --out projects/juros-compostos/timeline.json
7 scenes, 12 sfx cues, 29.40s @ 30fps -> projects/juros-compostos/timeline.json

"anchors": [
  {
    "id": "saldo",
    "phrase": "mil oitocentos e dezessete",
    "effect": "count-up",
    "start": 24.62,
    "end": 26.1,
    "startFrame": 739,
    "endFrame": 783
  }
]`,
      },
      {
        name: "Animação",
        phase: 2,
        file: "projects/juros-compostos/video/index.html",
        note: "Composição HyperFrames com uma timeline GSAP pausada. O render pede cada quadro pelo tempo, então a ênfase cai no quadro da palavra.",
        lang: "html",
        code: `<section id="s5" class="clip" data-start="22.9" data-duration="4.1">
  <p class="saldo">R$ <span id="saldo">1.000</span></p>
</section>

<script>
  const tl = gsap.timeline({ paused: true });
  const saldo = document.querySelector("#saldo");
  const conta = { v: 1000 };
  // quadro 739: a voz diz "mil oitocentos e dezessete"
  tl.to(conta, {
    v: 1817, duration: 0.8, ease: "power2.out",
    onUpdate: () => (saldo.textContent = conta.v.toFixed(0)),
  }, 24.62);
  window.__timelines["main"] = tl;
</script>`,
      },
      {
        name: "Som",
        phase: 2,
        file: "projects/juros-compostos/audio/mix.wav",
        note: "Cada efeito sonoro marca um evento visual, a voz fica sempre por cima e o mix final sai a −14 LUFS.",
        lang: "sh",
        code: `$ uv run scripts/synth_sfx.py --only whoosh,pop,riser,impact \\
    --out projects/juros-compostos/audio/sfx
$ uv run scripts/mix_audio.py projects/juros-compostos/timeline.json \\
    --voice projects/juros-compostos/audio/voice.mp3 \\
    --sfx-dir projects/juros-compostos/audio/sfx \\
    --out projects/juros-compostos/audio/mix.wav
mix: voice + 12 sfx, 29.40s -> projects/juros-compostos/audio/mix.wav`,
      },
      {
        name: "Zona segura",
        phase: 3,
        file: null,
        note: "Percorre o vídeo a cada 0,25 s e reprova texto, card ou logo que fica na área da interface. O render só sai com zero erro.",
        lang: "sh",
        code: `$ uv run scripts/safe_zone_check.py projects/juros-compostos/video --preset vertical
== projects/juros-compostos/video vs vertical (zona: topo 288 · base 672 · esq 65 · dir 192 px) · 29.4s a cada 0.25s
0 erro(s), 0 aviso(s)`,
      },
      {
        name: "Render",
        phase: 3,
        file: "creatives/reels/juros-compostos-ig-reels.mp4",
        note: "Um render vertical serve Reels, TikTok e Shorts. O vídeo sai em creatives/, fora da pasta do projeto.",
        lang: "sh",
        code: `$ cd projects/juros-compostos/video
$ npx hyperframes render -o ../../../creatives/reels/juros-compostos-ig-reels.mp4

creatives/reels/
  juros-compostos-ig-reels.mp4   1080×1920, 30 fps, 29,4 s
  juros-compostos-tiktok.mp4     cópia: a zona vertical já cobre o TikTok`,
      },
      {
        name: "QA",
        phase: 3,
        file: "projects/juros-compostos/out/juros-compostos_contact.jpg",
        note: "Confere canvas, fps, duração, codec e loudness, e gera a contact sheet com a zona da interface pintada de vermelho.",
        lang: "sh",
        code: `$ QA_DIR=projects/juros-compostos/out bash scripts/qa_video.sh \\
    creatives/reels/juros-compostos-ig-reels.mp4 ig-reels
== creatives/reels/juros-compostos-ig-reels.mp4
  OK   resolution 1080x1920 (expected 1080x1920)
  OK   fps 30.00 (expected 30)
  OK   video codec h264 / yuv420p (want h264 / yuv420p)
  OK   audio track aac
  INFO duration 29.40s
  OK   duration <= 180s (preset ig-reels)
  OK   loudness -14.1 LUFS (want -16..-12)
  OK   true peak -1.3 dBTP (want <= -1)
  OK   no silent gaps > 1.5s (found 0)
RESULT: PASS (now review the images)`,
      },
    ] as PipelineStep[],
  },

  teaser: {
    effectsTitle: "Um dicionário para pedir movimento",
    effectsBody:
      "São 44 efeitos curados, renderizados pelo próprio pipeline, e um catálogo de 388 em 16 famílias. Cada um tem duração, ease e código GSAP seguro para render. Para pedir: efeito, duração, ease e alvo.",
    effectsLink: "Abrir o explorador de efeitos",
    videoPlay: "Ver a demo",
    videoNote: "26 efeitos da parte 2 do dicionário, 70 s, sem som",
    zoneTitle: "Nada fica embaixo dos botões",
    zoneBody:
      "Um medidor percorre o vídeo a cada quarto de segundo e reprova texto, card ou logo que entra na área da interface do Reels, TikTok ou Shorts.",
    zoneLink: "Testar a zona segura",
    zoneEdges: { top: "topo", bottom: "base", left: "esq.", right: "dir." },
    zoneCard: "R$ 1.817",
    zoneError: "ERRO",
  },

  start: {
    title: "Monta o set",
    lead: "Precisa de Node 22+, FFmpeg, uv e um agente de código.",
    steps: [
      { label: "Clona o repositório", lines: [CLONE, "cd motion-cena"], note: "" },
      {
        label: "Prepara a máquina",
        lines: ["./setup.sh"],
        note: "Confere Node, FFmpeg, uv e o agente, cria as pastas locais e o .env.local.",
      },
      {
        label: "Abre o agente na pasta",
        lines: ["claude"],
        note: "Ou codex, agy, opencode, ou abre a pasta no Cursor, Windsurf ou VS Code com Copilot.",
      },
    ],
    copy: "Copiar",
    copied: "Copiado",
    copyStep: "Copiar os comandos do passo",
    keys: "Sem chave nenhuma o pipeline roda inteiro: voz grátis pelo edge-tts e efeitos sonoros sintetizados na sua máquina. Com ELEVENLABS_API_KEY no .env.local, a voz sobe de nível e dá pra clonar a sua.",
    windowsTitle: "No Windows",
    windows:
      "Use o WSL 2: o pipeline roda inteiro, igual no Linux. O setup.ps1 prepara a pasta pelo PowerShell, mas no Windows nativo parte do fluxo não roda.",
    windowsLink: "Passo a passo no Windows",
    firstTitle: "Depois, o primeiro pedido",
    first: "Faz um reels de 30 s explicando juros compostos. Pesquisa os fatos.",
    firstLink: "Guia do primeiro vídeo",
  },

  cost: {
    title: "Quanto leva e quanto custa",
    lead: "Números de produções reais feitas com este repositório no Claude Code (Opus 5.5), entre 20/10 e 04/11/2026, num notebook comum. Servem de ordem de grandeza: os seus vão variar.",
    colPiece: "Peça",
    colTime: "Tempo do agente",
    colTokens: "Tokens no total",
    colCost: "Custo equivalente na API",
    colRender: "Render",
    legendFirst: "até a 1ª entrega",
    legendTotal: "com os ajustes",
    unit: "min",
    rows: [
      {
        piece: "Reels de 30 s a partir do código de um produto",
        voice: "Voz ElevenLabs",
        first: 30,
        total: 42,
        firstLabel: "30 min",
        totalLabel: "42 min (1 ajuste)",
        tokens: "24,8 M",
        cost: "US$ 10,58",
        costFirst: "US$ 8,37 na 1ª entrega",
        render: "2 min 18 s",
      },
      {
        piece: "Reels de 46 s a partir do código de um produto, com trilha",
        voice: "Voz e trilha ElevenLabs",
        first: 25,
        total: 41,
        firstLabel: "25 min",
        totalLabel: "41 min (1 ajuste)",
        tokens: "25,2 M",
        cost: "US$ 12,18",
        costFirst: "US$ 8,03 na 1ª entrega",
        render: "2 min 20 s a 2 min 32 s",
      },
      {
        piece: "Carrossel de 6 slides a partir de um texto pronto, com checagem dos números na web",
        voice: "Sem voz",
        first: 3,
        total: 7,
        firstLabel: "3 min",
        totalLabel: "7 min (2 ajustes)",
        tokens: "8,5 M",
        cost: "US$ 3,22",
        costFirst: "US$ 1,24 na 1ª entrega",
        render: "5 s (PNG)",
      },
    ] as CostRow[],
    notes:
      "Os minutos contam o tempo em que o agente estava trabalhando, do seu pedido até a última ação dele. Cada rodada de ajuste nos vídeos somou de 12 a 16 min e de 8 a 10 M tokens (US$ 2 a 4).",
    tip: "Para gastar menos, faça uma peça por sessão: a cada pedido o agente relê a conversa inteira, e tudo fica gravado em projects/<slug>/ para a sessão seguinte continuar.",
    link: "Cada etapa medida, voz e planos do Claude",
  },

  agents: {
    title: "Qualquer agente",
    lead: "O pipeline é texto e linha de comando. Qualquer agente que lê arquivos e roda comandos no terminal consegue dirigir.",
    rows: [
      { file: "AGENTS.md", names: ["Codex", "Antigravity", "Cursor", "GitHub Copilot", "OpenCode", "Windsurf"], note: "" },
      { file: "CLAUDE.md", names: ["Claude Code"], note: "importa o AGENTS.md" },
    ],
    note: "Ferramenta que só existe num agente, como o Claude Design ou um conector MCP, é opcional: a skill sempre descreve o caminho que funciona em qualquer um.",
    link: "Como cada agente lê o projeto",
  },

  cta: {
    title: "Cena 01, tomada 1.",
    body: "Código, skill e documentação estão no GitHub, sob licença MIT. Efeito novo no dicionário, receita de estilo ou relato de instalação numa máquina diferente: tudo isso ajuda.",
    github: "Abrir no GitHub",
    contribute: "Como contribuir",
  },

  links: {
    guide: "/guia/introducao",
    effects: "/efeitos",
    platforms: "/referencia/plataformas",
    windows: "/guia/windows",
    firstVideo: "/guia/primeiro-video",
    cost: "/guia/custo-e-tempo",
    agents: "/guia/agentes",
    contribute: "/comunidade/contribuir",
  },
};

export type LandingCopy = typeof pt;
export type HeroCopy = LandingCopy["hero"];

const en: LandingCopy = {
  lang: "en-US",
  decimal: ".",
  hero: {
    title: ["You send the idea.", "The voice sets the timing."],
    lead: "A coding agent writes the script, records the voiceover, animates each scene on the frame where the word is spoken and delivers the MP4 ready to post.",
    clone: CLONE,
    copy: "Copy",
    copied: "Copied",
    copyLabel: "Copy the git clone command",
    guide: "Read the guide",
    suiteLabel: "Demo: a timeline anchored to the speech",
    tracks: { voice: "voice", scene: "scene", emphasis: "emphasis", sfx: "sfx" },
    play: "Play",
    pause: "Pause",
    playhead: "Playhead",
    wordsLabel: "Voiceover words",
    frameLabel: "frame",
    caption:
      "Each emphasis is pinned to a word of the voiceover. Drag the playhead or click a word: the same instant always shows the same frame, as in the render.",
    srStage:
      "Silent demo. The sentence appears word by word in the timing of the voiceover, and each effect fires on the word it is pinned to.",
    duration: 8,
    words: [
      { w: "The", s: 0.24, e: 0.36 },
      { w: "voice", s: 0.38, e: 0.86 },
      { w: "comes", s: 0.9, e: 1.24 },
      { w: "first.", s: 1.26, e: 1.92 },
      { w: "Every", s: 2.3, e: 2.58 },
      { w: "word", s: 2.6, e: 2.92 },
      { w: "gets", s: 2.94, e: 3.2 },
      { w: "a", s: 3.22, e: 3.3 },
      { w: "timestamp.", s: 3.32, e: 4.1 },
      { w: "Each", s: 4.5, e: 4.72 },
      { w: "emphasis", s: 4.74, e: 5.34 },
      { w: "fires", s: 5.36, e: 5.7 },
      { w: "on", s: 5.72, e: 5.82 },
      { w: "the", s: 5.84, e: 5.94 },
      { w: "exact", s: 5.96, e: 6.4 },
      { w: "frame.", s: 6.42, e: 6.96 },
    ],
    scenes: [
      { id: "s1", label: "s1 voice", start: 0, end: 2.12, lines: [{ words: [0, 1] }, { words: [2] }, { words: [3] }] },
      { id: "s2", label: "s2 timestamp", start: 2.12, end: 4.32, lines: [{ words: [4, 5] }, { words: [6, 7] }, { words: [8] }] },
      {
        id: "s3",
        label: "s3 exact frame",
        start: 4.32,
        end: 8,
        lines: [{ words: [9] }, { words: [10] }, { words: [11, 12, 13] }, { words: [14], big: true }, { words: [15] }],
      },
    ],
    anchors: [
      { word: 1, effect: "slam", dur: 0.5 },
      { word: 8, effect: "stagger", dur: 0.55 },
      { word: 10, effect: "highlight", dur: 0.4 },
      { word: 14, effect: "punch zoom", dur: 0.65 },
    ],
    sfx: [
      { type: "pop", s: 0.38, e: 0.52 },
      { type: "whoosh", s: 1.87, e: 2.37 },
      { type: "tick", s: 3.32, e: 3.42 },
      { type: "riser", s: 4.39, e: 5.96 },
      { type: "impact", s: 5.96, e: 6.3 },
    ],
  },

  ask: {
    title: "Make the request",
    lead: "Talk to the agent the way you would talk to a video editor. Write in any language: the video comes out in the language you wrote in.",
    colAsk: "You ask",
    colGet: "You get",
    rows: [
      [
        "Make a 30 s Reels explaining compound interest. Research the facts.",
        "sourced research, a script with 3 hooks, voiceover, animation and the MP4 for Reels and TikTok",
      ],
      [
        "Turn this PDF into a data video in my website's style.",
        "the best numbers from the report, with the source page, in the website's colors and fonts",
      ],
      [
        "Analyze the app in ../loja and make a 40 s product video.",
        "facts, screens and brand taken from the code itself, without reading .env or production data",
      ],
      [
        "Animate over this video of me talking, with word-by-word captions.",
        "your recording as the base, with captions, keywords and cards in the rhythm of the speech",
      ],
      ["Make it a 7-slide carousel.", "a cover with a hook, one slide per idea, a PNG per slide, post caption and alt text"],
      [
        "Title enters with a slide in, 0.4 s ease out, benefits with a 0.15 s stagger.",
        "exactly that: the dictionary turns each term into code",
      ],
    ],
    iterate: "Then you iterate:",
    iterations: ["switch to hook B", "drop the music", "split it into 3 stories", "make the YouTube version"],
  },

  pipeline: {
    title: "From request to MP4",
    lead: "Every step writes a file in projects/<slug>/. You can stop, review and ask for only the part that changed. Below, the compound interest request, step by step.",
    phases: ["direction", "review", "production", "delivery"],
    listLabel: "Pipeline steps",
    noFile: "no new file",
    steps: [
      {
        name: "Brief",
        phase: 0,
        file: "projects/compound-interest/brief.md",
        note: "Input mode, genre, platform, duration and where the brand and voice come from.",
        lang: "md",
        code: `# Compound interest in 30 s

- Input mode: tema (web research, sources in source/research.md)
- Genre: explainer
- Platform: vertical (Reels + TikTok), 1080×1920, 30 fps
- Target duration: 30 s (requested)
- Audience and tone: people with savings sitting idle; direct
- Brand: none in the request, visual direction comes from the central idea
- Voice: edge-tts, en-US-AriaNeural`,
      },
      {
        name: "Narrative format",
        phase: 0,
        file: "projects/compound-interest/plan.md",
        note: "Tests the same content in four formats or more and picks one, with the reason.",
        lang: "md",
        code: `## Format analysis
### Comparison
Angle: $1,000 sitting still against $1,000 at 1% a month.
Tension: the gap starts at $10 and grows on its own.
### Experiment
### Explanation by analogy
### Listicle

**Chosen:** comparison. Two balances side by side show
the gap without a formula.`,
      },
      {
        name: "Script + 3 hooks",
        phase: 0,
        file: "projects/compound-interest/plan.md",
        note: "Three hooks scored on the gap test, and narration inside the word budget for the duration.",
        lang: "md",
        code: `## Script
**Recommended hook:** A

- Hook A (against the belief, score 9): $1,000 sitting still
  stays $1,000. At 1% a month, in five years, it is $1,817.
- Hook B (gap, score 8): In month one you earn $10.
  In month 60, you earn $18.
- Hook C (gives it away, score 4): Compound interest is
  interest on interest.

Words: 74, budget for 30 s: 75
Estimated duration: 29 s`,
      },
      {
        name: "Central idea",
        phase: 0,
        file: "projects/compound-interest/plan.md",
        note: "Three ideas with different devices. The log of earlier videos vetoes the one that repeats.",
        lang: "md",
        code: `## Central idea
Idea A: the whole video is a bank statement that gains
  one line per month.
Idea B: a glass jar filling up with coins.
  Vetoed: repeats a video in the log.
Idea C: a 60-month ruler that turns into a chart.

**Chosen:** A. Opens on a statement at $1,000, each month
adds a line and the balance counts up to $1,817.`,
      },
      {
        name: "Storyboard",
        phase: 0,
        file: "projects/compound-interest/storyboard.json",
        note: "The contract between story and animation: speech excerpt, visual, motion and the word that fires each emphasis.",
        lang: "json",
        code: `{
  "id": "s5",
  "narration": "In five years, it becomes one thousand eight hundred seventeen.",
  "visual": "Line 60 of the statement, balance highlighted.",
  "motion": "balance: count-up 0.8 s power2.out",
  "anchors": [
    { "id": "balance", "phrase": "one thousand eight hundred seventeen", "effect": "count-up" }
  ],
  "sfx": [
    { "type": "riser", "at": "anchor:balance", "offset": -1.6 },
    { "type": "impact", "at": "anchor:balance" }
  ]
}`,
      },
      {
        name: "Review",
        phase: 1,
        file: null,
        note: "The agent shows plan.md and waits for your approval before spending voice and render credits. If you asked to “do it all straight through”, it goes on and notes that review was skipped.",
        lang: "chat",
        code: `agent   The plan is in projects/compound-interest/plan.md:
        hook A, the statement idea, 74 words, 29 s.
        Can I record the voiceover?
you     yes, but use hook B`,
      },
      {
        name: "Brand",
        phase: 2,
        file: "projects/compound-interest/brand.json",
        note: "Colors, fonts and motion tokens. With no brand in the request, all of it comes from the central idea.",
        lang: "json",
        code: `{
  "source": "central idea: bank statement",
  "colors": {
    "bg": "#F4F1EA",
    "text": "#1B1D21",
    "primary": "#1F7A4D",
    "negative": "#C2413B"
  },
  "fonts": {
    "display": { "family": "IBM Plex Mono", "weights": [500, 700], "source": "google" },
    "body": { "family": "Inter", "weights": [400, 600], "source": "google" }
  },
  "motion": { "ease_in": "power3.out", "ease_out": "power2.in", "base_duration": 0.45 }
}`,
      },
      {
        name: "Voiceover with timestamps",
        phase: 2,
        file: "projects/compound-interest/audio/words.json",
        note: "The voice is made before the animation, and every word gets a start and an end in seconds.",
        lang: "sh",
        code: `$ uv run scripts/tts_edge.py --text-file projects/compound-interest/narration.txt \\
    --voice en-US-AriaNeural --out projects/compound-interest/audio
voice.mp3 + words.json (75 words, ~28.9s) -> projects/compound-interest/audio

[
  {"word": "In", "start": 0.12, "end": 0.22},
  {"word": "month", "start": 0.23, "end": 0.55},
  {"word": "one", "start": 0.56, "end": 0.8},
  {"word": "you", "start": 0.83, "end": 0.96},
  {"word": "earn", "start": 0.97, "end": 1.28},`,
      },
      {
        name: "Timeline",
        phase: 2,
        file: "projects/compound-interest/timeline.json",
        note: "Every scene and every emphasis pinned to the spoken words, in seconds and in frames.",
        lang: "sh",
        code: `$ uv run scripts/build_timeline.py projects/compound-interest/storyboard.json \\
    projects/compound-interest/audio/words.json --fps 30 \\
    --out projects/compound-interest/timeline.json
7 scenes, 12 sfx cues, 29.40s @ 30fps -> projects/compound-interest/timeline.json

"anchors": [
  {
    "id": "balance",
    "phrase": "one thousand eight hundred seventeen",
    "effect": "count-up",
    "start": 24.62,
    "end": 26.1,
    "startFrame": 739,
    "endFrame": 783
  }
]`,
      },
      {
        name: "Animation",
        phase: 2,
        file: "projects/compound-interest/video/index.html",
        note: "A HyperFrames composition with one paused GSAP timeline. The render asks for each frame by time, so the emphasis lands on the word's frame.",
        lang: "html",
        code: `<section id="s5" class="clip" data-start="22.9" data-duration="4.1">
  <p class="balance">$<span id="balance">1,000</span></p>
</section>

<script>
  const tl = gsap.timeline({ paused: true });
  const balance = document.querySelector("#balance");
  const count = { v: 1000 };
  // frame 739: the voice says "one thousand eight hundred seventeen"
  tl.to(count, {
    v: 1817, duration: 0.8, ease: "power2.out",
    onUpdate: () => (balance.textContent = count.v.toFixed(0)),
  }, 24.62);
  window.__timelines["main"] = tl;
</script>`,
      },
      {
        name: "Sound",
        phase: 2,
        file: "projects/compound-interest/audio/mix.wav",
        note: "Each sound effect marks a visual event, the voice always sits on top and the final mix lands at −14 LUFS.",
        lang: "sh",
        code: `$ uv run scripts/synth_sfx.py --only whoosh,pop,riser,impact \\
    --out projects/compound-interest/audio/sfx
$ uv run scripts/mix_audio.py projects/compound-interest/timeline.json \\
    --voice projects/compound-interest/audio/voice.mp3 \\
    --sfx-dir projects/compound-interest/audio/sfx \\
    --out projects/compound-interest/audio/mix.wav
mix: voice + 12 sfx, 29.40s -> projects/compound-interest/audio/mix.wav`,
      },
      {
        name: "Safe zone",
        phase: 3,
        file: null,
        note: "Steps through the video every 0.25 s and fails any text, card or logo that stays in the interface area. The render only goes out with zero errors.",
        lang: "sh",
        code: `$ uv run scripts/safe_zone_check.py projects/compound-interest/video --preset vertical
== projects/compound-interest/video vs vertical (zona: topo 288 · base 672 · esq 65 · dir 192 px) · 29.4s a cada 0.25s
0 erro(s), 0 aviso(s)`,
      },
      {
        name: "Render",
        phase: 3,
        file: "creatives/reels/compound-interest-ig-reels.mp4",
        note: "One vertical render serves Reels, TikTok and Shorts. The video goes to creatives/, outside the project folder.",
        lang: "sh",
        code: `$ cd projects/compound-interest/video
$ npx hyperframes render -o ../../../creatives/reels/compound-interest-ig-reels.mp4

creatives/reels/
  compound-interest-ig-reels.mp4   1080×1920, 30 fps, 29.4 s
  compound-interest-tiktok.mp4     copy: the vertical zone already covers TikTok`,
      },
      {
        name: "QA",
        phase: 3,
        file: "projects/compound-interest/out/compound-interest_contact.jpg",
        note: "Checks canvas, fps, duration, codec and loudness, and makes the contact sheet with the interface area painted red.",
        lang: "sh",
        code: `$ QA_DIR=projects/compound-interest/out bash scripts/qa_video.sh \\
    creatives/reels/compound-interest-ig-reels.mp4 ig-reels
== creatives/reels/compound-interest-ig-reels.mp4
  OK   resolution 1080x1920 (expected 1080x1920)
  OK   fps 30.00 (expected 30)
  OK   video codec h264 / yuv420p (want h264 / yuv420p)
  OK   audio track aac
  INFO duration 29.40s
  OK   duration <= 180s (preset ig-reels)
  OK   loudness -14.1 LUFS (want -16..-12)
  OK   true peak -1.3 dBTP (want <= -1)
  OK   no silent gaps > 1.5s (found 0)
RESULT: PASS (now review the images)`,
      },
    ],
  },

  teaser: {
    effectsTitle: "A dictionary for asking for motion",
    effectsBody:
      "There are 44 curated effects, rendered by the pipeline itself, and a catalog of 388 in 16 families. Each one has a duration, an ease and render-safe GSAP code. To ask for one: effect, duration, ease and target.",
    effectsLink: "Open the effects explorer",
    videoPlay: "Watch the demo",
    videoNote: "26 effects from part 2 of the dictionary, 70 s, silent",
    zoneTitle: "Nothing ends up under the buttons",
    zoneBody:
      "A checker scans the video every quarter of a second and fails any text, card or logo that enters the Reels, TikTok or Shorts interface area.",
    zoneLink: "Try the safe zone",
    zoneEdges: { top: "top", bottom: "bottom", left: "left", right: "right" },
    zoneCard: "$1,817",
    zoneError: "ERRO",
  },

  start: {
    title: "Build the set",
    lead: "You need Node 22+, FFmpeg, uv and a coding agent.",
    steps: [
      { label: "Clone the repository", lines: [CLONE, "cd motion-cena"], note: "" },
      {
        label: "Prepare the machine",
        lines: ["./setup.sh"],
        note: "Checks Node, FFmpeg, uv and the agent, and creates the local folders and .env.local.",
      },
      {
        label: "Open the agent in the folder",
        lines: ["claude"],
        note: "Or codex, agy, opencode, or open the folder in Cursor, Windsurf or VS Code with Copilot.",
      },
    ],
    copy: "Copy",
    copied: "Copied",
    copyStep: "Copy this step's commands",
    keys: "With no API key at all, the whole pipeline runs: free voice through edge-tts and sound effects synthesized on your machine. With ELEVENLABS_API_KEY in .env.local, the voice gets better and you can clone your own.",
    windowsTitle: "On Windows",
    windows:
      "Use WSL 2: the whole pipeline runs, same as on Linux. setup.ps1 prepares the folder from PowerShell, but on native Windows part of the flow does not run.",
    windowsLink: "Windows step by step",
    firstTitle: "Then, the first request",
    first: "Make a 30 s Reels explaining compound interest. Research the facts.",
    firstLink: "First video guide",
  },

  cost: {
    title: "How long it takes and what it costs",
    lead: "Numbers from real productions made with this repository in Claude Code (Opus 5.5), between Oct 20 and Nov 4, 2026, on an ordinary laptop. Treat them as an order of magnitude: yours will vary.",
    colPiece: "Piece",
    colTime: "Agent time",
    colTokens: "Total tokens",
    colCost: "Equivalent API cost",
    colRender: "Render",
    legendFirst: "to 1st delivery",
    legendTotal: "with revisions",
    unit: "min",
    rows: [
      {
        piece: "30 s Reels from a product's code",
        voice: "ElevenLabs voice",
        first: 30,
        total: 42,
        firstLabel: "30 min",
        totalLabel: "42 min (1 revision)",
        tokens: "24.8 M",
        cost: "US$ 10.58",
        costFirst: "US$ 8.37 at 1st delivery",
        render: "2 min 18 s",
      },
      {
        piece: "46 s Reels from a product's code, with a music track",
        voice: "ElevenLabs voice and music",
        first: 25,
        total: 41,
        firstLabel: "25 min",
        totalLabel: "41 min (1 revision)",
        tokens: "25.2 M",
        cost: "US$ 12.18",
        costFirst: "US$ 8.03 at 1st delivery",
        render: "2 min 20 s to 2 min 32 s",
      },
      {
        piece: "6-slide carousel from finished text, with the numbers checked on the web",
        voice: "No voice",
        first: 3,
        total: 7,
        firstLabel: "3 min",
        totalLabel: "7 min (2 revisions)",
        tokens: "8.5 M",
        cost: "US$ 3.22",
        costFirst: "US$ 1.24 at 1st delivery",
        render: "5 s (PNG)",
      },
    ],
    notes:
      "The minutes count the time the agent was working, from your request to its last action. Each revision round on the videos added 12 to 16 min and 8 to 10 M tokens (US$ 2 to 4).",
    tip: "To spend less, make one piece per session: every request re-reads the whole conversation, and everything is saved in projects/<slug>/ so the next session picks up where it left off.",
    link: "Per-step timings, voice and Claude plans",
  },

  agents: {
    title: "Any agent",
    lead: "The pipeline is text and command line. Any agent that reads files and runs commands in a terminal can drive it.",
    rows: [
      { file: "AGENTS.md", names: ["Codex", "Antigravity", "Cursor", "GitHub Copilot", "OpenCode", "Windsurf"], note: "" },
      { file: "CLAUDE.md", names: ["Claude Code"], note: "imports AGENTS.md" },
    ],
    note: "A tool that only exists in one agent, such as Claude Design or an MCP connector, is optional: the skill always describes the path that works in any of them.",
    link: "How each agent reads the project",
  },

  cta: {
    title: "Scene 01, take 1.",
    body: "Code, skill and docs are on GitHub, under the MIT license. A new effect for the dictionary, a style recipe or an install report from a different machine: all of it helps.",
    github: "Open on GitHub",
    contribute: "How to contribute",
  },

  links: {
    guide: "/en/guide/introduction",
    effects: "/en/effects",
    platforms: "/en/reference/platforms",
    windows: "/en/guide/windows",
    firstVideo: "/en/guide/first-video",
    cost: "/en/guide/cost-and-time",
    agents: "/en/guide/agents",
    contribute: "/en/community/contributing",
  },
};

export const REPO_URL = "https://github.com/eusilvio/motion-cena";
export const COPY: Record<Locale, LandingCopy> = { pt, en };
