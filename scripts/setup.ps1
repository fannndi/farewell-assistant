# Setup - LLM Mode
# Usage: .\setup.ps1

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"

$MODEL_MAP = @{
    "eco"         = $null
    "on"          = "qwen2.5-coder-1.5b"
    "hot"         = "qwen3.5-0.8b"
    "balance"     = "qwen3.5-2b"
    "performance" = "qwen3.5-4b"
}

$VALID_MODES = $MODEL_MAP.Keys -join ", "
$CURRENT = Get-LLMMode

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host "  LLM Mode Setup" -ForegroundColor Magenta
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host ""
Write-OK "Current mode: $CURRENT"

Write-Step "INPUT" "Select LLM mode"

try {
    $MODE = Read-Host "  Enter mode [$VALID_MODES]"
    $MODE = $MODE.Trim().ToLower()
} catch {
    Write-Fail "Input error: $_"
    exit 1
}

if (-not $MODEL_MAP.ContainsKey($MODE)) {
    Write-Fail "Invalid mode '$MODE'. Valid: $VALID_MODES"
    exit 1
}

$MODEL = $MODEL_MAP[$MODE]

if ($MODE -ne "eco") {
    Write-Step "OLLAMA" "Starting Ollama service"
    if (Start-OllamaService) {
        Write-OK "Ollama is running"
    } else {
        Write-Fail "Could not start Ollama"
        exit 1
    }

    if ($MODEL) {
        Write-Step "MODEL" "Warming up model: $MODEL"
        try {
            $null = ollama run $MODEL --keep-alive 10m 2>&1
            Start-Sleep -Seconds 2
            Write-OK "Model $MODEL ready"
        } catch {
            Write-Fail "Model warm-up failed: $_"
            exit 1
        }
    }
} else {
    Write-Step "ECO" "Stopping running models"
    Stop-OllamaModels
    Write-OK "Models stopped"
}

Write-Step "SAVE" "Writing LLM mode"

$state = @{
    mode       = $MODE
    model      = $MODEL
    updated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")
}
Write-JsonState -Path $script:LLM_MODE_FILE -Data $state
Write-OK "Mode saved: $MODE"

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Green
Write-Host "  LLM mode set to: $MODE" -ForegroundColor Green
if ($MODEL) {
    Write-Host "  Model: $MODEL" -ForegroundColor Green
}
Write-Host "  =================================================" -ForegroundColor Green
Write-Host ""
