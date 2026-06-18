# Common Configuration - Centralized URLs, paths, and constants
# Usage: . "$PSScriptRoot\config.ps1"

if (-not $script:ROOT_DIR) {
    $script:ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
}

# ── URLs ──
$script:OLLAMA_URL = "http://localhost:11434"
$script:API_URL    = "http://localhost:20128"

# ── Directories ──
$script:ECC_DIR       = "$($script:ROOT_DIR)\ecc"
$script:ROUTER_DIR    = "$($script:ROOT_DIR)\9router"
$script:OPENCODE_DIR  = "$env:USERPROFILE\.config\opencode"
$script:OPENCODE_CFG  = "$($script:OPENCODE_DIR)\opencode.jsonc"
$script:MODELS_DIR    = "$($script:ROOT_DIR)\models"
$script:CONTEXT_DIR   = "$($script:ROOT_DIR)\projects\context"

# ── State Files ──
$script:STATE_DIR       = "$($script:ROOT_DIR)\.opencode"
$script:LLM_MODE_FILE   = "$($script:STATE_DIR)\llm-mode.json"
$script:WORK_MODE_FILE  = "$($script:STATE_DIR)\work-mode.json"
$script:COMBO_FILE      = "$($script:STATE_DIR)\combo.json"
$script:REGISTRY_FILE   = "$($script:ROOT_DIR)\projects\registry.json"
$script:SKILL_IDX_FILE  = "$($script:ROOT_DIR)\projects\skill-mode-index.json"
$script:API_KEY_FILE    = "$($script:ROOT_DIR)\api-key.txt"
$script:PROFILE_SRC     = "$($script:ROOT_DIR)\profiles\combo\opencode.jsonc"
