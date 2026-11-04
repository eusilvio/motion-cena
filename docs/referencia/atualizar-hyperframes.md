---
title: Atualizar o HyperFrames
description: Como conferir e aplicar uma versão nova das skills do HyperFrames com o tools/update-skills.sh, sem quebrar o pipeline.
---

# Atualizar o HyperFrames

As skills do HyperFrames em `.agents/skills/` (todas menos `motion-cena/`) são cópias de uma versão publicada do [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes). Cada versão do pacote `hyperframes` no npm tem uma tag `vX.Y.Z` no GitHub com as skills daquela versão. O `skills-lock.json` guarda a tag de origem (campo `ref`) e o hash de cada pasta: é ali que você vê a versão instalada hoje.

Não edite essas skills à mão. Bug nelas vai para o repositório do HyperFrames, e a versão nova chega por este script.

## Conferir

```bash
tools/update-skills.sh
```

Sem opção, o script só confere: mostra a versão atual, a última publicada e o que mudaria. Não muda nada. O código de saída diz o resultado:

| Saída | Significa |
|---|---|
| `0` | em dia |
| `2` | há atualização |
| `1` | erro |

## Aplicar

```bash
tools/update-skills.sh --apply                # atualiza para a última versão
tools/update-skills.sh --apply --to 0.9.13    # ou para uma versão específica
```

O `--apply` recusa quando:

- `.agents/skills/` ou o `skills-lock.json` têm mudança sem commit;
- você editou uma skill do HyperFrames que o update ia sobrescrever. Para seguir mesmo assim: `--overwrite-local nome1,nome2`;
- a versão nova tira uma skill que o `AGENTS.md` ou a skill `motion-cena` citam. `--allow-breaking` aplica e deixa as citações para você ajustar antes do commit.

Quando passa, ele troca as pastas, grava a versão nova no lock, refaz os links de `.claude/skills/`, confere hashes e citações e roda o `tools/check.sh`. Nunca mexe em `.agents/skills/motion-cena/` e não faz commit.

## Todas as opções

| Opção | Faz |
|---|---|
| `--check` | só confere e mostra o que mudaria (o padrão) |
| `--apply` | aplica a atualização |
| `--to <versão>` | versão de destino; sem ela, `hyperframes@latest` no npm |
| `--from <versão>` | versão de onde vieram as skills instaladas, quando o `skills-lock.json` não registra (só serve para comparar arquivos) |
| `--allow-breaking` | aplica mesmo se sair uma skill que o motion-cena cita |
| `--overwrite-local a,b` | sobrescreve essas skills mesmo com mudança local |

## Desfazer

Antes do commit, use o comando que o script imprime no fim (ele também aparece se algo falhar no meio). Depois do commit, `git revert <commit>` desfaz o update inteiro.

::: warning Evite `npx skills update` direto neste repositório
Ele atualiza só parte das skills, deixa as que saíram do upstream e acaba misturando versões. O `skills-lock.json` segue o formato do `npx skills`, e o script grava o `ref` que o `npx skills update` respeita, mas a troca completa e conferida é a do `tools/update-skills.sh`.
:::

## As demos ficam na versão delas

As demos do dicionário em `training/dicionario-demo*/` fixam a versão do HyperFrames no próprio `package.json` e continuam na versão em que foram validadas. Ao atualizar, o script mostra o comando para conferir cada uma antes de subir a versão delas.
