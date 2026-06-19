. "$PSScriptRoot\..\common\config.ps1"
. "$PSScriptRoot\..\common\helpers.ps1"
. "$PSScriptRoot\..\common\log.ps1"

function Write-Step2 { param([string]$Step,[string]$Message) Write-Host ""; Write-Host "[$Step] $Message" -ForegroundColor Cyan }
function Write-OK2 { param([string]$Message) Write-Host "  [OK] $Message" -ForegroundColor Green }

$ErrorActionPreference = "Continue"
$RootDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$startTime = Get-Date

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host "  farewell-assistant - Training Mode" -ForegroundColor Magenta
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host ""

$Count = 200

# S1 - generate cases
Write-Step2 "1/5" "Generate Test Cases"
. "$PSScriptRoot\generate-cases.ps1" -Count $Count
Write-OK2 "Test cases generated: $Count cases"

# S2 - evaluate
Write-Step2 "2/5" "Evaluate Pipeline"
. "$PSScriptRoot\evaluate.ps1" -InputFile "$PSScriptRoot\cases.json"

# S3 - load report
$report = Get-Content "$RootDir\training\report.json" -Raw | ConvertFrom-Json

# S4 - generate KB
Write-Step2 "3/5" "Generate Knowledge Base"

$writer = [System.IO.StreamWriter]::new("$RootDir\training\knowledge-base.md", $false, [System.Text.Encoding]::UTF8)
$writer.WriteLine("# Training Knowledge Base")
$writer.WriteLine("")
$writer.WriteLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
$writer.WriteLine("Test cases: $($report.total_cases)")
$writer.WriteLine("Duration: $($report.duration_seconds)s")
$writer.WriteLine("")
$writer.WriteLine("## Accuracy Metrics")
$writer.WriteLine("")
$writer.WriteLine("$($report.accuracy.overall)% overall accuracy")
$writer.WriteLine("- Intent: $($report.accuracy.intent)%")
$writer.WriteLine("- Domain: $($report.accuracy.domain)%")
$writer.WriteLine("- Complexity: $($report.accuracy.complexity)%")
$writer.WriteLine("- Hold: $($report.accuracy.hold)%")
$writer.WriteLine("")
$writer.WriteLine("## Domain Detection Keywords")
$writer.WriteLine("")
$writer.WriteLine("mobile: flutter, dart, kotlin, android, ios, swift, react native, firebase")
$writer.WriteLine("web: api, crud, auth, react, vue, next, django, fastapi, express")
$writer.WriteLine("infra: docker, kubernetes, deploy, ci/cd, pipeline, config, setup")
$writer.WriteLine("automation: powershell, script, task, schedule, windows, registry")
if ($report.errors.Count -gt 0) {
    $writer.WriteLine("")
    $writer.WriteLine("## Error Patterns")
    $errorTypes = $report.errors | Group-Object error_type
    foreach ($et in $errorTypes) {
        $writer.WriteLine("")
        $writer.WriteLine("### $($et.Name) Errors ($($et.Count) cases)")
        $writer.WriteLine("")
        $et.Group | Select-Object -First 5 | ForEach-Object {
            $expected = if ($et.Name -eq "intent") { $_.expected_intent } elseif ($et.Name -eq "domain") { $_.expected_domain } else { $_.expected_hold }
            $actual = if ($et.Name -eq "intent") { $_.actual_intent } elseif ($et.Name -eq "domain") { $_.actual_domain } else { $_.actual_hold }
            $writer.WriteLine("- [$($et.Name)] $($_.input) - expected: $expected, got: $actual")
        }
    }
}
$writer.WriteLine("")
$writer.WriteLine("## Chains")
$writer.WriteLine("")
$writer.WriteLine("build_web: 8 steps")
$writer.WriteLine("build_mobile: 7 steps")
$writer.WriteLine("build_infra: 7 steps")
$writer.WriteLine("fix_bug: 5 steps")
$writer.WriteLine("review_code: 5 steps")
$writer.WriteLine("deploy: 4 steps")
$writer.Close()

Write-OK2 "Knowledge base generated: training/knowledge-base.md"

# S5 - summary
Write-Step2 "4/5" "Summary"
$overall = $report.accuracy.overall
$grade = if ($overall -ge 95) { "A" } elseif ($overall -ge 85) { "B" } elseif ($overall -ge 75) { "C" } else { "D" }

Write-Host ""
Write-Host "  Grade: $grade ($overall%)" -ForegroundColor $(if ($overall -ge 90) {"Green"} elseif ($overall -ge 80) {"Yellow"} else {"Red"})
Write-Host "  Intent:   $($report.accuracy.intent)%"
Write-Host "  Domain:   $($report.accuracy.domain)%"
Write-Host "  Hold:     $($report.accuracy.hold)%"
Write-Host "  Duration: $($report.duration_seconds)s"
Write-Host "  Report:   training/report.json"
Write-Host "  KB:       training/knowledge-base.md"
Write-Host ""

Write-TaskLog -Stage "TRAINING" -Action "Training completed: Grade=$grade ($overall%), $($report.total_cases) cases" -Result "success"

Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host ""
