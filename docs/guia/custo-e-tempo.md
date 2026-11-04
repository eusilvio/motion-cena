---
title: Quanto leva e quanto custa
description: Tempo e tokens de produções reais no Claude Code, o custo da voz, o que cabe nos planos e como gastar menos.
---

# Quanto leva e quanto custa

Números de produções reais feitas com este repositório no Claude Code (Opus 5.5), entre 20/10 e 04/11/2026, num notebook comum. Servem de ordem de grandeza: os seus vão variar.

## Três peças medidas

| Peça | Voz | Até a 1ª entrega | Com os ajustes | Tokens no total | Custo equivalente na API | Render |
|---|---|---|---|---|---|---|
| Reels de 30 s a partir do código de um produto | ElevenLabs | 30 min | 42 min (1 ajuste) | 24,8 M | US$ 10,58 (US$ 8,37 na 1ª entrega) | 2 min 18 s |
| Reels de 46 s a partir do código de um produto, com trilha | ElevenLabs (voz e trilha) | 25 min | 41 min (1 ajuste) | 25,2 M | US$ 12,18 (US$ 8,03 na 1ª entrega) | 2 min 20 s a 2 min 32 s |
| Carrossel de 6 slides a partir de um texto pronto, com checagem dos números na web | sem voz | 3 min | 7 min (2 ajustes) | 8,5 M | US$ 3,22 (US$ 1,24 na 1ª entrega) | 5 s (PNG) |

Os minutos contam o tempo em que o agente estava trabalhando, do seu pedido até a última ação dele. O tempo que você leva para olhar e responder fica fora. Cada rodada de ajuste nos vídeos somou de 12 a 16 min e de 8 a 10 M tokens (US$ 2 a 4). Em todos os casos, 98 % dos tokens foram leitura de cache, a parte mais barata.

## Como gastar menos

- **Uma peça por sessão.** A cada pedido o agente relê a conversa inteira. Nas sessões medidas, a segunda peça na mesma conversa custou de 35 % a 41 % da sessão. Ao terminar um vídeo, abra uma sessão nova (`/clear` no Claude Code): tudo fica gravado em `projects/<slug>/` e o agente continua de onde parou.
- **Desligue o que não usa para vídeo.** Conectores e plugins pesam em todo pedido. Desligue-os neste projeto.
- **Itere em rascunho.** Enquanto ajusta, o render com `--quality draft` leva menos tempo (1 min 22 s em vez de 1 min 50 s para 30 s de vídeo).
- **Compacte antes de uma rodada longa de ajustes** (`/compact` no Claude Code).

## Cada etapa medida

Medido num Intel i5-8265U de 4 núcleos, 11,6 GB de RAM, sem GPU dedicada, Linux:

| Etapa | Tempo |
|---|---|
| Render de 30,5 s em 1080×1920 a 30 fps (`npx hyperframes render`, qualidade padrão) | 1 min 50 s, uns 5 núcleos ocupados e 1,5 GB de RAM a mais |
| O mesmo render com `--quality draft` (para iterar) | 1 min 22 s |
| Locução com edge-tts, 77 palavras em pt-BR (23 s de áudio) | 3 s (9 s na primeira vez, enquanto o `uv` instala a dependência) |
| Zona segura (`safe_zone_check.py`) + QA (`qa_video.sh`) | 21 s + 7 s |
| Exportar carrossel de 6 a 8 slides em PNG | 5 a 10 s |

## Voz

O edge-tts é grátis. Na ElevenLabs, uma locução de 30 s tem de 415 a 495 caracteres (82 a 96 palavras). A US$ 0,08 por 1.000 caracteres nos modelos multilingual v2, v3 e v4, cada geração custa uns US$ 0,04, e o plano Starter (US$ 6/mês, 75.000 caracteres nesses modelos) cobre umas 150 locuções de 30 s. A trilha pelo Eleven Music sai a US$ 0,15 por minuto ([preços da API da ElevenLabs](https://elevenlabs.io/pricing/api), consultados em 04/11/2026).

## O plano Pro dá conta?

Pro (US$ 20/mês) e Max (US$ 100/mês, com cinco vezes o uso do Pro) incluem o Claude Code. Os dois têm um limite por sessão de 5 horas e um limite semanal, compartilhados entre o Claude e o Claude Code, e a Anthropic não publica quantos tokens cabem em cada janela ([Claude Code no Pro e no Max](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan), [como os limites funcionam](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work), [plano Max](https://support.claude.com/en/articles/11049741-what-is-the-max-plan), consultados em 04/11/2026).

Ninguém testou ainda no Pro, então não dá para prometer quantos vídeos cabem nele. Acompanhe as barras com `/usage` no Claude Code. Se o limite chegar no meio de um vídeo, ative os créditos de uso ou continue depois do reset: cada etapa fica gravada em `projects/<slug>/` e o agente retoma de onde parou.

## Limites destes números

- Só Claude Code, com Opus 5.5 (esforço `xhigh` nos dois vídeos, `medium` no carrossel). Codex, Antigravity, Cursor e os outros contam uso de outro jeito e não foram medidos.
- "Custo equivalente na API" é tokens × preço de tabela do Opus 5.5 (por milhão: US$ 4 entrada, US$ 8 escrita de cache de 1 h, US$ 0,20 leitura de cache, US$ 20 saída). Quem usa plano não paga isso por vídeo; o número serve para comparar.
- Mais rodadas de ajuste, sessão longa, repositório grande para ler, pesquisa na web e esforço mais alto aumentam tokens e minutos.
- O render rodou só na CPU, com outras sessões abertas na mesma máquina, então os tempos estão um pouco pessimistas. Composições com fotos em tela cheia, desfoque e granulação demoram bem mais (uma de 62 s levou 6 min 20 s).

::: tip Mande os seus números
Medições em outras máquinas e agentes são bem-vindas. Abra uma [issue no GitHub](https://github.com/eusilvio/motion-cena/issues) com os seus números.
:::
