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
