# LLM Mode - Operating Mode Switch
# Usage: .\llm-mode.ps1 eco|on|status

param(
    [ValidateSet("eco", "on", "status")]
    [string]$Action = "status"
)

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$MODE_DIR = "$ROOT_DIR\.opencode"
$MODE_FILE = "$MODE_DIR\llm-mode.json"
$OLLAMA_URL = "http://localhost:11434"

$MODEL_MAP = @{
    "eco" = $null
    "on"  = "qwen2.5:1.5b-s"
}

function Get-Mode {
    if (Test-Path $MODE_FILE) {
        try {
            $state = Get-Content $MODE_FILE -Raw | ConvertFrom-Json
            return $state.mode
        } catch {}
    }
    return "eco"
}

function Set-Mode {
    param([string]$Mode, [string]$Model)
    New-Item -ItemType Directory -Path $MODE_DIR -Force | Out-Null
    $state = [PSCustomObject]@{
        mode = $Mode
        model = if ($Model) { $Model } else { "" }
        updated_at = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
    }
    $state | ConvertTo-Json -Depth 5 | Set-Content -Path $MODE_FILE -Encoding UTF8
}

function Test-OllamaRunning {
    try {
        $null = Invoke-RestMethod -Uri "$OLLAMA_URL/api/tags" -TimeoutSec 3 -ErrorAction Stop
        return $true
    } catch { return $false }
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
        $null = Invoke-RestMethod -Uri "$OLLAMA_URL/api/chat" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 120 -ErrorAction SilentlyContinue
    } catch {}
}

# ============================================================
# Execute
# ============================================================

switch ($Action) {
    "eco" {
        Set-Mode -Mode "eco" -Model $null
        ollama stop qwen2.5:1.5b-s 2>$null
        Write-Host "  [MODE] ECO — no LLM, zero GPU usage" -ForegroundColor Green
    }

    "on" {
        $model = $MODEL_MAP["on"]
        $running = Test-OllamaRunning
        if (-not $running) {
            Write-Host "  [MODE] Ollama not running. Starting..." -ForegroundColor Yellow
            try {
                Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
                Start-Sleep -Seconds 3
            } catch {}
        }
        Set-Mode -Mode "on" -Model $model
        Write-Host "  [MODE] Loading $model to GPU..." -ForegroundColor Gray
        Invoke-Warmup -ModelName $model
        Write-Host "  [MODE] ON — $model (~1GB VRAM, enrichment active)" -ForegroundColor Cyan
    }

    "status" {
        $mode = Get-Mode
        $model = if ($mode -eq "eco") { "none" } else { "qwen2.5:1.5b-s" }
        $running = Test-OllamaRunning
        $label = if ($mode -eq "eco") { "ECO" } else { "ON" }
        $color = if ($mode -eq "eco") { "Green" } else { "Cyan" }

        Write-Host ""
        Write-Host "  Mode:     $label" -ForegroundColor $color
        Write-Host "  Model:    $model" -ForegroundColor White
        Write-Host "  Ollama:   $(if ($running) { 'Running' } else { 'Stopped' })" -ForegroundColor $(if ($running) { "Green" } else { "Red" })

        if ($running) {
            try {
                $tags = Invoke-RestMethod -Uri "$OLLAMA_URL/api/tags" -TimeoutSec 5
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
