---
title: O que é
description: Um pipeline de vídeo em motion design dirigido por um agente de código, do pedido ao MP4 com a fala mandando no tempo.
---

# O que é o motion-cena

O motion-cena é um pipeline de vídeo em motion design dirigido por um agente de código. Você manda a ideia. O agente escreve o roteiro, grava a locução, anima cada cena no tempo da fala e entrega o MP4 pronto para postar.

![Cinco efeitos do dicionário renderizados pelo pipeline: scramble, line reveal, count-up, parallax e zoom through](../dicionario.gif)

## Por que ele existe

Pedir "faz um vídeo bonito" a um modelo gera animação aleatória, que não conversa com a fala. O motion-cena trabalha como uma produtora pequena: primeiro decide qual história contar, em qual formato e o que cada cena mostra. Só depois anima.

- **A fala manda no tempo.** A locução sai antes da animação. Cada palavra ganha um timestamp, e cada ênfase dispara no quadro em que a palavra é dita.
- **Uma ideia visual por vídeo.** Cada peça nasce de um dispositivo próprio (uma carteirinha, um painel, uma página), escolhido entre três conceitos. O sistema veta o que repete vídeos anteriores.
- **Cada etapa grava um arquivo.** Dá para parar, revisar e pedir só o pedaço que mudou: "troca o hook", "faz a versão pra story".
- **Nada fica embaixo dos botões.** Um medidor percorre o vídeo a cada quarto de segundo e reprova texto, card ou logo que entra na área da interface do Reels, do TikTok ou do Shorts. Veja no [playground da zona segura](/referencia/plataformas).

## O que entra

Quase qualquer coisa vira vídeo. O agente identifica o modo pelo que você mandou:

| Você manda | O que acontece |
|---|---|
| um texto ou roteiro seu | vira roteiro de vídeo: mantém fatos, intenção e as frases com a sua voz; ajusta duração, hook e fecho |
| um texto com "usa exatamente como está" | narração palavra por palavra |
| tópicos, bullets, uma transcrição | organiza em história, escolhe formato e escreve o roteiro |
| só o assunto | pesquisa na web com fontes, depois escreve o roteiro |
| PDF, relatório, artigo, URL | lê tudo e tira os melhores trechos, com a página de origem |
| planilha, CSV, números | acha a história nos números; cada número ganha um visual |
| uma locução gravada | transcreve com timestamps e anima em cima dessa voz |
| um vídeo de alguém falando | a imagem e a voz são a base; o motion entra por cima |
| o caminho de um repositório | fatos, telas e marca saem do código do produto |

## O que sai

- **Vídeo**: um MP4 por plataforma (Reels, Stories, TikTok, Shorts, YouTube, LinkedIn), com locução, efeitos sonoros e, se você quiser, legenda queimada.
- **Carrossel**: a mesma ideia em slides, sem narração, em PNG para o Instagram ou PDF para o LinkedIn. Veja [Carrossel](/referencia/carrossel).

O repositório sai zerado: nenhuma marca, voz ou persona de ninguém. A identidade de cada vídeo vem do pedido (um site, cores, o código do produto, a gravação de quem fala) ou nasce da ideia central do vídeo.

## Por baixo

A animação roda no [HyperFrames](https://github.com/heygen-com/hyperframes), que renderiza HTML, CSS e GSAP em vídeo. O vocabulário de movimento vem de um dicionário com 44 efeitos curados e um catálogo de 388, que você pode [explorar aqui](/efeitos). O agente pode ser Claude Code, Codex, Antigravity, Cursor, GitHub Copilot, OpenCode, Windsurf ou outro que leia arquivos e rode comandos: veja [Qualquer agente](/guia/agentes).

Sem nenhuma chave de API o pipeline roda inteiro, com voz grátis pelo edge-tts e efeitos sonoros sintetizados na sua máquina.

## Próximos passos

1. [Instale](/guia/instalacao) Node, FFmpeg, uv e o seu agente.
2. Faça o [primeiro vídeo](/guia/primeiro-video).
3. Entenda [cada etapa do pipeline](/guia/como-funciona) e os arquivos que ela grava.

Código e documentação sob a licença MIT. O motor de animação, HyperFrames, é Apache-2.0.
