# autostart.ps1 - Manage Windows Scheduled Task for 9Router auto-start on logon
# Usage:
#   .\autostart.ps1 -Action enable      Register scheduled task (AtLogon, restart-on-failure 3x)
#   .\autostart.ps1 -Action disable     Unregister scheduled task
#   .\autostart.ps1 -Action status      Show current state
#   .\autostart.ps1 -Action run         Manually trigger the task (test the action)

param(
    [ValidateSet("enable", "disable", "status", "run")]
    [string]$Action = "status"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$script:ROOT_DIR = Split-Path -Parent $PSScriptRoot
. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"
. "$PSScriptRoot\common\log.ps1"

# PowerShell executable (powershell.exe for Windows PowerShell 5.1 compat,
# or pwsh.exe if running under PS7 - prefer pwsh for consistency)
$pwshExe = (Get-Process -Id $PID).Path
if (-not $pwshExe) { $pwshExe = "powershell.exe" }

function Get-TaskExists {
    try {
        $task = Get-ScheduledTask -TaskName $script:TASK_NAME -ErrorAction Stop
        return $true
    } catch { return $false }
}

function Get-RouterHealth {
    try {
        $null = Invoke-RestMethod -Uri "$($script:API_URL)/api/health" -TimeoutSec 3 -ErrorAction Stop
        return $true
    } catch { return $false }
}

function Enable-Autostart {
    if (Get-TaskExists) {
        Write-Info "Task already registered, updating..."
        try { Unregister-ScheduledTask -TaskName $script:TASK_NAME -Confirm:$false } catch {}
    }

    if (-not (Test-Path $script:TASK_BG_SCRIPT)) {
        Write-Fail "Background wrapper missing: $($script:TASK_BG_SCRIPT)"
        return $false
    }

    # Action: hidden PowerShell invoking the bg wrapper
    $actionArg = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$($script:TASK_BG_SCRIPT)`""
    $action = New-ScheduledTaskAction -Execute $pwshExe -Argument $actionArg

    # Trigger: at user logon (no admin required)
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERDOMAIN\$env:USERNAME

    # Settings: restart on failure 3x with 5-minute interval, don't run on batteries unless plugged,
    # allow start on demand, stop if running longer than 1 hour (safety)
    $settings = New-ScheduledTaskSettingsSet `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 5) `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
        -StartWhenAvailable

    # Register under current user (no admin needed for AtLogon user trigger)
    try {
        Register-ScheduledTask `
            -TaskName $script:TASK_NAME `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Description "Start 9Router on user logon (farewell-assistant)" `
            -RunLevel Limited `
            -Force | Out-Null
    } catch {
        Write-Fail "Register-ScheduledTask failed: $_"
        Write-TaskLog -Stage "AUTOSTART" -Action "Register task" -Result "fail" -Files $script:TASK_BG_SCRIPT
        return $false
    }

    # Cleanup stale VBS from old approach (if any)
    $oldVbs = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\9router.vbs"
    if (Test-Path $oldVbs) {
        try {
            Remove-Item -LiteralPath $oldVbs -Force
            Write-Info "Removed stale Startup VBS: $oldVbs"
        } catch { Write-Info "Could not remove stale VBS (ignore): $_" }
    }

    Write-OK "Scheduled task registered: $($script:TASK_NAME)"
    Write-Info "Trigger: AtLogon ($($env:USERDOMAIN)\$($env:USERNAME))"
    Write-Info "Restart: 3x at 5-min interval on failure"
    Write-Info "Wrapper: $($script:TASK_BG_SCRIPT)"
    Write-Info "Logs:    $($script:LOG_DIR)\autostart.log"
    Write-TaskLog -Stage "AUTOSTART" -Action "Register scheduled task" -Result "success" -Files $script:TASK_BG_SCRIPT
    return $true
}

function Disable-Autostart {
    if (-not (Get-TaskExists)) {
        Write-Skip "Task not registered"
        return $true
    }
    try {
        Unregister-ScheduledTask -TaskName $script:TASK_NAME -Confirm:$false
        Write-OK "Scheduled task removed: $($script:TASK_NAME)"
        Write-TaskLog -Stage "AUTOSTART" -Action "Unregister scheduled task" -Result "success"
        return $true
    } catch {
        Write-Fail "Unregister failed: $_"
        Write-TaskLog -Stage "AUTOSTART" -Action "Unregister scheduled task" -Result "fail"
        return $false
    }
}

function Show-AutostartStatus {
    Write-Step "STATUS" "9Router autostart (Windows Scheduled Task)"

    $exists = Get-TaskExists
    Write-Info "Task name:    $($script:TASK_NAME)"
    Write-Info "Registered:   $(if ($exists) { 'yes' } else { 'no' })"

    if ($exists) {
        try {
            $task = Get-ScheduledTask -TaskName $script:TASK_NAME
            $info = $task | Get-ScheduledTaskInfo
            Write-Info "State:        $($task.State)"
            Write-Info "Last run:     $($info.LastRunTime)"
            Write-Info "Last result:  $($info.LastTaskResult)"
            Write-Info "Next run:     $($info.NextRunTime)"
            Write-Info "Trigger:      $($task.Triggers[0].CimClass.CimClassName)"
            Write-Info "Action:       $($task.Actions[0].Execute) $($task.Actions[0].Arguments)"
        } catch {
            Write-Fail "Could not read task info: $_"
        }
    }

    $healthy = Get-RouterHealth
    Write-Info "9Router API:  $(if ($healthy) { 'healthy' } else { 'not running' })"

    if (-not $healthy -and -not (Test-Path "$($script:ROUTER_DIR)\.next\standalone\server.js")) {
        Write-Fail "Standalone build missing - run: .\scripts\owner.ps1"
    }

    $oldVbs = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\9router.vbs"
    if (Test-Path $oldVbs) {
        Write-Info "Stale VBS:    $oldVbs (will be removed on enable)"
    }
}

function Invoke-AutostartRun {
    if (-not (Get-TaskExists)) {
        Write-Fail "Task not registered. Run: .\autostart.ps1 -Action enable"
        return $false
    }
    Write-Info "Triggering task manually..."
    try {
        Start-ScheduledTask -TaskName $script:TASK_NAME
        Write-OK "Task triggered. Check logs: $($script:LOG_DIR)\autostart.log"
        Start-Sleep -Seconds 5
        $healthy = Get-RouterHealth
        Write-Info "9Router API: $(if ($healthy) { 'healthy' } else { 'still warming up - check logs' })"
        return $true
    } catch {
        Write-Fail "Start-ScheduledTask failed: $_"
        return $false
    }
}

switch ($Action) {
    "enable"   { Enable-Autostart }
    "disable"  { Disable-Autostart }
    "status"   { Show-AutostartStatus }
    "run"      { Invoke-AutostartRun }
}
