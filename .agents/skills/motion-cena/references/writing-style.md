# Write like a person, not like an AI

Applies to everything that ends up in a piece: script, on-screen text, captions, carousel slides, post caption, end card, titles. Readers spot AI text in one line and stop trusting it. Write the way the user talks in a conversation: concrete, direct, in their vocabulary.

Copy is written in the user's language. The concrete phrase lists below are pt-BR and are what `scripts/lint_copy.py` checks; for other languages, apply the same principles with that language's equivalents.

Before delivering, run the checker:

```bash
uv run scripts/lint_copy.py projects/<slug>/narration.txt projects/<slug>/storyboard.json creatives/carrossel/<slug>-*/legenda.txt projects/<slug>/carousel/claude-design/project/*.dc.html
```

Error = rewrite. Warning = reread and decide (sometimes the word is the right one). In `roteiro` mode (default) the adaptation already replaces whatever the checker flags, and you say what you replaced. Only in `narracao-literal` do not rewrite: show the findings and suggest; the user decides.

## Forbidden (marks of AI text)

Applies when the output language is pt-BR. For other languages, forbid the equivalent structures and words in that language.

**Structures**
- Symmetric contrast: "Não é sobre X, é sobre Y." (it's not about X, it's about Y), "Não é só X. É Y.", "Mais do que X, é Y.", "X? Não. Y." Say directly what it is.
- One-word bait question: "O segredo?" (the secret?), "O resultado?", "A diferença?", "Spoiler:", "Plot twist:".
- Announcing what comes next: "Aqui está o porquê" (here's why), "Deixa eu te contar", "Vou te explicar", "E sabe o que mais?", "E o melhor:", "Presta atenção".
- Punchline ending: "Isso muda tudo." (this changes everything), "E tudo bem.", "Pensa nisso.", "Fica a reflexão.", "Simples assim.", "E é isso."
- Automatic adjective triad ("rápido, simples e eficiente") and three short sentences in a row with the same rhythm.
- Rhetorical questions in series (two or more in a row).
- Em dash (—) for a dramatic pause in piece copy. Use a period, comma or colon.
- Ellipsis for suspense in written copy ("e então..."). In TTS narration, only if the pause is needed.
- Consecutive exclamation marks, ALL CAPS for shouting, emoji (always forbidden).

**Words and phrases**

| Avoid | Prefer |
|---|---|
| no mundo de hoje, nos dias de hoje, em um mundo cada vez mais…, no cenário atual ("in today's world" openers) | state the fact and the date: "em 2026", "este ano" |
| mergulhar, mergulho profundo (dive, deep dive) | ver, entender, olhar de perto |
| jornada (journey; outside an actual trip) | caminho, os anos de, o processo |
| desbloquear, destravar o potencial, potencializar, alavancar, impulsionar, elevar (unlock, leverage, boost, elevate) | the concrete verb: aumentar, vender mais, aprender, ganhar tempo |
| revolucionar, transformador, divisor de águas, virada de chave, game changer (revolutionize, game changer) | what changed, with a number |
| crucial, fundamental, essencial, vital | cut it, or say why |
| robusto, holístico, sinergia, paradigma, ecossistema, alinhamento (corporate jargon) | the actual thing being discussed |
| incrível, surreal, insano, absurdo (as praise) | the fact that impresses |
| vale ressaltar, é importante destacar, nesse sentido, em suma, em resumo, além disso (essay connectors) | cut; start with the information |
| descubra, o que ninguém te conta, ninguém está falando sobre isso (clickbait) | state the fact |
| navegar (figurative), abraçar a mudança, sair da zona de conforto | what the person actually does |
| literalmente, simplesmente, basicamente | cut |
| fique ligado, vamos juntos, bora (generic calls to action) | the concrete question or CTA |

## What right sounds like

- **Concrete before abstract**: name, number, place, year. "Levei 3 anos de anúncio pra juntar 100 dólares" and not "a jornada do empreendedor é desafiadora".
- **One idea per sentence**, clear subject and verb, direct word order.
- **The user's vocabulary**: if they say "grana" (money, slang), "a parada" (the thing), "cara" (dude), use theirs, not a corporate "brand register". In pt-BR: if the request or the person speaking in the recording uses "você", never use "tu" (and vice versa). In other languages, match the user's form of address the same way.
- **End with a real question or a specific action**: "Qual o seu horário de trabalhar nos seus projetos?" and not "Pensa nisso."
- **Hook through the fact**: "A Torre Eiffel fica até 15 cm mais alta no verão." No need for "Você não vai acreditar".

## Rewrite examples

| AI | Human |
|---|---|
| "Não é sobre dinheiro. É sobre liberdade." | "Eu não queria mais dinheiro. Queria sair do trabalho às 18h." |
| "O segredo? Consistência." | "Postei todo dia por 60 dias." |
| "No mundo de hoje, a IA está revolucionando tudo." | "Este ano eu fiz meu app em metade do tempo usando IA." |
| "Bora mergulhar nessa jornada incrível?" | "Vou te mostrar como foi o primeiro mês." |
| "Isso muda tudo." | (cut; the previous sentence already said it) |
| "Disciplina, foco e resiliência." | "Treinava balé de manhã e estudava física de noite." |
| "Tem o cara que faz e tem o cara que só fala." | "Eu fiz o app em um fim de semana e não mostrei pra ninguém por dois meses." |
| "Movimento gera movimento." | "Manda pra uma pessoa hoje. Uma só." |
| "Fiquei 3 dias sem abrir o notebook. A lição aqui é que medo se disfarça de cansaço." | "Fiquei 3 dias sem abrir o notebook. Disse pra mim mesmo que era cansaço." |
| "Sinceramente? Depende do uso." | "Depende de quantas vezes por semana você vai usar." |
| "Especialistas dizem que a gente dorme mal." | "[número] dos adultos dormem menos de 7 horas, segundo [fonte] em [mês/ano]." (real data from the source) |
| "Ele vendeu 1 milhão, evidenciando a força do digital." | "Ele vendeu 1 milhão. Sem loja, só pelo Instagram." |

## More AI marks (from `humanizer`, adapted for scripts)

**Guru register** (the business-speaker tone that sounds like a sales pitch)
- Coach dichotomy: "tem o cara que X e tem o cara que Y" (there's the guy who X and the guy who Y), "existem dois tipos de pessoa", "enquanto uns X, outros Y". It invents two caricatures so the conclusion wins by default. Replace it with a real case.
- Slogan with no mechanism: "movimento gera movimento", "disciplina é liberdade", "faça acontecer", "quem quer dá um jeito". You can't test it or do anything with it. Replace it with the specific action.
- Stacked moral at the ending: two or three punchlines in a row at the end. One conclusion only (see `references/script-writing.md`, "Ending: choose by intent, not by habit").
- Spelled-out conclusion: "anota aí", "o insight é", "a lição aqui é", "sacou?", "ou seja:" (write this down, the insight is, the lesson here is, get it?, in other words) after a scene that already said it all. If cutting it loses nothing, cut it.

**Structure**
- Dangling gerund at the end of the sentence to fake depth: "…, evidenciando / reforçando / demonstrando / proporcionando / refletindo" (…, highlighting / reinforcing / showing). Write another sentence with the fact.
- Inflated importance: "marcou um momento", "desempenha um papel fundamental", "um testemunho de", "deixou sua marca". Say what happened.
- Vague attribution: "especialistas dizem", "estudos mostram", "pesquisas apontam" (experts say, studies show). Name the source and date, or cut.
- Façade authority: "a verdadeira questão é", "o que realmente importa", "no fundo", "na essência". Say the thing.
- Fake-sincere opener: "Sinceramente?", "Olha só:", "A real é que…" as a pause before an ordinary point.
- Formula aphorism: "X é a linguagem de Y", "X vira armadilha", "X não é ferramenta, é espelho". Replace it with the concrete statement.
- Manufactured staccato: three or more sentences of 1 to 3 words in a row to create drama ("Sem atalho. Sem desculpa. Sem volta."). One short emphasis sentence is fine; the machine gun is not.
- Rotating synonyms: "o empresário… o fundador… o executivo… o homem" for the same person. Repeat the name or "ele".
- False range: "do X ao Y" (from X to Y) when X and Y are not on a scale ("do sonho à realidade").
- More than one hedge in the same sentence: "talvez possa potencialmente". One is enough.
- Spaced hyphen instead of an em dash (" - "): same rule as the em dash.

**Words** (beyond the table above): abordagem, vivência, protagonismo, resiliência, agregar valor, otimizar (outside a technical context), cenário/panorama (figurative), pilar (figurative), vibrante, rico (figurative), tapeçaria.

## Speech rhythm

Sentences of the same length in a row sound read aloud. Vary by each sentence's role:

| Role | Spoken length |
|---|---|
| impact (stops the viewer) | 2 to 5 words, on its own |
| narrative (tells the scene) | 10 to 16 words |
| explanation (delivers the point) | 6 to 10 words |
| transition (links blocks) | 3 to 6 words |

Four sentences in a row of similar length is a flat line: break one. The fix is not "more short sentences": a machine gun of short ones is the opposite mistake.

## The predictable choice (from `de-default`)

Copy can pass the checker and still sound machine-made because every choice is the most likely one. After cleaning up, do one more pass:

1. **Default word**: the abstraction any model would use ("constância", "propósito", "mindset", "sucesso"). Replace it with the concrete thing from the story's world (the number, the object, the place, the time of day).
2. **Generic example**: "ir pra academia", "acordar cedo", "o cara que desistiu" (going to the gym, waking up early, the guy who gave up). Use the real data from `source/` or the brief. If there is none, **ask the user** for their case. Never invent a scene, number or quote.
3. **Punchline in every scene**: save it for 1 or 2 moments (the hook and the turn or the ending). The rest ends without a bow.
4. **Template repeated across videos**: check the "Time structure" of the latest pieces (`scripts/registro.py --recent 3`). If the new script has the same sequence of moves as the last 3 (e.g. mistake scene → concept → what to do → question), reorder it.
5. **"Cover the line and guess" test**: at the hook, the turn and the ending, cover the sentence and write what a model would say there. If it matches yours, switch to your second or third thought.

## What NOT to touch

- A single short sentence on its own for emphasis.
- An open loop that points forward ("Guarda esse número.", "Repara no que ele faz depois."): it is a hook trigger (`references/hooks.md`), not a spelled-out conclusion.
- Quoted speech from someone else (interview, talk): only the captions replace "tu" and profanity; the content stays.
- A single connector ("além disso" once). The signal is accumulation.
- A specific, odd detail, mixed feelings, a sentence that corrects itself midway: these are signs of a person. Keep them.

## Process

1. Write the draft.
2. Ask: **"what still sounds like AI here?"** and list it in 2 or 3 lines.
3. Rewrite, do the predictable-choice pass (above) and run `lint_copy.py`.
4. On delivery, say in one line what was changed.
