# Self-Heal Hook - Post-edit typecheck (project-aware)
# Trigger: after Edit or Write tool
# Only runs a typecheck if the edited file's project has the corresponding markers:
#   - TypeScript: tsconfig.json present in ProjectPath
#   - Dart/Flutter: pubspec.yaml present
#   - Python: pyproject.toml, requirements.txt, or Pipfile present
# This avoids running tsc on a .ts file inside a project that doesn't use TS,
# or flutter analyze when Flutter isn't installed, etc.

param(
    [string]$FilePath,
    [string]$ProjectPath
)

$ErrorActionPreference = "Continue"

if (-not $FilePath) { exit 0 }
if (-not $ProjectPath) { $ProjectPath = (Get-Location).Path }

$ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
$results = @()

function Test-ProjectMarker {
    param([string]$Root, [string[]]$Markers)
    foreach ($m in $Markers) {
        if (Test-Path -LiteralPath (Join-Path $Root $m)) { return $true }
    }
    return $false
}

switch ($ext) {
    { $_ -in ".ts", ".tsx" } {
        if (Test-ProjectMarker -Root $ProjectPath -Markers @("tsconfig.json")) {
            $result = & npx tsc --noEmit 2>&1
            if ($LASTEXITCODE -ne 0) {
                $results += "TypeScript errors found"
            }
        } else {
            exit 0
        }
    }
    { $_ -in ".dart" } {
        if (Test-ProjectMarker -Root $ProjectPath -Markers @("pubspec.yaml")) {
            $result = & flutter analyze "$FilePath" 2>&1
            if ($result -match "error") {
                $results += "Dart analysis errors found"
            }
        } else {
            exit 0
        }
    }
    { $_ -in ".py" } {
        if (Test-ProjectMarker -Root $ProjectPath -Markers @("pyproject.toml", "requirements.txt", "Pipfile")) {
            $result = & ruff check "$FilePath" 2>&1
            if ($result -match "E") {
                $results += "Python lint errors found"
            }
        } else {
            exit 0
        }
    }
    default {
        exit 0
    }
}

if ($results.Count -gt 0) {
    Write-Host "  [self-heal] Issues detected:" -ForegroundColor Yellow
    foreach ($r in $results) {
        Write-Host "    - $r" -ForegroundColor Yellow
    }
}
