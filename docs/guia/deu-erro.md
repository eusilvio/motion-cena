---
title: Deu erro?
description: Os erros que já apareceram rodando o motion-cena, com sintoma, causa e solução.
---

# Deu erro?

Rode primeiro os dois diagnósticos. O `setup.sh` aponta o que falta (Node, FFmpeg, uv) e o `doctor` do HyperFrames confere Node, FFmpeg, Chrome, memória e disco:

```bash
./setup.sh
npx hyperframes doctor
```

No `doctor`, falha em `TTS (Kokoro)` ou `BGM (MusicGen)` pode ser ignorada: são alternativas locais opcionais e o motion-cena não depende delas. É por causa delas que ele termina com "Some checks failed" mesmo com tudo certo.

Os casos abaixo apareceram em uso real. Cada um tem o sintoma, a causa e a solução.

## Render

::: details O render demora, para no meio ou some
**Sintoma.** Uma destas mensagens, ou um vídeo que nunca aparece:

```text
Command did not complete within its 600s timeout and was moved to the background
Render cancelled: render_cancelled_parent_exited
Background command "..." was stopped because the system is running low on memory
```

Às vezes sobra uma pasta `creatives/reels/work-*/` com um `video-only.mp4` que o `ffprobe` recusa com `moov atom not found`.

**Causa.** Um vídeo de 30 s leva de 1,5 a 2,5 min para renderizar num notebook comum, e composições pesadas (fotos em tela cheia, desfoque, granulação) passam de 6 min. Quando o comando do agente termina ou estoura o tempo, o HyperFrames cancela o render junto. Com outros renders ou previews do Studio abertos, a memória acaba.

**Solução.** Feche o que está aberto e rode o render desacoplado do agente, com menos workers:

```bash
npx hyperframes preview --list                 # previews do Studio ainda rodando
npx hyperframes preview --stop                 # dentro da pasta do projeto que não precisa mais dele
cd projects/<slug>/video
bash -c 'set -m; HYPERFRAMES_RENDER_DETACHED=1 npx hyperframes render -o ../../../creatives/reels/<slug>-ig-reels.mp4 --workers 2 < /dev/null > ../out/render.log 2>&1 &'
tail -f ../out/render.log                      # termina com "rendered in ..."
```

Enquanto ajusta, use `--quality draft` (1 min 22 s em vez de 1 min 50 s para 30 s de vídeo, na máquina medida). Apague a pasta `creatives/reels/work-*` que o render interrompido deixou.
:::

::: details Chrome do render não encontrado (HyperFrames)
**Sintoma.**

```text
[BrowserManager] Chrome binary not found at ... Run `hyperframes browser ensure` to re-download.
```

ou um aviso de que o arquivo do Chrome está danificado.

**Causa.** O HyperFrames renderiza com um Chrome próprio (uns 260 MB em `~/.cache/hyperframes/chrome`). O download do primeiro render falhou, foi interrompido, ou o cache foi apagado.

**Solução.**

```bash
npx hyperframes browser ensure          # baixa o Chrome fixado pelo HyperFrames
npx hyperframes browser ensure --force  # apaga um download quebrado e baixa de novo
npx hyperframes browser path            # mostra qual executável está sendo usado
```
:::

::: details Chrome do medidor de zona segura (Playwright)
**Sintoma.** O `safe_zone_check.py` para com:

```text
BrowserType.launch: Executable doesn't exist at .../ms-playwright/chromium_headless_shell-.../chrome-headless-shell
Looks like Playwright was just installed or updated.
Please run the following command to download new browsers:
    playwright install
```

**Causa.** O medidor usa o Playwright, que tem um Chromium separado do HyperFrames. O script tenta esse Chromium e depois um Google Chrome instalado no sistema. Sem nenhum dos dois, ele para.

**Solução.**

```bash
uv run --with playwright playwright install chromium
```

Num Linux sem as bibliotecas do navegador, acrescente `--with-deps` (pede sudo). Para ver o que vai baixar antes: `--dry-run`.
:::

## Voz

::: details edge-tts não gera áudio
**Sintoma.**

```text
edge_tts.exceptions.NoAudioReceived: No audio was received. Please verify that your parameters are correct.
```

**Causa.** Nome de voz errado, sem internet, ou versão do edge-tts desatualizada depois de uma mudança no serviço da Microsoft (o serviço é gratuito e não oficial).

**Solução.** Confira o nome da voz e force a versão mais nova:

```bash
uv run --with edge-tts edge-tts --list-voices | grep pt-BR
# pt-BR-AntonioNeural, pt-BR-FranciscaNeural, pt-BR-ThalitaMultilingualNeural
uv run --refresh-package edge-tts .agents/skills/motion-cena/scripts/tts_edge.py --text-file projects/<slug>/narration.txt --voice pt-BR-FranciscaNeural --out projects/<slug>/audio
```

Se continuar falhando, peça a locução pela ElevenLabs.
:::

::: details ElevenLabs recusa o pedido
**Sintoma.** Uma destas:

```text
ELEVENLABS_API_KEY not set (run: npx -y @elevenlabs/cli@latest onboard init)
status_code: 401 ... 'Neither authorization header nor xi-api-key received, please provide one.'
status_code: 400 ... 'code': 'voice_not_found'
status_code: 429 ... 'code': 'concurrent_limit_exceeded', 'message': 'Too many concurrent requests. ...'
```

**Causa.** A chave não está no `.env.local` (ou o script rodou fora do repositório); o `voice_id` pedido não existe mais na sua conta (uma voz clonada que foi apagada, por exemplo); ou o agente disparou mais gerações em paralelo do que o seu plano permite.

**Solução.** Coloque `ELEVENLABS_API_KEY=...` no `.env.local` da raiz e liste as vozes que a sua conta enxerga:

```bash
uv run .agents/skills/motion-cena/scripts/tts_elevenlabs.py --list-voices
```

No 429, peça para o agente gerar uma locução de cada vez.
:::

## Máquina

::: details Node, FFmpeg ou uv faltando ou na versão errada
**Sintoma.**

```text
HyperFrames requires Node.js >= 22 (current: v20...). Switch Node versions and retry.
[FFmpeg] ffmpeg not found
Unknown encoder 'libx264'
uv: command not found
```

**Causa.** Node antigo, FFmpeg ausente ou compilado sem H.264, ou o `uv` não instalado. Os scripts de QA e mixagem chamam o `ffmpeg` do PATH, então o primeiro `ffmpeg` do PATH precisa ter `libx264` e `aac`.

**Solução.**

```bash
node -v                                             # precisa ser 22 ou maior; com nvm: nvm install 22
which -a ffmpeg                                     # qual ffmpeg vem primeiro no PATH
ffmpeg -hide_banner -encoders | grep -E ' libx264 | aac '
curl -LsSf https://astral.sh/uv/install.sh | sh     # instala o uv
```

Se o HyperFrames precisar de outro FFmpeg, aponte para ele com `HYPERFRAMES_FFMPEG_PATH` e `HYPERFRAMES_FFPROBE_PATH` e confira com `npx hyperframes doctor`.
:::

## QA

::: details O QA reprovou o vídeo
**Sintoma.** O `qa_video.sh` termina em `RESULT: FAIL` com uma destas linhas:

```text
FAIL no silent gaps > 1.5s (found 1)
FAIL audio track none
FAIL loudness -16.55 LUFS (want -16..-12)
```

**Causa.** A primeira é a mais comum: o cartão final fica mudo depois da última palavra. A segunda aparece quando o render saiu sem o `mix.wav`. A terceira, quando a mixagem ficou baixa.

**Solução.** Encurte o cartão final ou deixe trilha e efeito embaixo dele. Para o áudio, refaça a mixagem e renderize de novo:

```bash
uv run .agents/skills/motion-cena/scripts/mix_audio.py projects/<slug>/timeline.json --voice projects/<slug>/audio/voice.mp3 --sfx-dir projects/<slug>/audio/sfx --lufs -14 --out projects/<slug>/audio/mix.wav
```
:::

::: details O medidor de zona segura marcou ERRO
**Sintoma.** O `safe_zone_check.py` termina com `1 erro(s)` ou mais e lista o elemento, o tempo e a borda que entrou na zona (`right +38px`, por exemplo).

**Causa.** Um texto, card, ícone ou logo ficou 0,5 s ou mais dentro da faixa que a interface do app cobre.

**Solução.** Mova ou reduza o elemento até ele caber na área livre. Se for só decoração de fundo, marque com `data-safe-ignore`, e o medidor passa a ignorar aquele elemento. O [playground da zona segura](/referencia/plataformas) mostra quanto cabe em cada preset.
:::

## Também apareceu

- `Prompt is too long` numa sessão de 16 horas: rode `/compact` ou abra uma sessão nova por vídeo. Cada etapa fica gravada em `projects/<slug>/`, então o agente retoma de onde parou.
- `[Compiler] WARNING: Failed to download CDN script: https://cdn.jsdelivr.net/npm/gsap@.../gsap.min.js (TypeError: fetch failed)` sem internet: salve o `gsap.min.js` em `video/assets/vendor/` e aponte o `<script>` para ele.
- `Continuing render despite lint issues` é aviso, não erro. Para ver os problemas: `npx hyperframes check`.

Achou outro erro? Abra uma [issue de bug](https://github.com/eusilvio/motion-cena/issues) com a mensagem, o sistema e o agente que você usa.
