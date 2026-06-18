# Setup - First Install
# Usage: .\setup.ps1

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"


Write-Host ""
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host "  farewell-assistant - First Install" -ForegroundColor Magenta
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host ""

# Step 1
Write-Step "1/4" "ECC (Expert Knowledge Base)"
if (Test-Path "$ECC_DIR\AGENTS.md") {
    Write-Skip "ECC already cloned"
} else {
    Write-Host "  Cloning ECC..." -ForegroundColor Gray
    git clone https://github.com/affaan-m/ECC.git $ECC_DIR 2>&1 | Out-Null
    Write-OK "ECC cloned"
}

# Step 2
Write-Step "2/4" "9Router (AI Gateway)"
if (Test-Path "$ROUTER_DIR\package.json") {
    Write-Skip "9Router already cloned"
} else {
    Write-Host "  Cloning 9Router..." -ForegroundColor Gray
    git clone https://github.com/decolua/9router.git $ROUTER_DIR 2>&1 | Out-Null
    Write-OK "9Router cloned"
}

# Step 2b
if (-not (Test-Path "$ROUTER_DIR\node_modules")) {
    Write-Host "  Installing npm dependencies..." -ForegroundColor Gray
    Push-Location $ROUTER_DIR
    npm install 2>&1 | Out-Null
    Pop-Location
    Write-OK "Dependencies installed"
}

# Step 3
Write-Step "3/4" "Initialize State"
$stateDir = "$($script:STATE_DIR)"
New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
$llmMode = @{ mode = "eco"; model = ""; updated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz") }
Write-JsonState -Path "$stateDir\llm-mode.json" -Data $llmMode
Write-OK "State initialized (ECO mode)"

# Step 4
Write-Step "4/4" "Setup Complete"
Write-Host ""
Write-Host "  =================================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "  =================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "    1. Edit api-key.txt - isi dengan key dari 9Router" -ForegroundColor White
Write-Host "       Dashboard: http://localhost:20128/dashboard" -ForegroundColor Gray
Write-Host "    2. Jalankan: .\scripts\start.ps1" -ForegroundColor White
Write-Host ""

