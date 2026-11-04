---
title: Plataformas e zona segura
description: Os presets de cada rede, a zona que a interface do app cobre e como o motion-cena mede que nada importante entra nela.
aside: false
---

<script setup>
import PresetTable from "../.vitepress/theme/components/safezone/PresetTable.vue";
</script>

# Plataformas e zona segura

Cada rede cobre uma parte do vídeo com a própria interface: nome do perfil, legenda, botões de curtir e comentar, barra de progresso. Essa faixa é a zona segura. Fundo, textura e movimento podem ocupar a tela toda, mas texto, número, card, ícone e logo ficam fora dela, sem encostar nem por um pedaço.

Escolha um preset, arraste o bloco e veja a distância até cada borda, em pixels do canvas.

<SafeZonePlayground locale="pt" />

## Presets

Cada plataforma é um preset em `assets/platforms.json`, tirado das documentações oficiais. A tabela abaixo é gerada desse arquivo no build do site, então ela muda junto com ele.

<PresetTable locale="pt" kind="video" />

- **Padrão** é a duração usada quando o pedido não diz quanto tempo o vídeo tem.
- **Ideal** é a faixa em que a retenção costuma se manter.
- **Máx.** é o limite da plataforma. Texto maior que isso faz o agente avisar e oferecer dividir em partes, condensar ou trocar de plataforma.

Para ver um preset no terminal:

```bash
uv run .agents/skills/motion-cena/scripts/platform_preset.py --list
uv run .agents/skills/motion-cena/scripts/platform_preset.py tiktok
```

## Um vídeo vertical para três redes

Pedido de Reels, TikTok ou Shorts sem dizer a plataforma usa o preset `vertical`. Ele junta a zona mais restritiva de cada borda entre `ig-reels`, `tiktok` e `yt-shorts`, então um render serve aos três. O agente entrega o mesmo arquivo como `-ig-reels.mp4` e `-tiktok.mp4` (e `-yt-shorts.mp4`, se você pedir).

A diferença está na direita: o Reels reserva 65 px, o TikTok 140 px e o Shorts 192 px, por causa da coluna de botões. Um layout feito só para `ig-reels` fica cortado no TikTok. No playground, monte o título em `ig-reels` e troque para `tiktok`: o bloco fica no mesmo lugar e a borda direita entra na zona.

::: tip Centralize no meio do canvas
A skill centraliza o conteúdo no centro horizontal do canvas (x 540 no vertical), e um título com um número embaixo conta como um grupo só. Com a direita em 192 px, um bloco centralizado no `vertical` pode ter no máximo 696 px de largura. O botão "Centralizar na horizontal" mostra isso.
:::

## Use as variáveis na composição

O `platform_preset.py` com `--css` imprime as variáveis do preset. A composição monta o layout dentro de um contêiner que respeita a zona; só fundo, textura e decoração marcada com `data-safe-ignore` saem dele.

```css
.safe {
  position: absolute;
  inset: var(--safe-top) var(--safe-right) var(--safe-bottom) var(--safe-left);
}
```

O tamanho do texto também depende do canvas. No vertical 1080×1920: título de 90 a 160 px, corpo com 56 px ou mais, número de destaque de 200 a 400 px, legenda de 60 a 70 px logo acima da zona, até 6 palavras na tela. A tabela completa por formato está em [`references/platforms.md`](https://github.com/eusilvio/motion-cena/blob/main/.agents/skills/motion-cena/references/platforms.md).

## Como a zona é medida

Antes do render final, o `safe_zone_check.py` abre a composição num Chrome sem janela, avança a timeline de 0,25 em 0,25 s e mede a caixa real de cada texto, imagem e caixa com fundo ou borda:

```bash
uv run .agents/skills/motion-cena/scripts/safe_zone_check.py projects/<slug>/video --preset vertical
```

| Resultado | Quando |
|---|---|
| `ERRO` | algo ficou na zona por 0,5 s ou mais. O vídeo não segue para o render. |
| `aviso` | uma passagem rápida, de entrada ou saída. Confira o quadro. |

Detalhes que o medidor leva em conta:

- Até 4 px dentro da zona passam (`--tol 4`), para não reprovar serrilhado de borda. O playground é mais estrito e marca a partir de 1 px.
- Card, gráfico, moldura de celular, etiqueta e chip contam como conteúdo.
- Forma de fundo que cobre mais de 45 % do canvas, ou com desfoque acima de 20 px, é tratada como decoração e fica de fora. Para qualquer outro elemento decorativo, marque `data-safe-ignore`.

Zero `ERRO` é obrigatório. Depois do render, o `qa_video.sh` gera a contact sheet com a zona pintada de vermelho e a borda da área livre: nada que importa pode aparecer no vermelho.

## YouTube horizontal

No 16:9 a área livre não é um retângulo. O player ocupa cantos: título e canal em cima à esquerda, ícones em cima à direita, informações e botões embaixo. O preset `yt-long` guarda esses cantos em `safe_corners`, a partir das zonas seguras universais do Google. O medidor só confere as margens gerais (54 / 140 / 96 px), mas a skill pede para tirar texto importante desses cantos sempre que der. No playground, os cantos aparecem hachurados.

## Codificação

Todos os presets saem no mesmo formato: MP4 H.264 High, `yuv420p`, frame rate constante, progressivo, `+faststart`, áudio AAC-LC 48 kHz estéreo e loudness de −14 LUFS. Uma narração e uma timeline geram todas as versões; só o layout é recomposto.

## Fontes

As margens e os limites vêm das páginas oficiais da Meta, do Google, do TikTok e do LinkedIn, pesquisadas em outubro de 2026 (as zonas da Meta e do Google foram conferidas de novo em 23/10/2026). A lista com os links está no fim de [`references/platforms.md`](https://github.com/eusilvio/motion-cena/blob/main/.agents/skills/motion-cena/references/platforms.md). Quando uma plataforma muda, os dois arquivos mudam juntos. Faltam presets para outras redes: veja as [frentes abertas](/comunidade/roadmap).
