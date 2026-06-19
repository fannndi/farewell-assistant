# Generate Test Cases — Domain Knowledge Based
# Generates test cases for Intent-Driven Pipeline training
# Focus: mobile, flutter, kotlin, rust domains
# Usage: .\generate-cases.ps1 -Count 200

param([int]$Count = 200)

# Ensure valid count
if ($Count -lt 1) { $Count = 200 }

$ErrorActionPreference = "Continue"

# -- Test Case Templates per Intent × Domain --
# Format: @{ intent; domain; templates; expected_complexity; expected_hold }

$Templates = @(
    # ============================
    # BUILD × MOBILE
    # ============================
    @{ intent = "build"; domain = "mobile"; templates = @(
        "bikin login screen dengan {framework} dan {feature}",
        "add push notification untuk user di {platform}",
        "implementasi state management {framework} di profile page",
        "bikin {feature} dengan {framework} untuk {platform}",
        "create {feature} di mobile app pakai {framework}",
        "build {feature} untuk {platform} pakai {framework}",
        "tambahkan {feature} ke {framework} app",
        "implement {feature} di {platform} menggunakan {framework}"
    ); complexity = "medium"; hold = $false },

    @{ intent = "build"; domain = "mobile"; templates = @(
        "bikin aplikasi {feature} dengan {framework} dari awal",
        "refactor {feature} di {framework} app pakai clean architecture"
    ); complexity = "high"; hold = $false },

    @{ intent = "build"; domain = "mobile"; templates = @(
        "bikin button",
        "tambah fitur"
    ); complexity = "low"; hold = $true },

    # ============================
    # BUILD × WEB
    # ============================
    @{ intent = "build"; domain = "web"; templates = @(
        "bikin {feature} dengan {framework} dan {stack}",
        "create {feature} API pakai {framework}",
        "implementasi {feature} di {framework} menggunakan {stack}",
        "tambahkan {feature} ke {framework} app"
    ); complexity = "medium"; hold = $false },

    @{ intent = "build"; domain = "web"; templates = @(
        "bikin CRUD {feature} dengan auth dan validasi",
        "build microservices {feature} dengan {framework}"
    ); complexity = "high"; hold = $false },

    @{ intent = "build"; domain = "web"; templates = @(
        "bikin API",
        "buat webpage"
    ); complexity = "low"; hold = $true },

    # ============================
    # BUILD × INFRA
    # ============================
    @{ intent = "build"; domain = "infra"; templates = @(
        "setup {tool} untuk {feature}",
        "config {tool} deployment pipeline",
        "implement {feature} di {tool}"
    ); complexity = "medium"; hold = $false },

    # ============================
    # BUILD × RUST
    # ============================
    @{ intent = "build"; domain = "general"; templates = @(
        "build CLI tool dengan {framework} untuk {feature}",
        "implement {feature} pakai Rust dan Tokio"
    ); complexity = "medium"; hold = $false },

    # ============================
    # FIX × MOBILE
    # ============================
    @{ intent = "fix"; domain = "mobile"; templates = @(
        "fix {bug} di {framework} {platform} app",
        "perbaiki {bug} di {framework} {feature}",
        "debug {bug} pada {framework} component",
        "resolve {bug} di {platform} {framework}"
    ); complexity = "medium"; hold = $false },

    @{ intent = "fix"; domain = "mobile"; templates = @(
        "fix bug"
    ); complexity = "low"; hold = $true },

    # ============================
    # FIX × WEB
    # ============================
    @{ intent = "fix"; domain = "web"; templates = @(
        "fix {bug} di {framework} {feature}",
        "perbaiki error {bug} di {stack} {feature}",
        "debug {bug} pada {framework} endpoint"
    ); complexity = "medium"; hold = $false },

    # ============================
    # FIX × KOTLIN
    # ============================
    @{ intent = "fix"; domain = "mobile"; templates = @(
        "fix {bug} di Kotlin {feature}",
        "perbaiki {bug} di KMP {feature}",
        "debug memory leak di Kotlin CoroutineScope"
    ); complexity = "medium"; hold = $false },

    # ============================
    # FIX × RUST
    # ============================
    @{ intent = "fix"; domain = "general"; templates = @(
        "fix {bug} di Rust async function",
        "perbaiki {bug} di Rust {feature}"
    ); complexity = "medium"; hold = $false },

    # ============================
    # REVIEW × MOBILE
    # ============================
    @{ intent = "review"; domain = "mobile"; templates = @(
        "review {area} di {framework} app",
        "audit {area} di {platform} {framework}",
        "check {area} di {framework} codebase",
        "inspect {area} di {framework} project"
    ); complexity = "medium"; hold = $false },

    # ============================
    # REVIEW × KOTLIN
    # ============================
    @{ intent = "review"; domain = "mobile"; templates = @(
        "review Kotlin {feature} implementation",
        "audit KMP {feature} architecture",
        "check Kotlin coroutines di {feature}"
    ); complexity = "medium"; hold = $false },

    # ============================
    # REVIEW × RUST
    # ============================
    @{ intent = "review"; domain = "general"; templates = @(
        "review Rust {feature} implementation",
        "audit error handling di Rust codebase"
    ); complexity = "medium"; hold = $false },

    # ============================
    # DEPLOY × MOBILE
    # ============================
    @{ intent = "deploy"; domain = "mobile"; templates = @(
        "deploy {platform} app ke {target}",
        "publish {framework} app ke app store",
        "release {platform} versi baru"
    ); complexity = "medium"; hold = $false },

    # ============================
    # RESEARCH × ALL
    # ============================
    @{ intent = "research"; domain = "mobile"; templates = @(
        "apa itu {concept} di {framework}?",
        "bandingkan {topic1} vs {topic2} untuk mobile",
        "cari solusi terbaik untuk {feature} di {platform}"
    ); complexity = "low"; hold = $false },

    @{ intent = "research"; domain = "mobile"; templates = @(
        "apa itu"
    ); complexity = "low"; hold = $true },

    # ============================
    # DOCS × ALL
    # ============================
    @{ intent = "docs"; domain = "mobile"; templates = @(
        "write documentation untuk {feature}",
        "create README untuk {framework} project"
    ); complexity = "low"; hold = $false },

    # ============================
    # ASK × ALL
    # ============================
    @{ intent = "ask"; domain = "general"; templates = @(
        "apa itu {concept}?",
        "gimana cara {action}?",
        "perbedaan {concept1} dan {concept2}?"
    ); complexity = "low"; hold = $false },

    @{ intent = "ask"; domain = "general"; templates = @(
        "hai",
        "ok"
    ); complexity = "low"; hold = $true }
)

# -- Variables for Template Expansion --
$frameworks_mobile = @("Flutter", "React Native", "Kotlin Compose", "SwiftUI")
$frameworks_web = @("React", "Next.js", "Vue", "Nuxt", "Angular", "Django", "FastAPI", "Express")
$platforms = @("Android", "iOS", "web")
$features = @("login page", "profile screen", "chat system", "payment gateway", "notification system", "user management", "dashboard", "settings page")
$bugs = @("memory leak", "crash", "slow performance", "layout issue", "navigation bug", "state corruption", "null pointer exception", "timeout error")
$areas = @("security", "performance", "architecture", "UI/UX", "state management")
$tools = @("Docker", "Kubernetes", "GitHub Actions", "Jenkins", "Firebase", "Supabase")
$stacks = @("PostgreSQL", "MongoDB", "Redis", "MySQL")
$concepts = @("closure", "state management", "dependency injection", "clean architecture", "MVVM", "MVI", "routing", "caching")

# -- Generate Test Cases --
$cases = @()
$targetCount = $Count
$perCase = [math]::Ceiling($targetCount / $Templates.Count)

foreach ($tmpl in $Templates) {
    $remainCount = [math]::Min($perCase, $targetCount - $cases.Count)
    for ($i = 0; $i -lt $remainCount; $i++) {
        $input = $tmpl.templates[($i % $tmpl.templates.Count)]
        # Expand variables
        $input = $input -replace '\{framework\}', ($frameworks_mobile + $frameworks_web | Get-Random)
        $input = $input -replace '\{framework\}', ($frameworks_mobile | Get-Random)
        $input = $input -replace '\{platform\}', ($platforms | Get-Random)
        $input = $input -replace '\{feature\}', ($features | Get-Random)
        $input = $input -replace '\{bug\}', ($bugs | Get-Random)
        $input = $input -replace '\{area\}', ($areas | Get-Random)
        $input = $input -replace '\{tool\}', ($tools | Get-Random)
        $input = $input -replace '\{stack\}', ($stacks | Get-Random)
        $input = $input -replace '\{concept\}', ($concepts | Get-Random)
        $input = $input -replace '\{concept1\}', ($concepts | Get-Random)
        $input = $input -replace '\{concept2\}', ($concepts | Get-Random)
        $input = $input -replace '\{topic1\}', ($concepts | Get-Random)
        $input = $input -replace '\{topic2\}', ($concepts | Get-Random)
        $input = $input -replace '\{action\}', ($features | Get-Random)
        $input = $input -replace '\{target\}', ($platforms + @("app store", "play store") | Get-Random)

        $cases += @{
            input = $input
            expected_intent = $tmpl.intent
            expected_domain = $tmpl.domain
            expected_complexity = $tmpl.complexity
            expected_hold = $tmpl.hold
        }
    }
}

# Trim to exact count
if ($cases.Count -gt $targetCount) { $cases = $cases | Sort-Object { Get-Random } | Select-Object -First $targetCount }

# Save
$cases | ConvertTo-Json -Depth 3 | Set-Content -Path "$PSScriptRoot\cases.json" -Encoding UTF8
Write-Host "Generated $($cases.Count) test cases"
Write-Host "  Intent distribution:"
$cases | Group-Object expected_intent | Sort-Object Count -Descending | ForEach-Object { Write-Host "    $($_.Name): $($_.Count)" }
Write-Host "  Domain distribution:"
$cases | Group-Object expected_domain | Sort-Object Count -Descending | ForEach-Object { Write-Host "    $($_.Name): $($_.Count)" }
