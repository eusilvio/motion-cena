#Requires -Version 5.1
# Prepara o motion-cena no Windows: confere dependências e cria os arquivos locais (fora do git).
# Pode rodar de novo: nunca sobrescreve o que já existe. Faz o mesmo que o setup.sh.
#
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1     (Windows PowerShell 5.1)
#   pwsh -File setup.ps1                                      (PowerShell 7, também em Linux e macOS)
#
# O pipeline completo (scripts .sh, interface tools/studio) roda no WSL 2 com ./setup.sh.
# Veja a seção Windows do README.
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$root = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
$onWindows = [System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT
$ok = $true

function Test-Tool([string]$Name) {
    [bool](Get-Command -Name $Name -CommandType Application, ExternalScript -ErrorAction SilentlyContinue)
}

function Write-Check([string]$Name, [string]$Hint) {
    if (Test-Tool $Name) {
        '  ok      {0}' -f $Name
    } else {
        '  FALTA   {0}  ({1})' -f $Name, $Hint
        $script:ok = $false
    }
}

function Get-NodeMajor {
    $ErrorActionPreference = 'Continue'
    try { $v = & node --version 2>$null | Select-Object -First 1 } catch { return $null }
    if ("$v" -match '^v?(\d+)\.') { return [int]$Matches[1] }
    $null
}

# Existe alguma entrada no caminho, mesmo um link quebrado?
function Test-Entry([string]$Path) {
    (Test-Path -LiteralPath $Path) -or ($null -ne (Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue))
}

# Caminho completo do destino de uma junction ou link simbólico; $null se não for link.
function Get-LinkTarget($Item) {
    if ($Item.LinkType -notin 'Junction', 'SymbolicLink') { return $null }
    $target = @($Item.Target)[0]
    if (-not $target) { return $null }
    if (-not [System.IO.Path]::IsPathRooted($target)) {
        $target = Join-Path (Split-Path -Parent $Item.FullName) $target
    }
    [System.IO.Path]::GetFullPath($target)
}

# Junction ou link simbólico cujo destino não existe mais. Test-Path não serve: no PowerShell 7
# ele responde $true para o próprio link quebrado.
function Test-DanglingLink($Item) {
    if ($Item.LinkType -notin 'Junction', 'SymbolicLink') { return $false }
    $target = Get-LinkTarget $Item
    if (-not $target) { return $true }
    -not (Test-Path -LiteralPath $target)
}

# Junction no Windows (não pede administrador nem modo desenvolvedor), link simbólico no
# Linux e no macOS, cópia se nenhum dos dois der certo. No Linux, New-Item -ItemType Junction
# volta sem erro e sem criar nada, por isso cada tentativa é conferida.
function Add-SkillLink([string]$Link, [string]$Target, [string]$Relative) {
    if ($onWindows) {
        try { New-Item -ItemType Junction -Path $Link -Target $Target | Out-Null } catch { Write-Debug "$_" }
        if (Test-Path -LiteralPath $Link -PathType Container) { return 'junction' }
    }
    $linkTarget = if ($onWindows) { $Target } else { $Relative }
    try { New-Item -ItemType SymbolicLink -Path $Link -Target $linkTarget | Out-Null } catch { Write-Debug "$_" }
    if (Test-Path -LiteralPath $Link -PathType Container) { return 'link' }
    if (Test-Entry $Link) { (Get-Item -LiteralPath $Link -Force).Delete() }
    Copy-Item -LiteralPath $Target -Destination $Link -Recurse -Force
    'copia'
}

function Copy-IfMissing([string]$From, [string]$To) {
    $dest = Join-Path $root $To
    if (Test-Entry $dest) {
        '  mantido {0}' -f $To
    } else {
        Copy-Item -LiteralPath (Join-Path $root $From) -Destination $dest
        '  criado  {0}' -f $To
    }
}

# bash do Git for Windows. O bash.exe do System32 é o do WSL e roda em outro sistema.
function Find-GitBash {
    foreach ($c in @(Get-Command bash -CommandType Application -All -ErrorAction SilentlyContinue)) {
        if ($env:SystemRoot -and $c.Path -like "$env:SystemRoot\*") { continue }
        return $c.Path
    }
    $bases = @($env:ProgramFiles, ${env:ProgramFiles(x86)})
    if ($env:LOCALAPPDATA) { $bases += Join-Path $env:LOCALAPPDATA 'Programs' }
    foreach ($base in $bases) {
        if (-not $base) { continue }
        $p = Join-Path $base 'Git\bin\bash.exe'
        if (Test-Path -LiteralPath $p) { return $p }
    }
    $null
}

# Política de execução que um Windows PowerShell novo vai usar (é nele que vários agentes rodam
# comandos). -ExecutionPolicy Bypass vale só para este processo e passa para os filhos por
# variável de ambiente, então ela sai antes da consulta.
function Get-WindowsPowerShellPolicy {
    $ErrorActionPreference = 'Continue'
    $saved = $env:PSExecutionPolicyPreference
    try {
        $env:PSExecutionPolicyPreference = $null
        "$(& powershell.exe -NoProfile -NonInteractive -Command 'Get-ExecutionPolicy' 2>$null | Select-Object -First 1)".Trim()
    } catch {
        ''
    } finally {
        $env:PSExecutionPolicyPreference = $saved
    }
}

if ($onWindows) {
    $hint = @{
        node = 'Node 22+: winget install OpenJS.NodeJS.LTS'
        ffmpeg = 'winget install Gyan.FFmpeg'
        uv = 'winget install astral-sh.uv'
    }
} else {
    $hint = @{
        node = 'Node 22+: https://nodejs.org'
        ffmpeg = 'https://ffmpeg.org/download.html'
        uv = 'https://docs.astral.sh/uv/'
    }
}

'Dependências:'
Write-Check node $hint.node
Write-Check npx 'vem com o Node'
Write-Check ffmpeg $hint.ffmpeg
Write-Check ffprobe 'vem com o FFmpeg'
Write-Check uv $hint.uv
if (Test-Tool node) {
    $major = Get-NodeMajor
    if ($null -eq $major -or $major -lt 22) {
        "  Node $major encontrado; precisa de 22+"
        $ok = $false
    }
}

''
'Agente de código (basta um):'
$found = $false
foreach ($a in 'claude', 'codex', 'agy', 'gemini', 'cursor-agent', 'opencode', 'copilot') {
    if (Test-Tool $a) {
        '  ok      {0}' -f $a
        $found = $true
    }
}
if (-not $found) {
    '  nenhum encontrado no PATH (Cursor, Windsurf e Copilot no editor também servem: abra a pasta)'
}

''
'Pastas locais:'
foreach ($d in 'projects', 'creatives/reels', 'creatives/carrossel', 'creatives/post', 'training/voz', 'training/referencias') {
    New-Item -ItemType Directory -Force -Path (Join-Path $root $d) | Out-Null
}
'  projects/  creatives/{reels,carrossel,post}/  training/{voz,referencias}/'

''
# Só as skills da lista viram skill nativa do Claude Code: cada uma manda a descrição em toda
# chamada. As outras ficam em .agents/skills/ e são lidas como documento quando o motion-cena pede.
'Skills para o Claude Code (.claude/skills/ -> .agents/skills/, lista em .agents/skills/claude-links.txt):'
$skillsDir = Join-Path $root '.claude/skills'
$agentsDir = [System.IO.Path]::GetFullPath((Join-Path $root '.agents/skills'))
$listFile = Join-Path $agentsDir 'claude-links.txt'
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
$wanted = @()
$hasList = Test-Path -LiteralPath $listFile -PathType Leaf
if ($hasList) {
    $wanted = @(Get-Content -LiteralPath $listFile -Encoding UTF8 | ForEach-Object { ($_ -replace '#.*$', '').Trim() } | Where-Object { $_ })
} else {
    '  FALTA   .agents/skills/claude-links.txt: nenhum link criado'
    $ok = $false
}
# Tira só o que este script criaria: link para .agents/skills/ que sumiu ou saiu da lista. Skill
# sua, pasta de verdade e link para outro lugar ficam como estão. Delete() sem recursão apaga só o
# link; Remove-Item -Recurse numa junction, no Windows PowerShell 5.1, pode apagar a skill de verdade.
$prefix = $agentsDir.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
$removed = 0
foreach ($l in @(Get-ChildItem -LiteralPath $skillsDir -Force)) {
    $target = Get-LinkTarget $l
    if (-not $target -or -not $target.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) { continue }
    if ((Test-DanglingLink $l) -or ($hasList -and $wanted -notcontains $l.Name)) {
        $l.Delete()
        $removed++
    }
}
$n = 0
$copies = 0
foreach ($name in $wanted) {
    $d = Join-Path $agentsDir $name
    if (-not (Test-Path -LiteralPath $d -PathType Container)) {
        '  aviso   {0} está na lista, mas .agents/skills/{0} não existe' -f $name
        continue
    }
    $link = Join-Path $skillsDir $name
    if (Test-Entry $link) { continue }
    if ((Add-SkillLink -Link $link -Target $d -Relative "../../.agents/skills/$name") -eq 'copia') { $copies++ }
    $n++
}
"  $n criado(s). Outros agentes leem .agents/skills/ direto."
if ($removed -gt 0) {
    "  $removed removido(s): link para skill fora da lista ou que não existe mais."
}
if ($copies -gt 0) {
    "  $copies como cópia: depois de atualizar o repositório, apague essas cópias em .claude/skills/ e rode de novo."
}
foreach ($c in @(Get-ChildItem -LiteralPath $skillsDir -Directory -Force)) {
    # cópia (feita quando o link falhou) de skill que saiu da lista: avisa, não apaga
    if ($c.LinkType -or ($wanted -contains $c.Name)) { continue }
    if (Test-Path -LiteralPath (Join-Path $agentsDir $c.Name) -PathType Container) {
        '  aviso   .claude/skills/{0} é uma cópia de skill fora da lista; apague à mão se não quiser carregá-la' -f $c.Name
    }
}

''
'Arquivos locais:'
Copy-IfMissing '.env.example' '.env.local'
if (-not $onWindows) {
    try { & chmod 600 (Join-Path $root '.env.local') } catch { Write-Debug "$_" }
}
Copy-IfMissing '.agents/skills/motion-cena/assets/registro.template.md' 'creatives/registro.md'

if ($onWindows) {
    ''
    'Windows:'
    $bash = Find-GitBash
    if ($bash) {
        '  ok      Git Bash  ({0})' -f $bash
    } else {
        '  aviso   Git Bash não encontrado: qa_video.sh e analyze_reference.sh precisam de bash (winget install Git.Git)'
    }
    $policy = Get-WindowsPowerShellPolicy
    if ($policy -in 'Restricted', 'AllSigned') {
        "  aviso   o Windows PowerShell bloqueia scripts ($policy) e o npx.ps1 do Node não roda nele."
        '          Libere só para o seu usuário: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned'
    }
    $utf8 = if ($env:PYTHONUTF8) { $env:PYTHONUTF8 } else { [Environment]::GetEnvironmentVariable('PYTHONUTF8', 'User') }
    if ($utf8 -ne '1') {
        '  aviso   sem PYTHONUTF8=1, o Python imprime em cp1252 e o lint_copy.py quebra quando o agente lê a saída.'
        '          Ligue para o seu usuário com: setx PYTHONUTF8 1   (vale a partir do próximo terminal)'
    }
    '  O pipeline completo, com a interface tools/studio, roda no WSL 2: veja a seção Windows do README.'
}

''
$self = if ($onWindows) { '.\setup.ps1' } else { 'pwsh setup.ps1' }
if ($ok) {
    'Pronto. Próximos passos:'
} else {
    "Instale o que falta, abra um terminal novo e rode $self de novo. Depois:"
}
'  1. (opcional) Coloque a chave da ElevenLabs em .env.local. Sem ela, a voz sai grátis pelo edge-tts.'
'  2. Abra seu agente na raiz (claude, codex, agy, Cursor...) e peça, por exemplo: "faz um reels de 30 s explicando juros compostos".'
'     Marca, voz e tom vão no próprio pedido (site, cores, código do produto ou a gravação de quem fala).'
if ($onWindows) {
    '  3. Para ver o vídeo sendo editado ao vivo, com chat e preview lado a lado: node tools/studio/server.mjs (pelo WSL 2)'
} else {
    '  3. Para ver o vídeo sendo editado ao vivo, com chat e preview lado a lado: node tools/studio/server.mjs'
}
