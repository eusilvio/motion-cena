# Ready-made prompts (for the user to copy)

Adapted from the 3-step method (Deborah Folloni, "O novo Claude Motion cria vídeos INSANOS", Oct/2026). With this skill installed, a short request already triggers the flow; these prompts give fine control. The prompts are in pt-BR; the user can write them in any language.

## Prompt 01: Plan (format + script + storyboard)

```
Quero fazer um Instagram Reels baseado neste [PDF/artigo/link].

1. Analise o conteúdo e encontre os takes mais interessantes considerando minha audiência ([descreva]). A ideia é contar uma história com os números, não jogar dados soltos.
2. Teste pelo menos 4 formatos narrativos (comparação, transformação, listicle, mito×verdade...) e escolha o melhor ângulo.
3. Escreva o roteiro no ângulo escolhido, no meu tom de voz, com 3 alternativas de hook.
4. Separe em cenas e descreva cada uma pensando como motion designer: visual, movimento, palavra-âncora, transição e SFX. Cenas sempre dinâmicas para retenção.

Me entregue um documento com: análise de formatos + escolha, roteiro com 3 hooks, storyboard. Ele será usado para produzir o vídeo, então inclua todo o contexto necessário.
```

## Prompt 02: Production

```
Ok, agora transforme essa história em um vídeo de motion design bem dinâmico para Reels (1080×1920).
- Locução: [Higgsfield MCP / ElevenLabs voz X / edge-tts Francisca]
- Estilo visual do meu site [URL]
- Efeitos sonoros sincronizados com a animação
- Captions queimadas: [sim/não]
Qualquer coisa que precisar, me avisa.
```

## Narrated-text prompt (no article, no website)

```
Narra esse texto num vídeo para [Story / Reels / TikTok / Shorts / YouTube]. É um vídeo [motivacional / de história / técnico / explicativo].
[Duração: 30 s]
[cole o texto]
```

By default the text is adapted for video and for the duration. Variations: "usa o texto exatamente como está" (use the text exactly as is: becomes literal narration), "faz também a versão pra YouTube horizontal" (also make the horizontal YouTube version: extra format with the same narration), "divide em 3 stories" (split into 3 stories).

## Loose-topic prompt

```
Faz um vídeo explicativo de ~45 s pro TikTok sobre [tema]. Pesquisa os fatos, me mostra o roteiro com 3 hooks antes de narrar.
```

## Prompt 03: Motion direction (dictionary)

Formula: effect + duration + ease + target. Terms in `references/motion-dictionary.md`.

```
Faça o título entrar com slide in em 0,4 s e ease out. Revele os benefícios com stagger de 0,15 s.
Troque "ideia" por "vídeo" com text swap. Termine com um punch zoom no produto e transição wipe na cor de acento.
```

## Common iterations

- "Gera a versão com o hook B" (make the hook B version) → only re-record the scene 1 voice + re-timeline + re-render.
- "Adiciona efeitos sonoros" / "tira a música" (add sound effects / remove the music) → only step 7 + render.
- "Troca a entrada do título por blur in 0,5 s" (change the title entrance to blur in 0.5 s) → only the effect line in step 6 + re-render.
- "Deixa mais rápido" (make it faster) → voice rate +5%, shorter scenes, more cuts.
- "Faz versão 16:9 para YouTube" (make a 16:9 version for YouTube) → same timeline, recompose the layout at 1920×1080.
- "Cria minha skill de tom de voz" (create my tone-of-voice skill) → gather 5–10 scripts and use skill-creator.
