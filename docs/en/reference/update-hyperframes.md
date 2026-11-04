---
title: Updating HyperFrames
description: How to check for and apply a new version of the HyperFrames skills with tools/update-skills.sh, without breaking the pipeline.
---

# Updating HyperFrames

The HyperFrames skills in `.agents/skills/` (all except `motion-cena/`) are copies of a published version of [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes). Every version of the `hyperframes` package on npm has a `vX.Y.Z` tag on GitHub with that version's skills. `skills-lock.json` stores the source tag (the `ref` field) and the hash of each folder: that is where you see the version installed today.

Do not edit these skills by hand. Bugs in them go to the HyperFrames repository, and the new version arrives through this script.

## Check

```bash
tools/update-skills.sh
```

With no option, the script only checks: it shows the current version, the latest published one and what would change. It changes nothing. The exit code tells you the result:

| Exit | Means |
|---|---|
| `0` | up to date |
| `2` | an update is available |
| `1` | error |

## Apply

```bash
tools/update-skills.sh --apply                # updates to the latest version
tools/update-skills.sh --apply --to 0.9.13    # or to a specific version
```

`--apply` refuses when:

- `.agents/skills/` or `skills-lock.json` have uncommitted changes;
- you edited a HyperFrames skill that the update would overwrite. To go ahead anyway: `--overwrite-local name1,name2`;
- the new version removes a skill that `AGENTS.md` or the `motion-cena` skill mention. `--allow-breaking` applies it and leaves those mentions for you to fix before committing.

When it passes, it swaps the folders, writes the new version to the lock, recreates the `.claude/skills/` links, checks hashes and mentions, and runs `tools/check.sh`. It never touches `.agents/skills/motion-cena/` and does not commit.

## All options

| Option | Does |
|---|---|
| `--check` | only checks and shows what would change (the default) |
| `--apply` | applies the update |
| `--to <version>` | target version; without it, `hyperframes@latest` on npm |
| `--from <version>` | the version the installed skills came from, when `skills-lock.json` does not record it (only used to compare files) |
| `--allow-breaking` | applies even if a skill motion-cena mentions goes away |
| `--overwrite-local a,b` | overwrites these skills even with local changes |

## Undo

Before committing, use the command the script prints at the end (it also shows up if something fails halfway). After committing, `git revert <commit>` undoes the whole update.

::: warning Avoid running `npx skills update` directly in this repository
It updates only some of the skills, leaves behind the ones that left upstream and ends up mixing versions. `skills-lock.json` follows the `npx skills` format, and the script writes the `ref` that `npx skills update` respects, but the complete, checked swap is the one `tools/update-skills.sh` does.
:::

## The demos keep their own version

The dictionary demos in `training/dicionario-demo*/` pin the HyperFrames version in their own `package.json` and stay on the version they were validated with. When you update, the script shows the command to check each one before bumping their version.
