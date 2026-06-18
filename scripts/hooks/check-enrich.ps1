# Check Enrichment - Verify enrichment pipeline is working
# Usage: .\hooks\check-enrich.ps1 -Input "test input"

param([string]$Input)

$ErrorActionPreference = "Continue"

# Source adapter for its overridden Invoke-LLMEnrich with tracking
. "$PSScriptRoot\..\llm-adapter.ps1"

$mode = Get-LLMMode
$gpu = Get-GPUInfo

Write-Host ""
Write-Host "  Enrichment Check" -ForegroundColor Cyan
Write-Host "  Mode: $mode" -ForegroundColor $(if ($mode -eq "eco") { "Green" } else { "Cyan" })
Write-Host "  GPU:  $(if ($gpu.available) { "$($gpu.memory_used)/$($gpu.memory_total) MB ($($gpu.utilization)%)" } else { 'Not available' })" -ForegroundColor Gray
Write-Host ""

if ($mode -eq "eco") {
    Write-Host "  [ECO] Enrichment disabled. Switch to ON mode:" -ForegroundColor Yellow
    Write-Host "    .\scripts\llm-mode.ps1 on" -ForegroundColor Gray
    return
}

Write-Host "  Testing enrichment with: $Input" -ForegroundColor Gray
$start = Get-Date
$result = Invoke-LLMEnrich -Text $Input -Force
$elapsed = ((Get-Date) - $start).TotalSeconds

if ($result -ne $Input) {
    Write-Host "  [OK] Enrichment working" -ForegroundColor Green
    Write-Host "  Input:    $Input" -ForegroundColor Gray
    Write-Host "  Enriched: $result" -ForegroundColor Gray
    Write-Host "  Time:     $([math]::Round($elapsed, 1))s" -ForegroundColor Gray
} else {
    Write-Host "  [SKIP] Input was short/simple - enrichment skipped (correct behavior)" -ForegroundColor Yellow
}

Write-Host ""
