# Mode Switch - Switch work mode (plan/build)
# Usage:
#   .\mode-switch.ps1 plan    → switch ke PLAN mode (read-only)
#   .\mode-switch.ps1 build   → switch ke BUILD mode (write/execute)
#   .\mode-switch.ps1 status  → lihat mode aktif

param(
    [ValidateSet("plan", "build", "status")]
    [string]$Action = "status"
)

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$MODE_DIR = "$ROOT_DIR\.opencode"
$MODE_FILE = "$MODE_DIR\work-mode.json"
$SKILL_INDEX = "$ROOT_DIR\projects\skill-mode-index.json"

# ============================================================
# Helpers
# ============================================================

function Get-Mode {
    if (Test-Path $MODE_FILE) {
        try {
            $state = Get-Content $MODE_FILE -Raw | ConvertFrom-Json
            return $state.mode
        } catch {}
    }
    return "build"
}

function Set-Mode {
    param([string]$NewMode)
    New-Item -ItemType Directory -Path $MODE_DIR -Force | Out-Null
    $state = [PSCustomObject]@{
        mode = $NewMode
        updated_at = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
    }
    $state | ConvertTo-Json -Depth 5 | Set-Content -Path $MODE_FILE -Encoding UTF8
}

function Show-ModeInfo {
    param([string]$Mode)
    $info = switch ($Mode) {
        "plan"  { @{ icon = "🔍"; label = "PLAN"; color = "Cyan"; desc = "Read-only: audit, research, analyze" } }
        "build" { @{ icon = "🔨"; label = "BUILD"; color = "Green"; desc = "Write/execute: implement, test, deploy" } }
    }

    Write-Host ""
    Write-Host "  $($info.icon) Current Mode: $($info.label)" -ForegroundColor $info.color
    Write-Host "  $($info.desc)" -ForegroundColor Gray
    Write-Host ""

    if (Test-Path $SKILL_INDEX) {
        try {
            $index = Get-Content $SKILL_INDEX -Raw | ConvertFrom-Json
            $modeData = $index.$Mode
            if ($modeData) {
                Write-Host "  Loaded skills:" -ForegroundColor Yellow
                foreach ($group in $modeData.skills.PSObject.Properties) {
                    Write-Host "    - $($group.Name): $($group.Value.Count) skills" -ForegroundColor Gray
                }
                Write-Host ""
                Write-Host "  Agents: $($modeData.agents -join ', ')" -ForegroundColor Gray
            }
        } catch {}
    }
}

# ============================================================
# Execute
# ============================================================

switch ($Action) {
    "plan" {
        Set-Mode -NewMode "plan"
        Show-ModeInfo -Mode "plan"
        Write-Host "  [MODE] Switched to PLAN — read-only enabled" -ForegroundColor Cyan
        Write-Host ""
    }

    "build" {
        Set-Mode -NewMode "build"
        Show-ModeInfo -Mode "build"
        Write-Host "  [MODE] Switched to BUILD — write/execute enabled" -ForegroundColor Green
        Write-Host ""
    }

    "status" {
        $mode = Get-Mode
        Show-ModeInfo -Mode $mode
    }
}
