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
  "complexity": "<low|medium|high>",
  "confidence": <0.0 to 1.0>
}

Rules:
- intent: what the user wants to DO (not just ask about)
- domain: which project category this belongs to
- stack: detected technologies (empty array if unknown)
- complexity: low=simple change, medium=feature, high=architectural
- confidence: how sure you are (be honest)
- Return ONLY the JSON object, nothing else
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
        $validComplexity = @("low", "medium", "high")

        $intent = if ($validIntents -contains $parsed.intent) { $parsed.intent } else { "ask" }
        $domain = if ($validDomains -contains $parsed.domain) { $parsed.domain } else { "general" }
        $complexity = if ($validComplexity -contains $parsed.complexity) { $parsed.complexity } else { "medium" }
        $stack = @()
        if ($parsed.stack -is [array]) { $stack = $parsed.stack }
        elseif ($parsed.stack) { $stack = @($parsed.stack) }
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

    if ($inputLower -match '(fix|bug|error|crash|broken|broken|debug)') {
        return @{ intent = "fix"; complexity = "medium"; confidence = 0.7 }
    }
    if ($inputLower -match '(review|audit|check|inspect|scan)') {
        return @{ intent = "review"; complexity = "medium"; confidence = 0.7 }
    }
    if ($inputLower -match '(deploy|release|ship|publish|ci|cd)') {
        return @{ intent = "deploy"; complexity = "high"; confidence = 0.7 }
    }
    if ($inputLower -match '(research|search|find|investigate|compare)') {
        return @{ intent = "research"; complexity = "low"; confidence = 0.7 }
    }
    if ($inputLower -match '(write|document|readme|docs|guide)') {
        return @{ intent = "docs"; complexity = "low"; confidence = 0.7 }
    }
    if ($inputLower -match '(create|build|make|add|implement|bikin|buat|tambah)') {
        $complexity = "medium"
        if ($inputLower -match '(simple|basic|quick|tipis)') { $complexity = "low" }
        if ($inputLower -match '(full|complex|advanced|enterprise|sistem|api|crud|auth)') { $complexity = "high" }
        return @{ intent = "build"; complexity = $complexity; confidence = 0.8 }
    }

    return @{ intent = "ask"; complexity = "low"; confidence = 0.6 }
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
