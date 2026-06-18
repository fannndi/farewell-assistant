# LLM Mode - Operating Mode Switch
# Usage:
#   .\llm-mode.ps1 eco            → no LLM, zero GPU
#   .\llm-mode.ps1 on             → use default eco model
#   .\llm-mode.ps1 hot            → hot profile (qwen3.5:0.8b)
#   .\llm-mode.ps1 balance        → balance profile (qwen3.5:2b)
#   .\llm-mode.ps1 performance    → performance profile (qwen3.5:4b)
#   .\llm-mode.ps1 status         → show current mode

param(
    [ValidateSet("eco", "on", "hot", "balance", "performance", "status")]
    [string]$Action = "status"
)

$ErrorActionPreference = "Stop"

. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"

$MODEL_MAP = @{
    "eco"         = $null
    "on"          = "qwen2.5-coder-1.5b"
    "hot"         = "qwen3.5-0.8b"
    "balance"     = "qwen3.5-2b"
    "performance" = "qwen3.5-4b"
}

$VRAM_MAP = @{
    "eco"         = "0"
    "on"          = "~1GB"
    "hot"         = "~600MB"
    "balance"     = "~1.4GB"
    "performance" = "~2.5GB"
}

function Set-LLMMode {
    param([string]$Mode, [string]$Model)
    Write-JsonState -Path $script:LLM_MODE_FILE -Data ([PSCustomObject]@{
        mode = $Mode
        model = if ($Model) { $Model } else { "" }
        updated_at = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
    })
}

function Invoke-Warmup {
    param([string]$ModelName)
    try {
        $body = @{
            model = $ModelName
            messages = @(@{ role = "user"; content = "ok" })
            stream = $false
            keep_alive = "5m"
            options = @{ num_predict = 2; num_gpu = 99 }
        } | ConvertTo-Json -Depth 5 -Compress
        $null = Invoke-RestMethod -Uri "$($script:OLLAMA_URL)/api/chat" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 120 -ErrorAction SilentlyContinue
    } catch {}
}

# ============================================================
# Execute
# ============================================================

switch ($Action) {
    "eco" {
        Set-LLMMode -Mode "eco" -Model $null
        Stop-OllamaModels
        Write-Host "  [MODE] ECO — no LLM, zero GPU usage" -ForegroundColor Green
    }

    { $_ -in "on", "hot", "balance", "performance" } {
        $model = $MODEL_MAP[$Action]
        if (-not (Test-OllamaRunning)) {
            Write-Host "  [MODE] Ollama not running. Starting..." -ForegroundColor Yellow
            Start-OllamaService | Out-Null
        }
        Set-LLMMode -Mode $Action -Model $model
        Write-Host "  [MODE] Loading $model to GPU..." -ForegroundColor Gray
        Invoke-Warmup -ModelName $model
        $color = switch ($Action) { "on" { "Cyan" } "hot" { "Red" } "balance" { "Yellow" } "performance" { "Magenta" } default { "White" } }
        Write-Host "  [MODE] $($Action.ToUpper()) — $model ($($VRAM_MAP[$Action]))" -ForegroundColor $color
    }

    "status" {
        $mode = Get-LLMMode
        $model = $MODEL_MAP[$mode]
        if (-not $model) { $model = "none" }
        $running = Test-OllamaRunning
        $label = $mode.ToUpper()
        $color = switch ($mode) {
            "eco" { "Green" }
            "on" { "Cyan" }
            "hot" { "Red" }
            "balance" { "Yellow" }
            "performance" { "Magenta" }
            default { "White" }
        }

        Write-Host ""
        Write-Host "  Mode:     $label" -ForegroundColor $color
        Write-Host "  Model:    $model" -ForegroundColor White
        Write-Host "  VRAM:     $($VRAM_MAP[$mode])" -ForegroundColor Gray
        Write-Host "  Ollama:   $(if ($running) { 'Running' } else { 'Stopped' })" -ForegroundColor $(if ($running) { "Green" } else { "Red" })

        if ($running) {
            try {
                $tags = Invoke-RestMethod -Uri "$($script:OLLAMA_URL)/api/tags" -TimeoutSec 5
                if ($tags.models) {
                    Write-Host "  Models:" -ForegroundColor Gray
                    foreach ($m in $tags.models) {
                        $size = [math]::Round($m.size / 1GB, 2)
                        Write-Host "    $($m.name) ($size GB)" -ForegroundColor Gray
                    }
                }
            } catch {}
        }
        Write-Host ""
    }
}
