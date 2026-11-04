# Short-video script

## Tone of voice

1. Look for a script/tone skill from the user that is already installed (the user's skills in the agent, project skills in `.agents/skills/`). Use it.
2. None? Write in a neutral, direct tone and **offer** to create one: the user gathers 5–10 old scripts, and you use skill-creator to generate a "roteiro-<nome>" skill that captures vocabulary, rhythm, typical openings, catchphrases and level of formality. It is the shortest path to non-generic copy.
3. Never imitate a specific real creator unless the user asks for it.

## No AI feel

Read `references/writing-style.md` before writing. Forbidden (pt-BR patterns; in other languages, their equivalents): "não é X, é Y", bait question ("O segredo?"), "mergulhar", "jornada", "desbloquear", "revolucionar", "no mundo de hoje", "isso muda tudo", em dash for effect, adjective triad, emoji. Check with `uv run scripts/lint_copy.py projects/<slug>/narration.txt`.

## Hooks (always 3)

The first 3s decide whether the person stays. Read `references/hooks.md` (triggers and the gap test; mandatory). Write 3 hooks from different triggers, run each through the test and recommend the highest-scoring one:

| Mechanic | Example |
|---|---|
| Shocking number | "Noventa e tantos por cento das maiores empresas dos EUA dizem usar IA. Quase nenhuma sabe se funciona." |
| Contradiction | "Quase toda empresa grande diz que usa IA. Uma em cada dez mede se deu resultado." (contrast with a fact, not a symmetric punchline) |
| Promise + proof | "Fiz esse vídeo em 18 minutos sem saber editar. Te mostro como." |
| Direct question | "Sua empresa está no raso ou no fundo da piscina?" |
| Impossible visual | (describes an image that only makes sense when watched) |

Visual and spoken hook together: the scene 1 storyboard needs motion already at frame 0 (no slow 1s fade-in).

## Structure (30–60s)

```
0–3s    HOOK        promessa/tensão
3–10s   CONTEXTO    mínimo necessário (fonte, quem diz)
10–40s  DESENVOLVIMENTO  2–4 batidas, cada uma escalando a tensão
40–52s  VIRADA/PAYOFF    o insight que justifica o vídeo
52–60s  FECHO       escolhido pela intenção do vídeo (ver abaixo)
```

## Ending: choose by intent, not by habit

Not every video ends in lesson + question. When the user only wants to tell someone's story, the video ends with the story. Before writing the end, ask yourself: what does the user want to stay with the viewer?

| Intent | Ending | Example |
|---|---|---|
| Just tell the story (profile, tribute, case) | last fact or strong image, no moral | "E aquela loja de garagem hoje tem três unidades." |
| Teach something | the takeaway in one sentence | "Juros compostos trabalham enquanto você dorme." |
| Open a conversation | open question for the viewer | only when the topic calls for opinion or the user asked |
| Sell / call to action | concrete CTA | "Link na bio." |
| Replay | a sentence that reconnects to the hook (loop) | |

Vary across videos: if the user's last videos ended in a question, don't repeat it by default. A final question and a "lesson" are never mandatory.

## Writing for the ear (TTS)

- Sentences of 6–14 words. One idea per sentence.
- Numbers written the way they are spoken. In pt-BR: "quase nove em cada dez" (almost nine in ten), not "87,3%"; in other languages, the same with their spoken forms. The screen can show the exact figure.
- Avoid acronyms the TTS misreads; in the narration version write them as pronounced (pt-BR: "a dezesseis z" for a16z) and keep the correct spelling on screen.
- Punctuation controls rhythm: comma = short pause, period = pause, ellipsis = suspense (the TTS respects it).
- ~2.5 words/s in natural pt-BR; 2.8–3 for Reels pace.

## Output in plan.md

```
## Roteiro
**Hook recomendado:** A
- Hook A: ...
- Hook B: ...
- Hook C: ...

**Narração (com Hook A):**
<texto corrido, exatamente o que será falado>

Palavras: N · duração estimada: Xs
Fontes dos números: <dado → página>
```

Also save the plain narration (only the spoken text) to `projects/<slug>/narration.txt`: it is the TTS input.
