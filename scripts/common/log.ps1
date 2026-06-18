# Common Logging - Append structured task log entries to logging.md
# Usage: . "$PSScriptRoot\log.ps1"
# Then:  Write-TaskLog -Stage "FIX" -Action "..." -Result "success" -Files "path1,path2"

if (-not $script:LOG_DIR) {
    $script:LOG_DIR = "$($script:ROOT_DIR)\.opencode\logs"
}

$script:LOG_FILE = "$($script:ROOT_DIR)\logging.md"

function Write-TaskLog {
    param(
        [Parameter(Mandatory)][string]$Stage,
        [Parameter(Mandatory)][string]$Action,
        [string]$Result = "success",
        [string]$Files = ""
    )
    try {
        if (-not (Test-Path $script:LOG_FILE)) {
            "# Logging" | Set-Content -Path $script:LOG_FILE -Encoding UTF8
        }
        $ts = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")
        $filesPart = if ($Files) { " | FILES: $Files" } else { "" }
        $entry = "[$ts] STAGE: $Stage | ACTION: $Action | RESULT: $Result$filesPart"
        Add-Content -Path $script:LOG_FILE -Value $entry -Encoding UTF8
    } catch {
        Write-Verbose "Write-TaskLog failed: $_"
    }
}

# Sync .opencode/session-state.json + .opencode/context.md from current mode/work state
function Sync-SessionState {
    try {
        $mode = Get-LLMMode
        $work = Get-WorkMode
        $now = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"

        # Read registry for active project + kategori
        $active = "farewell-assistant"
        $kategori = "AUTOMATION"
        if (Test-Path $script:REGISTRY_FILE) {
            try {
                $reg = Get-Content $script:REGISTRY_FILE -Raw | ConvertFrom-Json
                if ($reg.active) { $active = $reg.active }
                if ($reg.projects.$active.kategori) {
                    $katValues = @()
                    foreach ($kv in $reg.projects.$active.kategori.PSObject.Properties) {
                        $katValues += $kv.Value
                    }
                    $kategori = ($katValues | Select-Object -Unique) -join " - "
                }
            } catch {}
        }

        # GPU inference
        $gpu = if ($mode -eq "eco") { "off" } else { "on" }

        # Skill count from skill-mode-index.json
        $skillCount = 0
        if (Test-Path $script:SKILL_IDX_FILE) {
            try {
                $idx = Get-Content $script:SKILL_IDX_FILE -Raw | ConvertFrom-Json
                $modeData = $idx.$work
                if ($modeData -and $modeData.skills) {
                    foreach ($g in $modeData.skills.PSObject.Properties) {
                        $skillCount += $g.Value.Count
                    }
                }
            } catch {}
        }

        # Write session-state.json
        $state = @{
            session = @{
                project   = $active
                mode      = $mode
                work      = $work.ToUpper()
                kategori  = $kategori
                started   = $now
                last_save = $now
            }
            metrics = @{
                tokens_input    = 0
                tokens_output   = 0
                sessions_count  = 1
            }
        }
        Write-JsonState -Path "$($script:STATE_DIR)\session-state.json" -Data $state

        # Write context.md
        $ctx = @"
# Session State

- **Mode:** $mode
- **Role:** User
- **Project:** $active
- **Kategori:** $kategori
- **GPU:** $gpu
- **Work:** $($work.ToUpper())
- **Skills:** ON - $skillCount
- **Session:** $((Get-Date -Format 'yyyy-MM-dd'))
- **Started:** $now
"@
        Set-Content -Path "$($script:STATE_DIR)\context.md" -Value $ctx -Encoding UTF8
    } catch {
        Write-Verbose "Sync-SessionState failed: $_"
    }
}
