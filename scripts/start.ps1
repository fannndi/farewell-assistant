# Start - Daily Startup
# Usage: .\start.ps1 -Profile gratis|go

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("gratis", "go")]
    [string]$Profile
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$ECC_DIR = "$ROOT_DIR\ecc"
$ROUTER_DIR = "$ROOT_DIR\9router"
$OPENCODE_DIR = "$env:USERPROFILE\.config\opencode"
$OPENCODE_CONFIG = "$OPENCODE_DIR\opencode.jsonc"
$PROFILE_SRC = "$ROOT_DIR\profiles\$Profile\opencode.jsonc"
$API_URL = "http://localhost:20128"

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
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host "  farewell-assistant — Daily Startup" -ForegroundColor Cyan
Write-Host "  Profile: $Profile" -ForegroundColor Gray
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# Step 1: 9Router Health
# ============================================================

Write-Step "1/5" "9Router Health"

$routerRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$API_URL/health" -TimeoutSec 3 -ErrorAction Stop
    $routerRunning = $true
    Write-OK "9Router is running"
} catch {}

if (-not $routerRunning) {
    Write-Host "  Starting 9Router..." -ForegroundColor Gray
    if (Test-Path "$ROUTER_DIR\package.json") {
        try {
            Push-Location $ROUTER_DIR
            Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Minimized
            Pop-Location
            Start-Sleep -Seconds 5
            try {
                $null = Invoke-RestMethod -Uri "$API_URL/health" -TimeoutSec 10 -ErrorAction Stop
                Write-OK "9Router started successfully"
            } catch {
                Write-Fail "9Router started but not reachable yet. Wait a moment and retry."
            }
        } catch {
            Write-Fail "Failed to start 9Router"
        }
    } else {
        Write-Fail "9Router not found. Run: .\scripts\setup.ps1"
    }
}

# ============================================================
# Step 2: ECC Check
# ============================================================

Write-Step "2/5" "ECC (Skills)"

if (Test-Path "$ECC_DIR\AGENTS.md") {
    Write-OK "ECC available"
} else {
    Write-Fail "ECC not found at $ECC_DIR"
    Write-Host "  Run: .\scripts\setup.ps1" -ForegroundColor Yellow
}

# ============================================================
# Step 3: Apply Profile
# ============================================================

Write-Step "3/5" "Apply Profile: $Profile"

if (-not (Test-Path $PROFILE_SRC)) {
    Write-Fail "Profile not found: $PROFILE_SRC"
} else {
    New-Item -ItemType Directory -Path $OPENCODE_DIR -Force | Out-Null

    $config = Get-Content $PROFILE_SRC -Raw
    $config = $config -replace '\{project\}', ($ROOT_DIR -replace '\\', '/')
    $config | Set-Content -Path $OPENCODE_CONFIG -Encoding UTF8

    Write-OK "Profile applied"
}

# ============================================================
# Step 4: LLM Mode Check
# ============================================================

Write-Step "4/5" "LLM Mode"

$modeFile = "$ROOT_DIR\.opencode\llm-mode.json"
$mode = "eco"
if (Test-Path $modeFile) {
    try {
        $state = Get-Content $modeFile -Raw | ConvertFrom-Json
        $mode = $state.mode
    } catch {}
}

Write-Host "  Mode: $mode" -ForegroundColor $(if ($mode -eq "eco") { "Green" } else { "Cyan" })

if ($mode -ne "eco") {
    # Check Ollama
    $ollamaRunning = $false
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop
        $ollamaRunning = $true
    } catch {}

    if (-not $ollamaRunning) {
        Write-Host "  Starting Ollama..." -ForegroundColor Gray
        try {
            Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
            Start-Sleep -Seconds 3
            Write-OK "Ollama started"
        } catch {
            Write-Fail "Failed to start Ollama"
        }
    } else {
        Write-OK "Ollama running"
    }
} else {
    Write-Skip "ECO mode — Ollama not needed"
}

# ============================================================
# Step 5: Summary
# ============================================================

Write-Step "5/5" "Summary"

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Green
Write-Host "  Ready!" -ForegroundColor Green
Write-Host "  =================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Profile:     $Profile" -ForegroundColor White
Write-Host "  9Router:     $(if ($routerRunning) { 'Running' } else { 'Check manually' })" -ForegroundColor $(if ($routerRunning) { "Green" } else { "Yellow" })
Write-Host "  ECC:         $(if (Test-Path $ECC_DIR) { 'Available' } else { 'Missing' })" -ForegroundColor $(if (Test-Path $ECC_DIR) { "Green" } else { "Red" })
Write-Host "  LLM Mode:   $mode" -ForegroundColor $(if ($mode -eq "eco") { "Green" } else { "Cyan" })
Write-Host ""
Write-Host "  Start coding: opencode" -ForegroundColor Cyan
Write-Host ""
