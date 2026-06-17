# Detect Project - Auto-detect project type + multi-module kategori
# Usage: .\detect-project.ps1 [-Path "C:\path\to\project"] [-Force]

param(
    [string]$Path = (Get-Location).Path,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$REGISTRY_FILE = "$ROOT_DIR\projects\registry.json"
$SKILL_INDEX_FILE = "$ROOT_DIR\projects\skill-index.json"
$CONTEXT_DIR = "$ROOT_DIR\projects\context"

# ============================================================
# Helpers
# ============================================================

function Write-OK    { param([string]$Message) Write-Host "  [OK] $Message" -ForegroundColor Green }
function Write-Skip  { param([string]$Message) Write-Host "  [SKIP] $Message" -ForegroundColor Yellow }
function Write-Info  { param([string]$Message) Write-Host "  [..] $Message" -ForegroundColor Gray }

function Get-DetectorMarkers {
    if (Test-Path $SKILL_INDEX_FILE) {
        try { return (Get-Content $SKILL_INDEX_FILE -Raw | ConvertFrom-Json).detector_markers } catch {}
    }
    return $null
}

# ============================================================
# Kategori Detection Engine
# ============================================================

function Get-KategoriForFile {
    param([string]$FilePath)

    $ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
    $name = [System.IO.Path]::GetFileName($FilePath).ToLower()
    $dir = [System.IO.Path]::GetFileName([System.IO.Path]::GetDirectoryName($FilePath)).ToLower()

    # Primary files
    $primaryMap = @{
        "pubspec.yaml" = "MOBILE"
        "android/" = "MOBILE"
        "ios/" = "MOBILE"
        "package.json" = "WEB"
        "go.mod" = "WEB"
        "composer.json" = "WEB"
        "requirements.txt" = "WEB"
        "pyproject.toml" = "WEB"
        "Cargo.toml" = "WEB"
        "Gemfile" = "WEB"
        "pom.xml" = "WEB"
        "build.gradle" = "WEB"
        "Dockerfile" = "INFRA"
        "docker-compose.yml" = "INFRA"
        "render.yaml" = "INFRA"
        ".github/workflows/" = "INFRA"
        "schema.prisma" = "DATA"
        "migrations/" = "DATA"
        "supabase/" = "DATA"
        "supabase" = "DATA"
        "*.ps1" = "AUTOMATION"
        "*.sh" = "AUTOMATION"
    }

    foreach ($key in $primaryMap.Keys) {
        if ($key -like "*\*") {
            $pattern = $key.TrimEnd('*')
            if ($name -like "$pattern*") { return $primaryMap[$key] }
        } elseif ($key -like "*/") {
            $folder = $key.TrimEnd('/')
            if ($dir -eq $folder) { return $primaryMap[$key] }
        } elseif ($name -eq $key) {
            return $primaryMap[$key]
        }
    }

    # Extension-based
    $extMap = @{
        ".dart" = "MOBILE"
        ".kt" = "MOBILE"
        ".kts" = "MOBILE"
        ".swift" = "MOBILE"
        ".ts" = "WEB"
        ".tsx" = "WEB"
        ".js" = "WEB"
        ".jsx" = "WEB"
        ".vue" = "WEB"
        ".php" = "WEB"
        ".py" = "WEB"
        ".java" = "WEB"
        ".go" = "WEB"
        ".rb" = "WEB"
        ".rs" = "WEB"
        ".cs" = "WEB"
        ".yaml" = "INFRA"
        ".yml" = "INFRA"
        ".tf" = "INFRA"
        ".sql" = "DATA"
    }

    if ($extMap.ContainsKey($ext)) { return $extMap[$ext] }

    # Directory-based
    $dirMap = @{
        "android" = "MOBILE"
        "ios" = "MOBILE"
        "frontend" = "MOBILE"
        "mobile" = "MOBILE"
        "backend" = "WEB"
        "api" = "WEB"
        "server" = "WEB"
        "web" = "WEB"
        "infra" = "INFRA"
        "deploy" = "INFRA"
        "docker" = "INFRA"
        "scripts" = "AUTOMATION"
        "hooks" = "AUTOMATION"
        "data" = "DATA"
        "database" = "DATA"
    }

    if ($dirMap.ContainsKey($dir)) { return $dirMap[$dir] }

    return "AUTOMATION"
}

function Get-KategoriForModule {
    param([string]$ModulePath)

    $files = Get-ChildItem -Path $ModulePath -File -ErrorAction SilentlyContinue
    $dirs = Get-ChildItem -Path $ModulePath -Directory -ErrorAction SilentlyContinue

    $kategoriScores = @{
        "MOBILE" = 0
        "WEB" = 0
        "INFRA" = 0
        "DATA" = 0
        "AUTOMATION" = 0
        "AI_ML" = 0
    }

    # Score files
    foreach ($file in $files) {
        $kat = Get-KategoriForFile -FilePath $file.FullName
        if ($kategoriScores.ContainsKey($kat)) { $kategoriScores[$kat] += 2 }
    }

    # Score directories
    foreach ($dir in $dirs) {
        $dirName = $dir.Name.ToLower()
        $dirScoreMap = @{
            "android" = "MOBILE"; "ios" = "MOBILE"
            "frontend" = "MOBILE"; "mobile" = "MOBILE"
            "backend" = "WEB"; "api" = "WEB"; "server" = "WEB"
            "infra" = "INFRA"; "deploy" = "INFRA"; "docker" = "INFRA"
        "scripts" = "AUTOMATION"; "hooks" = "AUTOMATION"
        "data" = "DATA"; "database" = "DATA"; "migrations" = "DATA"; "supabase" = "DATA"
            "ml" = "AI_ML"; "ai" = "AI_ML"; "model" = "AI_ML"
        }
        if ($dirScoreMap.ContainsKey($dirName)) { $kategoriScores[$dirScoreMap[$dirName]] += 3 }
    }

    # Check primary markers in module
    $moduleName = (Get-Item $ModulePath).Name.ToLower()
    $primaryMap = @{
        "frontend" = "MOBILE"
        "android" = "MOBILE"
        "ios" = "MOBILE"
        "mobile" = "MOBILE"
        "backend" = "WEB"
        "api" = "WEB"
        "server" = "WEB"
        "web" = "WEB"
        "infra" = "INFRA"
        "deploy" = "INFRA"
        "scripts" = "AUTOMATION"
        "db" = "DATA"
        "database" = "DATA"
        "supabase" = "DATA"
    }

    if ($primaryMap.ContainsKey($moduleName)) {
        $kategoriScores[$primaryMap[$moduleName]] += 5
    }

    # Package-specific detection
    $packageJson = Join-Path $ModulePath "package.json"
    if (Test-Path $packageJson) {
        try {
            $pkg = Get-Content $packageJson -Raw | ConvertFrom-Json
            $allDeps = @{}
            if ($pkg.dependencies) { $pkg.dependencies.PSObject.Properties | ForEach-Object { $allDeps[$_.Name] = $_.Value } }
            if ($pkg.devDependencies) { $pkg.devDependencies.PSObject.Properties | ForEach-Object { $allDeps[$_.Name] = $_.Value } }

            $mobileDeps = @("flutter", "react-native", "nativescript", "cordova", "expo", "dart")
            $webDeps = @("react", "react-dom", "next", "vue", "nuxt", "@angular/core",
                        "@nestjs/core", "express", "fastify", "hono",
                        "prisma", "typeorm", "drizzle-orm",
                        "tailwindcss", "bootstrap", "chakra-ui", "antd",
                        "axios", "react-router", "react-query")

            foreach ($dep in $allDeps.Keys) {
                if ($mobileDeps -contains $dep) { $kategoriScores["MOBILE"] += 4 }
                if ($webDeps -contains $dep) { $kategoriScores["WEB"] += 3 }
            }
        } catch {}
    }

    # pubspec.yaml detection
    $pubspec = Join-Path $ModulePath "pubspec.yaml"
    if (Test-Path $pubspec) {
        try {
            $content = Get-Content $pubspec -Raw
            if ($content -match "flutter") { $kategoriScores["MOBILE"] += 5 }
            if ($content -match "dart") { $kategoriScores["MOBILE"] += 2 }
        } catch {}
    }

    # Winner
    $top = $kategoriScores.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1
    if ($top.Value -ge 3) { return $top.Key }

    return "AUTOMATION"
}

# ============================================================
# Multi-Module Scan
# ============================================================

function Invoke-ModuleScan {
    param([string]$ProjectPath)

    $modules = @{}
    $topDirs = Get-ChildItem -Path $ProjectPath -Directory -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -notmatch '^(\.git|node_modules|\.next|build|dist|\.dart_tool|\.pub-cache)$'
    }

    # Score root files
    $rootKategori = Get-KategoriForModule -ModulePath $ProjectPath
    if ($rootKategori -ne "AUTOMATION") {
        $modules["/"] = $rootKategori
    }

    # Score each top-level directory
    foreach ($dir in $topDirs) {
        $moduleKey = $dir.Name + "/"
        $kat = Get-KategoriForModule -ModulePath $dir.FullName
        Write-Info "    Module: $moduleKey → $kat"
        $modules[$moduleKey] = $kat
    }

    return $modules
}

# ============================================================
# AI Scan (Enrichment mode only)
# ============================================================

function Invoke-AIScan {
    param(
        [string]$ProjectPath,
        [hashtable]$Modules
    )

    $llmAdapter = "$ROOT_DIR\scripts\llm-adapter.ps1"
    if (-not (Test-Path $llmAdapter)) { return $Modules }

    try {
        . $llmAdapter
        $mode = Get-OperatingMode
        if ($mode -ne "on") { return $Modules }
    } catch { return $Modules }

    $moduleSummary = @()
    foreach ($key in $Modules.Keys) {
        $moduleSummary += "  - $key → $($Modules[$key])"
    }

    $prompt = @"
Analyze this project structure and recommend kategori per module.

Project: $(Split-Path $ProjectPath -Leaf)
Path: $ProjectPath

Modules detected by static scan:
$($moduleSummary -join "`n")

Available kategori: MOBILE, WEB, INFRA, DATA, AI_ML, AUTOMATION

Rules:
- MOBILE: flutter, dart, kotlin, swift, react-native
- WEB: nestjs, react, vue, angular, laravel, django, nextjs, node/express
- INFRA: docker, k8s, ci/cd, deploy configs
- DATA: database, migrations, analytics
- AI_ML: ML models, training, notebooks
- AUTOMATION: scripts, hooks, devops

Return ONLY a JSON object like:
{
  "modules": {
    "frontend/": "MOBILE",
    "backend/": "WEB"
  },
  "note": "(optional reasoning)"
}
"@

    $result = Invoke-LLM -Prompt $prompt -System "You are a project classifier. Return only valid JSON." -MaxTokens 300 -Temperature 0.1
    if (-not $result) { return $Modules }

    try {
        $parsed = $result.response | ConvertFrom-Json
        if ($parsed.modules) {
            $parsed.modules.PSObject.Properties | ForEach-Object {
                $modules[$_.Name] = $_.Value
            }
        }
    } catch {
        Write-Skip "AI scan returned unparseable result, using static scan"
    }

    return $Modules
}

# ============================================================
# Main
# ============================================================

Write-Host ""
Write-Host "  farewell-assistant - Project Detection" -ForegroundColor Cyan
Write-Host "  Path: $Path" -ForegroundColor Gray
Write-Host ""

# --- Detect Type (legacy) ---
$detectedType = "unknown"
$slug = (Get-Item $Path).Name.ToLower() -replace '[^a-z0-9\-]', '-'
$slug = $slug.Trim('-')

$legacyChecks = @(
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

foreach ($check in $legacyChecks) {
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

# Monorepo fallback: check subdirectories
if ($detectedType -eq "unknown") {
    $subChecks = @(
        "backend/package.json"
        "frontend/pubspec.yaml"
        "backend/composer.json"
        "backend/go.mod"
        "backend/Cargo.toml"
        "backend/Gemfile"
    )
    foreach ($subCheck in $subChecks) {
        $subPath = Join-Path $Path $subCheck
        if (Test-Path $subPath) {
            if ($subCheck -match "pubspec") { $detectedType = "flutter" }
            elseif ($subCheck -match "package.json") { $detectedType = "node" }
            elseif ($subCheck -match "composer.json") { $detectedType = "php" }
            elseif ($subCheck -match "go.mod") { $detectedType = "go" }
            elseif ($subCheck -match "Cargo.toml") { $detectedType = "rust" }
            elseif ($subCheck -match "Gemfile") { $detectedType = "ruby" }
            Write-OK ("Detected (sub): $detectedType via $subCheck")
            break
        }
    }

    if ($detectedType -eq "unknown") {
        Write-Skip "No characteristic files found. Type: unknown"
    }
}

# --- Multi-Module Scan ---
Write-Host ""
Write-Info "Scanning modules for kategori..."
$modules = Invoke-ModuleScan -ProjectPath $Path

# Optional AI enhancement
Write-Info "Running AI enrichment (if mode=ON)..."
$modules = Invoke-AIScan -ProjectPath $Path -Modules $modules

# Determine dominant kategori (weighted by file count + module)
$kategoriWeights = @{
    "MOBILE" = 0
    "WEB" = 0
    "INFRA" = 0
    "DATA" = 0
    "AI_ML" = 0
    "AUTOMATION" = 0
}
foreach ($key in $modules.Keys) {
    $kat = $modules[$key]
    $modulePath = Join-Path $Path $key.Replace('/','')
    $fileCount = 0
    if (Test-Path $modulePath) {
        $fileCount = (Get-ChildItem -Path $modulePath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    }
    $weight = if ($fileCount -gt 0) { [math]::Max(1, $fileCount / 10) } else { 1 }
    $kategoriWeights[$kat] += $weight
}
$sortedKat = $kategoriWeights.GetEnumerator() | Sort-Object Value -Descending
$dominantKategori = $sortedKat | Select-Object -First 1 | ForEach-Object { $_.Name }
$secondaryKat = $sortedKat | Select-Object -Skip 1 -First 2 | Where-Object { $_.Value -gt 0 } | ForEach-Object { $_.Name }

# Build dominant display (core categories)
$coreCategories = @("MOBILE", "WEB", "AI_ML")
$dominantKatParts = @($dominantKategori)
foreach ($sec in $secondaryKat) {
    $secWeight = $kategoriWeights[$sec]
    $domWeight = $kategoriWeights[$dominantKategori]
    if ($coreCategories -contains $sec -and $secWeight -gt ($domWeight * 0.5)) {
        $dominantKatParts += $sec
    }
}
$dominantKategori = $dominantKatParts -join "+"

# Build full display string (all unique)
$allKategori = $modules.Values | Sort-Object -Unique
$kategoriDisplay = $allKategori -join "+"

Write-Host ""
Write-OK "Modules scanned: $($modules.Count)"
foreach ($key in ($modules.Keys | Sort-Object)) {
    $icon = switch ($modules[$key]) {
        "MOBILE" { "📱" }
        "WEB" { "🌐" }
        "INFRA" { "⚙️" }
        "DATA" { "🗄️" }
        "AI_ML" { "🤖" }
        "AUTOMATION" { "🔧" }
        default { "📁" }
    }
    Write-Host "    $icon $key → $($modules[$key])"
}

# --- Update Registry ---
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

$kategori = @{}
foreach ($key in $modules.Keys) {
    $kategori[$key] = $modules[$key]
}

$registry.projects[$slug] = @{
    path = $cleanPath
    type = $detectedType
    kategori = $kategori
    dominan = $dominantKategori
    context_file = "context/$slug.md"
    last_used = $today
}

New-Item -ItemType Directory -Path (Split-Path $REGISTRY_FILE -Parent) -Force | Out-Null
$registry | ConvertTo-Json -Depth 5 | Set-Content -Path $REGISTRY_FILE -Encoding UTF8

Write-Host ""
Write-Host "  Registry updated:" -ForegroundColor Green
Write-Host "    Active:   $slug" -ForegroundColor White
Write-Host "    Type:     $detectedType" -ForegroundColor White
Write-Host "    Kategori: $kategoriDisplay" -ForegroundColor White
Write-Host "    Dominan:  $dominantKategori" -ForegroundColor White
Write-Host "    Path:     $cleanPath" -ForegroundColor White
Write-Host ""

# --- Create Context File ---
$contextFile = Join-Path $CONTEXT_DIR ($slug + ".md")
if (-not (Test-Path $contextFile) -or $Force) {
    New-Item -ItemType Directory -Path $CONTEXT_DIR -Force | Out-Null

    $lines = @(
        "# $slug",
        "",
        "Type: $detectedType",
        "Path: $cleanPath",
        "Kategori: $kategoriDisplay",
        "Focus: (describe current focus)",
        "Key files: (list important directories/files)"
    )
    $lines | Set-Content -Path $contextFile -Encoding UTF8
    Write-OK "Context file created: $contextFile"
}

Write-Host ""
