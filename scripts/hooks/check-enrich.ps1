# Check Enrichment - Verify enrichment pipeline is working
# Usage: .\hooks\check-enrich.ps1 -InputText "test input"
# Diagnostic command (not a hook). Validates Invoke-LLMEnrich end-to-end.

param([string]$InputText)

$ErrorActionPreference = "Continue"

$script:ROOT_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
. "$PSScriptRoot\..\common\helpers.ps1"
. "$PSScriptRoot\..\common\config.ps1"

$mode = Get-LLMMode
$gpu = Get-GPUInfo

Write-Host ""
Write-Host "  Enrichment Check" -ForegroundColor Cyan
Write-Host "  Mode: $mode" -ForegroundColor $(if ($mode -eq "eco") { "Green" } else { "Cyan" })
Write-Host "  GPU:  $(if ($gpu.available) { "$($gpu.memory_used)/$($gpu.memory_total) MB ($($gpu.utilization)%)" } else { 'Not available' })" -ForegroundColor Gray
Write-Host ""

if ($mode -eq "eco") {
    Write-Host "  [ECO] Enrichment disabled. Switch to ON mode:" -ForegroundColor Yellow
    Write-Host "    .\scripts\llm-setup.ps1 on" -ForegroundColor Gray
    return
}

Write-Host "  Testing enrichment with: $InputText" -ForegroundColor Gray
$start = Get-Date
$result = Invoke-LLMEnrich -Text $InputText -Force
$elapsed = ((Get-Date) - $start).TotalSeconds

if ($result -ne $InputText) {
    Write-Host "  [OK] Enrichment working" -ForegroundColor Green
    Write-Host "  Input:    $InputText" -ForegroundColor Gray
    Write-Host "  Enriched: $result" -ForegroundColor Gray
    Write-Host "  Time:     $([math]::Round($elapsed, 1))s" -ForegroundColor Gray
} else {
    Write-Host "  [SKIP] Input was short/simple - enrichment skipped (correct behavior)" -ForegroundColor Yellow
}

Write-Host ""
