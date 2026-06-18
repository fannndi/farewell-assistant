# workmode.ps1 - Switch between plan/build work modes
# Usage: .\workmode.ps1 [-Action plan|build|status]

param(
    [ValidateSet("plan", "build", "status")]
    [string]$Action = "status"
)

$ErrorActionPreference = "Stop"
$script:ROOT_DIR = $PSScriptRoot | Split-Path -Parent
. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"
. "$PSScriptRoot\common\log.ps1"

$ModeDefs = @{
    plan = @{
        Label = "PLAN"; Icon = "[P]"
        ToolsAllowed = @("read", "bash")
        ToolsBlocked = @("write", "edit")
        Groups = @("audit", "research", "explore", "planning")
    }
    build = @{
        Label = "BUILD"; Icon = "[B]"
        ToolsAllowed = @("write", "edit", "bash", "read")
        ToolsBlocked = @()
        Groups = @("orchestration", "tdd_testing", "coding", "security", "deployment", "agent_eng")
    }
}

function Show-ModeInfo {
    param([string]$Mode)
    $idx = Read-JsonState -Path $script:SKILL_IDX_FILE -Default { return $null }
    if (-not $idx) { Write-Fail "skill-mode-index.json not found"; return }

    $def = $ModeDefs[$Mode]
    $modeData = $idx.$Mode
    if (-not $modeData) { Write-Fail "Mode '$Mode' not found"; return }

    $totalSkills = 0
    $groups = $modeData.skills

    Write-Host ""
    Write-Step "MODE" "$($def.Icon) $($def.Label)"
    Write-Info "Description: $($modeData.description)"
    Write-Info "Tools allowed: $($def.ToolsAllowed -join ', ')"
    if ($def.ToolsBlocked.Count -gt 0) {
        Write-Info "Tools blocked: $($def.ToolsBlocked -join ', ')"
    } else {
        Write-Info "Tools blocked: none"
    }

    Write-Host ""
    Write-Step "SKILLS" "Groups loaded"
    foreach ($group in $def.Groups) {
        $skills = $groups.$group
        $count = if ($skills) { $skills.Count } else { 0 }
        $totalSkills += $count
        Write-OK "$group - $count skills"
        foreach ($s in $skills) { Write-Info "  $s" }
    }
    Write-Host ""
    Write-Step "TOTAL" "$totalSkills skills loaded"
}

$currentMode = Get-WorkMode
switch ($Action) {
    "status" {
        Write-Step "STATUS" "Current work mode"
        Write-OK "Mode: $($currentMode.ToUpper())"
        Show-ModeInfo -Mode $currentMode
    }
    { $_ -in "plan", "build" } {
        if ($Action -eq $currentMode) {
            Write-Info "Already in $($Action.ToUpper()) mode. No change."
            Show-ModeInfo -Mode $Action
            return
        }
        Write-Step "SWITCH" "Changing $($currentMode.ToUpper()) -> $($Action.ToUpper())"
        $state = @{ mode = $Action; updated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz") }
        Write-JsonState -Path $script:WORK_MODE_FILE -Data $state
        Write-OK "Work mode set to $($Action.ToUpper())"
        Show-ModeInfo -Mode $Action
        Sync-SessionState
        Write-TaskLog -Stage "WORKMODE" -Action "Switch to $($Action.ToUpper())" -Result "success"
    }
}
