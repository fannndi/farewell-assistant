# run-router.ps1 — Backward-compat wrapper (delegates to Python)
# Original replaced by farewell_assistant.run_router module

param([string]$InputText)

$ErrorActionPreference = "Continue"
$script:ROOT_DIR = Split-Path -Parent $PSScriptRoot

$py = "py"
if (-not (Get-Command $py -ErrorAction SilentlyContinue)) {
    $py = "python3"
    if (-not (Get-Command $py -ErrorAction SilentlyContinue)) {
        $py = "python"
    }
}

& $py -m farewell_assistant.run_router --input "$InputText"
exit $LASTEXITCODE
