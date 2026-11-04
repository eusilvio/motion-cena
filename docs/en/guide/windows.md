---
title: Windows
description: How to run motion-cena on Windows, through WSL 2 (recommended) or native PowerShell, and what does not run natively.
---

# Windows

Use **WSL 2**. There the whole pipeline runs, same as on Linux. `setup.ps1` prepares the folder from PowerShell, but on native Windows part of the flow does not run (the limits are at the end of this page).

## WSL 2 (recommended)

1. Open PowerShell as administrator, install Ubuntu and restart the computer:

   ```powershell
   wsl --install -d Ubuntu-24.04
   ```

   After restarting, open **Ubuntu** from the Start menu and create your username and password. All the commands below run in that terminal.

2. Install FFmpeg, Git, Node (through nvm) and uv:

   ```bash
   sudo apt update && sudo apt install -y git ffmpeg
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   exec bash                 # reloads the terminal with nvm and uv on the PATH
   nvm install --lts
   ```

3. Install the Chromium libraries. The render and the safe-zone checker use a headless Chrome:

   ```bash
   uvx playwright install --with-deps chromium
   ```

4. Clone **inside your Linux file system**, not in `/mnt/c`:

   ```bash
   cd ~
   git clone https://github.com/eusilvio/motion-cena.git
   cd motion-cena
   ./setup.sh
   npx hyperframes doctor    # checks Chrome and FFmpeg
   ```

   ::: warning Stay out of `/mnt/c`
   In `/mnt/c` every file access crosses over to Windows: `npx` and rendering get much slower, and the live preview does not notice files edited by Windows programs.
   :::

5. Install and open your agent in the same terminal, at the project root (`claude`, `codex`, `opencode` or another). For VS Code or Cursor, run `code .` or `cursor .` from here. The editor opens connected to WSL.

### Where the videos are

To open the finished videos in Windows, run `explorer.exe creatives` inside the project, or open `\\wsl.localhost\Ubuntu-24.04\home\<your-username>\motion-cena` in Explorer.

If you cloned from Windows earlier and `./setup.sh` fails with `bash\r`, clone again inside WSL.

## Native PowerShell

```powershell
winget install Git.Git
winget install OpenJS.NodeJS.LTS
winget install Gyan.FFmpeg
winget install astral-sh.uv
# close and reopen the terminal so the new PATH takes effect
git clone https://github.com/eusilvio/motion-cena.git
cd motion-cena
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

`setup.ps1` does the same as `setup.sh` and tells you what is missing. In `.claude\skills` it creates junctions, which do not need administrator rights. If you move the project folder, run `setup.ps1` again.

### What does not run natively

- `qa_video.sh` and `analyze_reference.sh` are bash scripts. Claude Code runs both through Git Bash when Git for Windows is installed. Agents that run commands in PowerShell (Codex, Gemini CLI, Copilot CLI) cannot run them.
- The `tools/studio` interface, with chat and preview side by side, does not run on native Windows.
- `tools/check.sh`, which runs the tests before a PR, is bash too: use Git Bash or WSL.

::: tip Script execution disabled
If PowerShell says running scripts is disabled when you run `npx`, allow it for your user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
:::

CI runs `setup.ps1` on PowerShell 7 and Windows PowerShell 5.1 on every push, to make sure preparing the folder keeps working. Porting the bash scripts to Windows is one of the [open fronts](/en/community/roadmap).
