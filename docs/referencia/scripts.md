---
title: Scripts
description: Cada script de .agents/skills/motion-cena/scripts, o que ele faz e um comando de exemplo.
---

# Scripts

Os scripts da skill ficam em `.agents/skills/motion-cena/scripts/`. O agente chama cada um na etapa certa, mas todos rodam à mão também. Os Python rodam com `uv run` e declaram as dependências no próprio arquivo (bloco `# /// script`), então nada é instalado no sistema. Os `.sh` rodam com `bash`.

Os exemplos abaixo rodam da raiz do repositório. Todo script aceita `--help`.

## Resumo

| Script | Etapa | Faz |
|---|---|---|
| `platform_preset.py` | brief, animação | mostra os presets de plataforma e gera as variáveis CSS da zona segura |
| `registro.py` | ideia central | resume o histórico de peças entregues para vetar conceito repetido |
| `motion_lookup.py` | storyboard, animação | busca no catálogo de 388 efeitos |
| `fetch_icon.py` | identidade visual | baixa bandeira, logo, ícone ou imagem livre com a licença |
| `asset_library.py` | identidade, voz, som | procura e reaproveita o que já foi produzido antes |
| `tts_edge.py` | locução | voz grátis pelo edge-tts, com timestamp por palavra |
| `tts_elevenlabs.py` | locução, som | voz, clonagem e efeitos sonoros pela ElevenLabs |
| `tts_chatterbox.py` | locução | voz clonada rodando local, na CPU |
| `align_words.py` | locução | timestamp por palavra de qualquer áudio (Whisper) |
| `isolate_voice.py` | locução | tira música e ruído de uma gravação |
| `build_timeline.py` | locução | ancora as cenas nas palavras faladas e gera o `timeline.json` |
| `find_words.py` | locução, animação | diz quando uma frase é falada, sem abrir o `words.json` |
| `snapshot_sheet.py` | animação | junta quadros-chave da composição numa imagem só |
| `safe_zone_check.py` | animação | reprova o que entra na zona da interface |
| `synth_sfx.py` | som | kit de 9 efeitos sonoros sintetizados, offline |
| `mix_audio.py` | som | mixa voz, efeitos e trilha a −14 LUFS |
| `qa_video.sh` | render | confere o MP4 e gera a contact sheet |
| `dc_to_carousel.py` | carrossel | converte as pranchas do Claude Design numa composição local |
| `render_carousel.py` | carrossel | exporta um PNG por slide, contact sheet e PDF |
| `lint_copy.py` | roteiro, entrega | aponta texto com cara de IA (pt-BR) |
| `analyze_reference.sh` | estilos | quebra um vídeo de referência em pranchas, fala e loudness |

## Plataforma e direção

### platform_preset.py

Lê `assets/platforms.json`. Sem argumento lista os presets; com um preset, mostra canvas, fps, durações e zona segura. `--css` imprime as variáveis `--safe-*` para a composição, `--shell` imprime variáveis para o bash e `--json` o preset inteiro.

```bash
uv run .agents/skills/motion-cena/scripts/platform_preset.py vertical --css
```

O [playground da zona segura](/referencia/plataformas) mostra a mesma saída para cada preset.

### registro.py

Resumo compacto do `creatives/registro.md`, o histórico de peças entregues, para vetar uma ideia central que repete vídeos anteriores sem ler o arquivo inteiro. `--recent N` mostra as últimas N linhas, `--counts` os valores mais usados em cada eixo visual.

```bash
uv run .agents/skills/motion-cena/scripts/registro.py --counts
```

### motion_lookup.py

Busca no catálogo de efeitos por termo, nome em português ou apelido, ignorando acento e caixa. Também filtra por família, gênero e intensidade. O agente nunca lê os JSON do catálogo inteiros: ele pergunta a este script.

```bash
uv run .agents/skills/motion-cena/scripts/motion_lookup.py "texto hacker" --brief
uv run .agents/skills/motion-cena/scripts/motion_lookup.py --family enfase --genre dados --intensity sutil
```

`--validate` confere o esquema e as referências cruzadas (roda no CI) e `--write-index` regenera o índice. O mesmo catálogo está no [explorador de efeitos](/efeitos).

## Símbolos e reaproveitamento

### fetch_icon.py

Baixa símbolos reais (bandeira, logo oficial), ícones de linha e imagens com licença livre, e registra fonte e licença no `CREDITS.md` da pasta. Nunca redesenha um símbolo real e não oferece emoji.

```bash
uv run .agents/skills/motion-cena/scripts/fetch_icon.py flag br --out projects/<slug>/video/assets/icons
uv run .agents/skills/motion-cena/scripts/fetch_icon.py icon medal --weight fill --color "#D4A72C" --out projects/<slug>/video/assets/icons
```

Para imagens, `image "<termo>"` lista candidatas do Openverse com a licença, e `--pick N` baixa a escolhida.

### asset_library.py

Índice do que já foi produzido em projetos anteriores (fontes, efeitos sonoros, trilhas, locuções, ícones, logos, bandeiras, imagens), para reaproveitar em vez de baixar, sintetizar ou pagar de novo. Só material bruto entra; composição e layout de projeto antigo não são modelo.

```bash
uv run .agents/skills/motion-cena/scripts/asset_library.py find --kind sfx whoosh
uv run .agents/skills/motion-cena/scripts/asset_library.py scan
```

## Voz e tempo

### tts_edge.py

Locução grátis pelas vozes do Microsoft Edge, sem chave. Grava `voice.mp3` e `words.json` com o tempo de cada palavra.

```bash
uv run .agents/skills/motion-cena/scripts/tts_edge.py --text-file projects/<slug>/narration.txt --voice pt-BR-FranciscaNeural --out projects/<slug>/audio
```

### tts_elevenlabs.py

ElevenLabs pelo SDK oficial: locução com timestamp por palavra, clonagem de voz e efeitos sonoros por texto. A chave vem do `.env.local`. Clone só uma voz com o consentimento do dono.

```bash
uv run .agents/skills/motion-cena/scripts/tts_elevenlabs.py --list-voices
uv run .agents/skills/motion-cena/scripts/tts_elevenlabs.py --text-file projects/<slug>/narration.txt --voice-id <id> --out projects/<slug>/audio
uv run .agents/skills/motion-cena/scripts/tts_elevenlabs.py --sfx "short airy whoosh, clean" --duration 0.5 --out projects/<slug>/audio/sfx/whoosh.mp3
```

### tts_chatterbox.py

Voz clonada com o Chatterbox Multilingual (MIT), rodando local na CPU. Precisa de 10 a 15 s limpos da voz de quem fala, com consentimento. Não gera timestamps: passe o resultado pelo `align_words.py`.

```bash
uv run .agents/skills/motion-cena/scripts/tts_chatterbox.py --text-file projects/<slug>/narration.txt --ref training/voz/ref.wav --out projects/<slug>/audio
```

### align_words.py

Timestamp por palavra de qualquer áudio, com faster-whisper. Serve para a sua gravação ou para voz de um serviço sem timestamps. Com `--script`, as palavras transcritas ganham a grafia do roteiro, mantendo o tempo.

```bash
uv run .agents/skills/motion-cena/scripts/align_words.py projects/<slug>/audio/voice.mp3 --lang pt --out projects/<slug>/audio/words.json
```

### isolate_voice.py

Tira música e ruído de fundo de uma gravação, local na CPU (Demucs e filtros do FFmpeg). Grava `voice.wav` em 48 kHz mono, pronto para a mixagem.

```bash
uv run .agents/skills/motion-cena/scripts/isolate_voice.py gravacao.mp3 --out projects/<slug>/audio
```

### build_timeline.py

Casa o trecho de narração de cada cena do storyboard com as palavras faladas e grava o `timeline.json`, com início e fim em segundos e em quadros, as palavras-âncora resolvidas e os efeitos sonoros em tempo absoluto. Palavra não encontrada vira aviso: o roteiro divergiu da fala.

```bash
uv run .agents/skills/motion-cena/scripts/build_timeline.py projects/<slug>/storyboard.json projects/<slug>/audio/words.json --fps 30 --out projects/<slug>/timeline.json
```

### find_words.py

Quando uma frase é dita? Consulta o `words.json` com a mesma casagem do `build_timeline.py`. `--around` lista as palavras perto de um tempo e `--gaps` as pausas, que são bons pontos de corte.

```bash
uv run .agents/skills/motion-cena/scripts/find_words.py projects/<slug>/audio/words.json "juro sobre juro"
uv run .agents/skills/motion-cena/scripts/find_words.py projects/<slug>/audio/words.json --gaps 0.6
```

## Conferência visual

### snapshot_sheet.py

Tira os quadros pedidos da composição com o HyperFrames e junta todos numa imagem pequena, com o tempo escrito em cada um. `--zoom x,y,w,h` recorta uma região em resolução cheia, para tirar a dúvida num detalhe.

```bash
uv run .agents/skills/motion-cena/scripts/snapshot_sheet.py projects/<slug>/video 1.2,4.8,9.5,14
```

### safe_zone_check.py

Abre a composição num Chrome sem janela, avança a timeline de 0,25 em 0,25 s e mede a caixa real de cada texto, imagem e caixa com fundo. O que fica 0,5 s ou mais na zona é `ERRO` e o script sai com código 1. Como a zona funciona: [Plataformas e zona segura](/referencia/plataformas).

```bash
uv run .agents/skills/motion-cena/scripts/safe_zone_check.py projects/<slug>/video --preset vertical
```

## Som

### synth_sfx.py

Kit de efeitos sonoros sintetizados na sua máquina, sem rede: whoosh, pop, tick, click, impact, riser, glitch, ding e beep. `--only` gera só alguns.

```bash
uv run .agents/skills/motion-cena/scripts/synth_sfx.py --out projects/<slug>/audio/sfx --only whoosh,pop
```

### mix_audio.py

Posiciona cada efeito pela timeline, soma com a voz, abaixa a trilha embaixo da fala e normaliza o loudness em −14 LUFS.

```bash
uv run .agents/skills/motion-cena/scripts/mix_audio.py projects/<slug>/timeline.json --voice projects/<slug>/audio/voice.mp3 --sfx-dir projects/<slug>/audio/sfx --out projects/<slug>/audio/mix.wav
```

Mais sobre som em [Som](/referencia/som).

## Render e QA

### qa_video.sh

Confere o MP4 contra o preset: resolução, fps, duração máxima, codec, `yuv420p`, áudio presente, silêncio longo e loudness. Gera a contact sheet com a zona pintada e o primeiro quadro. `QA_DIR` escolhe onde as imagens ficam.

```bash
QA_DIR=projects/<slug>/out bash .agents/skills/motion-cena/scripts/qa_video.sh creatives/reels/<slug>-ig-reels.mp4 ig-reels
```

## Carrossel

### dc_to_carousel.py

Converte as pranchas `.dc.html` do Claude Design numa composição HyperFrames local, para exportar sem depender do claude.ai. As fontes da marca vão em `assets/fonts/` da pasta de saída antes de rodar.

```bash
uv run .agents/skills/motion-cena/scripts/dc_to_carousel.py projects/<slug>/carousel/claude-design/project --out projects/<slug>/carousel/render --preset ig-carousel
```

### render_carousel.py

Exporta um PNG por slide, a `contact.jpg` para revisão e, com `--pdf` ou num preset de PDF, o `carousel.pdf`.

```bash
uv run .agents/skills/motion-cena/scripts/render_carousel.py projects/<slug>/carousel/render --slides 7 --out creatives/carrossel/<slug>-ig-carousel
```

O fluxo completo está em [Carrossel](/referencia/carrossel).

## Texto e referências

### lint_copy.py

Aponta texto com cara de IA em pt-BR: contraste simétrico ("não é X, é Y"), pergunta-isca, travessão de efeito, clichê, jargão e emoji. Lê `.txt`, `.json` de storyboard, `.html` e `.md`. Erro faz o script sair com código 1. O agente roda no roteiro, no texto da tela, nos slides e na legenda, e o CI roda nos documentos em português da raiz do repositório.

```bash
uv run .agents/skills/motion-cena/scripts/lint_copy.py projects/<slug>/narration.txt
```

### analyze_reference.sh

Quebra um vídeo de referência para virar receita de estilo: pranchas a 2 quadros por segundo com timecode, três quadros em resolução cheia, a fala com timestamps e o loudness. Veja [Estilos de referência](/referencia/estilos).

```bash
bash .agents/skills/motion-cena/scripts/analyze_reference.sh training/referencias/ref-01.mp4 training/referencias/ref-01 pt
```

Mudou um script? O PR traz um teste em `tests/` e atualiza onde ele é citado. Veja [Como contribuir](/comunidade/contribuir).
