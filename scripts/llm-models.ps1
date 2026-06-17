# LLM Models - Model download & profile management
# Usage:
#   .\llm-models.ps1 list            → lihat semua profile + status
#   .\llm-models.ps1 pull            → download semua model
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
$OLLAMA_URL = "http://localhost:11434"

# ============================================================
# Model Profiles
# ============================================================

$PROFILES = [ordered]@{
    "hot" = @{
        model = "qwen3.5:0.8b"
        vram = "~600MB"
        condition = "Outdoor, unplugged, high temp"
        mode = "full_gpu"
        modelfile = "$ROOT_DIR\Modelfile.qwen3.5-0.8b"
    }
    "eco" = @{
        model = "qwen2.5-coder:1.5b"
        vram = "~1GB"
        condition = "Indoor, unplugged"
        mode = "full_gpu"
        modelfile = "$ROOT_DIR\Modelfile.qwen2.5-coder-1.5b"
    }
    "balance" = @{
        model = "qwen3.5:2b"
        vram = "~1.4GB"
        condition = "Indoor, plugged, AC"
        mode = "full_gpu"
        modelfile = "$ROOT_DIR\Modelfile.qwen3.5-2b"
    }
    "performance" = @{
        model = "qwen3.5:4b"
        vram = "~2.5GB"
        condition = "Indoor, plugged, fan active"
        mode = "hybrid_gpu_cpu"
        modelfile = "$ROOT_DIR\Modelfile.qwen3.5-4b"
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

    Write-Host ""
    Write-Host "  LLM Model Profiles" -ForegroundColor Cyan
    Write-Host "  ==================" -ForegroundColor Cyan
    Write-Host ""

    foreach ($key in $PROFILES.Keys) {
        $p = $PROFILES[$key]
        $status = if ($downloadedNames.ContainsKey($p.model)) {
            "Downloaded"
        } else {
            "Pending"
        }
        $statusColor = if ($status -eq "Downloaded") { "Green" } else { "Yellow" }

        Write-Host "  $key" -NoNewline -ForegroundColor White
        Write-Host " " -NoNewline
        Write-Host ($p.model).PadRight(25) -NoNewline -ForegroundColor Gray
        Write-Host ($p.vram).PadRight(10) -NoNewline -ForegroundColor Gray
        Write-Host $status -ForegroundColor $statusColor
    }

    Write-Host ""
}

# ============================================================
# Pull Model
# ============================================================

function Invoke-Pull {
    param([string]$TargetProfile)

    Start-Ollama

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

    $downloaded = Get-DownloadedModels
    $downloadedNames = @{}
    foreach ($m in $downloaded) { $downloadedNames[$m.name] = $true }

    foreach ($key in $targets.Keys) {
        $p = $targets[$key]
        if ($downloadedNames.ContainsKey($p.model)) {
            Write-Host "  [SKIP] $($p.model) already downloaded" -ForegroundColor Yellow
            continue
        }

        Write-Host "  [PULL] $($p.model) ($($p.vram))..." -ForegroundColor Cyan
        try {
            & ollama pull $p.model
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK] $($p.model) downloaded" -ForegroundColor Green
            } else {
                Write-Host "  [FAIL] $($p.model) pull failed" -ForegroundColor Red
            }
        } catch {
            Write-Host "  [FAIL] Error pulling $($p.model): $_" -ForegroundColor Red
        }
    }
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
            Write-Host "  Models:    None downloaded" -ForegroundColor Yellow
        }
    }

    Write-Host ""
}

# ============================================================
# Remove Models
# ============================================================

function Invoke-Remove {
    Start-Ollama
    $downloaded = Get-DownloadedModels

    if ($downloaded.Count -eq 0) {
        Write-Host "  No models to remove" -ForegroundColor Yellow
        return
    }

    foreach ($m in $downloaded) {
        Write-Host "  [REMOVE] $($m.name)..." -ForegroundColor Yellow
        try {
            & ollama rm $m.name
            Write-Host "  [OK] $($m.name) removed" -ForegroundColor Green
        } catch {
            Write-Host "  [FAIL] Cannot remove $($m.name): $_" -ForegroundColor Red
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
