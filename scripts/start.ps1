# Start - Consolidated: initial bootstrap + git pull + update + health + config + autostart + launch
# Usage: .\start.ps1
# Safe to run every time laptop is turned on (guard skips already-done steps)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
$script:startTimestamp = Get-Date

. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"
. "$PSScriptRoot\common\log.ps1"

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host "  farewell-assistant - Start" -ForegroundColor Magenta
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host ""

# ------ Helpers ------

function Write-GitPull {
    param([string]$Repo, [string]$Dir, [string]$Remote, [string]$Branch)
    if (-not (Test-Path "$Dir\.git")) { Write-Skip "${Repo}: not cloned"; return }
    Push-Location $Dir
    try {
        git fetch origin 2>$null | Out-Null
        $before = git rev-parse HEAD 2>$null
        $behind = git rev-list --count "HEAD..$Remote/$Branch" 2>$null
        if ($behind -and $behind -gt 0) {
            Write-Host "  ${Repo}: $behind commit(s) behind" -ForegroundColor Yellow
            git pull --ff-only 2>&1 | Out-Null
            $afterShort = git log --oneline -1 2>$null
            Write-OK "${Repo} updated >> $afterShort"
            return $true
        }
        Write-Skip "${Repo}: up to date"
        return $false
    } finally { Pop-Location }
}

function Write-ShortChangelog {
    param([string]$File, [string]$Label)
    if (-not (Test-Path $File)) { Write-Skip "$Label not found"; return }
    $lines = Get-Content $File -First 15 -ErrorAction SilentlyContinue
    if ($lines) {
        Write-Info $Label
        foreach ($line in $lines) { Write-Host "    $line" -ForegroundColor Gray }
    }
    $content = Get-Content $File -Raw -ErrorAction SilentlyContinue
    if ($content) {
        foreach ($kw in @("breaking", "migration", "deprecated", "removed", "skill", "agent", "config")) {
            if ($content -match "(?i)$kw") {
                return $true
            }
        }
    }
    return $false
}

function Write-StartReport {
    param(
        [bool]$RouterRunning,
        [string]$Mode,
        [string[]]$ComboNamesFromFile,
        [hashtable]$ComboModelsByIndex,
        [array]$PingResults
    )

    $startTs = if ($script:startTimestamp) { $script:startTimestamp } else { Get-Date }
    $duration = [math]::Round(((Get-Date) - $startTs).TotalSeconds, 1)
    $commit = try { git -C $script:ROOT_DIR rev-parse --short HEAD 2>$null } catch { "unknown" }
    $now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    # 9Router details
    $routerPid = Get-9RouterPid
    $routerVersion = "?"
    if (Test-Path "$($script:ROUTER_DIR)\package.json") {
        try { $pv = (Get-Content "$($script:ROUTER_DIR)\package.json" -Raw | ConvertFrom-Json); $routerVersion = $pv.version } catch {}
    }

    # Dependencies
    $eccExists = Test-Path "$($script:ECC_DIR)\AGENTS.md"
    $standaloneExists = Test-Path "$($script:ROUTER_DIR)\.next\standalone\server.js"

    # GPU & LLM
    $gpu = Get-GPUInfo -Fields "name"
    $gpuName = if ($gpu.available) { $gpu.name } else { "not detected" }
    $ollamaOk = Test-OllamaRunning

    # Work mode & skills
    $workMode = Get-WorkMode
    $skillCount = Get-SkillCount -WorkMode $workMode

    # Autostart
    $taskExists = $false
    try { $taskExists = (Get-ScheduledTask -TaskName $script:TASK_NAME -ErrorAction Stop) -ne $null } catch {}

    # Agent-to-combo mapping
    $agentMap = @{}
    $combo0Agents = @("build", "tdd-guide", "security-reviewer")
    $combo1Agents = @("planner", "code-reviewer", "build-error-resolver", "doc-updater")
    if ($ComboNamesFromFile.Count -gt 0) { $agentMap[$ComboNamesFromFile[0]] = $combo0Agents }
    if ($ComboNamesFromFile.Count -gt 1) { $agentMap[$ComboNamesFromFile[1]] = $combo1Agents }

    # ============== RENDER ==============
    Write-Host ""
    Write-Host "  =================================================" -ForegroundColor Magenta
    Write-Host "  farewell-assistant - Start Report" -ForegroundColor Magenta
    Write-Host "  =================================================" -ForegroundColor Magenta
    Write-Host ""

    Write-Host "  SYSTEM" -ForegroundColor Cyan
    Write-Host "    Project:       farewell-assistant" -ForegroundColor White
    Write-Host "    Commit:        $commit" -ForegroundColor Gray
    Write-Host "    Duration:      ${duration}s" -ForegroundColor White
    Write-Host "    Timestamp:     $now" -ForegroundColor Gray
    Write-Host ""

    Write-Host "  9ROUTER" -ForegroundColor Cyan
    if ($RouterRunning) {
        Write-Host "    Status:        Running" -ForegroundColor Green
        Write-Host "    Port:          20128" -ForegroundColor White
        if ($routerPid) { Write-Host "    PID:           $routerPid" -ForegroundColor Gray }
        Write-Host "    Version:       $routerVersion" -ForegroundColor Gray
        Write-Host "    Dashboard:     http://localhost:20128/dashboard" -ForegroundColor Blue
    } else { Write-Host "    Status:        Stopped" -ForegroundColor Red }
    Write-Host ""

    Write-Host "  LLM & GPU" -ForegroundColor Cyan
    $modeColor = if ($Mode -eq "eco") { "Green" } else { "Cyan" }
    Write-Host "    Mode:          $Mode" -ForegroundColor $modeColor
    Write-Host "    GPU:           $gpuName" -ForegroundColor Gray
    $ollamaLabel = if ($Mode -eq "eco") { "skipped (eco mode)" } elseif ($ollamaOk) { "running" } else { "not running" }
    $ollamaColor = if ($Mode -eq "eco") { "Gray" } elseif ($ollamaOk) { "Green" } else { "Yellow" }
    Write-Host "    Ollama:        $ollamaLabel" -ForegroundColor $ollamaColor
    Write-Host ""

    Write-Host "  COMBOS & PROFILE" -ForegroundColor Cyan
    for ($i = 0; $i -lt $ComboNamesFromFile.Count; $i++) {
        $cName = $ComboNamesFromFile[$i]
        $cAgents = if ($i -eq 0) { "build, tdd-guide, security-reviewer" } else { "planner, code-reviewer, build-error-resolver, doc-updater" }
        $idxStr = "$i"
        $cModels = if ($ComboModelsByIndex -and $ComboModelsByIndex[$idxStr]) { @($ComboModelsByIndex[$idxStr]) } else { @() }
        $cModelStr = if ($cModels.Count -gt 0) { $cModels -join ', ' } else { "?" }
        Write-Host "    COMBO_$i`:       $cName" -ForegroundColor White
        Write-Host "      Agents:      $cAgents" -ForegroundColor Gray
        Write-Host "      Models:      $cModelStr" -ForegroundColor Gray
    }
    Write-Host "    Profile:       $($script:OPENCODE_CFG)" -ForegroundColor Gray
    Write-Host ""

    Write-Host "  MODEL HEALTH" -ForegroundColor Cyan
    if ($PingResults.Count -gt 0) {
        $groups = $PingResults | Group-Object combo
        foreach ($g in $groups) {
            Write-Host "    $($g.Name):" -ForegroundColor White
            foreach ($pr in $g.Group) {
                $icon = if ($pr.ok) { "+" } else { "x" }
                $iconColor = if ($pr.ok) { "Green" } else { "Red" }
                $statusLabel = if ($pr.ok) { "$($pr.code) ($($pr.time)s)" }
                    elseif ($pr.err -eq "timeout") { "timeout" }
                    else { "$($pr.code) error" }
                $line = "      $icon $($pr.model)".PadRight(46)
                Write-Host $line -ForegroundColor $iconColor -NoNewline
                Write-Host " $statusLabel" -ForegroundColor $(if ($pr.ok) { "Gray" } else { "Red" })
            }
        }
    } else {
        if (-not $RouterRunning) { Write-Host "    9Router not running" -ForegroundColor Yellow }
        else { Write-Host "    No model data found" -ForegroundColor Yellow }
    }
    Write-Host ""

    Write-Host "  DEPENDENCIES" -ForegroundColor Cyan
    $eccLabel = if ($eccExists) { "cloned" } else { "missing" }
    $standaloneLabel = if ($standaloneExists) { "built" } else { "missing" }
    Write-Host "    ECC:           $eccLabel $(if ($eccExists) {'(v)'} else {'(x)'})" -ForegroundColor $(if ($eccExists) { "Green" } else { "Red" })
    Write-Host "    9Router:       $standaloneLabel $(if ($standaloneExists) {'(v)'} else {'(x)'})" -ForegroundColor $(if ($standaloneExists) { "Green" } else { "Red" })
    Write-Host "    Skills:        ON - $skillCount" -ForegroundColor White
    Write-Host ""

    Write-Host "  AUTOSTART" -ForegroundColor Cyan
    $taskLabel = if ($taskExists) { "registered" } else { "not configured" }
    Write-Host "    Task:          $($script:TASK_NAME) $(if ($taskExists) {'(v)'} else {'(x)'})" -ForegroundColor $(if ($taskExists) { "Green" } else { "Gray" })
    Write-Host ""

    Write-Host "  WORK MODE" -ForegroundColor Cyan
    Write-Host "    Mode:          $($workMode.ToUpper())" -ForegroundColor $(if ($workMode -eq "build") { "Green" } else { "Yellow" })
    Write-Host ""

    Write-Host "  =================================================" -ForegroundColor Magenta
    Write-Host ""
}

# ------ ApiKeyFile Parser ------

function Read-ApiKeyFile {
    $result = @{
        apiKey             = $null
        comboEntries       = @()
        comboModelsByIndex = @{}
        comboNamesFromFile = @()
    }
    if (-not (Test-Path $script:API_KEY_FILE)) { return $result }

    Get-Content $script:API_KEY_FILE | ForEach-Object {
        $line = $_.Trim()
        if ($line -match '^([A-Z_0-9]+)=(.*)') {
            $key = $matches[1]; $val = $matches[2]
            Set-Item -Path "env:$key" -Value $val -ErrorAction SilentlyContinue
            if ($key -eq "NINEROUTER_API_KEY") { $result.apiKey = $val }
            if ($key -match '^COMBO_(\d+)$' -and $val) {
                $result.comboEntries += @{ name = $matches[1]; value = $val.Trim() }
            }
            if ($key -match '^MODELS_(\d+)$' -and $val) {
                $midx = $matches[1]
                $result.comboModelsByIndex[$midx] = $val -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }
            }
        }
    }

    $comboNamesByIndex = @{}
    foreach ($entry in $result.comboEntries) {
        $comboNamesByIndex[$entry.name] = $entry.value
    }
    $sortedIndices = $comboNamesByIndex.Keys | Sort-Object
    foreach ($idx in $sortedIndices) {
        $result.comboNamesFromFile += $comboNamesByIndex[$idx]
    }

    return $result
}

# ============================================================
#  Step 1/7: Git Pull Self (sync antar device)
# ============================================================

Write-Step "1/7" "Git Pull Self"

$startHashBefore = $null
try { $startHashBefore = (Get-FileHash $PSCommandPath -ErrorAction Stop).Hash } catch {}

$pulledSelf = Write-GitPull -Repo "farewell-assistant" -Dir $script:ROOT_DIR -Remote origin -Branch main

# Check if start.ps1 itself changed after pull
$startHashAfter = $null
try { $startHashAfter = (Get-FileHash $PSCommandPath -ErrorAction Stop).Hash } catch {}
if ($startHashBefore -and $startHashAfter -and $startHashBefore -ne $startHashAfter) {
    Write-Host "  start.ps1 updated -- run /start again to use the new version." -ForegroundColor Yellow
}

# ============================================================
#  Step 2/7: Initial Bootstrap (guard - only runs once)
# ============================================================

Write-Step "2/7" "Initial Bootstrap"

$needsInit = $false
if (-not (Test-Path $script:COMBO_FILE) -or -not (Test-Path $script:LLM_MODE_FILE) -or -not (Test-Path $script:WORK_MODE_FILE)) {
    $needsInit = $true
}

if ($needsInit) {
    Write-Info "First run detected. Running initial setup..."

    # Clone ECC
    if (-not (Test-Path "$($script:ECC_DIR)\AGENTS.md")) {
        Write-Info "Cloning ECC..."
        git clone https://github.com/affaan-m/ECC.git $script:ECC_DIR 2>&1 | Out-Null
        Write-OK "ECC cloned"
    } else { Write-Skip "ECC already cloned" }

    # Clone 9Router
    if (-not (Test-Path "$($script:ROUTER_DIR)\package.json")) {
        Write-Info "Cloning 9Router..."
        git clone https://github.com/decolua/9router.git $script:ROUTER_DIR 2>&1 | Out-Null
        Write-OK "9Router cloned"
    } else { Write-Skip "9Router already cloned" }

    # npm install
    if (-not (Test-Path "$($script:ROUTER_DIR)\node_modules")) {
        Write-Info "Installing npm dependencies..."
        Push-Location $script:ROUTER_DIR
        try { npm install 2>&1 | Out-Null } finally { Pop-Location }
        Write-OK "Dependencies installed"
    } else { Write-Skip "Dependencies already installed" }

    # Build standalone
    if (-not (Test-Path "$($script:ROUTER_DIR)\.next\standalone\server.js")) {
        Write-Info "Building 9Router (may take 1-2 min)..."
        Push-Location $script:ROUTER_DIR
        try { npm run build 2>&1 | Out-Null } finally { Pop-Location }
        Write-OK "9Router built"
    } else { Write-Skip "9Router already built" }

    # Start 9Router
    if (-not (Start-9Router)) {
        Write-Info "Start 9Router failed -- check logs after setup"
    }

    # api-key.txt
    if (-not (Test-Path $script:API_KEY_FILE)) {
        if (Test-Path "$($script:ROOT_DIR)\api-key.example.txt") {
            Copy-Item "$($script:ROOT_DIR)\api-key.example.txt" $script:API_KEY_FILE -Force
            Write-OK "api-key.txt created from example"
        }
    } else { Write-Skip "api-key.txt already exists" }

    # Dashboard guidance
    Write-Host ""
    Write-Host "  Open http://localhost:20128/dashboard in browser:" -ForegroundColor Cyan
    Write-Host "    1. Set dashboard password (default: 123456)" -ForegroundColor White
    Write-Host "    2. Create an API key" -ForegroundColor White
    Write-Host "    3. Create combos (model groups)" -ForegroundColor White
    Write-Host "    4. Edit api-key.txt with actual API key + combo models" -ForegroundColor White
    Write-Host ""
    try { Read-Host "  Press Enter when done" } catch { Write-Host "  (non-interactive -- continuing)" }

    # Validate API key
    $akf = Read-ApiKeyFile
    $apiKey = $akf.apiKey
    if ($apiKey -and $apiKey -ne "sk-your-api-key-here") {
        try {
            $null = Invoke-RestMethod -Uri "$($script:API_URL)/api/v1/models" -TimeoutSec 5 -ErrorAction Stop
            Write-OK "API key valid"
        } catch { Write-Fail "API key validation failed" }
    } else { Write-Skip "API key not set -- edit api-key.txt" }

    # Save combos
    if ($akf.comboEntries.Count -gt 0) {
        $validCombos = @()
        foreach ($entry in $akf.comboEntries) {
            $models = if ($akf.comboModelsByIndex[$entry.name]) { @($akf.comboModelsByIndex[$entry.name]) } else { @() }
            if ($models.Count -gt 0) {
                $validCombos += @{ name = $entry.name; combo = $entry.value; models = $models }
                Write-OK "Combo '$($entry.value)': $($models -join ', ')"
            }
        }
        if ($validCombos.Count -gt 0) {
            New-Item -ItemType Directory -Path $script:STATE_DIR -Force | Out-Null
            $validCombos | ConvertTo-Json -Depth 5 | Set-Content -Path $script:COMBO_FILE -Encoding UTF8
            Write-OK "Combos saved"
        } else { Write-Fail "No valid combos" }
    } else { Write-Skip "No COMBO_* entries" }

    # Init state
    New-Item -ItemType Directory -Path $script:STATE_DIR -Force | Out-Null
    Write-JsonState -Path $script:LLM_MODE_FILE -Data @{ mode = "eco"; model = ""; updated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz") }
    Write-JsonState -Path $script:WORK_MODE_FILE -Data @{ mode = "build"; updated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz") }
    Write-OK "State initialized (eco + build)"

    # MCP config
    $mcpCfg = "$($script:STATE_DIR)\mcp-config.json"
    $mcpExample = "$($script:ROOT_DIR)\mcp-config.example.json"
    if (-not (Test-Path $mcpCfg) -and (Test-Path $mcpExample)) {
        Copy-Item $mcpExample $mcpCfg -Force
        Write-OK "MCP config created"
    }

    # GPU detection
    $gpu = Get-GPUInfo -Fields "name,memory.total"
    if ($gpu.available) { Write-OK "GPU: $($gpu.name)" } else { Write-Skip "No GPU detected" }

    Write-TaskLog -Stage "INITIAL" -Action "First-run bootstrap completed" -Result "success"
} else {
    Write-Skip "Initial already done"
}

# ============================================================
#  Step 3/7: Update ECC + 9Router + npm
# ============================================================

Write-Step "3/7" "Update Check"

$eccUpdated = Write-GitPull -Repo "ECC" -Dir $script:ECC_DIR -Remote origin -Branch main
$routerUpdated = Write-GitPull -Repo "9Router" -Dir $script:ROUTER_DIR -Remote origin -Branch master

# Sync changelogs
if ($eccUpdated -or $routerUpdated) {
    if ($eccUpdated -and (Test-Path "$($script:ECC_DIR)\.git")) {
        Push-Location $script:ECC_DIR
        try { $changelog = git show origin/main:CHANGELOG.md 2>$null } finally { Pop-Location }
        if ($changelog) { $changelog | Out-File "$($script:ROOT_DIR)\CHANGELOG_ECC.md" -Encoding UTF8 -ErrorAction SilentlyContinue }
    }
    if ($routerUpdated -and (Test-Path "$($script:ROUTER_DIR)\.git")) {
        Push-Location $script:ROUTER_DIR
        try { $changelog = git show origin/master:CHANGELOG.md 2>$null } finally { Pop-Location }
        if ($changelog) { $changelog | Out-File "$($script:ROOT_DIR)\CHANGELOG_9ROUTER.md" -Encoding UTF8 -ErrorAction SilentlyContinue }
    }
}

# Rebuild 9Router if updated
if ($routerUpdated) {
    # Deteksi perubahan package.json
    Write-Info "Rebuilding 9Router..."
    Push-Location $script:ROUTER_DIR
    try {
        # npm install if node_modules missing or package.json changed
        if (-not (Test-Path "node_modules")) { npm install 2>&1 | Out-Null }
        Stop-9Router
        npm run build 2>&1 | Out-Null
        if (Test-Path ".next\standalone\server.js") {
            Write-OK "9Router rebuilt"
        } else { Write-Fail "Build failed" }
    } finally { Pop-Location }
    Start-9Router
}

# Check npm 9router version vs local
try {
    $npmVer = npm view 9router version 2>$null
    $localVer = (Get-Content "$($script:ROUTER_DIR)\package.json" -Raw | ConvertFrom-Json).version
    if ($npmVer -and $localVer -and $npmVer -ne $localVer) {
        Write-Host "  npm 9router v$npmVer available (local: v$localVer) -- pulling update..." -ForegroundColor Yellow
        Push-Location $script:ROUTER_DIR
        try { git pull --ff-only origin master 2>&1 | Out-Null; npm install 2>&1 | Out-Null; Stop-9Router; npm run build 2>&1 | Out-Null } finally { Pop-Location }
        if (Test-Path "$($script:ROUTER_DIR)\.next\standalone\server.js") {
            Write-OK "9Router updated to v$npmVer"
            Start-9Router
        }
    }
} catch { Write-Verbose "npm version check failed: $_" }

# Changelog analysis -- scan breaking changes
$hasBreaking = $false
if (Test-Path "$($script:ROOT_DIR)\CHANGELOG_ECC.md") {
    $eccContent = Get-Content "$($script:ROOT_DIR)\CHANGELOG_ECC.md" -Raw -ErrorAction SilentlyContinue
    if ($eccContent -match "(?i)(breaking|migration|deprecated|removed|skill|agent|config)") { $hasBreaking = $true }
}
if (Test-Path "$($script:ROOT_DIR)\CHANGELOG_9ROUTER.md") {
    $rContent = Get-Content "$($script:ROOT_DIR)\CHANGELOG_9ROUTER.md" -Raw -ErrorAction SilentlyContinue
    if ($rContent -match "(?i)(breaking|migration|deprecated|removed)") { $hasBreaking = $true }
}
if ($eccUpdated -or $routerUpdated) {
    if (Test-Path "$($script:ROOT_DIR)\CHANGELOG_ECC.md") { Write-ShortChangelog -File "$($script:ROOT_DIR)\CHANGELOG_ECC.md" -Label "CHANGELOG_ECC.md" | Out-Null }
    if (Test-Path "$($script:ROOT_DIR)\CHANGELOG_9ROUTER.md") { Write-ShortChangelog -File "$($script:ROOT_DIR)\CHANGELOG_9ROUTER.md" -Label "CHANGELOG_9ROUTER.md" | Out-Null }
}
if ($hasBreaking) {
    Write-Host "  WARNING: Potential breaking changes detected in changelogs." -ForegroundColor Yellow
    Write-Host "  Review CHANGELOG_ECC.md / CHANGELOG_9ROUTER.md before proceeding." -ForegroundColor Yellow
    $proceed = $true
    try { $resp = Read-Host "  Continue? [Y/n]"; if ($resp -eq 'n' -or $resp -eq 'N') { $proceed = $false } } catch { $proceed = $true }
    if (-not $proceed) { Write-Host "  Aborted by user." -ForegroundColor Red; Write-TaskLog -Stage "START" -Action "Update aborted by user" -Result "cancelled"; exit }
}

if ($eccUpdated -or $routerUpdated) { Write-TaskLog -Stage "UPDATE" -Action "ECC/9Router updated" -Result "success" }

# ============================================================
#  Step 4/7: 9Router Health
# ============================================================

Write-Step "4/7" "9Router Health"

$routerRunning = $false
try { $null = Invoke-RestMethod -Uri "$($script:API_URL)/api/health" -TimeoutSec 3 -ErrorAction Stop; $routerRunning = $true; Write-OK "9Router is running" } catch {}

if (-not $routerRunning) {
    $standaloneJs = "$($script:ROUTER_DIR)\.next\standalone\server.js"
    if (-not (Test-Path $standaloneJs)) {
        Write-Info "Standalone missing, rebuilding..."
        Push-Location $script:ROUTER_DIR
        try { npm run build 2>&1 | Out-Null } finally { Pop-Location }
    }
    if (Start-9Router) { $routerRunning = $true }
}

# ============================================================
#  Step 5/7: Load Configuration + Combo Check
# ============================================================

Write-Step "5/7" "Load Configuration"

# Parse api-key.txt
$akf = Read-ApiKeyFile
$comboNamesFromFile = $akf.comboNamesFromFile
$comboModelsByIndex = $akf.comboModelsByIndex

if ($comboNamesFromFile.Count -gt 0) {
    Write-OK "API keys loaded"

    # Sort indices for predictable iteration
    $sortedIndices = $akf.comboEntries | Sort-Object { [int]$_.name } | ForEach-Object { $_.name }

    # Diff vs cached combo.json
    $cached = @()
    if (Test-Path $script:COMBO_FILE) {
        try { $cached = Get-Content $script:COMBO_FILE -Raw | ConvertFrom-Json } catch {}
    }

    $changed = @()
    $newCombos = @()
    foreach ($idx in $sortedIndices) {
        $cachedEntry = $cached | Where-Object { $_.name -eq $idx }
        $entry = $akf.comboEntries | Where-Object { $_.name -eq $idx }
        $cName = $entry.value
        if (-not $cachedEntry) {
            $newCombos += "$idx ($cName)"
        } else {
            $oldModels = if ($cachedEntry.models) { @($cachedEntry.models) -join ',' } else { "" }
            $newModels = if ($comboModelsByIndex[$idx]) { $comboModelsByIndex[$idx] -join ',' } else { "" }
            if ($cachedEntry.combo -ne $cName -or $oldModels -ne $newModels) { $changed += $idx }
        }
    }

    if ($newCombos.Count -gt 0 -or $changed.Count -gt 0) {
        foreach ($nc in $newCombos) { Write-Host "  NEW combo: $nc" -ForegroundColor Green }
        foreach ($ch in $changed) {
            $cachedEntry = $cached | Where-Object { $_.name -eq $ch }
            $entry = $akf.comboEntries | Where-Object { $_.name -eq $ch }
            if ($cachedEntry) {
                Write-Host "  CHANGED combo: $ch ($($entry.value))" -ForegroundColor Yellow
                Write-Host "    Before: combo=$($cachedEntry.combo), models=$(@($cachedEntry.models) -join ',')" -ForegroundColor Gray
                Write-Host "    After:  combo=$($entry.value), models=$($comboModelsByIndex[$ch] -join ',')" -ForegroundColor White
            }
        }
    } else {
        Write-OK "Combos unchanged: $($comboNamesFromFile -join ', ')"
    }

    # Save to combo.json for next-run diff
    $saveCombos = @()
    foreach ($idx in $sortedIndices) {
        $entry = $akf.comboEntries | Where-Object { $_.name -eq $idx }
        $saveCombos += @{
            name   = $idx
            combo  = $entry.value
            models = if ($comboModelsByIndex[$idx]) { @($comboModelsByIndex[$idx]) } else { @() }
        }
    }
    New-Item -ItemType Directory -Path $script:STATE_DIR -Force | Out-Null
    $saveCombos | ConvertTo-Json -Depth 5 | Set-Content -Path $script:COMBO_FILE -Encoding UTF8
} else {
    # Fallback to combo.json
    if (Test-Path $script:COMBO_FILE) {
        try {
            $cached = Get-Content $script:COMBO_FILE -Raw | ConvertFrom-Json
            $comboNamesFromFile = @($cached | ForEach-Object { $_.combo })
            foreach ($ce in $cached) {
                if ($ce.models -and @($ce.models).Count -gt 0) {
                    $comboModelsByIndex[$ce.name] = @($ce.models)
                }
            }
        } catch {}
    }
    if ($comboNamesFromFile.Count -eq 0) { Write-Skip "api-key.txt not found" }
}

# ============================================================
#  Generate Profile
# ============================================================

if ($comboNamesFromFile.Count -gt 0) {
    $config = Get-Content $script:PROFILE_SRC -Raw
    $config = $config -replace '\{project\}', ($script:ROOT_DIR -replace '\\', '/')

    # Build combo models object
    $modelObj = @{}
    foreach ($c in $comboNamesFromFile) {
        $modelObj[$c] = @{ name = "$c combo" }
    }
    $comboModelsJson = $modelObj | ConvertTo-Json -Depth 3

    $config = $config -replace '\$\{COMBO_0\}', $comboNamesFromFile[0]
    $combo1 = if ($comboNamesFromFile.Count -gt 1) { $comboNamesFromFile[1] } else { $comboNamesFromFile[0] }
    $config = $config -replace '\$\{COMBO_1\}', $combo1
    $config = $config -replace '\$\{COMBO_MODELS\}', $comboModelsJson

    $contextSlug = "farewell-assistant"
    try {
        if (Test-Path $script:REGISTRY_FILE) {
            $reg = Get-Content $script:REGISTRY_FILE -Raw | ConvertFrom-Json
            if ($reg.active) { $contextSlug = $reg.active }
        }
    } catch {}
    $config = $config -replace '\{context_file\}', $contextSlug

    New-Item -ItemType Directory -Path $script:OPENCODE_DIR -Force | Out-Null
    $config | Set-Content -Path $script:OPENCODE_CFG -Encoding UTF8
    Write-OK "Profile applied"
} else {
    Write-Skip "No combos -- profile not generated"
}

# ============================================================
#  Step 6/7: Autostart Check
# ============================================================

Write-Step "6/7" "Autostart"

$taskExists = $false
try { $taskExists = (Get-ScheduledTask -TaskName $script:TASK_NAME -ErrorAction Stop) -ne $null } catch {}

if ($taskExists) {
    Write-Skip "Autostart task registered (manual start via /start)"
} else {
    Write-Skip "Autostart disabled — start 9Router via /start"
}

# Cleanup stale VBS (legacy)
$oldVbs = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\9router.vbs"
if (Test-Path $oldVbs) { try { Remove-Item $oldVbs -Force; Write-OK "Removed stale VBS" } catch {} }

# ============================================================
#  Step 7/7: Pipeline Prime + Launch
# ============================================================

Write-Step "7/7" "Pipeline + Launch"

$mode = Get-LLMMode
if ($mode -ne "eco") {
    $ollamaOk = Start-OllamaService
    if ($ollamaOk) { Write-OK "Ollama running" } else { Write-Fail "Ollama failed to start" }
}

# Prime pipeline — runs Invoke-IntentRouter to write fresh context files
try {
    if (Test-Path $script:ENRICHMENT_SCRIPT) {
        . $script:ENRICHMENT_SCRIPT
        . $script:SKILL_CHAIN_SCRIPT
        . $script:INTENT_ROUTER_SCRIPT
        $pipelineResult = Invoke-IntentRouter -TextInput "session start" -Force
        if ($pipelineResult.success) {
            Write-OK "Pipeline primed: $($pipelineResult.intent.intent)/$($pipelineResult.intent.domain)/$($pipelineResult.intent.complexity)"
        } else {
            Write-OK "Pipeline primed (startup)"
        }
    }
} catch {
    Write-Skip "Pipeline skip: $_"
}

# Ping models from MODELS_N (file-based, no SQLite dependency)
$pingResults = @()
if ($routerRunning -and $env:NINEROUTER_API_KEY -and @($comboNamesFromFile).Count -gt 0) {
    $hdrs = @{ "Authorization" = "Bearer $env:NINEROUTER_API_KEY"; "Content-Type" = "application/json" }
    foreach ($i in 0..($comboNamesFromFile.Count - 1)) {
        $midx = "$i"
        $models = if ($comboModelsByIndex -and $comboModelsByIndex.ContainsKey($midx)) { @($comboModelsByIndex[$midx]) } else { @() }
        if ($models.Count -eq 0) { continue }
        $cName = $comboNamesFromFile[$i]
        foreach ($m in $models) {
            $pingBody = @{ model = $m; messages = @(@{ role = "user"; content = "ping" }); max_tokens = 5 } | ConvertTo-Json -Compress
            $t0 = Get-Date; $ok = $false; $code = 0; $err = ""
            try {
                $resp = Invoke-WebRequest -Uri "$($script:API_URL)/v1/chat/completions" -Method Post -Headers $hdrs -Body $pingBody -TimeoutSec 10 -ErrorAction Stop
                $code = [int]$resp.StatusCode; $ok = ($code -eq 200)
            } catch {
                if ($_.Exception.Response) { try { $code = [int]$_.Exception.Response.StatusCode } catch {} }
                if ($_.Exception.Message -match "timeout|timed out") { $err = "timeout" } else { $err = "error" }
            }
            $elapsed = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
            $pingResults += @{ combo = $cName; model = $m; ok = $ok; code = $code; time = $elapsed; err = $err }
        }
    }
}

Write-StartReport -RouterRunning $routerRunning -Mode $mode -ComboNamesFromFile $comboNamesFromFile -ComboModelsByIndex $comboModelsByIndex -PingResults $pingResults

Sync-SessionState
Write-TaskLog -Stage "START" -Action "Consolidated start completed" -Result "success"

opencode
