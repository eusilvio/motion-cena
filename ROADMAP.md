# Frentes abertas

Lugares onde o motion-cena ainda tem buraco e onde ajuda é bem-vinda. Não é lista de promessas nem tem data: cada item diz o que falta e por onde começar. As marcadas com **boa primeira contribuição** cabem num PR pequeno e têm passo a passo no [CONTRIBUTING.md](CONTRIBUTING.md).

Antes de pegar uma frente grande, abra uma issue dizendo o que pretende fazer, para ninguém trabalhar duas vezes na mesma coisa.

## Conteúdo da skill

**Levar efeitos do catálogo para os curados** · boa primeira contribuição
O catálogo em `references/motion-dictionary/` tem 388 efeitos, e só 44 têm cena de demo renderizada. Os outros 344 rodam no navegador nos testes, mas ninguém os viu num vídeo. Escolher um, montar a cena na demo, olhar os quadros e corrigir o que ficar feio é um PR pequeno (CONTRIBUTING, porta 1b). Famílias sem nenhum curado ainda, como partículas, 3D e interface, são as que mais precisam.

**Efeitos que faltam no catálogo**
Termos que motion designers usam e que o catálogo ainda não tem entram como JSON na família certa, validados pelo `motion_lookup.py --validate` (CONTRIBUTING, porta 1a).

**Receitas de estilo da comunidade** · boa primeira contribuição
`references/styles/community/` começa vazia. Gramáticas próprias ou de gênero e escola, como grade tipográfica suíça, telejornal, tipografia cinética ou colagem de fanzine, viram estilos que qualquer pessoa pede pelo nome (CONTRIBUTING, porta 2).

**Mais presets de plataforma**
`assets/platforms.json` cobre Instagram, Facebook Reels, TikTok, YouTube e LinkedIn. Kwai, Threads, Pinterest, Snapchat Spotlight e Status do WhatsApp ainda não têm preset. Cada um precisa de canvas, durações e zona segura tirados da documentação oficial da plataforma, com a fonte citada.

**Texto sem cara de IA em outros idiomas**
O `lint_copy.py` e as listas de frase de `writing-style.md` e `hooks.md` só cobrem pt-BR. Para vídeo em inglês ou espanhol, o agente aplica os princípios de cabeça. Uma lista de padrões por idioma, com teste, resolveria.

## Pipeline e scripts

**Mais testes** · boa primeira contribuição
`tests/` acabou de nascer e boa parte dos scripts de `.agents/skills/motion-cena/scripts/` ainda não tem teste. Função pura, como a casagem de palavras do `build_timeline.py` ou a leitura de presets do `platform_preset.py`, é um bom começo.

**Outros motores de voz**
`references/voiceover.md` cita Kokoro e Piper como opção local e offline, mas não existe script para eles. Hoje há `tts_edge.py`, `tts_elevenlabs.py` e `tts_chatterbox.py`. Um motor novo precisa gerar `audio/voice.mp3` e `audio/words.json` no mesmo formato, com timestamp nativo ou passando pelo `align_words.py`.

**Windows nativo**
Já existe `setup.ps1`, mas `qa_video.sh`, `analyze_reference.sh` e `tools/check.sh` são bash. Falta portar esses passos ou rodar o pipeline inteiro no PowerShell e documentar o que precisa de WSL.

**Remotion de ponta a ponta**
`references/engines.md` descreve o caminho com Remotion, mas as demos e os checks só exercitam o HyperFrames. Falta um projeto de teste que passe pela locução, pela timeline e pelo render em Remotion, e a correção do que quebrar no caminho.

## Ferramentas

**Interface `tools/studio` para mais agentes**
O chat ao lado do vídeo funciona com Claude Code, Codex e Antigravity. Para OpenCode, Gemini CLI ou Copilot CLI entrarem, cada um precisa de uma entrada em `tools/studio/server.mjs` que rode o agente e leia a saída dele em streaming, como as três que já existem.

**Relatos de outras máquinas**
O pipeline foi exercitado em poucas máquinas. Rodar o fluxo completo num sistema diferente (macOS, Windows, outra distribuição Linux) e abrir uma issue de bug com o que quebrou ajuda tanto quanto código.
