# start-9router-bg.ps1 - Hidden launcher for Scheduled Task / autostart
# Loads config, ensures build present, starts 9Router, writes autostart log.
# Designed to be invoked by Task Scheduler on logon with -WindowStyle Hidden.
# Exit codes:
#   0 = 9Router healthy (already running or started successfully)
#   1 = standalone build missing
#   2 = start failed (timeout / error)
#   3 = config load error

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

try {
    . "$PSScriptRoot\helpers.ps1"
    . "$PSScriptRoot\config.ps1"
    . "$PSScriptRoot\log.ps1"
} catch {
    exit 3
}

# Ensure logs dir
New-Item -ItemType Directory -Path $script:LOG_DIR -Force | Out-Null
$autostartLog = "$($script:LOG_DIR)\autostart.log"

function Write-AutostartLog {
    param([string]$Msg, [string]$Level = "INFO")
    $ts = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")
    $line = "[$ts] [$Level] $Msg"
    try { Add-Content -Path $autostartLog -Value $line -Encoding UTF8 } catch {}
}

Write-AutostartLog "start-9router-bg invoked (PID: $PID)"

# Health check - if already running, exit 0
try {
    $null = Invoke-RestMethod -Uri "$($script:API_URL)/api/health" -TimeoutSec 3 -ErrorAction Stop
    Write-AutostartLog "9Router already healthy, exiting 0"
    Write-TaskLog -Stage "AUTOSTART" -Action "9Router already running" -Result "success"
    exit 0
} catch {
    Write-AutostartLog "9Router not healthy, will start"
}

# Guard: standalone build must exist
if (-not (Test-Path "$($script:ROUTER_DIR)\.next\standalone\server.js")) {
    Write-AutostartLog "Standalone build missing at $($script:ROUTER_DIR)\.next\standalone\server.js" "ERROR"
    Write-TaskLog -Stage "AUTOSTART" -Action "Start-9Router - standalone missing" -Result "fail" -Files "$($script:ROUTER_DIR)\.next\standalone\server.js"
    exit 1
}

# Load api-key.txt env (matches start.ps1 behavior) so INITIAL_PASSWORD etc. are set
if (Test-Path $script:API_KEY_FILE) {
    try {
        Get-Content $script:API_KEY_FILE | ForEach-Object {
            $line = $_.Trim()
            if ($line -match '^([A-Z_]+)=(.*)' -and $line -notmatch '^\s*#') {
                Set-Item -Path "env:$($matches[1])" -Value $matches[2]
            }
        }
    } catch {
        Write-AutostartLog "Failed to load api-key.txt: $_" "WARN"
    }
}

# Start
$ok = Start-9Router
if ($ok) {
    Write-AutostartLog "9Router started successfully"
    Write-TaskLog -Stage "AUTOSTART" -Action "Start-9Router via bg wrapper" -Result "success"
    exit 0
} else {
    Write-AutostartLog "Start-9Router returned false" "ERROR"
    Write-TaskLog -Stage "AUTOSTART" -Action "Start-9Router via bg wrapper" -Result "fail"
    exit 2
}
