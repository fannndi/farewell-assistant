# Run Router — Entry script for OpenCode plugin
# Dot-sources all pipeline modules and runs Invoke-IntentRouter.
# Called by .opencode/plugins/intent-router.js on chat.message hook.
# Usage: .\scripts\run-router.ps1 -InputText "<user message>"

param([string]$InputText)

$ErrorActionPreference = "Continue"
$script:ROOT_DIR = Split-Path -Parent $PSScriptRoot

. "$PSScriptRoot\common\config.ps1"
. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\enrichment-pipeline.ps1"
. "$PSScriptRoot\common\skill-chain.ps1"
. "$PSScriptRoot\common\intent-router.ps1"

$result = Invoke-IntentRouter -TextInput $InputText -Force
exit 0
