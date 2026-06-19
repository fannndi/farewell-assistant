# Run Tests — Execute all Pester tests for farewell-assistant pipeline
# Usage: .\run-tests.ps1
# Requires: Pester 3+

$ErrorActionPreference = "Continue"
$script:ROOT_DIR = Split-Path -Parent $PSCommandPath

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host "  farewell-assistant — Test Runner" -ForegroundColor Cyan
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host ""

# Import Pester
$pester = Get-Module -Name Pester -ListAvailable | Select-Object -First 1
if (-not $pester) {
    Write-Host "  [FAIL] Pester not installed. Install: Install-Module Pester -Force" -ForegroundColor Red
    exit 1
}

$testFiles = @(
    "$PSScriptRoot\tests\pipeline.tests.ps1"
)

$passed = 0
$failed = 0
$results = @()

foreach ($file in $testFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "  [SKIP] Test file not found: $file" -ForegroundColor Yellow
        continue
    }
    Write-Host "  [RUN] $file" -ForegroundColor White

    $output = & Invoke-Pester -Script @{ Path = $file } -Quiet -PassThru 2>&1

    $result = @{ file = $file; total = 0; pass = 0; fail = 0 }
    if ($output) {
        $total = ($output.PassedCount ?? 0) + ($output.FailedCount ?? 0) + ($output.SkippedCount ?? 0)
        $result.total = $total
        $result.pass = $output.PassedCount ?? 0
        $result.fail = $output.FailedCount ?? 0
    }
    $results += $result
    $passed += $result.pass
    $failed += $result.fail
}

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host "  Results: $passed passed, $failed failed, $(($results | Measure-Object total -Sum).Sum) total" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host ""

if ($failed -gt 0) { exit 1 } else { exit 0 }
