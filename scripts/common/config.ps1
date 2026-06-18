# Common Configuration - Centralized URLs, paths, and constants
# Usage: . "$PSScriptRoot\config.ps1"
#
# ROOT_DIR is resolved deterministically from this file's location:
#   scripts/common/config.ps1 -> up two levels -> project root.
# This avoids $MyInvocation fragility under nested dot-source.

if (-not $script:ROOT_DIR) {
    $script:ROOT_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

# -- URLs (configurable via env vars) --
$script:OLLAMA_PORT = $env:OLLAMA_PORT ?? "11434"
$script:ROUTER_PORT = $env:ROUTER_PORT ?? "20128"
$script:OLLAMA_URL = "http://localhost:$($script:OLLAMA_PORT)"
$script:API_URL    = "http://localhost:$($script:ROUTER_PORT)"

# -- Directories --
$script:ECC_DIR       = "$($script:ROOT_DIR)\ecc"
$script:ROUTER_DIR    = "$($script:ROOT_DIR)\9router"
$script:OPENCODE_DIR  = "$env:USERPROFILE\.config\opencode"
$script:OPENCODE_CFG  = "$($script:OPENCODE_DIR)\opencode.jsonc"
$script:MODELS_DIR    = "$($script:ROOT_DIR)\models"
$script:CONTEXT_DIR   = "$($script:ROOT_DIR)\projects\context"

# -- State Files --
$script:STATE_DIR       = "$($script:ROOT_DIR)\.opencode"
$script:LOG_DIR         = "$($script:STATE_DIR)\logs"
$script:ROUTER_PID_FILE = "$($script:STATE_DIR)\9router.pid"
$script:LLM_MODE_FILE   = "$($script:STATE_DIR)\llm-mode.json"
$script:WORK_MODE_FILE  = "$($script:STATE_DIR)\work-mode.json"
$script:COMBO_FILE      = "$($script:STATE_DIR)\combo.json"
$script:REGISTRY_FILE   = "$($script:ROOT_DIR)\projects\registry.json"
$script:SKILL_IDX_FILE  = "$($script:ROOT_DIR)\projects\skill-mode-index.json"
$script:API_KEY_FILE    = "$($script:ROOT_DIR)\api-key.txt"
$script:PROFILE_SRC     = "$($script:ROOT_DIR)\profiles\combo\opencode.jsonc"

# -- Scheduled Task --
$script:TASK_NAME       = "FarewellAssistant-9Router"
$script:TASK_BG_SCRIPT  = "$($script:ROOT_DIR)\scripts\common\start-9router-bg.ps1"
