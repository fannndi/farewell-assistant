# LLM Adapter - Ollama CLI Wrapper
# Source for functions: . .\llm-adapter.ps1
# Direct: .\llm-adapter.ps1 -Prompt "your text"

param(
    [string]$Prompt,
    [string]$Model,
    [string]$System,
    [int]$MaxTokens = 1024,
    [double]$Temperature = 0.3,
    [int]$TimeoutSec = 60
)

$ErrorActionPreference = "Continue"
. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"

$script:SessionTokens = 0

# ============================================================
# Status Update
# ============================================================

function Update-LLMStatus {
    param([string]$Model, [int]$Tokens, [double]$TokensPerSecond)

    $mode = Get-LLMMode
    $gpu = Get-GPUInfo

    $status = @{
        mode = $mode.ToUpper()
        model = $Model
        last_tokens = $Tokens
        session_tokens = $script:SessionTokens
        tokens_per_second = $TokensPerSecond
        gpu_available = $gpu.available
        gpu_utilization = $gpu.utilization
        gpu_memory_used = $gpu.memory_used
        gpu_memory_total = $gpu.memory_total
        last_updated = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    }

    try {
        Write-JsonState -Path "$($script:STATE_DIR)\llm-status.json" -Data $status
    } catch {}
}

# Override Invoke-LLM from helpers to add tracking
function Invoke-LLM {
    param(
        [string]$Prompt,
        [string]$System = "You are a helpful assistant.",
        [string]$Model,
        [int]$MaxTokens = 1024,
        [double]$Temperature = 0.3,
        [int]$TimeoutSec = 60
    )

    if (-not $Model) { $Model = Get-LLMModel }
    if (-not $Model) { return $null }

    $messages = @()
    if ($System) { $messages += @{ role = "system"; content = $System } }
    $messages += @{ role = "user"; content = $Prompt }

    $body = @{
        model = $Model
        messages = $messages
        stream = $false
        keep_alive = "5m"
        think = $false
        options = @{
            num_predict = $MaxTokens
            temperature = $Temperature
            num_gpu = 99
        }
    } | ConvertTo-Json -Depth 5 -Compress

    try {
        $start = Get-Date
        $response = Invoke-RestMethod -Uri "$($script:OLLAMA_URL)/api/chat" -Method POST -Body $body -ContentType "application/json" -TimeoutSec $TimeoutSec
        $elapsed = ((Get-Date) - $start).TotalSeconds

        if ($response.message.content) {
            $tokens = $response.eval_count
            if (-not $tokens) { $tokens = Estimate-Tokens $response.message.content }
            $tps = if ($elapsed -gt 0) { [math]::Round($tokens / $elapsed, 2) } else { 0 }

            $script:SessionTokens += $tokens
            Update-LLMStatus -Model $Model -Tokens $tokens -TokensPerSecond $tps

            return @{
                response = $response.message.content
                tokens = $tokens
                duration = $elapsed
                tokens_per_second = $tps
            }
        }
    } catch {
        Write-Verbose "LLM call failed: $_"
    }

    return $null
}

# ============================================================
# Direct Execution Mode
# ============================================================

if ($Prompt) {
    $result = Invoke-LLM -Prompt $Prompt -System $System -Model $Model -MaxTokens $MaxTokens -Temperature $Temperature -TimeoutSec $TimeoutSec
    if ($result) {
        Write-Host $result.response
        Write-Host ""
        Write-Host "  Tokens: $($result.tokens) | $($result.tokens_per_second) tok/s | $([math]::Round($result.duration, 1))s" -ForegroundColor Gray
    } else {
        Write-Host "  [ERROR] LLM call failed" -ForegroundColor Red
    }
}
