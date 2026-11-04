---
title: Estilos de referência
description: Receitas de gramática de vídeo que você pede pelo nome. As locais saem de um vídeo de referência; as da comunidade ficam no repositório.
---

# Estilos de referência

Um estilo é a receita de uma gramática de vídeo: o mecanismo que prende a atenção, a estrutura com tempos, a linguagem visual, os componentes, o som e como adaptar. Salvo uma vez, você pede pelo nome:

```text
Faz um reels de 15 s sobre juros compostos no estilo <nome>.
```

O estilo empresta a **gramática**: estrutura, ritmo, tipo de componente. Marca, texto, objetos e números são sempre os seus; da peça original não entra logo, personagem nem texto.

## Dois tipos, dois lugares

| Tipo | Onde fica | No git | Vem de |
|---|---|---|---|
| Local | `references/styles/<nome>.md` | não | um vídeo de referência que você mandou, a peça de outra pessoa |
| Comunidade | `references/styles/community/<nome>.md` | sim | uma gramática criada por quem escreveu, ou um gênero ou escola sem dono |

Quando você pede um estilo, o agente procura nos dois lugares. Se o mesmo nome existir nos dois, o local vence. Os caminhos são relativos a `.agents/skills/motion-cena/`.

## Estilo local, a partir de um vídeo

1. Copie o vídeo para `training/referencias/ref-01.mp4` (essa pasta fica fora do git).
2. Peça: *"analisa esse vídeo e cria um estilo"*.
3. O agente roda a análise:

   ```bash
   bash .agents/skills/motion-cena/scripts/analyze_reference.sh training/referencias/ref-01.mp4 training/referencias/ref-01 pt
   ```

   Ela gera pranchas a 2 quadros por segundo com timecode, três quadros em resolução cheia, a fala com timestamps e o loudness.
4. O agente olha as pranchas e escreve a receita seguindo `references/styles/_template.md`: estrutura com tempos, mecanismo, paleta, tipografia, densidade, componentes, transições, relação entre texto e fala, som. Cada componente aponta para um termo do dicionário de efeitos e para uma receita do HyperFrames.

A receita local fica só na sua máquina, porque é a análise da peça de outra pessoa. Ela nunca vai para `community/` nem para o README da pasta.

## Receitas da comunidade

Uma receita da comunidade descreve uma gramática que você criou e usa, ou um gênero ou escola que não tem dono: grade tipográfica suíça, lower thirds de telejornal, tipografia cinética, colagem de fanzine. Ela nunca quebra o vídeo, a série ou o canal específico de alguém: nada de perfil citado, tempos medidos numa peça, logo, personagem, bordão ou texto de terceiros.

O formato é o mesmo `_template.md`, com duas mudanças:

- a linha `Reference:` vira `Origin: own grammar (<autor>)` ou `Origin: genre/school (<nome>)`, com fontes públicas e genéricas se houver;
- os tempos da estrutura são escolha da receita, não a medição de uma peça.

O texto é em inglês, como o resto da skill, e o arquivo tem um nome curto em kebab-case (`swiss-grid.md`).

::: tip A pasta começa vazia
`references/styles/community/` ainda não tem nenhuma receita. Escrever a primeira é uma boa primeira contribuição: o passo a passo está em [Como contribuir](/comunidade/contribuir#porta-2-receita-de-estilo).
:::

Se a receita só faz sentido ao lado de um vídeo específico, ela é local e não entra no repositório.
