# llm-setup.ps1 — Backward-compat wrapper (delegates to Python)
# Original replaced by farewell_assistant.llm_setup module

param(
    [ValidateSet("eco", "on", "hot", "balance", "performance", "list", "pull", "status", "remove", "auto")]
    [string]$Action = "status",
    [string]$Profile = ""
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

if ($Profile) {
    & $py -m farewell_assistant.cli llm $Action --profile $Profile
} else {
    & $py -m farewell_assistant.cli llm $Action
}
exit $LASTEXITCODE
