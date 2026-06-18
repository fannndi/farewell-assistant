# Admin - Maintenance
# Usage: .\admin.ps1 [--doctor]

param([switch]$Doctor)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"

# ============================================================
# Banner
# ============================================================

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host "  farewell-assistant - Maintenance" -ForegroundColor Magenta
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: Pull Repos
# ============================================================

Write-Step "1/4" "Pull Latest Changes"

function Write-ChangelogDiff {
    param([string]$Repo, [string]$Dir, [string]$Branch, [string]$Before)
    if (-not (Test-Path "$Dir\.git")) { return }
    Push-Location $Dir
    try {
        $behind = git rev-list --count "$Before..origin/$Branch" 2>&1
        if ($behind -and $behind -gt 0) {
            Write-Host "  ── $Repo ($behind new commit(s)) ──" -ForegroundColor Cyan
            git log "$Before..origin/$Branch" --oneline --no-decorate 2>$null | Select-Object -First 10 | ForEach-Object {
                Write-Host "    $_" -ForegroundColor Gray
            }
            if ($behind -gt 10) {
                Write-Host "    ... and $($behind - 10) more" -ForegroundColor Gray
            }
        }
    } finally { Pop-Location }
}

function Write-PullECC {
    if (-not (Test-Path "$($script:ECC_DIR)\.git")) { Write-Skip "ECC not cloned"; return }
    Push-Location $script:ECC_DIR
    try {
        git fetch origin 2>&1 | Out-Null
        $before = git rev-parse HEAD 2>$null
        $behind = git rev-list --count "HEAD..origin/main" 2>&1
        if ($behind -and $behind -gt 0) {
            Write-Host "  ECC: $behind commit(s) behind" -ForegroundColor Yellow
            Write-ChangelogDiff "ECC" $script:ECC_DIR "main" $before
            git reset --hard origin/main 2>&1 | Out-Null
            $afterShort = git log --oneline -1 2>$null
            Write-Host "  ECC updated >> $afterShort" -ForegroundColor Green
            git show origin/main:CHANGELOG.md 2>$null | Out-File -FilePath "$($script:ROOT_DIR)\CHANGELOG_ECC.md" -Encoding UTF8
            Write-OK "CHANGELOG_ECC.md synced"
        } else {
            Write-Skip "ECC: already up to date"
        }
    } finally { Pop-Location }
}

function Write-Pull9Router {
    if (-not (Test-Path "$($script:ROUTER_DIR)\.git")) { Write-Skip "9Router not cloned"; return }
    Push-Location $script:ROUTER_DIR
    try {
        git fetch origin 2>&1 | Out-Null
        $before = git rev-parse HEAD 2>$null
        $beforePkg = Get-FileHash "package.json" 2>$null
        $behind = git rev-list --count "HEAD..origin/master" 2>&1
        if ($behind -and $behind -gt 0) {
            Write-Host "  9Router: $behind commit(s) behind" -ForegroundColor Yellow
            Write-ChangelogDiff "9Router" $script:ROUTER_DIR "master" $before
            git pull --ff-only 2>&1 | Out-Null
            $afterShort = git log --oneline -1 2>$null
            Write-Host "  9Router updated >> $afterShort" -ForegroundColor Green
            git show origin/master:CHANGELOG.md 2>$null | Out-File -FilePath "$($script:ROOT_DIR)\CHANGELOG_9ROUTER.md" -Encoding UTF8
            Write-OK "CHANGELOG_9ROUTER.md synced"
            $afterPkg = Get-FileHash "package.json" 2>$null
            if ($beforePkg.Hash -ne $afterPkg.Hash) {
                Write-Host "  package.json changed, updating npm..." -ForegroundColor Gray
                npm install 2>&1 | Out-Null
                Write-OK "npm dependencies updated"
            } else {
                Write-Skip "package.json unchanged, npm skipped"
            }
            Write-Host "  Restarting 9Router..." -ForegroundColor Gray
            $nodePids = Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -match [regex]::Escape($script:ROUTER_DIR) } | Select-Object -ExpandProperty ProcessId
            if ($nodePids) {
                $nodePids | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
                Start-Sleep -Seconds 2
            }
            if (-not (Test-Path "$($script:ROUTER_DIR)\.next\standalone\.next\static")) {
                Copy-Item -Path "$($script:ROUTER_DIR)\.next\static" -Destination "$($script:ROUTER_DIR)\.next\standalone\.next\static" -Recurse -Force
            }
            $pw = if ($env:9ROUTER_PASSWORD) { $env:9ROUTER_PASSWORD } else { "" }
            Start-Process -FilePath "node" -ArgumentList ".next/standalone/server.js" -WindowStyle Hidden -WorkingDirectory $script:ROUTER_DIR -Environment @{ PORT = "20128"; NODE_ENV = "production"; DATA_DIR = "$env:USERPROFILE\AppData\Roaming\9router"; INITIAL_PASSWORD = "$pw" }
            Write-OK "9Router restarted with new version"
        } else {
            Write-Skip "9Router: already up to date"
        }
    } finally { Pop-Location }
}

Write-PullECC
Write-Pull9Router

# ============================================================
# Step 2: Doctor Check
# ============================================================

Write-Step "2/4" "Doctor Check"

$issues = @()

if (-not (Test-Path "$($script:ECC_DIR)\AGENTS.md")) {
    $issues += "ECC not found - run: .\scripts\setup.ps1"
}

if (-not (Test-Path "$($script:ROUTER_DIR)\package.json")) {
    $issues += "9Router not found - run: .\scripts\setup.ps1"
}

if (-not (Test-Path $script:OPENCODE_CFG)) {
    $issues += "OpenCode config not found - run: .\scripts\setup.ps1"
}

try {
    $null = Invoke-RestMethod -Uri "$($script:API_URL)/api/health" -TimeoutSec 3 -ErrorAction Stop
} catch {
    $issues += "9Router not running - start with: .\scripts\start.ps1"
}

$mode = Get-LLMMode
if ($mode -ne "eco") {
    try {
        $null = Invoke-RestMethod -Uri "$($script:OLLAMA_URL)/api/tags" -TimeoutSec 3 -ErrorAction Stop
    } catch {
        $issues += "Ollama not running (mode: $mode) - start with: .\scripts\llm-mode.ps1 on"
    }
}

if ($issues.Count -eq 0) {
    Write-OK "All checks passed"
} else {
    foreach ($issue in $issues) {
        Write-Fail $issue
    }
}

# ============================================================
# Step 3: System Info
# ============================================================

Write-Step "3/4" "System Info"

Write-Host "  farewell-assistant root: $($script:ROOT_DIR)" -ForegroundColor Gray
Write-Host "  ECC path:                $($script:ECC_DIR)" -ForegroundColor Gray
Write-Host "  9Router path:            $($script:ROUTER_DIR)" -ForegroundColor Gray
Write-Host "  OpenCode config:         $($script:OPENCODE_CFG)" -ForegroundColor Gray
Write-Host "  LLM mode:                $mode" -ForegroundColor Gray

# ============================================================
# Step 4: Summary
# ============================================================

Write-Step "4/4" "Summary"

Write-Host ""
if ($issues.Count -eq 0) {
    Write-Host "  All systems operational." -ForegroundColor Green
} else {
    Write-Host "  $($issues.Count) issue(s) found. Fix above." -ForegroundColor Yellow
}
Write-Host ""
