<#
.SYNOPSIS
    LLM configuration script - merge of llm-mode.ps1 and llm-models.ps1
.DESCRIPTION
    Manages LLM modes, model profiles, Ollama services, and GPU detection.
    Supports eco/on/hot/balance/performance modes with automatic GPU-aware profiling.
.PARAMETER Action
    The action to perform: eco, on, hot, balance, performance, list, pull, status, remove, auto
.PARAMETER Profile
    Profile name for pull action. If empty, operates on all profiles.
.EXAMPLE
    .\llm-setup.ps1 -Action eco
    .\llm-setup.ps1 -Action pull -Profile hot
    .\llm-setup.ps1 -Action auto
#>

param(
    [ValidateSet("eco", "on", "hot", "balance", "performance", "list", "pull", "status", "remove", "auto")]
    [string]$Action = "status",
    [string]$Profile = ""
)

$ErrorActionPreference = "Stop"
$script:ROOT_DIR = Split-Path -Parent $PSScriptRoot

. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"
. "$PSScriptRoot\common\log.ps1"

$PROFILES = [ordered]@{
    "hot" = @{
        model = "qwen3.5-0.8b"; vram = "~600MB"; condition = "Outdoor, unplugged, high temp"
        hf_repo = "unsloth/Qwen3.5-0.8B-GGUF"; hf_file = "Qwen3.5-0.8B-Q4_K_M.gguf"
        modelfile = "$($script:ROOT_DIR)\Modelfile.qwen3.5-0.8b"; size_gb = 0.5
    }
    "eco" = @{
        model = "qwen2.5-coder-1.5b"; vram = "~1GB"; condition = "Indoor, unplugged"
        hf_repo = "Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF"; hf_file = "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
        modelfile = "$($script:ROOT_DIR)\Modelfile.qwen2.5-coder-1.5b"; size_gb = 1.0
    }
    "balance" = @{
        model = "qwen3.5-2b"; vram = "~1.4GB"; condition = "Indoor, plugged, AC"
        hf_repo = "unsloth/Qwen3.5-2B-GGUF"; hf_file = "Qwen3.5-2B-Q4_K_M.gguf"
        modelfile = "$($script:ROOT_DIR)\Modelfile.qwen3.5-2b"; size_gb = 1.4
    }
    "performance" = @{
        model = "qwen3.5-4b"; vram = "~2.5GB"; condition = "Indoor, plugged, fan active"
        hf_repo = "unsloth/Qwen3.5-4B-GGUF"; hf_file = "Qwen3.5-4B-Q4_K_M.gguf"
        modelfile = "$($script:ROOT_DIR)\Modelfile.qwen3.5-4b"; size_gb = 2.5
    }
}

$VRAM_MAP = [ordered]@{
    "hot"          = 600
    "eco"          = 1024
    "balance"      = 1433
    "performance"  = 2560
}

$MODEL_MAP = [ordered]@{
    "eco"          = "qwen2.5-coder-1.5b"
    "on"           = "qwen2.5-coder-1.5b"
    "hot"          = "qwen3.5-0.8b"
    "balance"      = "qwen3.5-2b"
    "performance"  = "qwen3.5-4b"
}

function Set-LLMMode {
    param([string]$Mode)
    $state = Read-JsonState -Path $script:LLM_MODE_FILE -Default { return @{} }
    if (-not $state) { $state = @{} }
    $state["mode"] = $Mode
    $state["updated_at"] = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")
    $model = $MODEL_MAP[$Mode]
    if ($model) { $state["model"] = $model }
    Write-JsonState -Path $script:LLM_MODE_FILE -Data $state
    if (Get-Command Sync-SessionState -ErrorAction SilentlyContinue) {
        Sync-SessionState
    }
    if (Get-Command Write-TaskLog -ErrorAction SilentlyContinue) {
        Write-TaskLog -Stage "LLM" -Action "Set mode to $Mode" -Result "success"
    }
}

function Get-GGUFPath {
    param([string]$ProfileName)
    $p = $PROFILES[$ProfileName]
    if (-not $p) { return $null }
    return "$($script:ROOT_DIR)\models\$($p.hf_file)"
}

function Get-ModelfileContent {
    param(
        [string]$ProfileName,
        [string]$GGUFRelativePath
    )
    $p = $PROFILES[$ProfileName]
    $templatePath = $p.modelfile
    if (Test-Path -LiteralPath $templatePath) {
        $content = Get-Content -LiteralPath $templatePath -Raw
        $content = $content -replace '\.gguf$', $GGUFRelativePath
        return $content
    }
    return @"
FROM $GGUFRelativePath
TEMPLATE "{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
"@
}

function Invoke-DownloadGGUF {
    param([string]$ProfileName)
    $p = $PROFILES[$ProfileName]
    if (-not $p) {
        Write-Fail "Unknown profile '$ProfileName'"
        return $false
    }

    $outDir = "$($script:ROOT_DIR)\models"
    if (-not (Test-Path -LiteralPath $outDir)) {
        New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    }

    $outFile = "$outDir\$($p.hf_file)"
    if (Test-Path -LiteralPath $outFile) {
        Write-Skip "GGUF already exists: $($p.hf_file)"
        return $true
    }

    $url = "https://huggingface.co/$($p.hf_repo)/resolve/main/$($p.hf_file)"
    Write-Step "Downloading $($p.model) ($($p.hf_file))..."
    Write-Info "  URL: $url"
    Write-Info "  Size: ~$($p.size_gb)GB"

    $tempFile = "$env:TEMP\$($p.hf_file)"
    $proc = Start-Process -FilePath "curl.exe" -ArgumentList "-L", "-o", "`"$tempFile`"", "`"$url`"" -NoNewWindow -PassThru -Wait
    if ($proc.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $tempFile)) {
        Write-Fail "Download failed (exit code: $($proc.ExitCode))"
        return $false
    }

    Move-Item -LiteralPath $tempFile -Destination $outFile -Force
    Write-OK "Downloaded to $outFile"
    return $true
}

function Invoke-ImportToOllama {
    param([string]$ProfileName)
    $p = $PROFILES[$ProfileName]
    if (-not $p) {
        Write-Fail "Unknown profile '$ProfileName'"
        return $false
    }

    $ggufPath = Get-GGUFPath -ProfileName $ProfileName
    if (-not (Test-Path -LiteralPath $ggufPath)) {
        Write-Fail "GGUF not found: $ggufPath"
        return $false
    }

    $existing = & ollama list 2>$null | Select-String -Pattern "^$($p.model)\s"
    if ($existing) {
        Write-Skip "Model '$($p.model)' already exists in Ollama"
        return $true
    }

    Write-Step "Importing $($p.model) into Ollama..."

    $ggufRelative = ".\models\$($p.hf_file)"
    $modelfileContent = Get-ModelfileContent -ProfileName $ProfileName -GGUFRelativePath $ggufRelative

    $modelfilePath = "$env:TEMP\Modelfile.$($p.model)"
    $modelfileContent | Set-Content -LiteralPath $modelfilePath -Encoding UTF8

    $proc = Start-Process -FilePath "ollama" -ArgumentList "create", $p.model, "-f", "`"$modelfilePath`"" -NoNewWindow -PassThru -Wait
    Remove-Item -LiteralPath $modelfilePath -Force -ErrorAction SilentlyContinue

    if ($proc.ExitCode -ne 0) {
        Write-Fail "Import failed (exit code: $($proc.ExitCode))"
        return $false
    }

    Write-OK "Imported '$($p.model)' into Ollama"
    return $true
}

function Stop-OllamaModels {
    $running = & ollama ps 2>$null
    if ($running -and $running -notmatch "NAME") {
        Write-Step "Stopping all Ollama models..."
        & ollama ps 2>$null | Select-Object -Skip 1 | ForEach-Object {
            $modelName = ($_ -split '\s+')[0]
            if ($modelName) {
                & ollama stop $modelName 2>$null
                Write-OK "Stopped $modelName"
            }
        }
    } else {
        Write-Skip "No running models"
    }
}

function Invoke-AutoMode {
    Write-Step "Detecting GPU hardware..."
    $gpuInfo = Get-GPUInfo -Fields "name,memory.total,temperature.gpu"

    if (-not $gpuInfo -or (-not $gpuInfo.name -and -not $gpuInfo.'memory.total')) {
        Write-Fail "No GPU detected"
        Write-Step "Setting mode to eco (no LLM)..."
        Set-LLMMode -Mode "eco"
        Write-OK "[MODE] ECO - no LLM, zero GPU usage"
        return
    }

    Write-Info "  GPU: $($gpuInfo.name)"
    $vramMB = 0
    if ($gpuInfo.'memory.total') {
        if ($gpuInfo.'memory.total' -match '(\d+)\s*MB') {
            $vramMB = [int]$Matches[1]
        } elseif ($gpuInfo.'memory.total' -match '(\d+)\s*GB') {
            $vramMB = [int]$Matches[1] * 1024
        } else {
            $vramMB = [int]$gpuInfo.'memory.total'
        }
    }
    Write-Info "  VRAM: ~${vramMB}MB"

    if ($gpuInfo.'temperature.gpu') {
        Write-Info "  Temp: $($gpuInfo.'temperature.gpu')C"
    }

    if ($vramMB -lt 1024) {
        Write-Info "Recommendation: hot (qwen3.5-0.8b, ~600MB)"
        Write-Step "Switch to hot profile?"
        $response = Read-Host "  [y/N]"
        if ($response -eq "y" -or $response -eq "Y") {
            $downloaded = Invoke-DownloadGGUF -ProfileName "hot"
            if (-not $downloaded) { return }
            $imported = Invoke-ImportToOllama -ProfileName "hot"
            if (-not $imported) { return }
            Write-Step "Setting mode to hot..."
            Set-LLMMode -Mode "hot"
            Write-OK "[MODE] HOT - qwen3.5-0.8b, ~600MB VRAM"
        } else {
            Write-Skip "Skipped profile switch"
        }
    } elseif ($vramMB -lt 2048) {
        Write-Info "Recommendation: balance (qwen3.5-2b, ~1.4GB)"
        Write-Step "Switch to balance profile?"
        $response = Read-Host "  [y/N]"
        if ($response -eq "y" -or $response -eq "Y") {
            $downloaded = Invoke-DownloadGGUF -ProfileName "balance"
            if (-not $downloaded) { return }
            $imported = Invoke-ImportToOllama -ProfileName "balance"
            if (-not $imported) { return }
            Write-Step "Setting mode to balance..."
            Set-LLMMode -Mode "balance"
            Write-OK "[MODE] BALANCE - qwen3.5-2b, ~1.4GB VRAM"
        } else {
            Write-Skip "Skipped profile switch"
        }
    } else {
        Write-Info "Recommendation: performance (qwen3.5-4b, ~2.5GB)"
        Write-Step "Switch to performance profile?"
        $response = Read-Host "  [y/N]"
        if ($response -eq "y" -or $response -eq "Y") {
            $downloaded = Invoke-DownloadGGUF -ProfileName "performance"
            if (-not $downloaded) { return }
            $imported = Invoke-ImportToOllama -ProfileName "performance"
            if (-not $imported) { return }
            Write-Step "Setting mode to performance..."
            Set-LLMMode -Mode "performance"
            Write-OK "[MODE] PERFORMANCE - qwen3.5-4b, ~2.5GB VRAM"
        } else {
            Write-Skip "Skipped profile switch"
        }
    }
}

function Invoke-ListProfiles {
    Write-Step "LLM Profiles"
    Write-Info ""

    $headers = "Profile", "Model", "VRAM", "Condition", "GGUF Status", "Ollama Status"
    $rows = @()

    foreach ($name in $PROFILES.Keys) {
        $p = $PROFILES[$name]
        $ggufPath = Get-GGUFPath -ProfileName $name
        $ggufStatus = if (Test-Path -LiteralPath $ggufPath) { "Downloaded" } else { "Not downloaded" }

        $ollamaStatus = "Not loaded"
        $ollamaList = & ollama list 2>$null
        if ($ollamaList -and ($ollamaList | Select-String -Pattern "^$($p.model)\s")) {
            $ollamaStatus = "Loaded"
        }

        $rows += [PSCustomObject]@{
            Profile       = $name
            Model         = $p.model
            VRAM          = $p.vram
            Condition     = $p.condition
            "GGUF Status" = $ggufStatus
            "Ollama Status" = $ollamaStatus
        }
    }

    $rows | Format-Table -AutoSize | Out-String | Write-Info

    if (Get-Command Get-GPUInfo -ErrorAction SilentlyContinue) {
        $gpu = Get-GPUInfo
        if ($gpu) {
            Write-Info "GPU Info: $($gpu | Out-String)"
        }
    }
}

# --- Main dispatch ---

switch ($Action) {
    "eco" {
        Write-Step "Setting mode to eco..."
        Set-LLMMode -Mode "eco"
        Stop-OllamaModels
        Write-OK "[MODE] ECO - no LLM, zero GPU usage"
    }

    "on" {
        Write-Step "Setting mode to on..."
        if (-not (Test-OllamaRunning)) {
            Start-OllamaService
        }
        $model = $MODEL_MAP["on"]
        $existing = & ollama list 2>$null | Select-String -Pattern "^$model\s"
        if (-not $existing) {
            Write-Step "Pulling default model $model..."
            & ollama pull $model 2>$null
        }
        Set-LLMMode -Mode "on"
        Write-OK "[MODE] ON - LLM active, GPU-enabled"
    }

    "hot" {
        Write-Step "Setting mode to hot..."
        if (-not (Test-OllamaRunning)) {
            Start-OllamaService
        }
        $model = $MODEL_MAP["hot"]
        Write-Step "Warming up $model..."
        & ollama run $model "" 2>$null
        Set-LLMMode -Mode "hot"
        Write-OK "[MODE] HOT - qwen3.5-0.8b, ~600MB VRAM"
    }

    "balance" {
        Write-Step "Setting mode to balance..."
        if (-not (Test-OllamaRunning)) {
            Start-OllamaService
        }
        $model = $MODEL_MAP["balance"]
        Write-Step "Warming up $model..."
        & ollama run $model "" 2>$null
        Set-LLMMode -Mode "balance"
        Write-OK "[MODE] BALANCE - qwen3.5-2b, ~1.4GB VRAM"
    }

    "performance" {
        Write-Step "Setting mode to performance..."
        if (-not (Test-OllamaRunning)) {
            Start-OllamaService
        }
        $model = $MODEL_MAP["performance"]
        Write-Step "Warming up $model..."
        & ollama run $model "" 2>$null
        Set-LLMMode -Mode "performance"
        Write-OK "[MODE] PERFORMANCE - qwen3.5-4b, ~2.5GB VRAM"
    }

    "list" {
        Invoke-ListProfiles
    }

    "pull" {
        if ($Profile) {
            if (-not $PROFILES.Contains($Profile)) {
                Write-Fail "Unknown profile '$Profile'. Valid: $($PROFILES.Keys -join ', ')"
                exit 1
            }
            Write-Step "Downloading GGUF for $Profile..."
            $downloaded = Invoke-DownloadGGUF -ProfileName $Profile
            if (-not $downloaded) { exit 1 }
            Write-Step "Importing to Ollama..."
            $imported = Invoke-ImportToOllama -ProfileName $Profile
            if (-not $imported) { exit 1 }
            Write-OK "Profile '$Profile' ready"
        } else {
            foreach ($name in $PROFILES.Keys) {
                Write-Step "Processing profile: $name"
                $downloaded = Invoke-DownloadGGUF -ProfileName $name
                if ($downloaded) {
                    Invoke-ImportToOllama -ProfileName $name | Out-Null
                }
            }
            Write-OK "All profiles processed"
        }
    }

    "status" {
        Write-Step "GPU Information..."
        $gpu = Get-GPUInfo -Fields "name,memory.total,temperature.gpu"
        if ($gpu) {
            Write-Info "  $($gpu | Format-List | Out-String)"
        } else {
            Write-Skip "No GPU detected"
        }

        Write-Step "Ollama Service..."
        if (Test-OllamaRunning) {
            Write-OK "Ollama is running"
        } else {
            Write-Skip "Ollama is not running"
        }

        Write-Step "Loaded Models..."
        $ollamaList = & ollama list 2>$null
        if ($ollamaList) {
            Write-Info "  $($ollamaList -replace '\n', "`n  ")"
        } else {
            Write-Skip "No models loaded"
        }

        Write-Step "GGUF Files..."
        $modelDir = "$($script:ROOT_DIR)\models"
        if (Test-Path -LiteralPath $modelDir) {
            $ggufs = Get-ChildItem -LiteralPath $modelDir -Filter "*.gguf" -ErrorAction SilentlyContinue
            if ($ggufs) {
                foreach ($f in $ggufs) {
                    $sizeInGB = [math]::Round($f.Length / 1GB, 2)
                    Write-Info "  $($f.Name) ($sizeInGB GB)"
                }
            } else {
                Write-Skip "No GGUF files"
            }
        } else {
            Write-Skip "No models directory"
        }
    }

    "remove" {
        Write-Step "Removing all Ollama models..."
        $ollamaList = & ollama list 2>$null
        if ($ollamaList -and $ollamaList -notmatch "^NAME") {
            & ollama list 2>$null | Select-Object -Skip 1 | ForEach-Object {
                $modelName = ($_ -split '\s+')[0]
                if ($modelName) {
                    & ollama rm $modelName 2>$null
                    Write-OK "Removed model: $modelName"
                }
            }
        } else {
            Write-Skip "No models to remove"
        }

        Write-Step "Removing all GGUF files..."
        $modelDir = "$($script:ROOT_DIR)\models"
        if (Test-Path -LiteralPath $modelDir) {
            Remove-Item -LiteralPath "$modelDir\*.gguf" -Force -ErrorAction SilentlyContinue
            Write-OK "Removed GGUF files from $modelDir"
        } else {
            Write-Skip "No models directory"
        }
    }

    "auto" {
        Invoke-AutoMode
    }
}
