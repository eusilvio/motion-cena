---
title: Tests and checks
description: What tools/check.sh runs on your machine, what CI runs on every push and pull request, and how to run only the Python tests.
---

# Tests and checks

Before opening a pull request, run at the repository root:

```bash
./tools/check.sh
```

It runs the same checks as CI (`.github/workflows/ci.yml`) on your machine, works from any folder and takes about half a minute. Each check runs even if the previous one failed. When something breaks, the script shows the output of the check that failed and exits with an error.

## What you need

`git`, `uv`, Node 22 or newer, `ffmpeg` and `ffprobe`: the same ones `setup.sh` checks. If any is missing, `check.sh` lists it and stops before the checks. shellcheck and actionlint come through `uvx`, without installing anything system-wide.

`check.sh` is bash. On Windows, run it through Git Bash or WSL.

## The checks

| Check | What it verifies |
|---|---|
| Line endings | no file in the repository with CRLF (`.gitattributes` sets LF; CRLF breaks the scripts on Linux and WSL) |
| Python tests | the tests in `tests/` with pytest, on synthetic fixtures |
| Docs text | `lint_copy.py` on the Portuguese `.md` files at the root (English ones, like `AGENTS.md` and `README.en.md`, are left out); an error fails, a warning is only shown |
| shellcheck | the project's `.sh` scripts and the `motion-cena` skill's |
| Workflows | actionlint on the GitHub workflow, which also runs shellcheck on the `run:` blocks |
| HyperFrames tests | the `node --test` tests that ship with the HyperFrames skills, offline (three are left out because they depend on the HyperFrames monorepo) |

### The 388 effects in a browser

One of the Python tests runs every effect in the dictionary catalog in a headless Chromium: it builds the effect on a paused timeline and checks that it throws no error, that the timing adds up, that seeking to any frame always gives the same result and that entrances end visible and exits end hidden. It needs Playwright's Chromium; without it, the test is skipped and `check.sh` shows the notice.

```bash
uv run --with playwright==1.58.0 playwright install chromium
```

### The speech sync has a reference test

`build_timeline.py`, which anchors the scenes to the spoken words, has a reference test: a fixed `words.json` and storyboard in `tests/fixtures/timeline/` must produce exactly the expected `timeline.json`.

## Run only the Python tests

```bash
uv run -q --no-project --with "pytest>=8,<10" pytest -c tests/pytest.ini tests -q
```

For a single file, replace `tests` with its path, such as `tests/test_build_timeline.py`.

## What CI runs

The workflow runs on every push and every pull request, with two jobs:

- **Linux** (`ubuntu-latest`): installs uv, Node 22, FFmpeg and Playwright's Chromium, and runs the same `./tools/check.sh`. So in CI the 388 effects always run in the browser.
- **Windows** (`windows-latest`): runs `setup.ps1` on PowerShell 7 and, in a fresh copy of the repository, on Windows PowerShell 5.1. It checks that the script creates `.env.local`, `creatives/registro.md` and the skill link in `.claude/skills/`, and that running it again neither fails nor overwrites `.env.local`.

## Changed a script?

The PR brings a test in `tests/` that fails without the fix and passes with it, following the pattern of the tests already there. Many scripts still have no test, and writing one is a good first contribution. See [Contributing](/en/community/contributing) and the [open fronts](/en/community/roadmap).
