# Owner - Daily Maintenance
# Usage: .\owner.ps1

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"
. "$PSScriptRoot\common\log.ps1"

# ============================================================
# Banner
# ============================================================

Write-Host ""
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host "  farewell-assistant - Owner" -ForegroundColor Magenta
Write-Host "  =================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Inline Functions
# ============================================================

function Write-ChangelogDiff {
    param([string]$Repo, [string]$Dir, [string]$Branch, [string]$Before)
    if (-not (Test-Path "$Dir\.git")) { return }
    Push-Location $Dir
    try {
        $behind = git rev-list --count "$Before..origin/$Branch" 2>&1
        if ($behind -and $behind -gt 0) {
            Write-Host "  -- $Repo ($behind new commit(s)) --" -ForegroundColor Cyan
            git log "$Before..origin/$Branch" --oneline --no-decorate 2>$null | Select-Object -First 10 | ForEach-Object {
                Write-Host "    $_" -ForegroundColor Gray
            }
            if ($behind -gt 10) {
                Write-Host "    ... and $($behind - 10) more" -ForegroundColor Gray
            }
        }
    } finally { Pop-Location }
}

# ============================================================
# Step 1/4: Pull Latest Changes
# ============================================================

Write-Step "1/4" "Pull Latest Changes"

function Write-PullECC {
    if (-not (Test-Path "$($script:ECC_DIR)\.git")) { Write-Skip "ECC not cloned"; return }
    Push-Location $script:ECC_DIR
    try {
        git fetch origin 2>&1 | Out-Null
        $before = git rev-parse HEAD 2>$null
        $behind = git rev-list --count "HEAD..origin/main" 2>&1
        if ($behind -and $behind -gt 0) {
            Write-Host "  ECC: $behind commit(s) behind" -ForegroundColor Yellow
            Write-ChangelogDiff "ECC" $script:ECC_DIR "main" $before
            git reset --hard origin/main 2>&1 | Out-Null
            $afterShort = git log --oneline -1 2>$null
            Write-Host "  ECC updated >> $afterShort" -ForegroundColor Green
            git show origin/main:CHANGELOG.md 2>$null | Out-File -FilePath "$($script:ROOT_DIR)\CHANGELOG_ECC.md" -Encoding UTF8
            Write-OK "CHANGELOG_ECC.md synced"
        } else {
            Write-Skip "ECC: already up to date"
        }
    } finally { Pop-Location }
}

function Write-Pull9Router {
    if (-not (Test-Path "$($script:ROUTER_DIR)\.git")) { Write-Skip "9Router not cloned"; return }
    Push-Location $script:ROUTER_DIR
    try {
        git fetch origin 2>&1 | Out-Null
        $before = git rev-parse HEAD 2>$null
        $behind = git rev-list --count "HEAD..origin/master" 2>&1
        if ($behind -and $behind -gt 0) {
            Write-Host "  9Router: $behind commit(s) behind" -ForegroundColor Yellow
            Write-ChangelogDiff "9Router" $script:ROUTER_DIR "master" $before
            # Snapshot key markers BEFORE pull to detect source-level changes (not just package.json)
            $beforeSrcHash = $null
            $srcPaths = @("src", "next.config.mjs", "custom-server.js", "package.json", "cli")
            foreach ($p in $srcPaths) {
                if (Test-Path $p) {
                    $items = Get-ChildItem -Path $p -Recurse -File -ErrorAction SilentlyContinue
                    if ($items) {
                        $hashInput = ($items | Get-FileHash | ForEach-Object { "$($_.Path):$($_.Hash)" }) -join "`n"
                        $beforeSrcHash += (Get-FileHash -InputStream ([System.IO.MemoryStream]::new([System.Text.Encoding]::UTF8.GetBytes($hashInput))).Hash)
                    }
                }
            }
            git pull --ff-only 2>&1 | Out-Null
            $afterShort = git log --oneline -1 2>$null
            Write-Host "  9Router updated >> $afterShort" -ForegroundColor Green
            git show origin/master:CHANGELOG.md 2>$null | Out-File -FilePath "$($script:ROOT_DIR)\CHANGELOG_9ROUTER.md" -Encoding UTF8
            Write-OK "CHANGELOG_9ROUTER.md synced"

            $afterSrcHash = $null
            foreach ($p in $srcPaths) {
                if (Test-Path $p) {
                    $items = Get-ChildItem -Path $p -Recurse -File -ErrorAction SilentlyContinue
                    if ($items) {
                        $hashInput = ($items | Get-FileHash | ForEach-Object { "$($_.Path):$($_.Hash)" }) -join "`n"
                        $afterSrcHash += (Get-FileHash -InputStream ([System.IO.MemoryStream]::new([System.Text.Encoding]::UTF8.GetBytes($hashInput))).Hash)
                    }
                }
            }

            $needsRebuild = $false
            $pkgChanged = $false
            $beforePkg = $null; $afterPkg = $null
            try { $beforePkg = (Get-FileHash "package.json" -ErrorAction SilentlyContinue).Hash } catch {}
            if (-not $beforePkg) { $beforePkg = "none" }

            if ($beforeSrcHash -ne $afterSrcHash) {
                $needsRebuild = $true
                Write-Host "  Source changed, rebuilding 9Router..." -ForegroundColor Gray
            }

            try { $afterPkg = (Get-FileHash "package.json" -ErrorAction SilentlyContinue).Hash } catch {}
            if ($beforePkg -ne $afterPkg) {
                $pkgChanged = $true
                Write-Host "  package.json changed, updating npm..." -ForegroundColor Gray
                npm install 2>&1 | Out-Null
                Write-OK "npm dependencies updated"
                $needsRebuild = $true
            }

            if ($needsRebuild) {
                Write-Host "  Building standalone..." -ForegroundColor Gray
                npm run build 2>&1 | Out-Null
                if (Test-Path ".next\standalone\server.js") {
                    Write-OK "9Router rebuilt"
                } else {
                    Write-Fail "Build failed - standalone/server.js missing"
                }
            } else {
                Write-Skip "No source/package.json change, skipping rebuild"
            }

            # Guard: only restart if standalone build is present
            if (Test-Path ".next\standalone\server.js") {
                Write-Host "  Restarting 9Router..." -ForegroundColor Gray
                Start-9Router
            } else {
                Write-Fail "Cannot restart - standalone build missing"
            }
        } else {
            Write-Skip "9Router: already up to date"
        }
    } finally { Pop-Location }
}

Write-PullECC
Write-Pull9Router

# ============================================================
# Step 2/4: Changelog Analysis
# ============================================================

Write-Step "2/4" "Changelog Analysis"

$changelogEcc = "$($script:ROOT_DIR)\CHANGELOG_ECC.md"
$changelogRouter = "$($script:ROOT_DIR)\CHANGELOG_9ROUTER.md"

$breakingKeywords = @("breaking", "migration", "deprecated", "removed", "skill", "agent", "config")
$changelogIssues = @()

if (Test-Path $changelogEcc) {
    Write-Info "CHANGELOG_ECC.md"
    $eccLines = Get-Content $changelogEcc -First 15 -ErrorAction SilentlyContinue
    if ($eccLines) {
        foreach ($line in $eccLines) {
            Write-Host "    $line" -ForegroundColor Gray
        }
    }
    $eccContent = Get-Content $changelogEcc -Raw -ErrorAction SilentlyContinue
    if ($eccContent) {
        foreach ($kw in $breakingKeywords) {
            if ($eccContent -match "(?i)$kw") {
                $changelogIssues += "ECC changelog mentions: $kw"
            }
        }
    }
} else {
    Write-Skip "CHANGELOG_ECC.md not found"
}

if (Test-Path $changelogRouter) {
    Write-Info "CHANGELOG_9ROUTER.md"
    $routerLines = Get-Content $changelogRouter -First 15 -ErrorAction SilentlyContinue
    if ($routerLines) {
        foreach ($line in $routerLines) {
            Write-Host "    $line" -ForegroundColor Gray
        }
    }
    $routerContent = Get-Content $changelogRouter -Raw -ErrorAction SilentlyContinue
    if ($routerContent) {
        foreach ($kw in $breakingKeywords) {
            if ($routerContent -match "(?i)$kw") {
                $changelogIssues += "9Router changelog mentions: $kw"
            }
        }
    }
} else {
    Write-Skip "CHANGELOG_9ROUTER.md not found"
}

if ($changelogIssues.Count -gt 0) {
    Write-Host ""
    Write-Host "  WARNING: Potential breaking changes detected:" -ForegroundColor Yellow
    foreach ($issue in $changelogIssues) {
        Write-Host "    - $issue" -ForegroundColor Yellow
    }
    Write-Host "  Review changelogs before proceeding." -ForegroundColor Yellow
}

# ============================================================
# Step 3/4: Doctor Check
# ============================================================

Write-Step "3/4" "Doctor Check"

$issues = @()

if (-not (Test-Path "$($script:ECC_DIR)\AGENTS.md")) {
    $issues += "ECC not found - run: .\scripts\setup.ps1"
}

if (-not (Test-Path "$($script:ROUTER_DIR)\package.json")) {
    $issues += "9Router not found - run: .\scripts\setup.ps1"
}

if (-not (Test-Path $script:OPENCODE_CFG)) {
    $issues += "OpenCode config not found - run: .\scripts\setup.ps1"
}

try {
    $null = Invoke-RestMethod -Uri "$($script:API_URL)/api/health" -TimeoutSec 3 -ErrorAction Stop
} catch {
    $issues += "9Router not running - start with: .\scripts\start.ps1"
}

$mode = Get-LLMMode
if ($mode -ne "eco") {
    try {
        $null = Invoke-RestMethod -Uri "$($script:OLLAMA_URL)/api/tags" -TimeoutSec 3 -ErrorAction Stop
    } catch {
        $issues += "Ollama not running (mode: $mode) - start with: .\scripts\llm-mode.ps1 on"
    }
}

Write-Host ""
Write-Host "  Root:           $($script:ROOT_DIR)" -ForegroundColor Gray
Write-Host "  ECC:            $($script:ECC_DIR)" -ForegroundColor Gray
Write-Host "  9Router:        $($script:ROUTER_DIR)" -ForegroundColor Gray
Write-Host "  OpenCode:       $($script:OPENCODE_CFG)" -ForegroundColor Gray
Write-Host "  LLM mode:       $mode" -ForegroundColor Gray
Write-Host ""

if ($issues.Count -eq 0) {
    Write-OK "All checks passed"
} else {
    foreach ($issue in $issues) {
        Write-Fail $issue
    }
}

# ============================================================
#  Step 3b/4: Ensure 9Router Running
# ============================================================

Write-Step "3b/4" "Ensure 9Router Running"

$routerHealthy = $false
try {
    $null = Invoke-RestMethod -Uri "$($script:API_URL)/api/health" -TimeoutSec 3 -ErrorAction Stop
    $routerHealthy = $true
    Write-OK "9Router is healthy"
} catch {}

if (-not $routerHealthy) {
    Write-Host "  9Router not running, starting..." -ForegroundColor Yellow
    if (Start-9Router) {
        Write-OK "9Router started successfully"
        $issues = $issues | Where-Object { $_ -notmatch "9Router not running" }
    }
}

# ============================================================
# Step 4/4: Summary
# ============================================================

Write-Step "4/4" "Summary"

Write-Host ""
if ($issues.Count -eq 0) {
    Write-Host "  All systems operational." -ForegroundColor Green
} else {
    Write-Host "  $($issues.Count) issue(s) found. Fix above." -ForegroundColor Yellow
}
Write-Host ""

Write-TaskLog -Stage "OWNER" -Action "Maintenance completed ($($issues.Count) issues)" -Result $(if ($issues.Count -eq 0) { "success" } else { "fail" })
