# Enrichment Pipeline - Structured intent classification via local LLM
# Usage: . "$PSScriptRoot\enrichment-pipeline.ps1"
# Depends on: helpers.ps1 (Invoke-LLM, Get-LLMMode, Get-LLMModel)

# -- Intent Classification via Local LLM --

function Invoke-StructuredEnrichment {
    param(
        [Parameter(Mandatory)][string]$TextInput,
        [string]$Context = "",
        [switch]$Force
    )

    $mode = Get-LLMMode
    if ($mode -eq "eco" -and -not $Force) { return $null }
    if ($TextInput.Split(' ').Count -lt 3 -and -not $Force) { return $null }

    $contextBlock = if ($Context) { "`nProject context: $Context`n" } else { "" }

    $systemPrompt = @"
You are a structured intent classifier. Analyze user input and return ONLY valid JSON.

Return this exact schema (no markdown, no explanation, no code fences):
{
  "intent": "<build|fix|review|deploy|research|docs|ask>",
  "domain": "<web|mobile|infra|data|ai_ml|automation|general>",
  "stack": ["<detected framework or language>"],
  "complexity": "<low|medium|high|critical>",
  "confidence": <0.0 to 1.0>
}

Domain classification rules:
- web: APIs, REST endpoints, CRUD, frontend, backend, authentication, web frameworks (React, Django, FastAPI, Express, Laravel, NestJS)
- mobile: Flutter, Dart, iOS, Android, Swift, Kotlin, React Native
- infra: Docker, Kubernetes, CI/CD, deployment, server configuration, networking
- data: databases, SQL, migrations, ETL, data pipelines, PostgreSQL, MySQL, Redis
- ai_ml: machine learning, model training, inference, LLM, PyTorch, TensorFlow
- automation: PowerShell, scripts, task automation, scheduling, Windows automation
- general: programming concepts, generic questions, unclear domain

Stack detection: identify specific technologies mentioned (e.g., ["python", "fastapi"], ["flutter", "dart"])

Complexity rules:
- low: simple question, one-line fix, typo
- medium: feature implementation, bug fix
- high: architectural change, multi-file refactor, system design
- critical: security vulnerability, production down

Return ONLY the JSON object, nothing else.
"@

    $prompt = "User input: $TextInput$contextBlock"
    $model = Get-LLMModel
    $maxTokens = 150
    $timeout = 45

    $result = Invoke-LLM -Prompt $prompt -System $systemPrompt -Model $model -MaxTokens $maxTokens -Temperature 0.1 -TimeoutSec $timeout
    if (-not $result) { return $null }

    $responseText = $result.response.Trim()

    # Strip markdown code fences if present
    $responseText = $responseText -replace '```json\s*', '' -replace '```\s*$', ''
    $responseText = $responseText.Trim()

    # Try parse JSON
    try {
        $parsed = $responseText | ConvertFrom-Json

        # Validate required fields
        $validIntents = @("build", "fix", "review", "deploy", "research", "docs", "ask")
        $validDomains = @("web", "mobile", "infra", "data", "ai_ml", "automation", "general")
        $validComplexity = @("low", "medium", "high", "critical")

        $intent = if ($validIntents -contains $parsed.intent) { $parsed.intent } else { "ask" }
        $domain = if ($validDomains -contains $parsed.domain) { $parsed.domain } else { "general" }
        $complexity = if ($validComplexity -contains $parsed.complexity) { $parsed.complexity } else { "medium" }
        $stack = @()
        if ($parsed.stack -is [array]) { $stack = $parsed.stack }
        elseif ($parsed.stack) { $stack = @($parsed.stack) }
        # Strip angle brackets from stack items
        $stack = $stack | ForEach-Object { $_ -replace '^<|>$', '' } | Where-Object { $_ }
        $confidence = if ($parsed.confidence -gt 0) { [math]::Min(1.0, [math]::Max(0.0, $parsed.confidence)) } else { 0.5 }

        return @{
            intent     = $intent
            domain     = $domain
            stack      = $stack
            complexity = $complexity
            confidence = $confidence
            source     = "structured"
            raw        = $parsed
        }
    } catch {
        # JSON parse failed - try regex extraction fallback
        $intentMatch = [regex]::Match($responseText, '"intent"\s*:\s*"(\w+)"')
        $domainMatch = [regex]::Match($responseText, '"domain"\s*:\s*"(\w+)"')
        $complexityMatch = [regex]::Match($responseText, '"complexity"\s*:\s*"(\w+)"')

        $intent = if ($intentMatch.Success) { $intentMatch.Groups[1].Value } else { "ask" }
        $domain = if ($domainMatch.Success) { $domainMatch.Groups[1].Value } else { "general" }
        $complexity = if ($complexityMatch.Success) { $complexityMatch.Groups[1].Value } else { "medium" }

        return @{
            intent     = $intent
            domain     = $domain
            stack      = @()
            complexity = $complexity
            confidence = 0.4
            source     = "regex_fallback"
            raw        = $responseText
        }
    }
}

# -- Quick Intent Fallback (no LLM, pattern-based) --

function Get-QuickIntent {
    param([string]$TextInput)

    $inputLower = $TextInput.ToLower().Trim()
    $domain = "general"
    $stack = @()

    # Detect domain from keywords
    if ($inputLower -match '(react|nextjs|next\.js|vue|angular|frontend|ui|css|html|api|rest|express|fastapi|django|laravel|spring|nest)') { $domain = "web" }
    elseif ($inputLower -match '(flutter|dart|kotlin|android|ios|swift|compose|mobile|react.native)') { $domain = "mobile" }
    elseif ($inputLower -match '(docker|kubernetes|k8s|ci|cd|deploy|nginx|terraform|ansible|infra)') { $domain = "infra" }
    elseif ($inputLower -match '(postgres|mysql|redis|clickhouse|database|sql|etl|pipeline|data)') { $domain = "data" }
    elseif ($inputLower -match '(pytorch|tensorflow|llm|model|train|inference|ml|ai|gpu|cuda)') { $domain = "ai_ml" }
    elseif ($inputLower -match '(powershell|script|automate|task|schedule|windows|registry|env)') { $domain = "automation" }

    # Detect stack from keywords
    if ($inputLower -match 'python|fastapi|django|flask') { $stack = @("python") }
    elseif ($inputLower -match 'node|javascript|typescript|express|nest') { $stack = @("nodejs") }
    elseif ($inputLower -match 'react|nextjs|next\.js') { $stack = @("react") }
    elseif ($inputLower -match 'flutter|dart') { $stack = @("flutter") }
    elseif ($inputLower -match 'powershell|ps1') { $stack = @("powershell") }
    elseif ($inputLower -match 'go|golang') { $stack = @("golang") }
    elseif ($inputLower -match 'rust|cargo') { $stack = @("rust") }
    elseif ($inputLower -match 'php|laravel') { $stack = @("php") }
    elseif ($inputLower -match 'java|spring') { $stack = @("java") }
    elseif ($inputLower -match 'kotlin') { $stack = @("kotlin") }
    elseif ($inputLower -match 'swift|ios') { $stack = @("swift") }

    if ($inputLower -match '(fix|bug|error|crash|broken|debug)') {
        return @{ intent = "fix"; domain = $domain; stack = $stack; complexity = "medium"; confidence = 0.7 }
    }
    if ($inputLower -match '(review|audit|check|inspect|scan)') {
        return @{ intent = "review"; domain = $domain; stack = $stack; complexity = "medium"; confidence = 0.7 }
    }
    if ($inputLower -match '(deploy|release|ship|publish|ci|cd)') {
        return @{ intent = "deploy"; domain = $domain; stack = $stack; complexity = "high"; confidence = 0.7 }
    }
    if ($inputLower -match '(research|search|find|investigate|compare)') {
        return @{ intent = "research"; domain = $domain; stack = $stack; complexity = "low"; confidence = 0.7 }
    }
    if ($inputLower -match '(write|document|readme|docs|guide)') {
        return @{ intent = "docs"; domain = $domain; stack = $stack; complexity = "low"; confidence = 0.7 }
    }
    if ($inputLower -match '(create|build|make|add|implement|bikin|buat|tambah)') {
        $complexity = "medium"
        if ($inputLower -match '(simple|basic|quick|tipis)') { $complexity = "low" }
        if ($inputLower -match '(full|complex|advanced|enterprise|sistem|api|crud|auth)') { $complexity = "high" }
        return @{ intent = "build"; domain = $domain; stack = $stack; complexity = $complexity; confidence = 0.8 }
    }

    return @{ intent = "ask"; domain = $domain; stack = $stack; complexity = "low"; confidence = 0.6 }
}

# -- Intent Cache (per session) --

$script:IntentCache = @{}

function Get-CachedIntent {
    param([string]$TextInput)
    $hash = ($TextInput -replace '\s+', ' ').ToLower().Trim().GetHashCode()
    return $script:IntentCache[$hash]
}

function Set-CachedIntent {
    param([string]$TextInput, $Intent)
    $hash = ($TextInput -replace '\s+', ' ').ToLower().Trim().GetHashCode()
    $script:IntentCache[$hash] = $Intent
}

function Clear-IntentCache { $script:IntentCache = @{} }

# -- Input Sufficiency Check --
# Detect if user input has enough detail for precise execution.
# Returns: @{ sufficient = $true/$false; reason = "what's missing" }

function Test-InputSufficiency {
    param(
        [string]$TextInput,
        $Classified
    )

    $inputLower = $TextInput.ToLower().Trim()
    $wordCount = ($TextInput -split '\s+').Count
    $intent = if ($Classified) { $Classified.intent } else { "unknown" }
    $domain = if ($Classified) { $Classified.domain } else { "general" }
    $stack = if ($Classified -and $Classified.stack) { $Classified.stack } else { @() }

    # Always sufficient: questions, research, docs (with enough detail)
    $skipIntents = @("research", "docs")
    if ($skipIntents -contains $intent) { return @{ sufficient = $true } }

    # HOLD: ask intent too short — AI should clarify, not just answer
    if ($intent -eq "ask" -and $wordCount -lt 4) {
        return @{
            sufficient = $false
            reason = "Input terlalu singkat. Jelaskan lebih detail apa yang kamu butuhkan."
            missing = @("detail lebih lanjut")
        }
    }

    # Always sufficient: fix with enough detail
    if ($intent -eq "fix" -and $inputLower -match '(bug|error|crash|broken|fix)\s+\w+\s+\w+') {
        return @{ sufficient = $true }
    }

    # Always sufficient: review with enough detail
    if ($intent -eq "review" -and $inputLower -match '(review|audit|check)\s+\w+\s+\w+') {
        return @{ sufficient = $true }
    }

    # Always sufficient: deploy with enough detail
    if ($intent -eq "deploy" -and $inputLower -match '(deploy|release)\s+\w+\s+\w+') {
        return @{ sufficient = $true }
    }

    # HOLD: build intent — needs entity + stack
    if ($intent -eq "build") {
        $missing = @()

        # Check for specific entity (not generic terms)
        $hasEntity = $inputLower -match '(user|product|order|payment|auth|login|register|profile|comment|post|article|task|item|category|admin|customer|invoice|report|dashboard|setting|notification|page|component|form|table|list|modal|menu|sidebar|header|footer|search|filter|cart|checkout|blog|forum|message|chat|email|notification|settings|upload|download|import|export|backup|migrate|sync|validate|verify|approve|reject|assign|schedule|queue|cache|log|monitor|alert|metric|analytics|saas|erp|crm|cms|pos|hrm|lms|iot)'
        if (-not $hasEntity) { $missing += "entity/fitur" }

        # Check for stack/framework
        $hasStack = $stack.Count -gt 0 -and $stack[0] -ne ""
        if (-not $hasStack) {
            $hasStackHint = $inputLower -match '(react|vue|angular|next|nuxt|django|fastapi|laravel|spring|express|nest|flutter|swift|kotlin|python|node|go|rust|php|java|typescript|javascript|powershell|postgres|mysql|redis|docker|kubernetes)'
            if (-not $hasStackHint) { $missing += "tech stack" }
        }

        if ($missing.Count -gt 0) {
            return @{
                sufficient = $false
                reason = "Input kurang presisi. Perlu: $($missing -join ', ')"
                missing = $missing
            }
        }
    }

    # HOLD: fix/deploy too short
    if (($intent -eq "fix" -or $intent -eq "deploy") -and $wordCount -lt 3) {
        return @{
            sufficient = $false
            reason = "Input terlalu singkat untuk '$intent'. Jelaskan apa yang perlu di-$intent."
            missing = @("detail lebih lanjut")
        }
    }

    return @{ sufficient = $true }
}
