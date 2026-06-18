# Initial - One-time setup for new laptop
# Usage: .\scripts\initial.ps1
# Clones dependencies, builds 9Router, validates keys, initializes state

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"
. "$PSScriptRoot\common\log.ps1"

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host "  farewell-assistant - Initial Setup" -ForegroundColor Magenta
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host ""

# ── Step 1/10: Clone ECC ──

Write-Step "1/10" "Clone ECC"

if (Test-Path "$($script:ECC_DIR)\AGENTS.md") {
    Write-Skip "ECC already cloned"
} else {
    Write-Host "  Cloning ECC..." -ForegroundColor Gray
    git clone https://github.com/affaan-m/ECC.git $script:ECC_DIR 2>&1 | Out-Null
    Write-OK "ECC cloned"
}

# ── Step 2/10: Clone 9Router ──

Write-Step "2/10" "Clone 9Router"

if (Test-Path "$($script:ROUTER_DIR)\package.json") {
    Write-Skip "9Router already cloned"
} else {
    Write-Host "  Cloning 9Router..." -ForegroundColor Gray
    git clone https://github.com/decolua/9router.git $script:ROUTER_DIR 2>&1 | Out-Null
    Write-OK "9Router cloned"
}

if (-not (Test-Path "$($script:ROUTER_DIR)\node_modules")) {
    Write-Host "  Installing npm dependencies..." -ForegroundColor Gray
    Push-Location $script:ROUTER_DIR
    try {
        npm install 2>&1 | Out-Null
    } finally {
        Pop-Location
    }
    Write-OK "Dependencies installed"
} else {
    Write-Skip "Dependencies already installed"
}

# ── Step 3/10: Build 9Router ──

Write-Step "3/10" "Build 9Router"

if (Test-Path "$($script:ROUTER_DIR)\.next\standalone\server.js") {
    Write-Skip "9Router already built"
} else {
    Write-Host "  Building 9Router (first time, this may take a minute)..." -ForegroundColor Gray
    Push-Location $script:ROUTER_DIR
    try {
        npm run build 2>&1 | Out-Null
    } finally {
        Pop-Location
    }
    Write-OK "9Router built"
}

# ── Step 4/10: Start 9Router ──

Write-Step "4/10" "Start 9Router"

$routerRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$($script:API_URL)/api/health" -TimeoutSec 3 -ErrorAction Stop
    $routerRunning = $true
    Write-OK "9Router is already running"
} catch {}

if (-not $routerRunning) {
    if (Start-9Router) {
        $routerRunning = $true
    } else {
        Write-Info "Check logs or try manual start from 9router directory"
    }
}

# ── Step 5/10: Dashboard & API Key ──

Write-Step "5/10" "Dashboard & API Key"

if (-not (Test-Path $script:API_KEY_FILE)) {
    if (Test-Path "$($script:ROOT_DIR)\api-key.example.txt") {
        Write-Info "Copying api-key.example.txt to api-key.txt..."
        Copy-Item -Path "$($script:ROOT_DIR)\api-key.example.txt" -Destination $script:API_KEY_FILE -Force
        Write-OK "api-key.txt created from example"
    } else {
        Write-Info "Creating api-key.txt..."
        @"
# === 9Router Configuration ===
NINEROUTER_API_KEY=sk-your-api-key-here
9ROUTER_PASSWORD=123456
# === Combo Definitions ===
# Format: COMBO_<Name>=<model1>,<model2>,<model3>
"@ | Set-Content -Path $script:API_KEY_FILE -Encoding UTF8
        Write-OK "api-key.txt created"
    }
} else {
    Write-Skip "api-key.txt already exists"
}

Write-Host ""
Write-Host "  Open 9Router dashboard and complete the following:" -ForegroundColor Cyan
Write-Host "    URL: http://localhost:20128/dashboard" -ForegroundColor White
Write-Host "    1. Set dashboard password" -ForegroundColor White
Write-Host "    2. Create an API key" -ForegroundColor White
Write-Host "    3. Create combos (model groups)" -ForegroundColor White
Write-Host "    4. Edit api-key.txt with your actual API key and combo definitions" -ForegroundColor White
Write-Host ""
Read-Host "  Press Enter when done"

# ── Step 6/10: Validate Keys ──

Write-Step "6/10" "Validate API Key & Combos"

$apiKey = $null
$comboEntries = @()

if (Test-Path $script:API_KEY_FILE) {
    Get-Content $script:API_KEY_FILE | ForEach-Object {
        $line = $_.Trim()
        if ($line -match '^([A-Z_]+)=(.*)') {
            $key = $matches[1]
            $val = $matches[2]
            if ($key -eq "NINEROUTER_API_KEY") { $apiKey = $val }
            if ($key -match '^COMBO_(.+)$' -and $val -and $val -ne '<model1>,<model2>,<model3>') {
                $comboEntries += @{ name = $key; combo = $matches[1]; value = $val }
            }
        }
    }
}

if (-not $apiKey -or $apiKey -eq "sk-your-api-key-here") {
    Write-Fail "NINEROUTER_API_KEY is not set in api-key.txt"
} elseif (-not ($apiKey -match '^sk-')) {
    Write-Fail "NINEROUTER_API_KEY looks invalid (expected to start with 'sk-'): $apiKey"
} else {
    Write-Info "Testing API key against 9Router..."
    $modelsOk = $false
    try {
        $models = Invoke-RestMethod -Uri "$($script:API_URL)/api/v1/models" -TimeoutSec 5 -ErrorAction Stop
        $modelsOk = $true
        Write-OK "API key valid, 9Router responded"
    } catch {
        Write-Fail "API key validation failed - 9Router returned error"
    }

    if ($modelsOk -and $comboEntries.Count -gt 0) {
        $availableModels = @()
        if ($models.data) {
            $availableModels = $models.data | Select-Object -ExpandProperty id
        }

        $validCombos = @()
        foreach ($entry in $comboEntries) {
            $comboModels = $entry.value -split ','
            $validModels = @()
            foreach ($m in $comboModels) {
                $mTrim = $m.Trim()
                if ($mTrim -in $availableModels) {
                    $validModels += $mTrim
                } else {
                    Write-Info "  Model '$mTrim' not found in 9Router - skipping"
                }
            }
            if ($validModels.Count -gt 0) {
                $validCombos += @{ name = $entry.combo; models = $validModels }
                Write-OK "Combo '$($entry.combo)': $($validModels -join ', ')"
            } else {
                Write-Fail "Combo '$($entry.combo)' has no valid models"
            }
        }

        if ($validCombos.Count -gt 0) {
            New-Item -ItemType Directory -Path $script:STATE_DIR -Force | Out-Null
            $validCombos | ConvertTo-Json -Depth 5 | Set-Content -Path $script:COMBO_FILE -Encoding UTF8
            Write-OK "Saved $($validCombos.Count) valid combo(s) to combo.json"
        } else {
            Write-Fail "No valid combos found - check api-key.txt combo definitions"
        }
    } elseif ($comboEntries.Count -eq 0) {
        Write-Skip "No COMBO_* entries found in api-key.txt"
    }
}

# ── Step 7/10: Initialize State ──

Write-Step "7/10" "Initialize State"

New-Item -ItemType Directory -Path $script:STATE_DIR -Force | Out-Null

$llmMode = @{
    mode      = "eco"
    model     = ""
    updated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")
}
Write-JsonState -Path $script:LLM_MODE_FILE -Data $llmMode
Write-OK "llm-mode.json set to eco"

$workMode = @{
    mode       = "build"
    updated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")
}
Write-JsonState -Path $script:WORK_MODE_FILE -Data $workMode
Write-OK "work-mode.json set to build"

# ── Step 8/10: LLM Setup ──

Write-Step "8/10" "LLM Setup"

$gpu = Get-GPUInfo -Fields "name,memory.total"

if ($gpu.available) {
    Write-OK "NVIDIA GPU detected: $($gpu.name) ($($gpu.memory_total) MiB VRAM)"
    Write-Host ""
    Write-Host "  VRAM-based model recommendations:" -ForegroundColor Cyan

    if ($gpu.memory_total -ge 24000) {
        Write-Host "    >= 24GB: Can run 7B-14B models comfortably" -ForegroundColor Green
        Write-Host "    Suggested: ollama run qwen2.5:14b" -ForegroundColor Gray
    } elseif ($gpu.memory_total -ge 16000) {
        Write-Host "    16GB: Can run 7B-8B models" -ForegroundColor Green
        Write-Host "    Suggested: ollama run qwen2.5:7b" -ForegroundColor Gray
    } elseif ($gpu.memory_total -ge 8000) {
        Write-Host "    8GB: Can run small models (3B-4B)" -ForegroundColor Yellow
        Write-Host "    Suggested: ollama run qwen2.5:3b" -ForegroundColor Gray
    } else {
        Write-Host "    < 8GB: Limited to tiny models" -ForegroundColor Yellow
        Write-Host "    Suggested: ollama run qwen2.5:1.5b or use eco mode" -ForegroundColor Gray
    }

    Write-Host ""
    Write-Info "To enable local LLM, run: .\scripts\llm-setup.ps1 on"
} else {
    Write-Skip "No NVIDIA GPU detected"
    Write-Info "Local LLM not available - use eco mode (cloud only)"
    Write-Info "To change mode later, run: .\scripts\llm-setup.ps1"
}

# ── Step 9/10: MCP Configuration ──

Write-Step "9/10" "MCP Configuration"

$mcpConfig = "$($script:STATE_DIR)\mcp-config.json"
$mcpExample = "$($script:ROOT_DIR)\mcp-config.example.json"

if (Test-Path $mcpConfig) {
    Write-Skip "mcp-config.json already exists"
    try {
        $mcpContent = Get-Content $mcpConfig -Raw
        if ($mcpContent -match "YOUR_GITHUB_PAT_HERE") {
            Write-Host "  WARNING: mcp-config.json has GitHub PAT placeholder." -ForegroundColor Yellow
            Write-Host "  Either set GITHUB_PERSONAL_ACCESS_TOKEN or remove the github server." -ForegroundColor Yellow
        }
    } catch {}
} elseif (Test-Path $mcpExample) {
    Write-Info "Copying mcp-config.example.json to .opencode/mcp-config.json..."
    Copy-Item -Path $mcpExample -Destination $mcpConfig -Force
    Write-OK "mcp-config.json created from example"
    Write-Host ""
    Write-Host "  MCP servers configured:" -ForegroundColor Cyan
    Write-Host "    - context7: live docs lookup (no auth needed)" -ForegroundColor White
    Write-Host "    - github: GitHub ops (REQUIRES PAT — edit mcp-config.json)" -ForegroundColor White
    Write-Host "    - sequential-thinking: chain-of-thought" -ForegroundColor White
    Write-Host "    - memory: persistent memory across sessions" -ForegroundColor White
    Write-Host ""
    Write-Host "  To get a GitHub PAT:" -ForegroundColor Cyan
    Write-Host "    1. https://github.com/settings/tokens (classic or fine-grained)" -ForegroundColor White
    Write-Host "    2. Scope: repo (for PR/issue ops)" -ForegroundColor White
    Write-Host "    3. Edit .opencode/mcp-config.json -> replace YOUR_GITHUB_PAT_HERE" -ForegroundColor White
    Write-Host "    4. Or remove the 'github' server entirely if not needed" -ForegroundColor White
    Write-Host ""
} else {
    Write-Skip "No mcp-config.example.json found (skipping MCP setup)"
}

# ── Step 10/10: Autostart Recommendation ──

Write-Step "10/10" "Autostart (optional)"

Write-Host "  To auto-start 9Router on Windows logon:" -ForegroundColor Cyan
Write-Host "    .\scripts\autostart.ps1 -Action enable" -ForegroundColor White
Write-Host "  Manages Scheduled Task 'FarewellAssistant-9Router':" -ForegroundColor Gray
Write-Host "    - Trigger: AtLogon (no admin required)" -ForegroundColor Gray
Write-Host "    - Restart: 3x at 5-min interval on failure" -ForegroundColor Gray
Write-Host "    - Logs: .opencode/logs/autostart.log" -ForegroundColor Gray
Write-Host ""
$enableAutostart = Read-Host "  Enable autostart now? [y/N]"
if ($enableAutostart -eq "y" -or $enableAutostart -eq "Y") {
    & "$($script:ROOT_DIR)\scripts\autostart.ps1" -Action enable
} else {
    Write-Skip "Autostart skipped (enable later: .\scripts\autostart.ps1 -Action enable)"
}

# ── Completion ──

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Green
Write-Host "  Initial Setup Complete!" -ForegroundColor Green
Write-Host "  =================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Summary:" -ForegroundColor Cyan
Write-Host "    ECC:        $(if (Test-Path "$($script:ECC_DIR)\AGENTS.md") { 'Cloned' } else { 'Missing' })" -ForegroundColor $(if (Test-Path "$($script:ECC_DIR)\AGENTS.md") { "Green" } else { "Red" })
Write-Host "    9Router:    $(if ($routerRunning) { 'Running' } else { 'Not running' })" -ForegroundColor $(if ($routerRunning) { "Green" } else { "Yellow" })
Write-Host "    LLM Mode:   eco" -ForegroundColor Green
Write-Host "    Work Mode:  build" -ForegroundColor Green
Write-Host "    MCP:        $(if (Test-Path $mcpConfig) { 'Configured' } else { 'Not configured' })" -ForegroundColor $(if (Test-Path $mcpConfig) { "Green" } else { "Yellow" })
Write-Host "    Autostart:  $(if ($enableAutostart -eq 'y' -or $enableAutostart -eq 'Y') { 'Enabled' } else { 'Skipped' })" -ForegroundColor $(if ($enableAutostart -eq 'y' -or $enableAutostart -eq 'Y') { "Green" } else { "Gray" })
Write-Host ""
Write-Host "  Next step: Run .\scripts\start.ps1 to start daily session" -ForegroundColor Cyan
Write-Host ""
