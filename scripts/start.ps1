# Start - Daily startup (lightweight)
# Usage: .\start.ps1

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"
. "$PSScriptRoot\common\log.ps1"

function Write-UpdateCheck {
    param([string]$Repo, [string]$Dir, [string]$Remote, [string]$Branch)
    if (-not (Test-Path "$Dir\.git")) { Write-Skip "${Repo}: not cloned"; return $false }
    Push-Location $Dir
    try {
        git fetch $Remote 2>&1 | Out-Null
        $behind = git rev-list --count "HEAD..$Remote/$Branch" 2>&1
    } finally { Pop-Location }
    if ($behind -and $behind -gt 0) {
        Write-Host "  ${Repo}: $behind commit(s) behind" -ForegroundColor Yellow
        return $true
    }
    Write-Skip "${Repo}: up to date"
    return $false
}

# ============================================================
#  Step 1/5: 9Router Health
# ============================================================

Write-Step "1/5" "9Router Health"

$routerRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$($script:API_URL)/api/health" -TimeoutSec 3 -ErrorAction Stop
    $routerRunning = $true
    Write-OK "9Router is running"
} catch {}

if (-not $routerRunning) {
    $standaloneJs = "$($script:ROUTER_DIR)\.next\standalone\server.js"
    if (-not (Test-Path $standaloneJs)) {
        Write-Info "Building 9Router (may take 1-2 min)..."
        Push-Location $script:ROUTER_DIR
        try { npm run build 2>&1 | Out-Null }
        finally { Pop-Location }
        Write-OK "9Router built"
    }
    if (Start-9Router) {
        $routerRunning = $true
    }
}

# ============================================================
#  Step 2/5: Update Check
# ============================================================

Write-Step "2/5" "Update Check"

$eccBehind = Write-UpdateCheck -Repo "ECC" -Dir $script:ECC_DIR -Remote origin -Branch main
$routerBehind = Write-UpdateCheck -Repo "9Router" -Dir $script:ROUTER_DIR -Remote origin -Branch master

if ($eccBehind -or $routerBehind) {
    Write-Host "  Run /owner to pull updates" -ForegroundColor Yellow
}

# ============================================================
#  Step 3/5: Load Configuration
# ============================================================

Write-Step "3/5" "Load Configuration"

$comboNames = @()
if (Test-Path $script:API_KEY_FILE) {
    Get-Content $script:API_KEY_FILE | ForEach-Object {
        $line = $_.Trim()
        if ($line -match '^([A-Z_]+)=(.*)') {
            Set-Item -Path "env:$($matches[1])" -Value $matches[2]
            if ($matches[1] -match '^COMBO_\d+$') {
                $comboNames += $matches[2]
            }
        }
    }
    Write-OK "API keys loaded"
} else {
    Write-Skip "api-key.txt not found"
}

if ($comboNames.Count -gt 0 -and -not (Test-Path $script:COMBO_FILE)) {
    New-Item -ItemType Directory -Path $script:STATE_DIR -Force | Out-Null
    $comboNames | ConvertTo-Json | Set-Content -Path $script:COMBO_FILE -Encoding UTF8
    Write-OK "Combo names saved to combo.json"
} elseif ($comboNames.Count -eq 0 -and (Test-Path $script:COMBO_FILE)) {
    try { $comboNames = Get-Content $script:COMBO_FILE -Raw | ConvertFrom-Json } catch {}
}

# ============================================================
#  Step 4/5: Apply Profile
# ============================================================

Write-Step "4/5" "Apply Profile"

if ($comboNames.Count -eq 0) {
    Write-Fail "No combos found in api-key.txt or combo.json"
} else {
    $modelEntries = ""
    for ($i = 0; $i -lt $comboNames.Count; $i++) {
        if ($i -gt 0) { $modelEntries += "," }
        $modelEntries += "`n      `"$($comboNames[$i])`": { `"name`": `"$($comboNames[$i]) combo`" }"
    }
    $comboModels = "{$modelEntries`n    }"

    $config = Get-Content $script:PROFILE_SRC -Raw
    $config = $config -replace '\{project\}', ($script:ROOT_DIR -replace '\\', '/')
    $config = $config -replace '\$\{COMBO_0\}', $comboNames[0]
    $combo1 = if ($comboNames.Count -gt 1) { $comboNames[1] } else { $comboNames[0] }
    $config = $config -replace '\$\{COMBO_1\}', $combo1
    $config = $config -replace '\$\{COMBO_MODELS\}', $comboModels

    New-Item -ItemType Directory -Path $script:OPENCODE_DIR -Force | Out-Null
    $config | Set-Content -Path $script:OPENCODE_CFG -Encoding UTF8
    Write-OK "Profile applied"
}

# ============================================================
#  Step 5/5: Launch
# ============================================================

Write-Step "5/5" "Launch"

$mode = Get-LLMMode
if ($mode -ne "eco") {
    $ollamaOk = Start-OllamaService
    if ($ollamaOk) { Write-OK "Ollama running" }
    else { Write-Fail "Ollama failed to start" }
}

Write-Host ""
Write-Host "  9Router:    $(if ($routerRunning) { 'Running' } else { 'Check manually' })" -ForegroundColor $(if ($routerRunning) { "Green" } else { "Yellow" })
Write-Host "  Combos:     $($comboNames -join ', ')" -ForegroundColor White
Write-Host "  LLM Mode:   $mode" -ForegroundColor $(if ($mode -eq "eco") { "Green" } else { "Cyan" })
Write-Host ""

Sync-SessionState
Write-TaskLog -Stage "START" -Action "Daily startup completed" -Result "success"

opencode
