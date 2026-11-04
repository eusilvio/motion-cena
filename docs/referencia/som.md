---
title: Som
description: Efeitos sonoros sincronizados com a animação, o kit sintetizado, os prompts da ElevenLabs e a mixagem final.
---

# Som

Efeito sonoro no tempo da animação muda bastante a percepção de qualidade, e é o primeiro ajuste que as pessoas pedem depois da primeira versão. Por isso ele entra já na primeira.

## Mapa de efeitos

O agente monta a lista de efeitos a partir do `timeline.json`. Cada efeito marca um evento visual:

| Evento na tela | Efeito | Volume em relação à voz |
|---|---|---|
| transição de cena (whip, wipe) | whoosh curto, de 200 a 400 ms, começando uns 150 ms antes do corte | −12 dB |
| elemento aparece | pop ou click suave | −16 dB |
| itens em sequência | ticks leves, um por item (até uns 8; mais que isso vira ruído) | −20 dB |
| contador subindo | tick que acelera ou riser tonal | −18 dB |
| número-chave revelado | impacto grave com um pouco de reverb | −10 dB |
| antes de uma revelação | riser de 1 a 2 s terminando no impacto | −16 dB |
| texto sendo digitado | cliques de teclado | −20 dB |
| erro ou negativo | buzz curto, glitch | −14 dB |

Menos é mais: um efeito por ação importante, nunca em cima de uma palavra-chave, todos do mesmo "kit" para o timbre combinar.

O efeito entra pelo evento visual que ele marca, compensando o pico do arquivo. Um whoosh tem o pico uns 0,25 s depois do início; um riser começa antes e termina exatamente no impacto (no storyboard, `"offset": -1.6`, a duração do riser).

## O kit sintetizado

Sem chave e sem rede, o `synth_sfx.py` gera um kit de 9 efeitos na sua máquina: whoosh, pop, tick, click, impact, riser, glitch, ding e beep. Serve bem para a primeira versão.

```bash
uv run .agents/skills/motion-cena/scripts/synth_sfx.py --out projects/<slug>/audio/sfx
uv run .agents/skills/motion-cena/scripts/synth_sfx.py --out projects/<slug>/audio/sfx --only beep,ding
```

## Prompts da ElevenLabs

Com chave da ElevenLabs, o efeito é gerado sob encomenda a partir de um texto. O arquivo `assets/sfx-prompts.json` traz prompts e durações que já funcionaram em produções reais, escritos de forma genérica, cada um com a indicação de quando usar: transições (whoosh, rebobinar fita), interface (tecla, erro, bipe, vibração), objetos (carimbo, assinatura, papel, fita adesiva, impressora, metal), impacto, veículos e ambiente (multidão, chuva).

```bash
uv run .agents/skills/motion-cena/scripts/tts_elevenlabs.py --sfx "short airy whoosh, clean" --duration 0.5 --out projects/<slug>/audio/sfx/whoosh.mp3
```

::: warning Por que o repositório não traz os áudios
Os termos da ElevenLabs proíbem publicar o áudio gerado como arquivo avulso ou como biblioteca de sons. Por isso só os prompts ficam no repositório: cada pessoa gera com a própria chave dentro de `projects/<slug>/audio/sfx/`, que fica fora do git. Nunca copie esses arquivos para o repositório.
:::

## Outras fontes

- Bibliotecas livres: Pixabay Sound Effects, Freesound (confira se é CC0 ou CC-BY e dê o crédito quando pedido) e Kenney (CC0, sons de interface).
- Higgsfield, se o conector estiver ligado no seu agente.
- A biblioteca local: antes de gerar, o agente procura com `asset_library.py find --kind sfx <tipo>` o que já foi produzido.

## Trilha (opcional)

Uma trilha instrumental leve, de 100 a 128 BPM para Reels, vinda da sua biblioteca, do Pixabay Music ou gerada pela ElevenLabs Music. Ela fica de 18 a 22 dB abaixo da voz, corta no fim de um compasso e sai com 1 s de fade.

## Mixagem

O `mix_audio.py` posiciona cada efeito no tempo, aplica o ganho, soma com a voz, abaixa a trilha embaixo da fala (ducking) e normaliza o resultado em −14 LUFS com pico real de −1 dBTP:

```bash
uv run .agents/skills/motion-cena/scripts/mix_audio.py projects/<slug>/timeline.json --voice projects/<slug>/audio/voice.mp3 --sfx-dir projects/<slug>/audio/sfx --music trilha.mp3 --out projects/<slug>/audio/mix.wav
```

O `mix.wav` vira a única faixa de áudio da composição, para nada sair duplicado. O `qa_video.sh` confere depois se o loudness ficou entre −16 e −12 LUFS e se não sobrou silêncio maior que 1,5 s.
