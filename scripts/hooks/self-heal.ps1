# Self-Heal Hook - Post-edit typecheck
# Trigger: after Edit or Write tool
# Checks: tsc (TypeScript), flutter analyze (Dart), ruff (Python)

param(
    [string]$FilePath,
    [string]$ProjectPath
)

$ErrorActionPreference = "Continue"

if (-not $FilePath) { exit 0 }

$ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
$results = @()

switch ($ext) {
    { $_ -in ".ts", ".tsx" } {
        $result = & npx tsc --noEmit 2>&1
        if ($LASTEXITCODE -ne 0) {
            $results += "TypeScript errors found"
        }
    }
    { $_ -in ".dart" } {
        $result = & flutter analyze "$FilePath" 2>&1
        if ($result -match "error") {
            $results += "Dart analysis errors found"
        }
    }
    { $_ -in ".py" } {
        $result = & ruff check "$FilePath" 2>&1
        if ($result -match "E") {
            $results += "Python lint errors found"
        }
    }
}

if ($results.Count -gt 0) {
    Write-Host "  [self-heal] Issues detected:" -ForegroundColor Yellow
    foreach ($r in $results) {
        Write-Host "    - $r" -ForegroundColor Yellow
    }
}
