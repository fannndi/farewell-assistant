# Admin - Maintenance
# Usage: .\admin.ps1 [--doctor]

param(
    [switch]$Doctor
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$ECC_DIR = "$ROOT_DIR\ecc"
$ROUTER_DIR = "$ROOT_DIR\9router"

# ============================================================
# Helpers
# ============================================================

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host ""
    Write-Host "[$Step] $Message" -ForegroundColor Cyan
}

function Write-OK {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Skip {
    param([string]$Message)
    Write-Host "  [SKIP] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "  [FAIL] $Message" -ForegroundColor Red
}

# ============================================================
# Banner
# ============================================================

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host "  farewell-assistant — Maintenance" -ForegroundColor Magenta
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: Pull Repos
# ============================================================

Write-Step "1/4" "Pull Latest Changes"

if (Test-Path "$ECC_DIR\.git") {
    Push-Location $ECC_DIR
    $before = git log --oneline -1 2>$null
    git pull 2>&1 | Out-Null
    $after = git log --oneline -1 2>$null
    Pop-Location
    if ($before -ne $after) {
        Write-Host "  ECC updated: $before → $after" -ForegroundColor Green
    } else {
        Write-Skip "ECC: already up to date"
    }
} else {
    Write-Skip "ECC not cloned"
}

if (Test-Path "$ROUTER_DIR\.git") {
    Push-Location $ROUTER_DIR
    $before = git log --oneline -1 2>$null
    git pull 2>&1 | Out-Null
    $after = git log --oneline -1 2>$null
    Pop-Location
    if ($before -ne $after) {
        Write-Host "  9Router updated: $before → $after" -ForegroundColor Green
    } else {
        Write-Skip "9Router: already up to date"
    }
} else {
    Write-Skip "9Router not cloned"
}

# ============================================================
# Step 2: Doctor Check
# ============================================================

Write-Step "2/4" "Doctor Check"

$issues = @()

# Check ECC
if (-not (Test-Path "$ECC_DIR\AGENTS.md")) {
    $issues += "ECC not found — run: .\scripts\setup.ps1"
}

# Check 9Router
if (-not (Test-Path "$ROUTER_DIR\package.json")) {
    $issues += "9Router not found — run: .\scripts\setup.ps1"
}

# Check OpenCode config
$openCodeConfig = "$env:USERPROFILE\.config\opencode\opencode.jsonc"
if (-not (Test-Path $openCodeConfig)) {
    $issues += "OpenCode config not found — run: .\scripts\setup.ps1"
}

# Check 9Router running
try {
    $null = Invoke-RestMethod -Uri "http://localhost:20128/health" -TimeoutSec 3 -ErrorAction Stop
} catch {
    $issues += "9Router not running — start with: .\scripts\start.ps1"
}

# Check Ollama
$modeFile = "$ROOT_DIR\.opencode\llm-mode.json"
$mode = "eco"
if (Test-Path $modeFile) {
    try {
        $state = Get-Content $modeFile -Raw | ConvertFrom-Json
        $mode = $state.mode
    } catch {}
}
if ($mode -ne "eco") {
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop
    } catch {
        $issues += "Ollama not running (mode: $mode) — start with: .\scripts\llm-mode.ps1 on"
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

Write-Host "  farewell-assistant root: $ROOT_DIR" -ForegroundColor Gray
Write-Host "  ECC path:                $ECC_DIR" -ForegroundColor Gray
Write-Host "  9Router path:            $ROUTER_DIR" -ForegroundColor Gray
Write-Host "  OpenCode config:         $openCodeConfig" -ForegroundColor Gray
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
