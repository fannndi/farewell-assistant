# LLM Models - GGUF download & profile management
# Usage:
#   .\llm-models.ps1 list            → lihat semua profile + status
#   .\llm-models.ps1 pull            → download semua model GGUF
#   .\llm-models.ps1 pull hot        → download model hot saja
#   .\llm-models.ps1 pull balance    → download model balance saja
#   .\llm-models.ps1 status          → status GPU + VRAM
#   .\llm-models.ps1 remove          → hapus semua model

param(
    [ValidateSet("list", "pull", "status", "remove")]
    [string]$Action = "list",
    [string]$Profile = ""
)

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$MODELS_DIR = "$ROOT_DIR\models"
$OLLAMA_URL = "http://localhost:11434"

# ============================================================
# Model Profiles (GGUF from HuggingFace)
# ============================================================

$PROFILES = [ordered]@{
    "hot" = @{
        model = "qwen3.5-0.8b"
        vram = "~600MB"
        condition = "Outdoor, unplugged, high temp"
        hf_repo = "unsloth/Qwen3.5-0.8B-GGUF"
        hf_file = "Qwen3.5-0.8B-Q4_K_M.gguf"
        modelfile = "$ROOT_DIR\Modelfile.qwen3.5-0.8b"
        size_gb = 0.5
    }
    "eco" = @{
        model = "qwen2.5-coder-1.5b"
        vram = "~1GB"
        condition = "Indoor, unplugged"
        hf_repo = "Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF"
        hf_file = "Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf"
        modelfile = "$ROOT_DIR\Modelfile.qwen2.5-coder-1.5b"
        size_gb = 1.0
    }
    "balance" = @{
        model = "qwen3.5-2b"
        vram = "~1.4GB"
        condition = "Indoor, plugged, AC"
        hf_repo = "unsloth/Qwen3.5-2B-GGUF"
        hf_file = "Qwen3.5-2B-Q4_K_M.gguf"
        modelfile = "$ROOT_DIR\Modelfile.qwen3.5-2b"
        size_gb = 1.4
    }
    "performance" = @{
        model = "qwen3.5-4b"
        vram = "~2.5GB"
        condition = "Indoor, plugged, fan active"
        hf_repo = "unsloth/Qwen3.5-4B-GGUF"
        hf_file = "Qwen3.5-4B-Q4_K_M.gguf"
        modelfile = "$ROOT_DIR\Modelfile.qwen3.5-4b"
        size_gb = 2.5
    }
}

# ============================================================
# Helpers
# ============================================================

function Test-OllamaRunning {
    try {
        $null = Invoke-RestMethod -Uri "$OLLAMA_URL/api/tags" -TimeoutSec 3 -ErrorAction Stop
        return $true
    } catch { return $false }
}

function Start-Ollama {
    if (-not (Test-OllamaRunning)) {
        Write-Host "  [..] Starting Ollama..." -ForegroundColor Yellow
        try {
            Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
            Start-Sleep -Seconds 3
            if (Test-OllamaRunning) {
                Write-Host "  [OK] Ollama started" -ForegroundColor Green
            } else {
                Write-Host "  [FAIL] Ollama failed to start" -ForegroundColor Red
            }
        } catch {
            Write-Host "  [FAIL] Cannot start Ollama: $_" -ForegroundColor Red
        }
    }
}

function Get-DownloadedModels {
    if (-not (Test-OllamaRunning)) { return @() }
    try {
        $tags = Invoke-RestMethod -Uri "$OLLAMA_URL/api/tags" -TimeoutSec 5
        if ($tags.models) { return $tags.models } else { return @() }
    } catch { return @() }
}

function Get-GGUFFiles {
    $map = @{}
    if (-not (Test-Path $MODELS_DIR)) { return $map }
    $files = Get-ChildItem -Path $MODELS_DIR -Filter "*.gguf" -ErrorAction SilentlyContinue
    foreach ($f in $files) { $map[$f.Name] = $f.FullName }
    return $map
}

function Get-GPUInfo {
    try {
        $gpuRaw = nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu --format=csv,noheader 2>$null
        if ($gpuRaw) {
            $parts = $gpuRaw.Trim() -split ','
            return @{
                name = $parts[0].Trim()
                memory_used = [int]($parts[1].Trim().Replace(' MiB',''))
                memory_total = [int]($parts[2].Trim().Replace(' MiB',''))
                temperature = [int]($parts[3].Trim().Replace(' C',''))
            }
        }
    } catch {}
    return $null
}

# ============================================================
# List Profiles
# ============================================================

function Show-List {
    $downloaded = Get-DownloadedModels
    $downloadedNames = @{}
    foreach ($m in $downloaded) { $downloadedNames[$m.name] = $true }

    $ggufFiles = Get-GGUFFiles

    Write-Host ""
    Write-Host "  LLM Model Profiles (GGUF)" -ForegroundColor Cyan
    Write-Host "  ==========================" -ForegroundColor Cyan
    Write-Host ""

    foreach ($key in $PROFILES.Keys) {
        $p = $PROFILES[$key]
        $ggufStatus = if ($ggufFiles.ContainsKey($p.hf_file)) { "Downloaded" } else { "Pending" }
        $ollamaStatus = if ($downloadedNames.ContainsKey($p.model)) { "Loaded" } else { "Not Loaded" }
        $statusColor = if ($ggufStatus -eq "Downloaded") { "Green" } else { "Yellow" }

        Write-Host "  $key" -NoNewline -ForegroundColor White
        Write-Host " " -NoNewline
        Write-Host ($p.vram).PadRight(10) -NoNewline -ForegroundColor Gray
        Write-Host $ggufStatus -NoNewline -ForegroundColor $statusColor
        Write-Host " " -NoNewline
        Write-Host $ollamaStatus -ForegroundColor $(if ($ollamaStatus -eq "Loaded") { "Green" } else { "DarkGray" })
    }

    Write-Host ""
}

# ============================================================
# Pull GGUF
# ============================================================

function Invoke-Pull {
    param([string]$TargetProfile)

    New-Item -ItemType Directory -Path $MODELS_DIR -Force | Out-Null

    $ggufFiles = Get-GGUFFiles

    $targets = if ($TargetProfile) {
        if ($PROFILES.ContainsKey($TargetProfile)) {
            @{ $TargetProfile = $PROFILES[$TargetProfile] }
        } else {
            Write-Host "  [ERROR] Unknown profile: $TargetProfile" -ForegroundColor Red
            Write-Host "  Available: hot, eco, balance, performance" -ForegroundColor Gray
            return
        }
    } else {
        $PROFILES
    }

    foreach ($key in $targets.Keys) {
        $p = $targets[$key]

        # Skip if already downloaded
        if ($ggufFiles.ContainsKey($p.hf_file)) {
            Write-Host "  [SKIP] $($p.hf_file) already downloaded" -ForegroundColor Yellow
            continue
        }

        $url = "https://huggingface.co/$($p.hf_repo)/resolve/main/$($p.hf_file)"
        $outFile = "$MODELS_DIR\$($p.hf_file)"

        Write-Host "  [PULL] $($p.model) (~$($p.size_gb)GB)..." -ForegroundColor Cyan
        Write-Host "         $url" -ForegroundColor DarkGray

        try {
            # Use curl.exe for large file download (supports resume)
            $result = & curl.exe -L -C - -o $outFile $url 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK] $($p.hf_file) downloaded" -ForegroundColor Green
            } else {
                Write-Host "  [FAIL] Download failed" -ForegroundColor Red
                continue
            }
        } catch {
            Write-Host "  [FAIL] Error: $_" -ForegroundColor Red
            continue
        }

        # Create Ollama model from GGUF
        Write-Host "  [CREATE] Importing to Ollama..." -ForegroundColor Gray
        try {
            Start-Ollama
            & ollama create $p.model -f $p.modelfile
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK] $($p.model) imported to Ollama" -ForegroundColor Green
            } else {
                Write-Host "  [FAIL] Import failed" -ForegroundColor Red
            }
        } catch {
            Write-Host "  [FAIL] Import error: $_" -ForegroundColor Red
        }
    }

    Write-Host ""
}

# ============================================================
# GPU Status
# ============================================================

function Show-Status {
    $gpu = Get-GPUInfo
    $ollama = Test-OllamaRunning

    Write-Host ""
    Write-Host "  System Status" -ForegroundColor Cyan
    Write-Host "  =============" -ForegroundColor Cyan
    Write-Host ""

    if ($gpu) {
        $tempColor = if ($gpu.temperature -gt 70) { "Red" } elseif ($gpu.temperature -gt 55) { "Yellow" } else { "Green" }
        Write-Host "  GPU:       $($gpu.name)" -ForegroundColor White
        Write-Host "  VRAM:      $($gpu.memory_used)/$($gpu.memory_total) MB" -ForegroundColor Gray
        Write-Host "  Temp:      $($gpu.temperature)°C" -ForegroundColor $tempColor
    } else {
        Write-Host "  GPU:       Not detected" -ForegroundColor Red
    }

    Write-Host "  Ollama:    $(if ($ollama) { 'Running' } else { 'Stopped' })" -ForegroundColor $(if ($ollama) { "Green" } else { "Red" })

    if ($ollama) {
        $models = Get-DownloadedModels
        if ($models.Count -gt 0) {
            Write-Host "  Models:" -ForegroundColor Gray
            foreach ($m in $models) {
                $size = [math]::Round($m.size / 1GB, 2)
                Write-Host "    $($m.name) ($size GB)" -ForegroundColor Gray
            }
        } else {
            Write-Host "  Models:    None loaded" -ForegroundColor Yellow
        }
    }

    $ggufFiles = Get-GGUFFiles
    if ($ggufFiles.Count -gt 0) {
        Write-Host "  GGUF:" -ForegroundColor Gray
        foreach ($name in $ggufFiles.Keys) {
            $size = [math]::Round((Get-Item $ggufFiles[$name]).Length / 1GB, 2)
            Write-Host "    $name ($size GB)" -ForegroundColor Gray
        }
    }

    Write-Host ""
}

# ============================================================
# Remove Models
# ============================================================

function Invoke-Remove {
    # Remove from Ollama
    $downloaded = Get-DownloadedModels
    if ($downloaded.Count -gt 0) {
        Start-Ollama
        foreach ($m in $downloaded) {
            Write-Host "  [REMOVE] $($m.name) from Ollama..." -ForegroundColor Yellow
            try {
                & ollama rm $m.name
                Write-Host "  [OK] $($m.name) removed" -ForegroundColor Green
            } catch {
                Write-Host "  [FAIL] Cannot remove: $_" -ForegroundColor Red
            }
        }
    }

    # Remove GGUF files
    $ggufFiles = Get-GGUFFiles
    if ($ggufFiles.Count -gt 0) {
        foreach ($name in $ggufFiles.Keys) {
            Write-Host "  [REMOVE] $name ..." -ForegroundColor Yellow
            Remove-Item -Path $ggufFiles[$name] -Force
            Write-Host "  [OK] $name removed" -ForegroundColor Green
        }
    }
}

# ============================================================
# Execute
# ============================================================

switch ($Action) {
    "list"    { Show-List }
    "pull"    { Invoke-Pull -TargetProfile $Profile }
    "status"  { Show-Status }
    "remove"  { Invoke-Remove }
}
