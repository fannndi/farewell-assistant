# Test Helper — Bootstrap test environment
$script:ROOT_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
. "$PSScriptRoot\..\scripts\common\config.ps1"
. "$PSScriptRoot\..\scripts\common\helpers.ps1"
. "$PSScriptRoot\..\scripts\common\enrichment-pipeline.ps1"
. "$PSScriptRoot\..\scripts\common\skill-chain.ps1"
. "$PSScriptRoot\..\scripts\common\intent-router.ps1"
