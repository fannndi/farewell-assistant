# Setup - First Install
# Usage: .\setup.ps1 [-Profile gratis|go]

param(
    [ValidateSet("gratis", "go")]
    [string]$Profile = "gratis"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$ECC_DIR = "$ROOT_DIR\ecc"
$ROUTER_DIR = "$ROOT_DIR\9router"
$PROFILE_SRC = "$ROOT_DIR\profiles\$Profile\opencode.jsonc"
$OPENCODE_DIR = "$env:USERPROFILE\.config\opencode"
$OPENCODE_CONFIG = "$OPENCODE_DIR\opencode.jsonc"

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
Write-Host "  farewell-assistant — First Install" -ForegroundColor Magenta
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: Clone ECC
# ============================================================

Write-Step "1/5" "ECC (Expert Knowledge Base)"

if (Test-Path "$ECC_DIR\AGENTS.md") {
    Write-Skip "ECC already cloned at $ECC_DIR"
} else {
    Write-Host "  Cloning ECC..." -ForegroundColor Gray
    try {
        git clone https://github.com/affaan-m/ECC.git $ECC_DIR 2>&1 | Out-Null
        Write-OK "ECC cloned"
    } catch {
        Write-Fail "Failed to clone ECC. Check your internet connection."
        Write-Host "  Error: $_" -ForegroundColor Red
    }
}

# ============================================================
# Step 2: Clone 9Router
# ============================================================

Write-Step "2/5" "9Router (AI Gateway)"

if (Test-Path "$ROUTER_DIR\package.json") {
    Write-Skip "9Router already cloned at $ROUTER_DIR"
} else {
    Write-Host "  Cloning 9Router..." -ForegroundColor Gray
    try {
        git clone https://github.com/decolua/9router.git $ROUTER_DIR 2>&1 | Out-Null
        Write-OK "9Router cloned"
    } catch {
        Write-Fail "Failed to clone 9Router. Check your internet connection."
        Write-Host "  Error: $_" -ForegroundColor Red
    }
}

# ============================================================
# Step 3: Install 9Router Dependencies
# ============================================================

Write-Step "3/5" "9Router Dependencies"

if (Test-Path "$ROUTER_DIR\node_modules") {
    Write-Skip "node_modules already installed"
} else {
    Write-Host "  Installing npm dependencies..." -ForegroundColor Gray
    try {
        Push-Location $ROUTER_DIR
        npm install 2>&1 | Out-Null
        Pop-Location
        Write-OK "Dependencies installed"
    } catch {
        Write-Fail "Failed to install dependencies"
        Write-Host "  Error: $_" -ForegroundColor Red
    }
}

# ============================================================
# Step 4: Apply Profile
# ============================================================

Write-Step "4/5" "Apply Profile: $Profile"

if (-not (Test-Path $PROFILE_SRC)) {
    Write-Fail "Profile not found: $PROFILE_SRC"
} else {
    New-Item -ItemType Directory -Path $OPENCODE_DIR -Force | Out-Null

    if (Test-Path $OPENCODE_CONFIG) {
        $backup = "$OPENCODE_CONFIG.bak.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $OPENCODE_CONFIG $backup
        Write-Host "  Backed up existing config" -ForegroundColor Gray
    }

    # Replace {project} placeholder with actual path
    $config = Get-Content $PROFILE_SRC -Raw
    $config = $config -replace '\{project\}', ($ROOT_DIR -replace '\\', '/')
    $config | Set-Content -Path $OPENCODE_CONFIG -Encoding UTF8

    Write-OK "Profile '$Profile' applied to $OPENCODE_CONFIG"
}

# ============================================================
# Step 5: Initialize State
# ============================================================

Write-Step "5/5" "Initialize State"

$stateDir = "$ROOT_DIR\.opencode"
New-Item -ItemType Directory -Path $stateDir -Force | Out-Null

$llmMode = @{ mode = "eco"; model = ""; updated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz") }
$llmMode | ConvertTo-Json | Set-Content -Path "$stateDir\llm-mode.json" -Encoding UTF8

$llmStatus = @{ mode = "ECO"; model = ""; last_updated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss") }
$llmStatus | ConvertTo-Json | Set-Content -Path "$stateDir\llm-status.json" -Encoding UTF8

Write-OK "State initialized (ECO mode)"

# ============================================================
# Done
# ============================================================

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "  =================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "    1. Edit api-key.txt — isi dengan key dari 9Router" -ForegroundColor White
Write-Host "       Dashboard: http://localhost:20128/dashboard" -ForegroundColor Gray
Write-Host "    2. Jalankan: .\scripts\start.ps1 -Profile $Profile" -ForegroundColor White
Write-Host "    3. Buka opencode: opencode" -ForegroundColor White
Write-Host ""
