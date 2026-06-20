# detect-project.ps1 — Backward-compat wrapper (delegates to Python)
# Original replaced by farewell_assistant.detect_project module

param(
    [string]$Path = (Get-Location).Path,
    [switch]$EmitContext
)

$ErrorActionPreference = "Continue"
$script:ROOT_DIR = Split-Path -Parent $PSScriptRoot

$py = "py"
if (-not (Get-Command $py -ErrorAction SilentlyContinue)) {
    $py = "python3"
    if (-not (Get-Command $py -ErrorAction SilentlyContinue)) {
        $py = "python"
    }
}

$extra = @()
if ($EmitContext) { $extra += "--context" }
& $py -m farewell_assistant.cli detect $Path @extra
exit $LASTEXITCODE
