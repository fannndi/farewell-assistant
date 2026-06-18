# Common Helpers - Shared functions for all scripts
# Usage: . "$PSScriptRoot\helpers.ps1"

# -- Write Helpers --

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host ""
    Write-Host "[$Step] $Message" -ForegroundColor Cyan
}

function Write-OK {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Skip {
    param([string]$Message)
    Write-Host "  [SKIP] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "  [FAIL] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  [..] $Message" -ForegroundColor Gray
}

# -- JSON State Helpers --

function Read-JsonState {
    param(
        [string]$Path,
        [scriptblock]$Default = { return $null }
    )
    if (-not (Test-Path $Path)) {
        return (& $Default)
    }
    try {
        return Get-Content $Path -Raw | ConvertFrom-Json
    } catch {
        Write-Verbose "Failed to read JSON state: $Path - $_"
        return (& $Default)
    }
}

function Write-JsonState {
    param(
        [string]$Path,
        [object]$Data
    )
    New-Item -ItemType Directory -Path (Split-Path $Path -Parent) -Force | Out-Null
    $Data | ConvertTo-Json -Depth 5 | Set-Content -Path $Path -Encoding UTF8
}

# -- Mode Helpers --

function Get-LLMMode {
    $state = Read-JsonState -Path $script:LLM_MODE_FILE -Default { return @{ mode = "eco"; model = "" } }
    if ($state.mode) { return $state.mode } else { return "eco" }
}

function Get-WorkMode {
    $state = Read-JsonState -Path $script:WORK_MODE_FILE -Default { return @{ mode = "build" } }
    if ($state.mode) { return $state.mode } else { return "build" }
}

function Get-LLMModel {
    $state = Read-JsonState -Path $script:LLM_MODE_FILE -Default { return @{ model = "" } }
    return if ($state.model) { $state.model } else { "" }
}

# -- Ollama Helpers --

function Test-OllamaRunning {
    try {
        $null = Invoke-RestMethod -Uri "$($script:OLLAMA_URL)/api/tags" -TimeoutSec 3 -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Start-OllamaService {
    if (Test-OllamaRunning) { return $true }
    try {
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        return (Test-OllamaRunning)
    } catch {
        Write-Verbose "Failed to start Ollama: $_"
        return $false
    }
}

function Stop-OllamaModels {
    if (-not (Test-OllamaRunning)) { return }
    try {
        $tags = Invoke-RestMethod -Uri "$($script:OLLAMA_URL)/api/tags" -TimeoutSec 5
        if ($tags.models) {
            foreach ($m in $tags.models) {
                ollama stop $m.name 2>$null
            }
        }
    } catch {}
}

# -- 9Router Helpers --

function Get-9RouterPid {
    try {
        if (Test-Path $script:ROUTER_PID_FILE) {
            $pidVal = [int](Get-Content $script:ROUTER_PID_FILE -Raw).Trim()
            $proc = Get-Process -Id $pidVal -ErrorAction SilentlyContinue
            if ($proc -and $proc.ProcessName -eq "node") { return $pidVal }
        }
    } catch {}
    return $null
}

function Stop-9Router {
    $existingPid = Get-9RouterPid
    if ($existingPid) {
        try { Stop-Process -Id $existingPid -Force -ErrorAction Stop; Start-Sleep -Seconds 1 } catch {}
    }
    # Fallback: kill whatever owns port 20128 (precision, not regex over all node.exe)
    try {
        $conns = Get-NetTCPConnection -LocalPort 20128 -State Listen -ErrorAction SilentlyContinue
        foreach ($c in $conns) {
            if ($c.OwningProcess -and $c.OwningProcess -ne 0) {
                $proc = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
                if ($proc -and $proc.ProcessName -eq "node") {
                    Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Seconds 1
                }
            }
        }
    } catch {}
    if (Test-Path $script:ROUTER_PID_FILE) {
        Remove-Item $script:ROUTER_PID_FILE -Force -ErrorAction SilentlyContinue
    }
}

function Start-9Router {
    if (-not (Test-Path "$($script:ROUTER_DIR)\.next\standalone\server.js")) {
        Write-Fail "9Router standalone build missing. Run: .\scripts\owner.ps1"
        return $false
    }

    # Kill stale instance first (precision by PID + port, no regex false-positives)
    Stop-9Router

    # Ensure static assets present in standalone build
    if (-not (Test-Path "$($script:ROUTER_DIR)\.next\standalone\.next\static")) {
        if (Test-Path "$($script:ROUTER_DIR)\.next\static") {
            Copy-Item -Path "$($script:ROUTER_DIR)\.next\static" -Destination "$($script:ROUTER_DIR)\.next\standalone\.next\static" -Recurse -Force
        }
    }

    # Logs dir for stdout/stderr (autostart + manual start share this)
    New-Item -ItemType Directory -Path $script:LOG_DIR -Force | Out-Null
    $logOut = "$($script:LOG_DIR)\9router.log"
    $logErr = "$($script:LOG_DIR)\9router-error.log"

    $env:PORT = "20128"
    $env:NODE_ENV = "production"
    $env:DATA_DIR = "$env:USERPROFILE\AppData\Roaming\9router"
    $env:INITIAL_PASSWORD = if ($env:9ROUTER_PASSWORD) { $env:9ROUTER_PASSWORD } else { "" }

    $startArgs = @{
        FilePath               = "node"
        ArgumentList           = ".next/standalone/server.js"
        WorkingDirectory       = $script:ROUTER_DIR
        WindowStyle            = "Hidden"
        RedirectStandardOutput = $logOut
        RedirectStandardError  = $logErr
        PassThru               = $true
    }
    $proc = Start-Process @startArgs
    if ($proc -and $proc.Id) {
        Set-Content -Path $script:ROUTER_PID_FILE -Value $proc.Id -Encoding UTF8
    }

    # Health-check with backoff: 2s, 3s, 5s, 8s, 12s, 15s (max ~45s)
    # First /api/health hit on a cold Next.js standalone build triggers route
    # compilation, so the first request can take several seconds -- use 10s
    # timeout per probe (not 2s) to avoid false-negative on slow cold start.
    $waits = @(2, 3, 5, 8, 12, 15)
    $total = 0
    foreach ($w in $waits) {
        Start-Sleep -Seconds $w
        $total += $w
        try {
            $null = Invoke-RestMethod -Uri "$($script:API_URL)/api/health" -TimeoutSec 10 -ErrorAction Stop
            Write-OK "9Router started (${total}s, PID: $($proc.Id))"
            return $true
        } catch {}
    }
    Write-Fail "9Router not reachable after ${total}s (see $($script:LOG_DIR)\9router-error.log)"
    return $false
}

# -- GPU Helpers --

function Get-GPUInfo {
    param([string]$Fields = "utilization.gpu,memory.used,memory.total")
    try {
        $gpuRaw = nvidia-smi --query-gpu=$Fields --format=csv,noheader 2>$null
        if ($gpuRaw) {
            $parts = $gpuRaw.Trim() -split ','
            $result = @{ available = $true }
            foreach ($part in $parts) {
                $p = $part.Trim()
                if ($p -match '^\d+(\.\d+)?\s*%$') {
                    $result.utilization = [int]($p.Replace(' %',''))
                } elseif ($p -match '^\d+\s*MiB$') {
                    if (-not $result.memory_used) {
                        $result.memory_used = [int]($p.Replace(' MiB',''))
                    } else {
                        $result.memory_total = [int]($p.Replace(' MiB',''))
                    }
                } elseif ($p -match '^\d+\s*C$') {
                    $result.temperature = [int]($p.Replace(' C',''))
                } elseif ($p -notmatch '^\d') {
                    $result.name = $p
                }
            }
            if (-not $result.ContainsKey('utilization')) { $result.utilization = 0 }
            if (-not $result.ContainsKey('memory_used')) { $result.memory_used = 0 }
            if (-not $result.ContainsKey('memory_total')) { $result.memory_total = 0 }
            return $result
        }
    } catch {}
    return @{ available = $false; utilization = 0; memory_used = 0; memory_total = 0 }
}

# -- Token Estimation (multi-language aware) --

function Estimate-Tokens {
    param([string]$Text)
    if (-not $Text) { return 0 }
    $tokens = 0
    foreach ($char in $Text.ToCharArray()) {
        $code = [int]$char
        if (($code -ge 0x4E00 -and $code -le 0x9FFF) -or
            ($code -ge 0x3040 -and $code -le 0x309F) -or
            ($code -ge 0x30A0 -and $code -le 0x30FF) -or
            ($code -ge 0xAC00 -and $code -le 0xD7AF) -or
            ($code -ge 0x3400 -and $code -le 0x4DBF)) {
            $tokens += 1
        } elseif ($code -lt 0x30 -or ($code -ge 0x2000 -and $code -le 0x206F)) {
            $tokens += 0.5
        } else {
            $tokens += 0.25
        }
    }
    return [math]::Max(1, [math]::Ceiling($tokens))
}

# -- LLM Call --

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

# -- Smart Enrichment --

function Invoke-LLMEnrich {
    param(
        [string]$Text,
        [string]$Context,
        [string]$System,
        [int]$MaxTokens = 256,
        [switch]$Force
    )

    $mode = Get-LLMMode
    if ($mode -eq "eco" -and -not $Force) { return $Text }

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
        $System = if ($Context) {
            "You are a universal input preprocessor. Given input and context, return enriched output with domain detection, stack detection, and feature extraction."
        } else {
            "You are a universal input preprocessor. Return enriched version of the input with key details extracted."
        }
    }

    $prompt = if ($Context) { "Context: $Context`n`nInput: $Text" } else { $Text }
    $tokens = if ($mode -eq "on") { 200 } else { 100 }
    $timeout = if ($mode -eq "on") { 45 } else { 30 }

    $result = Invoke-LLM -Prompt $prompt -System $System -MaxTokens $tokens -Temperature 0.3 -TimeoutSec $timeout
    if (-not $result) { return $Text }

    return $result.response.Trim()
}
