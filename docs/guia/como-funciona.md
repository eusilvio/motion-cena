---
title: Do pedido ao MP4
description: As etapas do pipeline, o arquivo que cada uma grava, a revisão antes de gastar crédito e a sincronia com a fala.
---

# Do pedido ao MP4

O método é **entrada, formato, roteiro, ideia central, cenas, vídeo**, nessa ordem. Cada etapa grava um arquivo que a seguinte consome, e o storyboard é o contrato entre a história e a animação. A parte pesada é a direção: qual história, qual formato, qual ideia visual, o que cada cena mostra. Animar é a parte fácil.

## As etapas e o que cada uma grava

Tudo fica em `projects/<slug>/`, uma pasta por projeto, fora do git.

| Etapa | O que acontece | Grava |
|---|---|---|
| **0. Brief** | classifica o modo de entrada, o gênero, a plataforma e a duração; guarda o material original | `brief.md`, `source/` |
| **1. Formato narrativo** | testa o conteúdo em pelo menos 4 formatos (comparação, transformação, listicle, mito × verdade e outros) e escolhe um | `plan.md` |
| **2. Roteiro** | escreve ou adapta o texto para a duração, com 3 hooks alternativos; no modo literal, usa o seu texto palavra por palavra | `plan.md`, `narration.txt` |
| **2.5. Ideia central** | propõe 3 dispositivos visuais diferentes, veta os que repetem vídeos anteriores e escolhe um | `plan.md` |
| **3. Storyboard** | quebra o roteiro em cenas: trecho falado, visual, movimento, palavra-âncora, transição, efeito sonoro | `plan.md`, `storyboard.json` |
| **Revisão** | mostra o plano e espera a sua aprovação | |
| **4. Identidade visual** | paleta, fontes e ritmo a partir da ideia central e da marca, se o pedido trouxer uma; baixa os símbolos com licença | `brand.json`, `video/assets/` |
| **5. Locução** | gera a voz com timestamp por palavra e ancora as cenas na fala | `audio/voice.mp3`, `audio/words.json`, `timeline.json` |
| **6. Animação** | monta a composição no HyperFrames e mede a zona segura | `video/` |
| **7. Som** | posiciona os efeitos pela timeline e mixa voz, efeitos e trilha | `audio/sfx/`, `audio/mix.wav` |
| **8. Render e QA** | renderiza, confere canvas, fps, duração, codec e loudness, e gera a contact sheet | `creatives/reels/<slug>-<preset>.mp4`, `out/` |

No fim, o agente acrescenta uma linha ao `creatives/registro.md` com a ideia central e os eixos visuais do vídeo. É esse histórico que ele consulta na etapa 2.5 para não repetir conceito.

No carrossel, as etapas 5 e 7 não existem: a 6 vira layout estático e a 8 vira exportação de slides. Veja [Carrossel](/referencia/carrossel).

## A revisão antes de gastar crédito

Depois do storyboard, o agente para e mostra o `plan.md`: os formatos testados e o escolhido, o roteiro ao lado do seu texto original (com o motivo de cada mudança), os 3 hooks, a ideia central com as duas descartadas e o storyboard. Só com a sua aprovação ele gasta crédito de voz e tempo de render.

O `plan.md` é autossuficiente: outro agente consegue produzir o vídeo só com ele. Se você pedir *"faz tudo direto"*, a revisão é pulada, e o plano registra isso.

## A fala manda no tempo

A locução sai **antes** da animação. Com o áudio pronto, cada palavra tem um timestamp:

```json
[{"word": "quase", "start": 0.12, "end": 0.41}, ...]
```

O `build_timeline.py` casa o trecho de narração de cada cena com essas palavras (ignorando acento, pontuação e caixa) e gera o `timeline.json`, com início e fim de cada cena em segundos e em quadros. Cada ênfase do storyboard tem uma palavra-âncora, e o efeito dispara no quadro em que essa palavra é dita.

```bash
uv run .agents/skills/motion-cena/scripts/build_timeline.py projects/<slug>/storyboard.json projects/<slug>/audio/words.json --fps 30 --out projects/<slug>/timeline.json
```

A voz pode vir de três lugares:

- **edge-tts**, grátis e sem chave, com timestamps nativos;
- **ElevenLabs**, com chave no `.env.local`, timestamps nativos e clonagem de voz;
- **um áudio sem timestamps** (a sua gravação, outro serviço), que passa pelo `align_words.py` (Whisper) para ganhar o tempo de cada palavra.

Se a voz sair mais de 10 % fora da duração pedida, o agente ajusta o texto e gera de novo, ou muda a velocidade entre 0,9 e 1,1.

## Animação e conferência

O motor padrão é o HyperFrames: HTML, CSS e uma timeline GSAP pausada, que o renderizador avança quadro a quadro. Remotion e Motion Canvas são alternativas descritas na skill, para quem já tem um projeto React ou quer um explicativo técnico.

Antes do render final, duas conferências:

- o `safe_zone_check.py` percorre o vídeo a cada 0,25 s e reprova o que fica na zona da interface (veja [Plataformas e zona segura](/referencia/plataformas));
- o `snapshot_sheet.py` junta quadros-chave numa imagem só, que o agente olha antes de renderizar.

Depois do render, o `qa_video.sh` confere resolução, fps, duração máxima, codec, áudio e loudness (−14 LUFS), e gera a contact sheet com a zona pintada. O agente abre essa imagem e passa pelo checklist de QA antes de entregar.

## Ajustes refazem só o que mudou

Como cada etapa está num arquivo, *"troca o hook"* refaz a voz da primeira cena, a timeline e o render; *"tira a música"* refaz só o som e o render; *"faz a versão pra story"* recompõe o layout em `video-ig-stories/` com a mesma narração. A lista de scripts de cada etapa está em [Scripts](/referencia/scripts).
