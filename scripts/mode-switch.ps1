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

. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"

# ============================================================
# Helpers
# ============================================================

function Set-WorkMode {
    param([string]$NewMode)
    Write-JsonState -Path $script:WORK_MODE_FILE -Data ([PSCustomObject]@{
        mode = $NewMode
        updated_at = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
    })
}

function Show-ModeInfo {
    param([string]$Mode)
    $info = switch ($Mode) {
        "plan"  { @{ icon = "[?]"; label = "PLAN"; color = "Cyan"; desc = "Read-only: audit, research, analyze" } }
        "build" { @{ icon = "[*]"; label = "BUILD"; color = "Green"; desc = "Write/execute: implement, test, deploy" } }
    }

    Write-Host ""
    Write-Host "  $($info.icon) Current Mode: $($info.label)" -ForegroundColor $info.color
    Write-Host "  $($info.desc)" -ForegroundColor Gray
    Write-Host ""

    if (Test-Path $script:SKILL_IDX_FILE) {
        try {
            $index = Get-Content $script:SKILL_IDX_FILE -Raw | ConvertFrom-Json
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
        Set-WorkMode -NewMode "plan"
        Show-ModeInfo -Mode "plan"
        Write-Host "  [MODE] Switched to PLAN — read-only enabled" -ForegroundColor Cyan
        Write-Host ""
    }

    "build" {
        Set-WorkMode -NewMode "build"
        Show-ModeInfo -Mode "build"
        Write-Host "  [MODE] Switched to BUILD — write/execute enabled" -ForegroundColor Green
        Write-Host ""
    }

    "status" {
        $mode = Get-WorkMode
        Show-ModeInfo -Mode $mode
    }
}
