function Write-Step2 { param([string]$Step,[string]$Message) Write-Host ""; Write-Host "[$Step] $Message" -ForegroundColor Cyan }
function Write-OK2 { param([string]$Message) Write-Host "  [OK] $Message" -ForegroundColor Green }

. "$PSScriptRoot\..\common\config.ps1"
. "$PSScriptRoot\..\common\helpers.ps1"
. "$PSScriptRoot\..\common\enrichment-pipeline.ps1"
. "$PSScriptRoot\..\common\skill-chain.ps1"
. "$PSScriptRoot\..\common\intent-router.ps1"

$InputFile = "$PSScriptRoot\cases.json"

if (-not (Test-Path $InputFile)) {
    Write-Host "  Test cases not found. Run generate-cases.ps1 first." -ForegroundColor Red
    exit 1
}

$cases = Get-Content $InputFile -Raw | ConvertFrom-Json
Write-Host ""
Write-Host "  Running pipeline on $($cases.Count) test cases..." -ForegroundColor Cyan

$intentCorrect = 0; $domainCorrect = 0; $complexityCorrect = 0; $holdCorrect = 0
$errors = @()

Remove-Item "$($script:STATE_DIR)\turn-count" -Force -ErrorAction SilentlyContinue

$sw = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($case in $cases) {
    $classified = Get-QuickIntent -TextInput $case.input
    $structured = $null
    try { $structured = Invoke-StructuredEnrichment -TextInput $case.input -Force } catch {}

    if ($structured -and $structured.intent -ne "ask") {
        $classified = $structured
    } elseif ($structured) {
        $classified = $structured
    }

    $sufficiency = Test-InputSufficiency -TextInput $case.input -Classified $classified
    $holdResult = (-not $sufficiency.sufficient)

    if ($classified.intent -eq $case.expected_intent) { $intentCorrect++ } else {
        $errors += @{ input = $case.input; expected_intent = $case.expected_intent; actual_intent = $classified.intent; error_type = "intent" }
    }
    if ($classified.domain -eq $case.expected_domain) { $domainCorrect++ } else {
        $errors += @{ input = $case.input; expected_domain = $case.expected_domain; actual_domain = $classified.domain; error_type = "domain" }
    }
    if ($classified.complexity -eq $case.expected_complexity) { $complexityCorrect++ } else {
        $errors += @{ input = $case.input; expected_complexity = $case.expected_complexity; actual_complexity = $classified.complexity; error_type = "complexity" }
    }
    if ($holdResult -eq $case.expected_hold) { $holdCorrect++ } else {
        $errors += @{ input = $case.input; expected_hold = $case.expected_hold; actual_hold = $holdResult; error_type = "hold" }
    }
}

$sw.Stop()
$total = $cases.Count

$intentAcc = [math]::Round(($intentCorrect / $total) * 100, 1)
$domainAcc = [math]::Round(($domainCorrect / $total) * 100, 1)
$complexityAcc = [math]::Round(($complexityCorrect / $total) * 100, 1)
$holdAcc = [math]::Round(($holdCorrect / $total) * 100, 1)
$overallAcc = [math]::Round((($intentCorrect + $domainCorrect + $complexityCorrect + $holdCorrect) / ($total * 4)) * 100, 1)

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host "  EVALUATION RESULTS" -ForegroundColor Cyan
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Total:     $total test cases"
Write-Host "  Duration:  $([math]::Round($sw.Elapsed.TotalSeconds, 1))s"
Write-Host "  Intent:    $intentAcc% ($intentCorrect/$total)"
Write-Host "  Domain:    $domainAcc% ($domainCorrect/$total)"
Write-Host "  Complexity: $complexityAcc% ($complexityCorrect/$total)"
Write-Host "  Hold:      $holdAcc% ($holdCorrect/$total)"
Write-Host "  Overall:   $overallAcc%"
Write-Host ""

$report = @{
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")
    total_cases = $total
    duration_seconds = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    accuracy = @{ intent = $intentAcc; domain = $domainAcc; complexity = $complexityAcc; hold = $holdAcc; overall = $overallAcc }
    correct = @{ intent = $intentCorrect; domain = $domainCorrect; complexity = $complexityCorrect; hold = $holdCorrect }
    wrong = @{ intent = ($total - $intentCorrect); domain = ($total - $domainCorrect); complexity = ($total - $complexityCorrect); hold = ($total - $holdCorrect) }
    errors = $errors
}
$RootDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$report | ConvertTo-Json -Depth 5 | Set-Content -Path "$RootDir\training\report.json" -Encoding UTF8

if ($errors.Count -gt 0) {
    Write-Host "  Errors: $($errors.Count) (first 10):" -ForegroundColor Yellow
    $errors | Select-Object -First 10 | ForEach-Object {
        $eType = $_.error_type
        if ($eType -eq "intent") { Write-Host "    [$eType] $($_.input) - expected: $($_.expected_intent), got: $($_.actual_intent)" -ForegroundColor Red }
        elseif ($eType -eq "domain") { Write-Host "    [$eType] $($_.input) - expected: $($_.expected_domain), got: $($_.actual_domain)" -ForegroundColor Red }
        else { Write-Host "    [$eType] $($_.input) - expected hold: $($_.expected_hold), got: $($_.actual_hold)" -ForegroundColor Red }
    }
}

Write-Host ""
Write-Host "  Report: training/report.json" -ForegroundColor Green
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host ""
