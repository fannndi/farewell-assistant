# Pipeline Trigger - Silent wrapper to invoke intent router per-turn
# Usage: .\scripts\common\trigger-pipeline.ps1 -Input "user input"
# Called by AI at start of each turn. Writes pipeline-result.json + context.md.

param([string]$InputText = "")

$ErrorActionPreference = "Continue"
$script:ROOT_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

. "$PSScriptRoot\config.ps1"
. "$PSScriptRoot\helpers.ps1"
. "$PSScriptRoot\enrichment-pipeline.ps1"
. "$PSScriptRoot\skill-chain.ps1"
. "$PSScriptRoot\intent-router.ps1"

if (-not $InputText) {
    $InputText = "session start"
    $mode = Get-LLMMode
    if ($mode -eq "eco") { $InputText = "startup" }
}

$result = Invoke-IntentRouter -TextInput $InputText -Force
if ($result.success -and $result.intent) {
    exit 0
}
exit 1
