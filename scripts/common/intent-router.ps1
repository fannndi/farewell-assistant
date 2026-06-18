# Intent Router - Routes user intent to appropriate skill chain and model
# Usage: . "$PSScriptRoot\intent-router.ps1"
# Depends on: enrichment-pipeline.ps1, skill-chain.ps1, helpers.ps1, config.ps1

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

    # Step 1: Classify intent (structured or quick)
    $classified = Get-CachedIntent -Input $TextInput
    if (-not $classified) {
        $structured = Invoke-StructuredEnrichment -TextInput $TextInput -Context $Context -Force:$Force
        if ($structured) {
            $classified = $structured
        } else {
            $classified = Get-QuickIntent -TextInput $TextInput
            $classified.source = "quick"
        }
        Set-CachedIntent -Input $TextInput -Intent $classified
    }

    # Step 2: Check permissions against work mode
    $permission = Test-TaskPermission -Intent $classified -WorkMode $WorkMode
    if (-not $permission.allowed) {
        return @{
            success = $false
            reason = $permission.reason
            intent = $classified
        }
    }

    # Step 3: Build skill chain
    $chain = Get-SkillChain -Intent $classified.intent -Domain $classified.domain

    # Step 4: Select model route based on complexity + profile
    $modelRoute = Select-ModelRoute -Complexity $classified.complexity -Profile $ActiveProfile

    # Step 5: Determine if planning phase is needed
    $needsPlanning = $classified.complexity -eq "high" -and $classified.intent -eq "build"

    return @{
        success = $true
        intent = $classified
        skill_chain = $chain
        model_route = $modelRoute
        needs_planning = $needsPlanning
        work_mode = $WorkMode
        profile = $ActiveProfile
    }
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

    # Complexity-based routing
    $routeMap = @{
        "low"    = @{ primary = "Free"; secondary = "Free"; heavy = "Free" }
        "medium" = @{ primary = "Free"; secondary = "Free"; heavy = "Free" }
        "high"   = @{ primary = "Free"; secondary = "Emergency"; heavy = "Emergency" }
    }

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
