# Start - Single daily command
# Usage: .\start.ps1
# Auto-setup, combo config, start 9Router, buka opencode

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$ECC_DIR = "$ROOT_DIR\ecc"
$ROUTER_DIR = "$ROOT_DIR\9router"
$OPENCODE_DIR = "$env:USERPROFILE\.config\opencode"
$OPENCODE_CONFIG = "$OPENCODE_DIR\opencode.jsonc"
$API_KEY_FILE = "$ROOT_DIR\api-key.txt"
$API_URL = "http://localhost:20128"
$COMBO_FILE = "$ROOT_DIR\.opencode\combo.json"
$PROFILE_SRC = "$ROOT_DIR\profiles\combo\opencode.jsonc"
$stateDir = "$ROOT_DIR\.opencode"

# ── Helpers ──

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

# ── Load API keys ──

if (Test-Path $API_KEY_FILE) {
    Get-Content $API_KEY_FILE | ForEach-Object {
        $line = $_.Trim()
        if ($line -match '^([A-Z_]+)=(.*)') {
            Set-Item -Path "env:$($matches[1])" -Value $matches[2]
        }
    }
    if ($env:NINEROUTER_API_KEY) {
        try { setx NINEROUTER_API_KEY $env:NINEROUTER_API_KEY 2>&1 | Out-Null } catch {}
    }
}

# ── Banner ──

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host "  farewell-assistant - Daily Startup" -ForegroundColor Cyan
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host ""

# ── Step 0: Auto-Setup ──

Write-Step "0/8" "Auto-Setup"

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

# ── Step 1: 9Router Health ──

Write-Step "1/8" "9Router Health"

$routerRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$API_URL/api/health" -TimeoutSec 3 -ErrorAction Stop
    $routerRunning = $true
    Write-OK "9Router is running"
} catch {}

if (-not $routerRunning) {
    Write-Host "  Starting 9Router..." -ForegroundColor Gray
    if (-not (Test-Path "$ROUTER_DIR\.next\standalone\server.js")) {
        Write-Host "  Building 9Router (first time)..." -ForegroundColor Gray
        Push-Location $ROUTER_DIR
        npm run build 2>&1 | Out-Null
        Pop-Location
        Write-OK "9Router built"
    }
    $env:PORT = "20128"
    $env:DATA_DIR = "$env:USERPROFILE\AppData\Roaming\9router"
    Start-Process -FilePath "node" -ArgumentList ".next/standalone/server.js" -WindowStyle Hidden -WorkingDirectory $ROUTER_DIR -Environment @{ PORT = "20128"; NODE_ENV = "production"; DATA_DIR = "$env:USERPROFILE\AppData\Roaming\9router" }
    Start-Sleep -Seconds 8
    try {
        $null = Invoke-RestMethod -Uri "$API_URL/api/health" -TimeoutSec 10 -ErrorAction Stop
        Write-OK "9Router started successfully"
    } catch {
        Write-Fail "9Router started but not reachable yet"
    }
}

# ── Step 2: Combo Setup ──

Write-Step "2/8" "Combo Setup"

# Fetch combos from 9Router API
$remoteCombos = @()
try {
    $models = Invoke-RestMethod -Uri "$API_URL/api/v1/models" -TimeoutSec 5 -ErrorAction Stop
    $remoteCombos = $models.data | Where-Object { $_.owned_by -eq "combo" } | Select-Object -ExpandProperty id
} catch {}

if ($remoteCombos.Count -gt 0) {
    Write-Host "  Combo tersedia: $($remoteCombos -join ', ')" -ForegroundColor Gray
} else {
    Write-Host "  (Tidak ada combo terdeteksi - buat dulu di dashboard)" -ForegroundColor Gray
}

# Read saved combos
$savedCombos = @()
if (Test-Path $COMBO_FILE) {
    try {
        $savedCombos = Get-Content $COMBO_FILE -Raw | ConvertFrom-Json
    } catch {}
}

$needsSetup = $savedCombos.Count -eq 0

if (-not $needsSetup) {
    Write-Host "  Combo saat ini: $($savedCombos -join ', ')" -ForegroundColor White
    $ans = Read-Host "  Ada revisi? (y/N)"
    if ($ans -eq "y" -or $ans -eq "Y") { $needsSetup = $true }
}

if ($needsSetup) {
    $combos = @()
    do {
        $c = Read-Host "  Input nama combo (enter 0 jika tidak ada)"
        if ($c -and $c -ne "0") {
            $combos += $c
            $ans = Read-Host "  Ada lagi? (y/tidak)"
        } else {
            $ans = "tidak"
        }
    } while ($ans -eq "y" -or $ans -eq "Y")

    if ($combos.Count -gt 0) {
        New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
        $combos | ConvertTo-Json | Set-Content -Path $COMBO_FILE -Encoding UTF8
        $savedCombos = $combos
        Write-OK "Combo tersimpan: $($combos -join ', ')"
    }
}

Write-Host "  >> 0: $($savedCombos[0] -replace '^.*','(model utama)')" -ForegroundColor Gray
if ($savedCombos.Count -gt 1) {
    Write-Host "  >> 1: $($savedCombos[1]) (small_model)" -ForegroundColor Gray
}

# ── Step 3: Apply Profile ──

Write-Step "3/8" "Apply Profile"

# Generate models section
$modelEntries = ""
for ($i = 0; $i -lt $savedCombos.Count; $i++) {
    $name = $savedCombos[$i]
    if ($i -gt 0) { $modelEntries += "," }
    $modelEntries += "`n      `"$name`": { `"name`": `"$name combo`" }"
}
$comboModels = "{$modelEntries`n    }"

$config = Get-Content $PROFILE_SRC -Raw
$config = $config -replace '\{project\}', ($ROOT_DIR -replace '\\', '/')
$config = $config -replace '\$\{COMBO_0\}', $savedCombos[0]
$combo1 = if ($savedCombos.Count -gt 1) { $savedCombos[1] } else { $savedCombos[0] }
$config = $config -replace '\$\{COMBO_1\}', $combo1
$config = $config -replace '\$\{COMBO_MODELS\}', $comboModels

New-Item -ItemType Directory -Path $OPENCODE_DIR -Force | Out-Null
$config | Set-Content -Path $OPENCODE_CONFIG -Encoding UTF8
Write-OK "Profile applied"

# ── Step 4: LLM Mode Check ──

Write-Step "4/8" "LLM Mode"

$modeFile = "$stateDir\llm-mode.json"
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
    Write-Skip "ECO mode - Ollama not needed"
}

# ── Step 5: Update Check ──

Write-Step "5/8" "Update Check"

$hasUpdates = $false
if (Write-UpdateCheck "ECC" $ECC_DIR "origin" "main") { $hasUpdates = $true }
if (Write-UpdateCheck "9Router" $ROUTER_DIR "origin" "master") { $hasUpdates = $true }

if ($hasUpdates) {
    Write-Host ""
    Write-Host "  ! Update tersedia! Jalankan: .\scripts\admin.ps1" -ForegroundColor Cyan
    Write-Host "  Lihat changelog: CHANGELOG_ECC.md atau CHANGELOG_9ROUTER.md" -ForegroundColor Gray
}

# ── Step 6: Changelog Sync ──

Write-Step "6/8" "Changelog Sync"

Push-Location $ECC_DIR
$eccNew = git rev-list --count "HEAD..origin/main" 2>$null
Pop-Location

Push-Location $ROUTER_DIR
$routerNew = git rev-list --count "HEAD..origin/master" 2>$null
Pop-Location

if ($eccNew -and $eccNew -gt 0) {
    Push-Location $ECC_DIR
    git show origin/main:CHANGELOG.md 2>$null | Out-File -FilePath "$ROOT_DIR\CHANGELOG_ECC.md" -Encoding UTF8
    Pop-Location
    Write-OK "CHANGELOG_ECC.md updated"
} else {
    Write-Skip "ECC changelog already current"
}

if ($routerNew -and $routerNew -gt 0) {
    Push-Location $ROUTER_DIR
    git show origin/master:CHANGELOG.md 2>$null | Out-File -FilePath "$ROOT_DIR\CHANGELOG_9ROUTER.md" -Encoding UTF8
    Pop-Location
    Write-OK "CHANGELOG_9ROUTER.md updated"
} else {
    Write-Skip "9Router changelog already current"
}

# ── Step 7: Summary ──

Write-Step "7/8" "Summary"

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Green
Write-Host "  Ready!" -ForegroundColor Green
Write-Host "  =================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  9Router:     $(if ($routerRunning) { 'Running' } else { 'Check manually' })" -ForegroundColor $(if ($routerRunning) { "Green" } else { "Yellow" })
Write-Host "  ECC:         Available" -ForegroundColor Green
Write-Host "  Combo:       $($savedCombos -join ', ')" -ForegroundColor White
Write-Host "  LLM Mode:    $mode" -ForegroundColor $(if ($mode -eq "eco") { "Green" } else { "Cyan" })
Write-Host ""
Write-Host "  >> Membuka opencode..." -ForegroundColor Cyan
opencode

