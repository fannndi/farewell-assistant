# LLM Adapter - Ollama API Wrapper with Smart Enrichment
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
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$MODE_FILE = "$ROOT_DIR\.opencode\llm-mode.json"
$STATUS_FILE = "$ROOT_DIR\.opencode\llm-status.json"
$OLLAMA_URL = "http://localhost:11434"

$script:SessionTokens = 0

# ============================================================
# Token Estimation (multi-language aware)
# ============================================================

function Estimate-Tokens {
    param([string]$Text)
    if (-not $Text) { return 0 }
    $tokens = 0
    foreach ($char in $Text.ToCharArray()) {
        $code = [int]$char
        # CJK characters = 1 token each
        if (($code -ge 0x4E00 -and $code -le 0x9FFF) -or
            ($code -ge 0x3040 -and $code -le 0x309F) -or
            ($code -ge 0x30A0 -and $code -le 0x30FF) -or
            ($code -ge 0xAC00 -and $code -le 0xD7AF) -or
            ($code -ge 0x3400 -and $code -le 0x4DBF)) {
            $tokens += 1
        }
        # Symbols and punctuation = ~0.5 token each (counted in pairs)
        elseif ($code -lt 0x30 -or ($code -ge 0x2000 -and $code -le 0x206F)) {
            $tokens += 0.5
        }
        # Regular ASCII = ~0.25 token each (4 chars per token)
        else {
            $tokens += 0.25
        }
    }
    return [math]::Max(1, [math]::Ceiling($tokens))
}

# ============================================================
# Mode Helpers
# ============================================================

function Get-OperatingMode {
    if (-not (Test-Path $MODE_FILE)) { return "eco" }
    try {
        $state = Get-Content $MODE_FILE -Raw | ConvertFrom-Json
        return $state.mode
    } catch { return "eco" }
}

function Get-LLMModel {
    if (Test-Path $MODE_FILE) {
        try {
            $state = Get-Content $MODE_FILE -Raw | ConvertFrom-Json
            if ($state.model) { return $state.model }
        } catch {}
    }
    return "qwen2.5:1.5b-s"
}

# ============================================================
# GPU Info
# ============================================================

function Get-GPUInfo {
    try {
        $gpuRaw = nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader 2>$null
        if ($gpuRaw) {
            $parts = $gpuRaw.Trim() -split ','
            return @{
                available = $true
                utilization = [int]($parts[0].Trim().Replace(' %',''))
                memory_used = [int]($parts[1].Trim().Replace(' MiB',''))
                memory_total = [int]($parts[2].Trim().Replace(' MiB',''))
            }
        }
    } catch {}
    return @{ available = $false; utilization = 0; memory_used = 0; memory_total = 0 }
}

# ============================================================
# Status Update
# ============================================================

function Update-LLMStatus {
    param([string]$Model, [int]$Tokens, [double]$TokensPerSecond)

    $mode = Get-OperatingMode
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
        New-Item -ItemType Directory -Path (Split-Path $STATUS_FILE -Parent) -Force | Out-Null
        $status | ConvertTo-Json -Depth 3 | Set-Content -Path $STATUS_FILE -Encoding UTF8
    } catch {}
}

# ============================================================
# Core LLM Call
# ============================================================

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

    $messages = @()
    if ($System) { $messages += @{ role = "system"; content = $System } }
    $messages += @{ role = "user"; content = $Prompt }

    $body = @{
        model = $Model
        messages = $messages
        stream = $false
        keep_alive = "5m"
        options = @{
            num_predict = $MaxTokens
            temperature = $Temperature
            num_gpu = 99
        }
    } | ConvertTo-Json -Depth 5 -Compress

    try {
        $start = Get-Date
        $response = Invoke-RestMethod -Uri "$OLLAMA_URL/api/chat" -Method POST -Body $body -ContentType "application/json" -TimeoutSec $TimeoutSec
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
# Smart Enrichment
# ============================================================

function Invoke-LLMEnrich {
    param(
        [string]$Text,
        [string]$Context,
        [string]$System,
        [int]$MaxTokens = 256,
        [switch]$Force
    )

    $mode = Get-OperatingMode
    if ($mode -eq "eco" -and -not $Force) { return $Text }

    # Smart skip: short input, simple questions
    if (-not $Force) {
        $skipKeywords = @("apa itu", "jelaskan", "what is", "how to", "hai", "ok", "thanks", "oke", "baik")
        $inputLower = $Text.ToLower().Trim()
        $wordCount = ($Text -split '\s+').Count
        if ($wordCount -lt 5) { return $Text }
        foreach ($kw in $skipKeywords) {
            if ($inputLower -match [regex]::Escape($kw)) { return $Text }
        }
    }

    if (-not $System) {
        if ($Context) {
            $System = "You are a universal input preprocessor. Given input and context, return enriched output with domain detection, stack detection, and feature extraction."
        } else {
            $System = "You are a universal input preprocessor. Return enriched version of the input with key details extracted."
        }
    }

    $prompt = if ($Context) { "Context: $Context`n`nInput: $Text" } else { $Text }
    $tokens = if ($mode -eq "on") { 200 } else { 100 }
    $timeout = if ($mode -eq "on") { 45 } else { 30 }

    $result = Invoke-LLM -Prompt $prompt -System $System -MaxTokens $tokens -Temperature 0.3 -TimeoutSec $timeout
    if (-not $result) { return $Text }

    $enriched = $result.response.Trim()
    return $enriched
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
