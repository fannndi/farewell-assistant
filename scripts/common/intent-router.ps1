# Intent Router - Routes user intent to appropriate skill chain and model
# Usage: . "$PSScriptRoot\intent-router.ps1"
# Depends on: enrichment-pipeline.ps1, skill-chain.ps1, helpers.ps1, config.ps1

# -- Turn Counter (persisted to .opencode/turn-count) --
$script:TurnCount = 0
$script:TurnCountFile = "$($script:STATE_DIR)\turn-count"
function Get-TurnCount {
    if (Test-Path $script:TurnCountFile) {
        try { return [int](Get-Content $script:TurnCountFile -Raw).Trim() } catch { return 0 }
    }
    return 0
}
function Set-TurnCount {
    param([int]$Count)
    try { New-Item -ItemType Directory -Path (Split-Path $script:TurnCountFile -Parent) -Force | Out-Null } catch {}
    $Count | Set-Content -Path $script:TurnCountFile -Encoding UTF8
}

# -- Main Router Function --

function Invoke-IntentRouter {
    param(
        [Parameter(Mandatory)][string]$TextInput,
        [string]$Context = "",
        [string]$WorkMode = "",
        [string]$ActiveProfile = "",
        [switch]$Force
    )

    # Default values
    if (-not $WorkMode) { $WorkMode = Get-WorkMode }
    if (-not $ActiveProfile) { $ActiveProfile = Get-LLMMode }

    # Increment turn counter (persisted)
    $script:TurnCount = (Get-TurnCount) + 1
    Set-TurnCount -Count $script:TurnCount

    # Step 1: Classify intent (structured or quick)
    $classified = Get-CachedIntent -Input $TextInput
    if (-not $classified) {
        $structured = Invoke-StructuredEnrichment -TextInput $TextInput -Context $Context -Force:$Force
        $quick = Get-QuickIntent -TextInput $TextInput
        # Priority: quick (if confident) > structured > quick (fallback)
        # Threshold 0.8: only override structured enrichment for high-confidence quick matches
        if ($quick.confidence -ge 0.8) {
            $classified = $quick
            $classified.source = "quick"
        } elseif ($structured) {
            $classified = $structured
        } else {
            $classified = $quick
            $classified.source = "quick"
        }
        Set-CachedIntent -Input $TextInput -Intent $classified
    }

    # Step 2: Check permissions against work mode
    $permission = Test-TaskPermission -Intent $classified -WorkMode $WorkMode
    if (-not $permission.allowed) {
        $result = @{
            success = $false
            reason = $permission.reason
            intent = $classified
        }
        Sync-TurnState -Result $result -UserInput $TextInput
        return $result
    }

    # Step 3: Build skill chain
    $chain = Get-SkillChain -Intent $classified.intent -Domain $classified.domain

    # Step 4: Select model route based on complexity + profile
    $modelRoute = Select-ModelRoute -Complexity $classified.complexity -Profile $ActiveProfile

    # Step 5: Determine if planning phase is needed
    $needsPlanning = ($classified.complexity -eq "high" -or $classified.complexity -eq "critical") -and $classified.intent -eq "build"

    # Step 6: Build blocked intents list
    $blocked = @()
    if ($WorkMode -eq "plan") { $blocked = @("build", "fix", "deploy") }

    $result = @{
        success = $true
        intent = $classified
        skill_chain = $chain
        model_route = $modelRoute
        needs_planning = $needsPlanning
        work_mode = $WorkMode
        profile = $ActiveProfile
        turn = $script:TurnCount
        blocked = $blocked
        chain_summary = ($chain | ForEach-Object { $_.name }) -join " → "
    }

    # Step 7: Persist to context files
    Sync-TurnState -Result $result -UserInput $TextInput

    return $result
}

# -- Permission Check --

function Test-TaskPermission {
    param($Intent, [string]$WorkMode)

    # PLAN mode: block write-heavy tasks
    if ($WorkMode -eq "plan") {
        $writeIntents = @("build", "fix", "deploy")
        if ($writeIntents -contains $Intent.intent) {
            return @{
                allowed = $false
                reason = "Intent '$($Intent.intent)' requires BUILD mode. Current mode: PLAN"
            }
        }
    }

    return @{ allowed = $true }
}

# -- Model Route Selection --

function Select-ModelRoute {
    param(
        [string]$Complexity,
        [string]$Profile
    )

    # Complexity-based routing (single source: $script:MODEL_ROUTES from config.ps1)
    $routeMap = $script:MODEL_ROUTES
    if (-not $routeMap) { return @{ primary = "Free"; secondary = "Free"; heavy = "Free" } }

    $routes = $routeMap[$Complexity]
    if (-not $routes) { $routes = $routeMap["medium"] }

    return $routes
}

# -- Execution Summary Display --

function Show-IntentRouterResult {
    param($Result)

    if (-not $Result.success) {
        Write-Host ""
        Write-Host "  [BLOCKED] $($Result.reason)" -ForegroundColor Red
        Write-Host "  Switch to BUILD mode: /workmode build" -ForegroundColor Yellow
        Write-Host ""
        return
    }

    $intent = $Result.intent
    $chain = $Result.skill_chain
    $model = $Result.model_route

    Write-Host ""
    Write-Host "  =================================================" -ForegroundColor Cyan
    Write-Host "  Intent Router" -ForegroundColor Cyan
    Write-Host "  =================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Intent:       $($intent.intent)" -ForegroundColor White
    Write-Host "  Domain:       $($intent.domain)" -ForegroundColor White
    Write-Host "  Complexity:   $($intent.complexity)" -ForegroundColor $(if ($intent.complexity -eq "high") {"Yellow"} elseif ($intent.complexity -eq "medium") {"Cyan"} else {"Green"})
    Write-Host "  Confidence:   $([math]::Round($intent.confidence * 100))%" -ForegroundColor Gray
    Write-Host "  Source:       $($intent.source)" -ForegroundColor Gray
    if ($intent.stack.Count -gt 0) {
        Write-Host "  Stack:        $($intent.stack -join ', ')" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  Model:        Free=$($model.primary) / Emergency=$($model.secondary)" -ForegroundColor White
    Write-Host "  Planning:     $($Result.needs_planning)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Skill Chain ($($chain.Count) steps):" -ForegroundColor White
    for ($i = 0; $i -lt $chain.Count; $i++) {
        $step = $chain[$i]
        Write-Host "    $($i+1). $($step.name)" -ForegroundColor Cyan
        Write-Host "       $($step.desc)" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  =================================================" -ForegroundColor Cyan
    Write-Host ""
}

# -- Persist Turn State to Context Files --

function Sync-TurnState {
    param($Result, [string]$UserInput = "")

    $stateDir = if ($script:STATE_DIR) { $script:STATE_DIR } else { "$($script:ROOT_DIR)\.opencode" }

    # 1. Write pipeline-result.json (structured, machine-readable)
    $pipelineData = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")
        input = $UserInput
        turn = if ($Result.turn) { $Result.turn } else { $script:TurnCount }
    }

    if ($Result.success) {
        $pipelineData.intent = $Result.intent.intent
        $pipelineData.domain = $Result.intent.domain
        $pipelineData.stack = @($Result.intent.stack)
        $pipelineData.complexity = $Result.intent.complexity
        $pipelineData.confidence = $Result.intent.confidence
        $pipelineData.source = $Result.intent.source
        $pipelineData.needs_planning = $Result.needs_planning
        $pipelineData.model_primary = $Result.model_route.primary
        $pipelineData.model_heavy = $Result.model_route.heavy
        $pipelineData.chain = ($Result.skill_chain | ForEach-Object { $_.name })
        $pipelineData.chain_summary = $Result.chain_summary
        $pipelineData.blocked = $Result.blocked
        $pipelineData.work_mode = $Result.work_mode
        $pipelineData.profile = $Result.profile
    } else {
        $pipelineData.blocked = $true
        $pipelineData.reason = $Result.reason
        $pipelineData.intent = $Result.intent.intent
    }

    $pipelineJson = $pipelineData | ConvertTo-Json -Depth 5
    $pipelinePath = Join-Path $stateDir "pipeline-result.json"
    try {
        New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
        $pipelineJson | Set-Content -Path $pipelinePath -Encoding UTF8
    } catch { Write-Verbose "Sync-TurnState: Failed to write pipeline-result.json: $_" }

    # 2. Update context.md (human-readable, AI-injectable)
    $mode = "eco"
    $work = "BUILD"
    try {
        $modeData = Get-Content (Join-Path $stateDir "llm-mode.json") -Raw | ConvertFrom-Json
        if ($modeData.mode) { $mode = $modeData.mode }
    } catch {}
    try {
        $workData = Get-Content (Join-Path $stateDir "work-mode.json") -Raw | ConvertFrom-Json
        if ($workData.mode) { $work = $workData.mode.ToUpper() }
    } catch {}

    $active = "farewell-assistant"
    $kategori = "AUTOMATION"
    try {
        if (Test-Path "$($script:ROOT_DIR)\projects\registry.json") {
            $reg = Get-Content "$($script:ROOT_DIR)\projects\registry.json" -Raw | ConvertFrom-Json
            if ($reg.active) { $active = $reg.active }
            if ($reg.projects.$active.kategori) {
                $katValues = @()
                foreach ($kv in $reg.projects.$active.kategori.PSObject.Properties) { $katValues += $kv.Value }
                $kategori = ($katValues | Select-Object -Unique) -join " > "
            }
        }
    } catch {}

    # Build chain display
    $chainDisplay = ""
    $intentDisplay = ""
    $complexityDisplay = ""
    $confidenceDisplay = ""
    $stackDisplay = ""
    $planningDisplay = ""
    $blockedDisplay = ""
    $modelDisplay = ""

    if ($Result.success) {
        $chainDisplay = $Result.chain_summary
        $intentDisplay = $Result.intent.intent
        $complexityDisplay = $Result.intent.complexity
        $confidenceDisplay = "$([math]::Round($Result.intent.confidence * 100))%($($Result.intent.source))"
        $stackDisplay = if ($Result.intent.stack.Count -gt 0) { ($Result.intent.stack -join ', ') } else { "-" }
        $planningDisplay = if ($Result.needs_planning) { "yes" } else { "no" }
        $blockedDisplay = if ($Result.blocked.Count -gt 0) { ($Result.blocked -join ', ') } else { "none" }
        $modelDisplay = "$($Result.model_route.primary)/$($Result.model_route.heavy)"
    } else {
        $intentDisplay = "BLOCKED"
        $blockedDisplay = $Result.reason
    }

    $turnCount = if ($Result.turn) { $Result.turn } else { $script:TurnCount }

    # Get session start time from session-state.json
    $sessionStarted = ""
    try {
        $ssPath = Join-Path $stateDir "session-state.json"
        if (Test-Path $ssPath) {
            $ss = Get-Content $ssPath -Raw | ConvertFrom-Json
            if ($ss.session.started) { $sessionStarted = $ss.session.started }
        }
    } catch {}
    if (-not $sessionStarted) { $sessionStarted = Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz' }

    $contextContent = @"
# Session State

- **Project:** $active
- **Kategori:** $kategori
- **Mode:** $mode
- **Work:** $work
- **Started:** $sessionStarted

# Turn State

- **Intent:** $intentDisplay
- **Complexity:** $complexityDisplay
- **Confidence:** $confidenceDisplay
- **Stack:** $stackDisplay
- **Chain:** $chainDisplay
- **Model:** $modelDisplay
- **Planning:** $planningDisplay
- **Blocked:** $blockedDisplay
- **Turn:** $turnCount
"@

    $contextPath = Join-Path $stateDir "context.md"
    try {
        $contextContent | Set-Content -Path $contextPath -Encoding UTF8
    } catch { Write-Verbose "Sync-TurnState: Failed to write context.md: $_" }
}
