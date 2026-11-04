---
title: Windows
description: Como rodar o motion-cena no Windows, pelo WSL 2 (recomendado) ou pelo PowerShell nativo, e o que não roda no nativo.
---

# Windows

Use o **WSL 2**. Nele o pipeline roda inteiro, igual no Linux. O `setup.ps1` prepara a pasta pelo PowerShell, mas no Windows nativo parte do fluxo não roda (os limites estão no fim desta página).

## WSL 2 (recomendado)

1. Abra o PowerShell como administrador, instale o Ubuntu e reinicie o computador:

   ```powershell
   wsl --install -d Ubuntu-24.04
   ```

   Depois de reiniciar, abra **Ubuntu** no menu Iniciar e crie seu usuário e senha. Todos os comandos abaixo rodam nesse terminal.

2. Instale FFmpeg, Git, Node (pelo nvm) e uv:

   ```bash
   sudo apt update && sudo apt install -y git ffmpeg
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   exec bash                 # recarrega o terminal com nvm e uv no PATH
   nvm install --lts
   ```

3. Instale as bibliotecas do Chromium. O render e o medidor de zona segura usam um Chrome sem janela:

   ```bash
   uvx playwright install --with-deps chromium
   ```

4. Clone **dentro da sua pasta do Linux**, não em `/mnt/c`:

   ```bash
   cd ~
   git clone https://github.com/eusilvio/motion-cena.git
   cd motion-cena
   ./setup.sh
   npx hyperframes doctor    # confere Chrome e FFmpeg
   ```

   ::: warning Fora de `/mnt/c`
   Em `/mnt/c` cada acesso a arquivo atravessa para o Windows: `npx` e render ficam bem mais lentos, e o preview ao vivo não percebe arquivos editados por programas do Windows.
   :::

5. Instale e abra seu agente no mesmo terminal, na raiz do projeto (`claude`, `codex`, `opencode` ou outro). No VS Code ou no Cursor, rode `code .` ou `cursor .` aqui dentro. O editor abre conectado ao WSL.

### Onde ficam os vídeos

Para abrir os vídeos prontos no Windows, rode `explorer.exe creatives` dentro do projeto, ou abra `\\wsl.localhost\Ubuntu-24.04\home\<seu-usuário>\motion-cena` no Explorer.

Se você clonou pelo Windows antes e o `./setup.sh` falha com `bash\r`, clone de novo dentro do WSL.

## PowerShell nativo

```powershell
winget install Git.Git
winget install OpenJS.NodeJS.LTS
winget install Gyan.FFmpeg
winget install astral-sh.uv
# feche e abra o terminal para o PATH novo valer
git clone https://github.com/eusilvio/motion-cena.git
cd motion-cena
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

O `setup.ps1` faz o mesmo que o `setup.sh` e avisa o que falta. Em `.claude\skills` ele cria junctions, que não pedem administrador. Se você mover a pasta do projeto, rode o `setup.ps1` de novo.

### O que não roda no nativo

- `qa_video.sh` e `analyze_reference.sh` são scripts bash. O Claude Code roda os dois pelo Git Bash quando o Git for Windows está instalado. Agentes que executam comandos no PowerShell (Codex, Gemini CLI, Copilot CLI) não conseguem.
- A interface `tools/studio`, com chat e preview lado a lado, não roda no Windows nativo.
- O `tools/check.sh`, que roda os testes antes de um PR, também é bash: use o Git Bash ou o WSL.

::: tip Execução de scripts desabilitada
Se o PowerShell disser que a execução de scripts está desabilitada ao rodar `npx`, libere para o seu usuário:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
:::

O CI roda o `setup.ps1` no PowerShell 7 e no Windows PowerShell 5.1 a cada push, para garantir que a preparação da pasta continua funcionando. Portar os scripts bash para o Windows é uma das [frentes abertas](/comunidade/roadmap).
