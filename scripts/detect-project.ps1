# Detect Project - Auto-detect project type from working directory
# Usage: .\detect-project.ps1 [-Path "C:\path\to\project"]

param(
    [string]$Path = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$REGISTRY_FILE = "$ROOT_DIR\projects\registry.json"
$CONTEXT_DIR = "$ROOT_DIR\projects\context"

# ============================================================
# Helpers
# ============================================================

function Write-OK {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Skip {
    param([string]$Message)
    Write-Host "  [SKIP] $Message" -ForegroundColor Yellow
}

# ============================================================
# Banner
# ============================================================

Write-Host ""
Write-Host "  farewell-assistant - Project Detection" -ForegroundColor Cyan
Write-Host "  Path: $Path" -ForegroundColor Gray
Write-Host ""

# ============================================================
# Detect Type
# ============================================================

$detectedType = "unknown"
$slug = (Get-Item $Path).Name.ToLower() -replace '[^a-z0-9\-]', '-'

$checks = @(
    @{ file = "pubspec.yaml";      type = "flutter";  label = "Flutter" },
    @{ file = "package.json";      type = "node";     label = "Node.js" },
    @{ file = "go.mod";            type = "go";       label = "Go" },
    @{ file = "composer.json";     type = "php";      label = "PHP/Laravel" },
    @{ file = "requirements.txt";  type = "python";   label = "Python" },
    @{ file = "pyproject.toml";    type = "python";   label = "Python" },
    @{ file = "Cargo.toml";        type = "rust";     label = "Rust" },
    @{ file = "*.sln";             type = "dotnet";   label = ".NET" },
    @{ file = "Gemfile";           type = "ruby";     label = "Ruby" }
)

foreach ($check in $checks) {
    $pattern = $check.file
    if ($pattern -match '^\*') {
        $found = Get-ChildItem -Path $Path -Filter $pattern -ErrorAction SilentlyContinue
        if ($found) {
            $detectedType = $check.type
            Write-OK ("Detected: " + $check.label + " (" + $check.file + ")")
            break
        }
    } else {
        $testPath = Join-Path $Path $check.file
        if (Test-Path $testPath) {
            $detectedType = $check.type
            Write-OK ("Detected: " + $check.label + " (" + $check.file + ")")
            break
        }
    }
}

if ($detectedType -eq "unknown") {
    Write-Skip "No characteristic files found. Type: unknown"
}

# ============================================================
# Update Registry
# ============================================================

$registry = @{ active = $slug; projects = @{} }
if (Test-Path $REGISTRY_FILE) {
    try {
        $raw = Get-Content $REGISTRY_FILE -Raw | ConvertFrom-Json
        $projects = @{}
        if ($raw.projects) {
            $raw.projects.PSObject.Properties | ForEach-Object {
                $projects[$_.Name] = $_.Value
            }
        }
        $registry = @{ active = $raw.active; projects = $projects }
    } catch {
        $registry = @{ active = $slug; projects = @{} }
    }
}

$registry.active = $slug
$cleanPath = $Path -replace '\\', '/'
$today = Get-Date -Format "yyyy-MM-dd"
$registry.projects[$slug] = @{
    path = $cleanPath
    type = $detectedType
    context_file = "context/$slug.md"
    last_used = $today
}

New-Item -ItemType Directory -Path (Split-Path $REGISTRY_FILE -Parent) -Force | Out-Null
$registry | ConvertTo-Json -Depth 5 | Set-Content -Path $REGISTRY_FILE -Encoding UTF8

Write-Host ""
Write-Host "  Registry updated:" -ForegroundColor Green
Write-Host "    Active: $slug" -ForegroundColor White
Write-Host "    Type:   $detectedType" -ForegroundColor White
Write-Host "    Path:   $cleanPath" -ForegroundColor White
Write-Host ""

# ============================================================
# Create Context File (if not exists)
# ============================================================

$contextFile = Join-Path $CONTEXT_DIR ($slug + ".md")
if (-not (Test-Path $contextFile)) {
    New-Item -ItemType Directory -Path $CONTEXT_DIR -Force | Out-Null

    $lines = @(
        "# $slug",
        "",
        "Type: $detectedType",
        "Path: $cleanPath",
        "Focus: (describe current focus)",
        "Key files: (list important directories/files)"
    )
    $lines | Set-Content -Path $contextFile -Encoding UTF8

    $createdMsg = "  Context file created: " + $contextFile
    Write-Host $createdMsg -ForegroundColor Gray
}

Write-Host ""
