# Start - Single daily command (cukup jalankan, auto semua)
# Usage: .\start.ps1 [[-Profile] gratis|go]

param(
    [ValidateSet("gratis", "go")]
    [string]$Profile = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$ECC_DIR = "$ROOT_DIR\ecc"
$ROUTER_DIR = "$ROOT_DIR\9router"
$OPENCODE_DIR = "$env:USERPROFILE\.config\opencode"
$OPENCODE_CONFIG = "$OPENCODE_DIR\opencode.jsonc"
$API_KEY_FILE = "$ROOT_DIR\api-key.txt"
$API_URL = "http://localhost:20128"
$PROFILE_FILE = "$ROOT_DIR\.opencode\profile"
$stateDir = "$ROOT_DIR\.opencode"

# Set API key env for OpenCode
if (Test-Path $API_KEY_FILE) {
    $key = Get-Content $API_KEY_FILE -Raw | ForEach-Object { $_.Trim() }
    if ($key) {
        $env:NINEROUTER_API_KEY = $key
    }
}

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
# First-run wizard (API key + profile)
# ============================================================

$firstRun = $false

$apiKey = ""
if (Test-Path $API_KEY_FILE) {
    $apiKey = Get-Content $API_KEY_FILE -Raw | ForEach-Object { $_.Trim() }
}
if (-not $apiKey) {
    $firstRun = $true
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║   Selamat datang di farewell-assistant!  ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  API key 9Router diperlukan." -ForegroundColor Yellow
    Write-Host "  Cek dashboard: http://localhost:20128/dashboard (setelah 9Router jalan)" -ForegroundColor Gray
    Write-Host ""
    $key = Read-Host "  Masukkan API key"
    if ($key) {
        New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
        $key | Set-Content -Path $API_KEY_FILE -Encoding UTF8 -NoNewline
        Write-OK "API key saved"
    }
}

if (-not $Profile) {
    if (Test-Path $PROFILE_FILE) {
        $Profile = Get-Content $PROFILE_FILE -Raw | ForEach-Object { $_.Trim() }
    }
}

if (-not $Profile -or ($Profile -ne "gratis" -and $Profile -ne "go")) {
    $firstRun = $true
    Write-Host ""
    Write-Host "  Pilih profile:" -ForegroundColor Cyan
    Write-Host "    [1] gratis  — Free models (default)" -ForegroundColor White
    Write-Host "    [2] go      — Paid models" -ForegroundColor White
    $choice = Read-Host "  Masukkan pilihan (1/2)"
    $Profile = if ($choice -eq "2") { "go" } else { "gratis" }
}

New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
$Profile | Set-Content -Path $PROFILE_FILE -Encoding UTF8 -NoNewline
$PROFILE_SRC = "$ROOT_DIR\profiles\$Profile\opencode.jsonc"

function Write-UpdateCheck {
    param([string]$Repo, [string]$Dir, [string]$Remote, [string]$Branch)
    if (Test-Path "$Dir\.git") {
        Push-Location $Dir
        git fetch $Remote 2>&1 | Out-Null
        $behind = git rev-list --count "HEAD..$Remote/$Branch" 2>&1
        Pop-Location
        if ($behind -and $behind -gt 0) {
            Write-Host "  ${Repo}: $behind commit(s) behind" -ForegroundColor Yellow
            return $true
        } else {
            Write-Skip "${Repo}: up to date"
        }
    } else {
        Write-Skip "${Repo}: not cloned"
    }
    return $false
}

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host "  farewell-assistant — Daily Startup" -ForegroundColor Cyan
Write-Host "  Profile: $Profile" -ForegroundColor Gray
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# Step 0: Auto-Setup (clone if missing)
# ============================================================

Write-Step "0/7" "Auto-Setup"

if (-not (Test-Path "$ECC_DIR\AGENTS.md")) {
    Write-Host "  Cloning ECC..." -ForegroundColor Gray
    git clone https://github.com/affaan-m/ECC.git $ECC_DIR 2>&1 | Out-Null
    Write-OK "ECC cloned"
} else {
    Write-Skip "ECC already cloned"
}

if (-not (Test-Path "$ROUTER_DIR\package.json")) {
    Write-Host "  Cloning 9Router..." -ForegroundColor Gray
    git clone https://github.com/decolua/9router.git $ROUTER_DIR 2>&1 | Out-Null
    Write-OK "9Router cloned"
} else {
    Write-Skip "9Router already cloned"
}

if (-not (Test-Path "$ROUTER_DIR\node_modules")) {
    Write-Host "  Installing 9Router dependencies..." -ForegroundColor Gray
    Push-Location $ROUTER_DIR
    npm install 2>&1 | Out-Null
    Pop-Location
    Write-OK "Dependencies installed"
} else {
    Write-Skip "9Router dependencies already installed"
}

# ============================================================
# Step 1: 9Router Health
# ============================================================

Write-Step "1/7" "9Router Health"

$routerRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$API_URL/api/health" -TimeoutSec 3 -ErrorAction Stop
    $routerRunning = $true
    Write-OK "9Router is running"
} catch {}

if (-not $routerRunning) {
    Write-Host "  Starting 9Router..." -ForegroundColor Gray
    $env:PORT = "20128"
    $env:DATA_DIR = "$env:USERPROFILE\AppData\Roaming\9router"
    Start-Process -FilePath "node" -ArgumentList ".next/standalone/server.js" -WindowStyle Hidden -WorkingDirectory $ROUTER_DIR -Environment @{ PORT = "20128"; NODE_ENV = "production"; DATA_DIR = "$env:USERPROFILE\AppData\Roaming\9router" }
    Start-Sleep -Seconds 8
    try {
        $null = Invoke-RestMethod -Uri "$API_URL/api/health" -TimeoutSec 10 -ErrorAction Stop
        Write-OK "9Router started successfully (v0.5.2)"
    } catch {
        Write-Fail "9Router started but not reachable yet"
    }
}

# ============================================================
# Step 2: Apply Profile
# ============================================================

Write-Step "2/7" "Apply Profile: $Profile"

New-Item -ItemType Directory -Path $OPENCODE_DIR -Force | Out-Null
$config = Get-Content $PROFILE_SRC -Raw
$config = $config -replace '\{project\}', ($ROOT_DIR -replace '\\', '/')
$config | Set-Content -Path $OPENCODE_CONFIG -Encoding UTF8
Write-OK "Profile applied"

# ============================================================
# Step 3: LLM Mode Check
# ============================================================

Write-Step "3/7" "LLM Mode"

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
    $ollamaRunning = $false
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop
        $ollamaRunning = $true
    } catch {}
    if (-not $ollamaRunning) {
        Write-Host "  Starting Ollama..." -ForegroundColor Gray
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        Write-OK "Ollama started"
    } else {
        Write-OK "Ollama running"
    }
} else {
    Write-Skip "ECO mode — Ollama not needed"
}

# ============================================================
# Step 4: Update Check
# ============================================================

Write-Step "4/7" "Update Check"

$hasUpdates = $false
if (Write-UpdateCheck "ECC" $ECC_DIR "origin" "main") { $hasUpdates = $true }
if (Write-UpdateCheck "9Router" $ROUTER_DIR "origin" "master") { $hasUpdates = $true }

if ($hasUpdates) {
    Write-Host ""
    Write-Host "  ⚡ Update tersedia! Jalankan: .\scripts\admin.ps1" -ForegroundColor Cyan
    Write-Host "  Lihat changelog: CHANGELOG_ECC.md atau CHANGELOG_9ROUTER.md" -ForegroundColor Gray
}

# ============================================================
# Step 5: Changelog Check (new in upstream)
# ============================================================

Write-Step "5/7" "Changelog Sync"

# Check if ECC or 9Router changelogs need updating
$eccChanged = $false
$routerChanged = $false

Push-Location $ECC_DIR
$eccLocal = git log --oneline -1 2>$null
$eccNew = git rev-list --count "HEAD..origin/main" 2>$null
Pop-Location

Push-Location $ROUTER_DIR
$routerLocal = git log --oneline -1 2>$null
$routerNew = git rev-list --count "HEAD..origin/master" 2>$null
Pop-Location

if ($eccNew -and $eccNew -gt 0) {
    Push-Location $ECC_DIR
    git show origin/main:CHANGELOG.md 2>$null | Out-File -FilePath "$ROOT_DIR\CHANGELOG_ECC.md" -Encoding UTF8
    Pop-Location
    Write-OK "CHANGELOG_ECC.md updated"
    $eccChanged = $true
} else {
    Write-Skip "ECC changelog already current"
}

if ($routerNew -and $routerNew -gt 0) {
    Push-Location $ROUTER_DIR
    git show origin/master:CHANGELOG.md 2>$null | Out-File -FilePath "$ROOT_DIR\CHANGELOG_9ROUTER.md" -Encoding UTF8
    Pop-Location
    Write-OK "CHANGELOG_9ROUTER.md updated"
    $routerChanged = $true
} else {
    Write-Skip "9Router changelog already current"
}

# ============================================================
# Step 6: Summary
# ============================================================

Write-Step "6/7" "Summary"

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Green
Write-Host "  Ready!" -ForegroundColor Green
Write-Host "  =================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Profile:     $Profile" -ForegroundColor White
Write-Host "  9Router:     $(if ($routerRunning) { 'Running' } else { 'Check manually' })" -ForegroundColor $(if ($routerRunning) { "Green" } else { "Yellow" })
Write-Host "  ECC:         Available" -ForegroundColor Green
Write-Host "  LLM Mode:    $mode" -ForegroundColor $(if ($mode -eq "eco") { "Green" } else { "Cyan" })
Write-Host ""
Write-Host "  Start coding: opencode" -ForegroundColor Cyan
Write-Host ""
