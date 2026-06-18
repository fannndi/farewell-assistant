# detect-project.ps1 - Detect project type from directory markers
# Usage:
#   .\detect-project.ps1                              Detect in current dir
#   .\detect-project.ps1 -Path "C:\my-project"        Detect in given path
#   .\detect-project.ps1 -Path "..." -EmitContext     Emit context template markdown

param(
    [string]$Path = (Get-Location).Path,
    [switch]$EmitContext
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$script:ROOT_DIR = Split-Path -Parent $PSScriptRoot
. "$PSScriptRoot\common\helpers.ps1"
. "$PSScriptRoot\common\config.ps1"
. "$PSScriptRoot\common\log.ps1"

if (-not (Test-Path -LiteralPath $Path)) {
    Write-Fail "Path not found: $Path"
    exit 1
}

# Marker -> project type mapping (ordered by specificity)
$Markers = [ordered]@{
    "pubspec.yaml"           = @{ Type = "Flutter"; Stack = "Flutter + Dart" }
    "go.mod"                 = @{ Type = "Go"; Stack = "Go module" }
    "Cargo.toml"             = @{ Type = "Rust"; Stack = "Rust + Cargo" }
    "composer.json"          = @{ Type = "PHP/Laravel"; Stack = "PHP + Composer" }
    "Gemfile"                = @{ Type = "Ruby"; Stack = "Ruby + Bundler" }
    "requirements.txt"       = @{ Type = "Python"; Stack = "Python + pip" }
    "pyproject.toml"         = @{ Type = "Python"; Stack = "Python + PEP 621" }
    "package.json"           = @{ Type = "Node"; Stack = "Node.js + npm" }
    "tsconfig.json"          = @{ Type = "TypeScript"; Stack = "TypeScript" }
    "*.csproj"               = @{ Type = ".NET"; Stack = "C# / .NET" }
    "*.vbproj"               = @{ Type = ".NET"; Stack = "VB.NET / .NET" }
    "Pipfile"                = @{ Type = "Python"; Stack = "Python + Pipenv" }
    "mix.exs"                = @{ Type = "Elixir"; Stack = "Elixir + Mix" }
    "build.gradle"           = @{ Type = "Java/Kotlin"; Stack = "JVM + Gradle" }
    "build.gradle.kts"       = @{ Type = "Java/Kotlin"; Stack = "JVM + Gradle KTS" }
    "pom.xml"                = @{ Type = "Java"; Stack = "Java + Maven" }
}

# Heuristics for sub-type refinement
function Test-FileContains {
    param([string]$File, [string]$Pattern)
    if (-not (Test-Path -LiteralPath $File)) { return $false }
    try { (Get-Content -LiteralPath $File -Raw) -match $Pattern } catch { $false }
}

function Refine-NodeType {
    param([string]$Root)
    $pkg = Join-Path $Root "package.json"
    if (-not (Test-Path -LiteralPath $pkg)) { return "Node.js" }
    if (Test-FileContains $pkg '"next"') { return "Next.js" }
    if (Test-FileContains $pkg '"nuxt"') { return "Nuxt" }
    if (Test-FileContains $pkg '"vue"') { return "Vue" }
    if (Test-FileContains $pkg '"react"') { return "React" }
    if (Test-FileContains $pkg '"express"') { return "Express" }
    if (Test-FileContains $pkg '"nestjs"') { return "NestJS" }
    if (Test-FileContains $pkg '"svelte"') { return "Svelte" }
    return "Node.js"
}

function Refine-PHPType {
    param([string]$Root)
    $composer = Join-Path $Root "composer.json"
    if (-not (Test-Path -LiteralPath $composer)) { return "PHP" }
    if (Test-FileContains $composer '"laravel/framework"') { return "Laravel" }
    if (Test-FileContains $composer '"symfony/symfony"') { return "Symfony" }
    return "PHP"
}

# -- Detect --

Write-Step "DETECT" "Project type detection"
Write-Info "Path: $Path"

$detected = $null
$subType = $null
$stack = $null

foreach ($kv in $Markers.GetEnumerator()) {
    $marker = $kv.Key
    $info = $kv.Value
    if ($marker.StartsWith("*")) {
        # Glob pattern (e.g. *.csproj)
        $pattern = $marker
        $matches = Get-ChildItem -LiteralPath $Path -Filter $pattern -ErrorAction SilentlyContinue
        if ($matches) {
            $detected = $info.Type
            $stack = $info.Stack
            break
        }
    } else {
        $file = Join-Path $Path $marker
        if (Test-Path -LiteralPath $file) {
            $detected = $info.Type
            $stack = $info.Stack
            if ($detected -eq "Node") { $subType = Refine-NodeType -Root $Path }
            if ($detected -eq "PHP/Laravel") { $subType = Refine-PHPType -Root $Path }
            break
        }
    }
}

if (-not $detected) {
    Write-Fail "No project markers found in $Path"
    Write-Info "Supported markers: $($Markers.Keys -join ', ')"
    Write-TaskLog -Stage "DETECT" -Action "Detect $Path" -Result "fail" -Files $Path
    exit 1
}

$displayType = if ($subType) { "$detected ($subType)" } else { $detected }
Write-OK "Type: $displayType"
Write-OK "Stack: $stack"

# Suggest context template
if ($EmitContext) {
    $slug = (Split-Path -Leaf $Path) -replace '[^a-z0-9-]', '-' -replace '-+', '-'
    $ctxFile = "$($script:CONTEXT_DIR)\$slug.md"
    if (-not (Test-Path $script:CONTEXT_DIR)) {
        New-Item -ItemType Directory -Path $script:CONTEXT_DIR -Force | Out-Null
    }
    $template = @"
# $slug

Type: $displayType
Path: $($Path -replace '\\','/')
Stack: $stack
Focus: (describe current focus)
Key files: (list important directories/files)
"@
    Set-Content -Path $ctxFile -Value $template -Encoding UTF8
    Write-OK "Context template written: $ctxFile"
    Write-Info "Edit it to add focus + key files, then register in projects/registry.json"
}

Write-TaskLog -Stage "DETECT" -Action "Detect $Path -> $displayType" -Result "success" -Files $Path
