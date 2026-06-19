# Check Enrichment - Verify structured enrichment pipeline is working
# Usage: .\hooks\check-enrich.ps1 -InputText "test input"
# Diagnostic command (not a hook). Validates Invoke-StructuredEnrichment end-to-end.

param([string]$InputText)

$ErrorActionPreference = "Continue"

$script:ROOT_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
. "$PSScriptRoot\..\common\helpers.ps1"
. "$PSScriptRoot\..\common\config.ps1"
. "$PSScriptRoot\..\common\enrichment-pipeline.ps1"
. "$PSScriptRoot\..\common\skill-chain.ps1"
. "$PSScriptRoot\..\common\intent-router.ps1"

$mode = Get-LLMMode
$gpu = Get-GPUInfo

Write-Host ""
Write-Host "  Pipeline Check" -ForegroundColor Cyan
Write-Host "  Mode: $mode" -ForegroundColor $(if ($mode -eq "eco") { "Green" } else { "Cyan" })
Write-Host "  GPU:  $(if ($gpu.available) { "$($gpu.memory_used)/$($gpu.memory_total) MB ($($gpu.utilization)%)" } else { 'Not available' })" -ForegroundColor Gray
Write-Host ""

if ($mode -eq "eco" -and -not $InputText) {
    Write-Host "  [ECO] Enrichment disabled. Switch mode:" -ForegroundColor Yellow
    Write-Host "    .\scripts\llm-setup.ps1 on" -ForegroundColor Gray
    return
}

if (-not $InputText) { $InputText = "bikin CRUD user dengan auth JWT" }

Write-Host "  Testing pipeline with: $InputText" -ForegroundColor Gray
Write-Host ""

# Run the full intent router
$start = Get-Date
$result = Invoke-IntentRouter -TextInput $InputText -Force
$elapsed = ((Get-Date) - $start).TotalSeconds

if ($result.success) {
    $intent = $result.intent
    Write-Host "  [OK] Pipeline completed in $([math]::Round($elapsed, 1))s" -ForegroundColor Green
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
    Write-Host "  Model Route:  $($result.model_route.primary)/$($result.model_route.heavy)" -ForegroundColor White
    Write-Host "  Skill Chain:  $($result.skill_chain.Count) steps" -ForegroundColor White
    Write-Host "  Planning:     $($result.needs_planning)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Files written:" -ForegroundColor White
    Write-Host "    .opencode/pipeline-result.json" -ForegroundColor Gray
    Write-Host "    .opencode/context.md" -ForegroundColor Gray
} else {
    Write-Host "  [BLOCKED] $($result.reason)" -ForegroundColor Red
}

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host ""
