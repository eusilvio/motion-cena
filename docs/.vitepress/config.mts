import { defineConfig } from "vitepress";
import { fileURLToPath } from "node:url";

const REPO = "https://github.com/eusilvio/motion-cena";
const BASE = "/motion-cena/";
const repoRoot = fileURLToPath(new URL("../../", import.meta.url));

/** pt-BR is the root locale (the project's main language); English lives under /en/. */
function sidebarPt() {
  return [
    {
      text: "Começando",
      items: [
        { text: "O que é", link: "/guia/introducao" },
        { text: "Instalação", link: "/guia/instalacao" },
        { text: "Windows", link: "/guia/windows" },
        { text: "Primeiro vídeo", link: "/guia/primeiro-video" },
      ],
    },
    {
      text: "Como funciona",
      items: [
        { text: "Do pedido ao MP4", link: "/guia/como-funciona" },
        { text: "Qualquer agente", link: "/guia/agentes" },
        { text: "Quanto leva e quanto custa", link: "/guia/custo-e-tempo" },
        { text: "Deu erro?", link: "/guia/deu-erro" },
      ],
    },
    {
      text: "Referência",
      items: [
        { text: "Explorador de efeitos", link: "/efeitos" },
        { text: "Plataformas e zona segura", link: "/referencia/plataformas" },
        { text: "Scripts", link: "/referencia/scripts" },
        { text: "Carrossel", link: "/referencia/carrossel" },
        { text: "Som", link: "/referencia/som" },
        { text: "Estilos de referência", link: "/referencia/estilos" },
        { text: "Atualizar o HyperFrames", link: "/referencia/atualizar-hyperframes" },
        { text: "Testes e checagens", link: "/referencia/testes" },
      ],
    },
    {
      text: "Comunidade",
      items: [
        { text: "Como contribuir", link: "/comunidade/contribuir" },
        { text: "Frentes abertas", link: "/comunidade/roadmap" },
      ],
    },
  ];
}

function sidebarEn() {
  return [
    {
      text: "Getting started",
      items: [
        { text: "What it is", link: "/en/guide/introduction" },
        { text: "Installation", link: "/en/guide/installation" },
        { text: "Windows", link: "/en/guide/windows" },
        { text: "First video", link: "/en/guide/first-video" },
      ],
    },
    {
      text: "How it works",
      items: [
        { text: "From request to MP4", link: "/en/guide/how-it-works" },
        { text: "Any agent", link: "/en/guide/agents" },
        { text: "Time and cost", link: "/en/guide/cost-and-time" },
        { text: "Troubleshooting", link: "/en/guide/troubleshooting" },
      ],
    },
    {
      text: "Reference",
      items: [
        { text: "Effects explorer", link: "/en/effects" },
        { text: "Platforms and safe zones", link: "/en/reference/platforms" },
        { text: "Scripts", link: "/en/reference/scripts" },
        { text: "Carousel", link: "/en/reference/carousel" },
        { text: "Sound", link: "/en/reference/sound" },
        { text: "Reference styles", link: "/en/reference/styles" },
        { text: "Updating HyperFrames", link: "/en/reference/update-hyperframes" },
        { text: "Tests and checks", link: "/en/reference/tests" },
      ],
    },
    {
      text: "Community",
      items: [
        { text: "Contributing", link: "/en/community/contributing" },
        { text: "Open fronts", link: "/en/community/roadmap" },
      ],
    },
  ];
}

export default defineConfig({
  title: "motion-cena",
  base: BASE,
  cleanUrls: true,
  appearance: "dark", // an edit suite: dark first, light available
  lastUpdated: true,
  // README assets live next to the site sources; package files are not pages.
  srcExclude: ["README.md", "node_modules/**"],

  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: `${BASE}favicon.svg` }],
    ["meta", { name: "theme-color", content: "#0f1012" }],
    ["link", { rel: "preconnect", href: "https://fonts.googleapis.com" }],
    ["link", { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "" }],
    [
      "link",
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Anton&family=Instrument+Sans:ital,wght@0,400..700;1,400..700&family=JetBrains+Mono:wght@400;500;700&display=swap",
      },
    ],
    ["meta", { property: "og:type", content: "website" }],
    ["meta", { property: "og:site_name", content: "motion-cena" }],
  ],

  markdown: {
    // containers without a title get pt-BR labels (every page sets explicit titles anyway)
    container: { tipLabel: "Dica", warningLabel: "Atenção", dangerLabel: "Cuidado", infoLabel: "Nota", detailsLabel: "Detalhes" },
  },

  vite: {
    // data loaders read the skill's own JSON (dictionary, platform presets) from the repo root
    server: { fs: { allow: [repoRoot] } },
  },

  themeConfig: {
    logo: { src: "/favicon.svg", alt: "" },
    search: {
      provider: "local",
      options: {
        locales: {
          root: {
            translations: {
              button: { buttonText: "Buscar", buttonAriaLabel: "Buscar" },
              modal: {
                displayDetails: "Exibir detalhes",
                resetButtonTitle: "Limpar busca",
                backButtonTitle: "Voltar",
                noResultsText: "Nada encontrado para",
                footer: { selectText: "abrir", navigateText: "navegar", closeText: "fechar" },
              },
            },
          },
        },
      },
    },
    socialLinks: [{ icon: "github", link: REPO }],
  },

  locales: {
    root: {
      label: "Português",
      lang: "pt-BR",
      description:
        "Você manda a ideia. Um agente de código escreve o roteiro, grava a locução, anima cada cena no tempo da fala e entrega o MP4.",
      themeConfig: {
        nav: [
          { text: "Guia", link: "/guia/introducao", activeMatch: "/guia/" },
          { text: "Efeitos", link: "/efeitos" },
          { text: "Zona segura", link: "/referencia/plataformas" },
          { text: "Contribuir", link: "/comunidade/contribuir", activeMatch: "/comunidade/" },
        ],
        sidebar: { "/guia/": sidebarPt(), "/referencia/": sidebarPt(), "/comunidade/": sidebarPt() },
        editLink: { pattern: `${REPO}/edit/main/docs/:path`, text: "Sugerir alteração nesta página" },
        docFooter: { prev: "Anterior", next: "Próxima" },
        outline: { label: "Nesta página" },
        lastUpdated: { text: "Atualizado em" },
        darkModeSwitchLabel: "Aparência",
        lightModeSwitchTitle: "Mudar para tema claro",
        darkModeSwitchTitle: "Mudar para tema escuro",
        sidebarMenuLabel: "Menu",
        returnToTopLabel: "Voltar ao topo",
        langMenuLabel: "Idioma",
        notFound: {
          title: "Cena não encontrada",
          quote: "Essa página saiu na edição.",
          linkText: "Voltar para o início",
        },
        footer: {
          message: "Código e documentação sob a licença MIT. Motor de animação: HyperFrames (Apache-2.0).",
          copyright: "Criado por Silvio Campos",
        },
      },
    },
    en: {
      label: "English",
      lang: "en-US",
      link: "/en/",
      description:
        "You send the idea. A coding agent writes the script, records the voiceover, animates every scene on the beat of the speech and delivers the MP4.",
      themeConfig: {
        nav: [
          { text: "Guide", link: "/en/guide/introduction", activeMatch: "/en/guide/" },
          { text: "Effects", link: "/en/effects" },
          { text: "Safe zones", link: "/en/reference/platforms" },
          { text: "Contribute", link: "/en/community/contributing", activeMatch: "/en/community/" },
        ],
        sidebar: { "/en/guide/": sidebarEn(), "/en/reference/": sidebarEn(), "/en/community/": sidebarEn() },
        editLink: { pattern: `${REPO}/edit/main/docs/:path`, text: "Suggest a change to this page" },
        footer: {
          message: "Code and docs under the MIT License. Animation engine: HyperFrames (Apache-2.0).",
          copyright: "Created by Silvio Campos",
        },
      },
    },
  },
});
