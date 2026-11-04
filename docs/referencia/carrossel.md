---
title: Carrossel
description: A mesma ideia em slides, sem narração, em PNG para o Instagram ou PDF para o LinkedIn. Como ligar, presets, estrutura e o que sai.
---

<script setup>
import PresetTable from "../.vitepress/theme/components/safezone/PresetTable.vue";
</script>

# Carrossel

O modo carrossel usa o mesmo conteúdo e entrega slides estáticos no lugar do vídeo narrado. Não tem narração, locução, timeline nem som. O fluxo vira brief, plano de slides, design e exportação.

## Como ligar

Qualquer um destes liga o modo carrossel:

- o pedido diz "carrossel", "carousel", "slides pro Instagram", "post de arrastar" ou traz `--carrossel`;
- o material vem de um calendário com o formato "Carrossel";
- você pede *"também em carrossel"*: aí sai o vídeo e o carrossel do mesmo brief.

Sem nada disso, o padrão é vídeo. Quando o conteúdo pede carrossel e você não disse nada, o agente recomenda em uma linha e segue o que você pediu.

| Conteúdo | Melhor saída |
|---|---|
| informativo, dados, notícia comentada, passo a passo, lista, comparação, guia de referência | carrossel: a pessoa lê no ritmo dela, salva e compartilha |
| campanha, lançamento, oferta com vários benefícios | carrossel no feed, com um vídeo curto opcional |
| história, motivacional, tom de voz que importa, demonstração em movimento | vídeo |

## Presets

<PresetTable locale="pt" kind="carousel" />

Todos os slides têm a mesma proporção: o primeiro define o corte dos outros. A margem segura existe porque o app sobrepõe o contador e os ícones nas bordas.

## Estrutura

1. **Capa (slide 1).** Um gancho com gatilho, que abre uma pergunta e puxa o arrasto. Capa que entrega a conclusão do post é reprovada: a pessoa precisa sair dela querendo o slide 2.
2. **Slide 2 vai direto ao ponto.** O Instagram mostra o carrossel de novo, abrindo no slide 2, para quem não interagiu. Então ele funciona como uma segunda capa: título forte e sentido completo para quem nunca viu a primeira.
3. **Miolo (2 a 6 slides).** Uma ideia por slide, título curto e até umas 40 palavras. Sempre que existir, um print, tela, foto ou mockup do que o texto descreve. Cada slide termina com uma linha que puxa para o próximo.
4. **Virada ou síntese (1 slide).** A ideia que justifica o post.
5. **Fecho.** Segue a intenção do post: uma pergunta, um pedido para salvar ou compartilhar, ou um material gratuito ligado ao post, se ele existir de verdade. Sempre com o @ e a fonte dos dados.

Os textos passam pelo `lint_copy.py`, os números têm fonte e emoji não entra, nem na legenda.

## Dois motores, uma fonte

| Motor | Quando | Entrega |
|---|---|---|
| **Local** (HyperFrames para PNG) | qualquer agente | `creatives/carrossel/<slug>-<preset>/01.png … NN.png`, `contact.jpg` e, para o LinkedIn, `carousel.pdf` |
| **Claude Design** | só num agente Claude com a ferramenta Artifact | um canvas editável no claude.ai, uma prancheta por slide |

Os dois partem da mesma fonte: as pranchas `.dc.html`, guardadas em `projects/<slug>/carousel/claude-design/project/`. O motor local converte essa fonte, então o PNG sai igual ao canvas. Sem a ferramenta Artifact, o agente escreve as pranchas do mesmo jeito e usa só o motor local.

```bash
S=.agents/skills/motion-cena/scripts
uv run $S/dc_to_carousel.py projects/<slug>/carousel/claude-design/project --out projects/<slug>/carousel/render --preset ig-carousel
(cd projects/<slug>/carousel/render && npx hyperframes check)
uv run $S/render_carousel.py projects/<slug>/carousel/render --slides 7 --out creatives/carrossel/<slug>-ig-carousel
```

Antes de rodar, as fontes da marca vão em `projects/<slug>/carousel/render/assets/fonts/`.

::: tip Publique no Claude Design uma vez só
O agente itera olhando a `contact.jpg` do render local e publica no Claude Design quando os slides estão aprovados, ou quando você pede o canvas editável. Cada publicação acrescenta uns 20 mil tokens à conversa, e todo pedido seguinte paga por eles de novo.
:::

## O que sai

- Um PNG por slide e a `contact.jpg` em `creatives/carrossel/<slug>-<preset>/`.
- `carousel.pdf` no preset do LinkedIn (ou com `--pdf`).
- `legenda.txt`: a legenda do post, de 3 a 5 linhas, com a primeira linha sendo outra versão do gancho.
- `alt-text.txt`: o texto alternativo de cada slide.
- O link do canvas no Claude Design, se o agente tiver a ferramenta.

Exportar 6 a 8 slides leva de 5 a 10 s na máquina medida em [Quanto leva e quanto custa](/guia/custo-e-tempo).
