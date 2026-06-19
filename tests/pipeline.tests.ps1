# Tests — Get-QuickIntent pure function
. "$PSScriptRoot\test-helper.ps1"

Describe "Get-QuickIntent" {

    It "detects 'fix bug' as fix intent" {
        $r = Get-QuickIntent -TextInput "fix bug auth token expiry"
        $r.intent | Should Be "fix"
        $r.confidence | Should BeExactly 0.7
    }

    It "detects 'bikin CRUD user' as build intent" {
        $r = Get-QuickIntent -TextInput "bikin CRUD user dengan auth"
        $r.intent | Should Be "build"
        $r.confidence | Should BeExactly 0.8
    }

    It "detects 'deploy docker' as deploy intent with infra domain" {
        $r = Get-QuickIntent -TextInput "deploy docker kubernetes cluster"
        $r.intent | Should Be "deploy"
        $r.domain | Should Be "infra"
    }

    It "detects 'review code' as review intent" {
        $r = Get-QuickIntent -TextInput "review code security"
        $r.intent | Should Be "review"
    }

    It "returns 'ask' for unrecognized input" {
        $r = Get-QuickIntent -TextInput "apa itu closure"
        $r.intent | Should Be "ask"
    }
}

Describe "Get-SkillChain" {

    It "returns domain-specific chain for build_web" {
        $chain = Get-SkillChain -Intent "build" -Domain "web"
        $chain.Count | Should Be 8
        $chain[0].name | Should Be "orch-add-feature"
        $chain[-1].name | Should Be "git-workflow"
    }

    It "returns domain-specific chain for build_mobile" {
        $chain = Get-SkillChain -Intent "build" -Domain "mobile"
        $chain.Count | Should Be 7
        $chain[1].name | Should Be "dart-flutter-patterns"
    }

    It "returns fix chain for fix intent" {
        $chain = Get-SkillChain -Intent "fix" -Domain "general"
        $chain.Count | Should Be 3
        $chain[0].name | Should Be "search-first"
    }

    It "returns deploy chain for deploy intent" {
        $chain = Get-SkillChain -Intent "deploy" -Domain "general"
        $chain.Count | Should Be 4
        $chain[0].name | Should Be "production-audit"
    }

    It "returns ask chain for unknown intent" {
        $chain = Get-SkillChain -Intent "unknown" -Domain "general"
        $chain[0].name | Should Be "documentation-lookup"
    }
}

Describe "Test-TaskPermission" {

    It "blocks build intent in PLAN mode" {
        $r = Test-TaskPermission -Intent @{ intent = "build" } -WorkMode "plan"
        $r.allowed | Should Be $false
        $r.reason | Should Match "requires BUILD mode"
    }

    It "allows review intent in PLAN mode" {
        $r = Test-TaskPermission -Intent @{ intent = "review" } -WorkMode "plan"
        $r.allowed | Should Be $true
    }

    It "allows all intents in BUILD mode" {
        $r = Test-TaskPermission -Intent @{ intent = "build" } -WorkMode "build"
        $r.allowed | Should Be $true
    }

    It "allows docs intent in PLAN mode" {
        $r = Test-TaskPermission -Intent @{ intent = "docs" } -WorkMode "plan"
        $r.allowed | Should Be $true
    }
}

Describe "Select-ModelRoute" {

    It "routes low complexity to Free" {
        $r = Select-ModelRoute -Complexity "low" -Profile "eco"
        $r.primary | Should Be "Free"
    }

    It "routes high complexity to Emergency secondary" {
        $r = Select-ModelRoute -Complexity "high" -Profile "eco"
        $r.secondary | Should Be "Emergency"
    }

    It "routes critical to Emergency" {
        $r = Select-ModelRoute -Complexity "critical" -Profile "eco"
        $r.primary | Should Be "Emergency"
    }
}

Describe "Regression Guard" {

    It "all referenced functions exist" {
        # Pastikan fungsi yang dipanggil di pipeline benar-benar ada
        { Get-QuickIntent -TextInput "test" } | Should Not Throw
        { Get-SkillChain -Intent "build" -Domain "web" } | Should Not Throw
        { Test-TaskPermission -Intent @{ intent = "build" } -WorkMode "build" } | Should Not Throw
        { Select-ModelRoute -Complexity "low" -Profile "eco" } | Should Not Throw
    }

    It "Invoke-StructuredEnrichment function exists (not removed)" {
        $cmd = Get-Command -Name "Invoke-StructuredEnrichment" -ErrorAction SilentlyContinue
        $cmd | Should Not BeNullOrEmpty
    }

    It "Invoke-LLMEnrich function was removed" {
        $cmd = Get-Command -Name "Invoke-LLMEnrich" -ErrorAction SilentlyContinue
        $cmd | Should BeNullOrEmpty
    }
}

Describe "Test-InputSufficiency" {

    It "research intent always sufficient" {
        $r = Test-InputSufficiency -TextInput "apa itu closure" -Classified @{ intent = "research"; stack = @() }
        $r.sufficient | Should Be $true
    }

    It "docs intent always sufficient" {
        $r = Test-InputSufficiency -TextInput "write documentation" -Classified @{ intent = "docs"; stack = @() }
        $r.sufficient | Should Be $true
    }

    It "ask with < 4 words triggers hold" {
        $r = Test-InputSufficiency -TextInput "hai" -Classified @{ intent = "ask"; stack = @() }
        $r.sufficient | Should Be $false
    }

    It "ask with detail proceeds" {
        $r = Test-InputSufficiency -TextInput "apa itu closure di JavaScript?" -Classified @{ intent = "ask"; stack = @("javascript") }
        $r.sufficient | Should Be $true
    }

    It "fix with detail proceeds" {
        $r = Test-InputSufficiency -TextInput "fix bug token expired di middleware auth" -Classified @{ intent = "fix"; stack = @() }
        $r.sufficient | Should Be $true
    }

    It "fix too short triggers hold" {
        $r = Test-InputSufficiency -TextInput "fix" -Classified @{ intent = "fix"; stack = @() }
        $r.sufficient | Should Be $false
    }

    It "deploy with detail proceeds" {
        $r = Test-InputSufficiency -TextInput "deploy docker kubernetes production" -Classified @{ intent = "deploy"; stack = @("docker") }
        $r.sufficient | Should Be $true
    }

    It "deploy too short triggers hold" {
        $r = Test-InputSufficiency -TextInput "deploy" -Classified @{ intent = "deploy"; stack = @() }
        $r.sufficient | Should Be $false
    }

    It "build with entity + stack proceeds" {
        $r = Test-InputSufficiency -TextInput "bikin CRUD user dengan auth JWT dan React" -Classified @{ intent = "build"; stack = @("react") }
        $r.sufficient | Should Be $true
    }

    It "build without entity triggers hold" {
        $r = Test-InputSufficiency -TextInput "bikin sesuatu yang bagus" -Classified @{ intent = "build"; stack = @() }
        $r.sufficient | Should Be $false
        $r.reason | Should Match "entity/fitur"
    }

    It "build without stack triggers hold" {
        $r = Test-InputSufficiency -TextInput "bikin user login page" -Classified @{ intent = "build"; stack = @() }
        $r.sufficient | Should Be $false
        $r.reason | Should Match "tech stack"
    }

    It "build with entity but no stack triggers hold" {
        $r = Test-InputSufficiency -TextInput "bikin dashboard admin" -Classified @{ intent = "build"; stack = @() }
        $r.sufficient | Should Be $false
    }

    It "build with entity and stack proceeds" {
        $r = Test-InputSufficiency -TextInput "bikin user management dengan FastAPI dan PostgreSQL" -Classified @{ intent = "build"; stack = @("python") }
        $r.sufficient | Should Be $true
    }

    It "unknown intent with enough words proceeds" {
        $r = Test-InputSufficiency -TextInput "bikin CRUD user dengan auth" -Classified @{ intent = "unknown"; stack = @() }
        $r.sufficient | Should Be $true
    }
}

Describe "Cache Functions" {

    It "Get-CachedIntent returns null for unknown input" {
        $r = Get-CachedIntent -TextInput "unique input $(Get-Random)"
        $r | Should BeNullOrEmpty
    }

    It "Set-CachedIntent stores and Get-CachedIntent retrieves" {
        $testInput = "test cache roundtrip $(Get-Random)"
        $testIntent = @{ intent = "build"; confidence = 0.8 }
        Set-CachedIntent -TextInput $testInput -Intent $testIntent
        $retrieved = Get-CachedIntent -TextInput $testInput
        $retrieved.intent | Should Be "build"
        $retrieved.confidence | Should BeExactly 0.8
    }

    It "Clear-IntentCache empties all cached entries" {
        Set-CachedIntent -TextInput "cache test $(Get-Random)" -Intent @{ intent = "fix" }
        Clear-IntentCache
        $r = Get-CachedIntent -TextInput "cache test $(Get-Random)"
        $r | Should BeNullOrEmpty
    }
}

Describe "Sync-TurnState Output" {

    It "writes pipeline-result.json with required fields on success" {
        $result = @{
            success = $true
            intent = @{ intent = "build"; domain = "web"; complexity = "medium"; confidence = 0.95; source = "structured"; stack = @("react") }
            skill_chain = @(@{ name = "step1"; desc = "first" })
            model_route = @{ primary = "Free"; secondary = "Free"; heavy = "Free" }
            needs_planning = $false
            work_mode = "build"
            profile = "eco"
            turn = 1
            chain_summary = "step1"
        }
        Sync-TurnState -Result $result -UserInput "test input"

        $jsonPath = "$($script:STATE_DIR)\pipeline-result.json"
        Test-Path $jsonPath | Should Be $true
        $json = Get-Content $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $json.intent | Should Be "build"
        $json.domain | Should Be "web"
        $json.input | Should Be "test input"
        $json.turn | Should Be 1
    }

    It "writes pipeline-result.json with hold field on blocked" {
        $result = @{
            success = $false
            hold = $true
            reason = "Input kurang presisi"
            missing = @("entity/fitur")
            intent = @{ intent = "build" }
        }
        Sync-TurnState -Result $result -UserInput "buatkan crud"

        $json = Get-Content "$($script:STATE_DIR)\pipeline-result.json" -Raw -Encoding UTF8 | ConvertFrom-Json
        $json.blocked | Should Be $true
        $json.hold | Should Be $true
        $json.reason | Should Match "presisi"
        $json.input | Should Be "buatkan crud"
    }

    It "writes context.md with Session State and Turn State" {
        $result = @{
            success = $true
            intent = @{ intent = "fix"; domain = "web"; complexity = "medium"; confidence = 0.9; source = "quick"; stack = @() }
            skill_chain = @(@{ name = "a"; desc = "" })
            model_route = @{ primary = "Free"; secondary = "Free"; heavy = "Free" }
            needs_planning = $false
            work_mode = "build"
            profile = "eco"
            turn = 99
            chain_summary = "a"
        }
        Sync-TurnState -Result $result -UserInput "test"
        $ctx = Get-Content "$($script:STATE_DIR)\context.md" -Raw
        $ctx.Contains("Session State") | Should Be $true
        $ctx.Contains("Turn State") | Should Be $true
        $ctx.Contains("fix") | Should Be $true
        $ctx.Contains("99") | Should Be $true
    }
}
