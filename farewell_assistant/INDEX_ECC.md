# ECC Feature Index

> Complete skill, agent, command, rule & hook index for AI-assisted lookup.
> Everything Claude Code — 271 skills, 67 agents, 92 commands, 20 hooks, 22 rule dirs

---

## Quick Reference

| Component | Count | Path |
|-----------|-------|------|
| Skills | 271 | `ecc/skills/*/SKILL.md` |
| Agents | 67 | `ecc/agents/*.md` |
| Commands | 92 | `ecc/commands/*.md` |
| Hooks | 20 | `ecc/hooks/hooks.json` |
| Rules | 22 dirs, ~90+ files | `ecc/rules/*/` |

---

## 1. Skills by Category

### CORE WORKFLOW / ORCHESTRATION (16)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `orch-add-feature` | Orchestrate new feature (research→plan→TDD→review→commit) | add new capability |
| `orch-build-mvp` | Bootstrap MVP from design/spec doc | SDD/PRD to running app |
| `orch-change-feature` | Alter existing feature behavior with tests | change behavior |
| `orch-fix-defect` | Fix bug: reproduce→fix→review→commit | bug fix |
| `orch-pipeline` | Shared orchestration engine for orch-* family | internal |
| `orch-refine-code` | Behavior-preserving refactor orchestration | restructure |
| `tdd-workflow` | Test-driven development with 80%+ coverage | new feature, fix, refactor |
| `verification-loop` | Build, lint, test, typecheck verification | verify after changes |
| `coding-standards` | Enforce coding standards across languages | review quality |
| `error-handling` | Typed errors, error boundaries, retries, circuit breakers | error handling |
| `git-workflow` | Branching, commit conventions, merge vs rebase | git operations |
| `plan-orchestrate` | Read plan doc, decompose into agent chains | multi-step plans |
| `parallel-execution-optimizer` | Parallel agents, batched tool calls, worktrees | speed up tasks |
| `search-first` | Research-before-coding workflow | avoid reinventing |
| `safety-guard` | Prevent destructive operations on production | dangerous ops |
| `gateguard` | Fact-forcing gate demanding investigation before edit | premature edits |

### SECURITY & COMPLIANCE (12)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `security-review` | Comprehensive security checklist + patterns | auth, input, secrets, API |
| `security-scan` | Scan Claude Code config for vulnerabilities | config audit |
| `security-bounty-hunter` | Hunt bounty-worthy remotely-reachable vulns | security audit |
| `repo-scan` | Cross-stack source code asset audit with HTML reports | codebase audit |
| `hipaa-compliance` | HIPAA-specific PHI/PII compliance | US healthcare |
| `healthcare-phi-compliance` | PHI/PII data classification, access control | healthcare apps |
| `llm-trading-agent-security` | Trading agent security (prompt injection, circuit breakers) | trading bots |
| `prediction-market-risk-review` | Compliance, safety risk review for prediction markets | market workflows |
| `santa-method` | Multi-agent adversarial verification with convergence loop | critical output |
| `governance-capture` | Capture governance events (secrets, policy violations) | via hooks |
| `config-protection` | Block modifications to linter/formatter config | Edit/Write hooks |
| `safety-guard` | Prevent destructive ops on production systems | production safety |

### LANGUAGE PATTERNS & FRAMEWORKS

#### Python (10)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `python-patterns` | Pythonic idioms, PEP 8, type hints, best practices | Python code |
| `python-testing` | pytest, TDD, fixtures, mocking, parametrization | Python tests |
| `fastapi-patterns` | FastAPI best practices, Pydantic v2, async, auth | FastAPI apps |
| `pytorch-patterns` | PyTorch training pipelines, model architectures | deep learning |
| `django-patterns` | Django architecture, ORM, services, caching | Django apps |
| `django-security` | Django security best practices | Django security |
| `django-celery` | Django Celery async task patterns | background jobs |
| `django-tdd` | Django TDD with pytest-django, factory_boy | Django tests |
| `django-verification` | Django verification loop | Django CI |
| `generating-python-installer` | Commercial-grade Python installer (Nuitka + Inno Setup) | Python packaging |

#### JavaScript / TypeScript (7)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `frontend-patterns` | React, Next.js, state management, UI best practices | frontend dev |
| `nextjs-turbopack` | Next.js 16+ Turbopack incremental bundling | Next.js dev |
| `vite-patterns` | Vite config, plugins, HMR, SSR, library mode | Vite projects |
| `bun-runtime` | Bun runtime patterns and best practices | Bun projects |
| `nestjs-patterns` | NestJS modules, controllers, providers, guards | NestJS apps |
| `prisma-patterns` | Prisma ORM schema, query optimization, traps | Prisma projects |
| `mcp-server-patterns` | Build MCP servers with Node/TypeScript SDK | MCP development |

#### React (7)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `react-patterns` | React 18/19 hooks, Suspense, form actions, a11y | React code |
| `react-performance` | 70+ performance optimization rules across 8 categories | React perf |
| `react-testing` | React Testing Library, Vitest, MSW, axe | React tests |
| `motion-foundations` | Motion tokens, springs, performance rules | React animation |
| `motion-patterns` | Production-ready animation patterns | React/Next.js animation |
| `motion-advanced` | Advanced motion: drag, gestures, SVG, imperative sequences | advanced React animation |
| `motion-ui` | Production-ready UI motion system | React/Next.js motion |

#### Vue / Nuxt (4)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `vue-patterns` | Vue 3 Composition API, Pinia, Vue Router, Nuxt SSR | Vue projects |
| `nuxt4-patterns` | Nuxt 4 hydration, performance, SSR-safe data fetching | Nuxt projects |
| `ui-to-vue` | Batch convert UI screenshots to Vue 3 components | UI→Vue |
| `angular-developer` | Angular signals, DI, routing, testing, components | Angular projects |

#### Go (2)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `golang-patterns` | Idiomatic Go patterns, best practices | Go code |
| `golang-testing` | Table-driven tests, benchmarks, fuzzing | Go tests |

#### Kotlin / JVM (7)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `kotlin-patterns` | Idiomatic Kotlin, coroutines, null safety | Kotlin code |
| `kotlin-testing` | Kotest, MockK, coroutine testing | Kotlin tests |
| `kotlin-coroutines-flows` | Coroutines and Flow for Android/KMP | Android/KMP |
| `kotlin-exposed-patterns` | JetBrains Exposed ORM, DSL queries | Exposed projects |
| `kotlin-ktor-patterns` | Ktor server patterns, routing, auth, DI | Ktor projects |
| `compose-multiplatform-patterns` | Compose Multiplatform patterns | KMP Compose |
| `android-clean-architecture` | Android clean architecture patterns | Android projects |

#### Java (11)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `java-coding-standards` | Java standards for Spring Boot and Quarkus | Java code |
| `jpa-patterns` | JPA/Hibernate entity design, query optimization | JPA projects |
| `springboot-patterns` | Spring Boot architecture, REST, caching | Spring Boot apps |
| `springboot-security` | Spring Security authn/authz, CSRF, headers | Spring security |
| `springboot-tdd` | Spring Boot TDD with JUnit 5, Mockito | Spring tests |
| `springboot-verification` | Spring Boot verification loop | Spring CI |
| `quarkus-patterns` | Quarkus 3.x with Camel, CDI, Panache | Quarkus apps |
| `quarkus-security` | Quarkus Security best practices | Quarkus security |
| `quarkus-tdd` | Quarkus TDD with JUnit 5, REST Assured | Quarkus tests |
| `quarkus-verification` | Quarkus verification loop | Quarkus CI |
| `tinystruct-patterns` | tinystruct Java framework guidance | tinystruct projects |

#### Rust (2)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `rust-patterns` | Ownership, error handling, traits, concurrency | Rust code |
| `rust-testing` | Unit, integration, async, property-based testing | Rust tests |

#### C/C++ (2)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `cpp-coding-standards` | C++ coding standards and best practices | C++ code |
| `cpp-testing` | GoogleTest, gcov/lcov testing | C++ tests |

#### Swift / Apple (7)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `swiftui-patterns` | SwiftUI architecture, @Observable, navigation | SwiftUI projects |
| `swift-concurrency-6-2` | Swift 6.2 Approachable Concurrency | Swift concurrency |
| `swift-actor-persistence` | Thread-safe persistence with actors | Swift persistence |
| `swift-protocol-di-testing` | Protocol-based DI for testable Swift | Swift testing |
| `liquid-glass-design` | iOS 26 Liquid Glass design system | iOS 26 UI |
| `foundation-models-on-device` | Apple FoundationModels for on-device LLM (iOS 26+) | iOS 26 AI |
| `ios-icon-gen` | Generate iOS app icons from SF Symbols/Iconify | iOS icons |

#### Dart / Flutter (2)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `dart-flutter-patterns` | Dart and Flutter patterns | Flutter projects |
| `flutter-dart-code-review` | Flutter/Dart code review checklist | Flutter review |

#### PHP / Laravel (5)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `laravel-patterns` | Laravel architecture, Eloquent, queues, events | Laravel apps |
| `laravel-security` | Laravel security best practices | Laravel security |
| `laravel-tdd` | Laravel testing with PHPUnit/Pest | Laravel tests |
| `laravel-verification` | Laravel verification loop | Laravel CI |
| `laravel-plugin-discovery` | Discover Laravel packages via LaraPlugins.io MCP | Laravel packages |

#### Perl (3)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `perl-patterns` | Modern Perl 5.36+ idioms | Perl code |
| `perl-security` | Taint mode, input validation, DBI parameterized queries | Perl security |
| `perl-testing` | Test2::V0, Test::More, Devel::Cover | Perl tests |

#### F# (1)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `fsharp-testing` | F# testing with xUnit, FsUnit, FsCheck | F# tests |

#### C# (2)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `dotnet-patterns` | Idiomatic C# and .NET patterns | .NET projects |
| `csharp-testing` | C# testing patterns | C# tests |

#### Database (6)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `postgres-patterns` | PostgreSQL query optimization, schema, indexing | Postgres work |
| `mysql-patterns` | MySQL/MariaDB schema, queries, replication | MySQL work |
| `redis-patterns` | Redis caching, distributed locks, rate limiting | Redis work |
| `clickhouse-io` | ClickHouse patterns | analytics DB |
| `database-migrations` | Database migration patterns | schema changes |
| `kubernetes-patterns` | K8s workload patterns, RBAC, autoscaling | deployment |

#### AI/ML & Data Science (8)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `mle-workflow` | Production ML engineering workflow | ML systems |
| `ml-adoption-playbook` | Add ML algorithms to existing codebases | ML adoption |
| `ai-regression-testing` | AI regression testing patterns | AI model testing |
| `ai-first-engineering` | AI-first engineering methodology | new AI features |
| `pytorch-patterns` | PyTorch training pipelines | deep learning |
| `recsys-pipeline-architect` | Recommendation/ranking pipeline design | feeds, reranking |
| `agentic-engineering` | Agentic AI engineering patterns | autonomous agents |
| `agentic-os` | Agentic OS patterns | agent infrastructure |

#### Agent Framework & Meta (14)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `agent-self-evaluation` | Agent self-evaluation framework | quality check |
| `agent-eval` | Agent evaluation harness | eval agent |
| `agent-harness-construction` | Build agent harnesses | harness creation |
| `agent-introspection-debugging` | Agent introspection and debugging | debug agents |
| `agent-sort` | Sort agent catalogs and assignment surfaces | catalog management |
| `agent-architecture-audit` | Audit agent architecture | agent review |
| `agent-payment-x402` | Agent payment via x402 protocol | agent payments |
| `autonomous-agent-harness` | Autonomous agent harness | long-running agents |
| `autonomous-loops` | Autonomous loop patterns | autonomous work |
| `continuous-agent-loop` | Continuous agent loop | persistent agents |
| `eval-harness` | Formal evaluation framework for sessions | EDD principles |
| `team-agent-orchestration` | Team-based agent orchestration with Kanban | multi-agent work |
| `team-builder` | Interactive agent picker for parallel teams | compose teams |
| `claude-devfleet` | Orchestrate parallel Claude Code agents via DevFleet | fleet orchestration |

#### Orchestration & Multi-Model (6)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `ralphinho-rfc-pipeline` | RFC-driven multi-agent DAG execution | DAG orchestration |
| `gan-style-harness` | GAN-inspired Generator-Evaluator harness | autonomous building |
| `dynamic-workflow-mode` | Dynamic workflow mode switching | workflow adaptation |
| `intent-driven-development` | Turn ambiguous changes into verifiable acceptance criteria | clarify requirements |
| `recursive-decision-ledger` | Repeated rollouts, stochastic optimization | decision processes |
| `harness-optimizer` | Harness config tuning for reliability/cost | optimize harness |

#### DevOps & Deployment (8)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `deployment-patterns` | Deployment patterns and best practices | deploy |
| `docker-patterns` | Docker containerization patterns | docker |
| `production-audit` | Local-evidence production readiness audit | prod readiness |
| `canary-watch` | Canary deployment monitoring | canary deploys |
| `uncloud` | Manage Uncloud cluster (Caddy, ports, scaling) | Uncloud ops |
| `flox-environments` | Reproducible dev environments with Flox/Nix | env setup |
| `config-gc` | Configuration garbage collection | cleanup |
| `configure-ecc` | Configure ECC settings | ECC setup |

#### Networking & Homelab (10)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `homelab-network-setup` | Home network planning (gateways, switches, APs) | homelab |
| `homelab-network-readiness` | VLAN/DNS/WireGuard readiness checklist | before config change |
| `homelab-pihole-dns` | Pi-hole installation, blocklists, DoH | DNS filtering |
| `homelab-vlan-segmentation` | VLAN segmentation (UniFi, pfSense, MikroTik) | network segmentation |
| `homelab-wireguard-vpn` | WireGuard VPN server/peer setup | VPN setup |
| `cisco-ios-patterns` | Cisco IOS configuration patterns | Cisco devices |
| `netmiko-ssh-automation` | Safe Python Netmiko SSH patterns | network automation |
| `network-bgp-diagnostics` | BGP troubleshooting patterns | BGP issues |
| `network-config-validation` | Pre-deploy router/switch config checks | config validation |
| `network-interface-health` | Interface error/duplex/flapping diagnostics | interface issues |

#### Web & Frontend Design (10)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `design-system` | Design system patterns | UI consistency |
| `frontend-a11y` | Frontend accessibility patterns | accessibility |
| `frontend-design-direction` | Set frontend design direction | UI polish |
| `make-interfaces-feel-better` | Polished UI details (spacing, typography, motion) | UI refinement |
| `click-path-audit` | Click-path and user flow audit | UX review |
| `liquid-glass-design` | iOS 26 Liquid Glass design system | iOS 26 UI |
| `taste` | Creative direction for music videos/short-form edits | video aesthetic |
| `ui-demo` | Record polished UI demo videos using Playwright | demo recording |
| `blender-motion-state-inspection` | Blender motion state inspection | 3D motion |
| `windows-desktop-e2e` | E2E testing for Windows native desktop apps | WPF/WinForms |

#### Video, Media & Content (8)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `video-editing` | AI-assisted video editing (FFmpeg, Remotion, ElevenLabs) | video editing |
| `videodb` | See/Understand/Act on video and audio | video intelligence |
| `remotion-video-creation` | Remotion video creation in React | React video |
| `manim-video` | Manim explainers for technical concepts | math/tech animation |
| `fal-ai-media` | Unified media generation via fal.ai (image, video, audio) | AI media gen |
| `content-engine` | Content engine for media production | content creation |
| `dmux-workflows` | DMUX workflow patterns | media workflows |
| `frontend-slides` | Create HTML presentations from scratch or PPT conversion | slide decks |

#### Business, Marketing & Finance (14)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `brand-discovery` | Brand discovery and identity framework | brand work |
| `brand-voice` | Brand voice and tone profiling | voice/tone |
| `marketing-campaign` | End-to-end marketing campaign planning | product launch |
| `market-research` | Market research, competitive analysis, due diligence | market intel |
| `lead-intelligence` | AI-native lead intelligence and outreach pipeline | lead gen |
| `seo` | SEO audit, planning, and implementation | search visibility |
| `social-publisher` | Social media publishing across 13 platforms | social posting |
| `social-graph-ranker` | Social graph ranking for warm intro discovery | networking |
| `investor-materials` | Pitch decks, one-pagers, financial models | fundraising |
| `investor-outreach` | Cold emails, warm intros, follow-ups | investor comms |
| `competitive-platform-analysis` | Competitive platform analysis | competitor research |
| `competitive-report-structure` | Structured competitive report | competitor reports |
| `crosspost` | Cross-post content across platforms | content distribution |
| `finance-billing-ops` | Revenue, pricing, refunds, billing workflow | billing ops |

#### Healthcare (4)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `healthcare-cdss-patterns` | Clinical Decision Support System patterns | CDSS dev |
| `healthcare-emr-patterns` | EMR/EHR development patterns | EMR work |
| `healthcare-eval-harness` | Patient safety evaluation harness | healthcare deploy |
| `hipaa-compliance` | HIPAA-specific compliance patterns | HIPAA |

#### Scientific & Research (7)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `research-ops` | Evidence-first current-state research workflow | research |
| `deep-research` | Deep research workflow | thorough research |
| `documentation-lookup` | Documentation lookup via Context7 | API docs |
| `scientific-thinking-literature-review` | Systematic literature review | academic review |
| `scientific-thinking-scholar-evaluation` | Scholarly work evaluation | paper review |
| `scientific-db-pubmed-database` | PubMed/NCBI E-utilities search | biomedical lit |
| `scientific-db-uspto-database` | USPTO patent and trademark data | IP research |

#### Crypto, DeFi & Prediction Markets (7)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `evm-token-decimals` | Prevent EVM decimal mismatch bugs | EVM chains |
| `nodejs-keccak256` | Prevent Ethereum Keccak-256 hashing bugs | Ethereum hashing |
| `prediction-market-oracle-research` | Prediction market research as data sources | oracle research |
| `ito-basket-compare` | Compare prediction-market baskets | basket comparison |
| `ito-market-intelligence` | Prediction market event research | market intel |
| `ito-trade-planner` | Non-advisory prediction-market trade planner | trade planning |
| `ito-data-atlas-agent` | Background Data Atlas agents for basket research | agent architecture |

#### Knowledge & Learning (8)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `knowledge-ops` | Knowledge base management, sync, retrieval | knowledge mgmt |
| `continuous-learning` | Continuous learning patterns | learn from sessions |
| `continuous-learning-v2` | V2 continuous learning with instincts | learn from sessions |
| `codebase-onboarding` | Codebase onboarding workflow | new codebase |
| `code-tour` | Guided codebase tour | explore codebase |
| `architecture-decision-records` | ADR workflow | document decisions |
| `article-writing` | Article writing workflow | write articles |
| `rules-distill` | Scan skills, extract principles, distill into rules | rule creation |

#### Code Quality & Metrics (10)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `codehealth-mcp` | Code health MCP integration | code quality |
| `benchmark` | Benchmarking patterns | performance test |
| `benchmark-methodology` | Benchmark methodology | benchmark design |
| `benchmark-optimization-loop` | Benchmark optimization loop | perf optimization |
| `cost-tracking` | Cost tracking patterns | cost monitoring |
| `cost-aware-llm-pipeline` | Cost-aware LLM pipeline | cost optimization |
| `ecc-tools-cost-audit` | ECC Tools burn and billing audit | billing audit |
| `token-budget-advisor` | Token budget advisory | context management |
| `context-budget` | Context window usage analysis | token overhead |
| `plankton-code-quality` | Write-time code quality enforcement via Plankton | auto-format/lint |

#### Session & Workflow Management (9)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `strategic-compact` | Manual context compaction at logical intervals | context management |
| `blueprint` | Anti-pattern detection and plan mutation protocol | planning |
| `product-capability` | PRD-to-capability plan translation | PRD work |
| `product-lens` | Validate "why" before building | product validation |
| `terminal-ops` | Evidence-first repo execution workflow | command execution |
| `jira-integration` | Jira ticket retrieval and management | Jira ops |
| `project-flow-ops` | GitHub-Linear execution flow coordination | project management |
| `unified-notifications-ops` | Notification routing, dedup, escalation | alert management |
| `email-ops` | Mailbox triage, drafting, send verification | email ops |

#### Operations & Specific Domains (10)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `customer-billing-ops` | Customer billing operations | billing support |
| `automation-audit-ops` | Automation audit operations | automation review |
| `enterprise-agent-ops` | Long-lived agent workloads with observability | enterprise agents |
| `latency-critical-systems` | Latency-sensitive realtime systems | HFT, realtime |
| `data-scraper-agent` | Data scraping agent | scraping |
| `data-throughput-accelerator` | Data throughput acceleration | data pipeline |
| `connections-optimizer` | Connections optimization | connection tuning |
| `iterative-retrieval` | Progressive context retrieval refinement | subagent context |
| `regex-vs-llm-structured-text` | Decision: regex vs LLM for text parsing | text parsing |
| `prompt-optimizer` | Optimize prompts for ECC enrichment | prompt improvement |

#### Open Source & Legacy (5)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `opensource-pipeline` | Fork, sanitize, package for public release | open source this |
| `inherit-legacy-style` | Prevent style drift on legacy projects | legacy onboarding |
| `hermes-imports` | Convert Hermes workflows to ECC skills | workflow import |
| `hookify-rules` | Write/create hookify rules | hookify config |
| `skill-comply` | Visualize whether skills/rules are followed | compliance check |

#### Skill Management (4)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `skill-scout` | Search existing skills before creating new ones | create/find skill |
| `skill-stocktake` | Audit skills and commands for quality | quality audit |
| `ecc-guide` | Guide users through ECC surface | ECC help |
| `workspace-surface-audit` | Audit workspace capabilities and recommend skills | env assessment |

#### Specialized / Niche (10)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `visa-doc-translate` | Translate visa documents to English bilingual PDF | visa docs |
| `x-api` | X/Twitter API integration | tweet/post |
| `exa-search` | Neural search via Exa MCP | web/code search |
| `google-workspace-ops` | Google Drive/Docs/Sheets/Slides workflow | Google Workspace |
| `messages-ops` | Live messaging workflow (texts, DMs) | messaging |
| `nutrient-document-processing` | Document processing (PDF, DOCX, OCR, signing) | document ops |
| `openclaw-persona-forge` | OpenClaw AI Agent persona creation | persona creation |
| `nanoclaw-repl` | NanoClaw v2 session-aware REPL | REPL ops |
| `inventory-demand-planning` | Inventory and demand planning | supply chain |
| `quality-nonconformance` | Quality nonconformance handling | quality mgmt |

---

## 2. Agents (67)

### Language-Specific Reviewers (18)

| Agent | Description | File |
|-------|-------------|------|
| `cpp-reviewer` | C/C++ code review | `agents/cpp-reviewer.md` |
| `csharp-reviewer` | F# functional code review | `agents/csharp-reviewer.md` |
| `django-reviewer` | Django apps, DRF, ORM, migrations | `agents/django-reviewer.md` |
| `fastapi-reviewer` | FastAPI code review | `agents/fastapi-reviewer.md` |
| `flutter-reviewer` | Flutter/Dart code review | `agents/flutter-reviewer.md` |
| `fsharp-reviewer` | F# functional code review | `agents/fsharp-reviewer.md` |
| `go-reviewer` | Go code review | `agents/go-reviewer.md` |
| `java-reviewer` | Java/Spring Boot review | `agents/java-reviewer.md` |
| `kotlin-reviewer` | Kotlin/Android/KMP review | `agents/kotlin-reviewer.md` |
| `mle-reviewer` | Production ML pipeline review | `agents/mle-reviewer.md` |
| `php-reviewer` | PHP code review | `agents/php-reviewer.md` |
| `python-reviewer` | Python code review | `agents/python-reviewer.md` |
| `react-reviewer` | React code review | `agents/react-reviewer.md` |
| `rust-reviewer` | Rust code review | `agents/rust-reviewer.md` |
| `swift-reviewer` | Swift code review | `agents/swift-reviewer.md` |
| `typescript-reviewer` | TypeScript/JavaScript review | `agents/typescript-reviewer.md` |
| `vue-reviewer` | Vue code review | `agents/vue-reviewer.md` |

### Language-Specific Build Resolvers (13)

| Agent | Description | File |
|-------|-------------|------|
| `build-error-resolver` | Generic build/type error fix | `agents/build-error-resolver.md` |
| `cpp-build-resolver` | C/C++ build errors | `agents/cpp-build-resolver.md` |
| `dart-build-resolver` | Dart build errors | `agents/dart-build-resolver.md` |
| `django-build-resolver` | Django build/migration/setup errors | `agents/django-build-resolver.md` |
| `go-build-resolver` | Go build errors | `agents/go-build-resolver.md` |
| `harmonyos-app-resolver` | HarmonyOS app build errors | `agents/harmonyos-app-resolver.md` |
| `java-build-resolver` | Java/Maven/Gradle build errors | `agents/java-build-resolver.md` |
| `kotlin-build-resolver` | Kotlin/Gradle build errors | `agents/kotlin-build-resolver.md` |
| `pytorch-build-resolver` | PyTorch runtime/CUDA/training errors | `agents/pytorch-build-resolver.md` |
| `react-build-resolver` | React build errors | `agents/react-build-resolver.md` |
| `rust-build-resolver` | Rust build/borrow checker errors | `agents/rust-build-resolver.md` |
| `swift-build-resolver` | Swift build errors | `agents/swift-build-resolver.md` |

### Core / Architectural Agents (16)

| Agent | Description | File |
|-------|-------------|------|
| `architect` | System design and scalability | `agents/architect.md` |
| `planner` | Implementation planning | `agents/planner.md` |
| `code-architect` | Code architecture decisions | `agents/code-architect.md` |
| `code-reviewer` | Code quality and maintainability | `agents/code-reviewer.md` |
| `code-simplifier` | Code simplification | `agents/code-simplifier.md` |
| `code-explorer` | Codebase exploration | `agents/code-explorer.md` |
| `security-reviewer` | Vulnerability detection | `agents/security-reviewer.md` |
| `tdd-guide` | Test-driven development guidance | `agents/tdd-guide.md` |
| `refactor-cleaner` | Dead code cleanup | `agents/refactor-cleaner.md` |
| `doc-updater` | Documentation and codemaps | `agents/doc-updater.md` |
| `docs-lookup` | Documentation lookup via Context7 | `agents/docs-lookup.md` |
| `e2e-runner` | End-to-end Playwright testing | `agents/e2e-runner.md` |
| `spec-miner` | Brownfield spec extraction | `agents/spec-miner.md` |
| `type-design-analyzer` | Type design analysis | `agents/type-design-analyzer.md` |
| `comment-analyzer` | Comment quality analysis | `agents/comment-analyzer.md` |
| `conversation-analyzer` | Conversation pattern analysis | `agents/conversation-analyzer.md` |

### Specialized Agents (18)

| Agent | Description | File |
|-------|-------------|------|
| `a11y-architect` | Accessibility architecture | `agents/a11y-architect.md` |
| `agent-evaluator` | Agent evaluation | `agents/agent-evaluator.md` |
| `chief-of-staff` | Chief of staff coordination | `agents/chief-of-staff.md` |
| `database-reviewer` | PostgreSQL/Supabase specialist | `agents/database-reviewer.md` |
| `gan-evaluator` | GAN evaluator | `agents/gan-evaluator.md` |
| `gan-generator` | GAN generator | `agents/gan-generator.md` |
| `gan-planner` | GAN planner | `agents/gan-planner.md` |
| `harness-optimizer` | Harness config tuning | `agents/harness-optimizer.md` |
| `healthcare-reviewer` | Healthcare code review | `agents/healthcare-reviewer.md` |
| `homelab-architect` | Homelab architecture | `agents/homelab-architect.md` |
| `loop-operator` | Autonomous loop execution | `agents/loop-operator.md` |
| `marketing-agent` | Marketing agent | `agents/marketing-agent.md` |
| `network-architect` | Network architecture | `agents/network-architect.md` |
| `network-config-reviewer` | Network config review | `agents/network-config-reviewer.md` |
| `network-troubleshooter` | Network troubleshooting | `agents/network-troubleshooter.md` |
| `performance-optimizer` | Performance optimization | `agents/performance-optimizer.md` |
| `pr-test-analyzer` | PR test analysis | `agents/pr-test-analyzer.md` |
| `seo-specialist` | SEO specialist | `agents/seo-specialist.md` |
| `silent-failure-hunter` | Hunt silent failures | `agents/silent-failure-hunter.md` |

### Open Source Agents (3)

| Agent | Description | File |
|-------|-------------|------|
| `opensource-forker` | Fork for open-sourcing | `agents/opensource-forker.md` |
| `opensource-packager` | Package for open-source release | `agents/opensource-packager.md` |
| `opensource-sanitizer` | Sanitize private code for public | `agents/opensource-sanitizer.md` |

---

## 3. Commands (92)

### Core Workflow

| Command | Description |
|---------|-------------|
| `/plan` | Implementation plan with risk assessment |
| `/code-review` | Full code quality, security, maintainability review |
| `/build-fix` | Auto-detect language and fix build errors |
| `/quality-gate` | Quality gate check against project standards |
| `/feature-dev` | Feature development workflow |
| `/test-coverage` | Report test coverage, identify gaps |

### Language-Specific Review

| Command | Description |
|---------|-------------|
| `/python-review` | Python review (PEP 8, type hints, security) |
| `/go-review` | Go review (idiomatic patterns, concurrency) |
| `/kotlin-review` | Kotlin review (null safety, coroutines) |
| `/rust-review` | Rust review (ownership, lifetimes) |
| `/cpp-review` | C++ review (memory safety, modern idioms) |
| `/react-review` | React review |
| `/flutter-review` | Flutter review |
| `/fastapi-review` | FastAPI review |
| `/vue-review` | Vue review |

### Language-Specific Build

| Command | Description |
|---------|-------------|
| `/go-build` | Fix Go build errors |
| `/kotlin-build` | Fix Kotlin/Gradle errors |
| `/rust-build` | Fix Rust build + borrow checker |
| `/cpp-build` | Fix C++ CMake/linker |
| `/react-build` | Fix React build errors |
| `/flutter-build` | Fix Flutter build errors |
| `/gradle-build` | Fix Gradle errors |

### Language-Specific Test

| Command | Description |
|---------|-------------|
| `/go-test` | Go TDD workflow |
| `/kotlin-test` | Kotlin TDD workflow |
| `/rust-test` | Rust TDD workflow |
| `/cpp-test` | C++ TDD workflow |
| `/react-test` | React test workflow |
| `/flutter-test` | Flutter test workflow |

### Orchestration

| Command | Description |
|---------|-------------|
| `/orch-add-feature` | Orchestrate new feature (research→plan→TDD→review→commit) |
| `/orch-build-mvp` | Orchestrate MVP bootstrap from spec |
| `/orch-change-feature` | Orchestrate feature behavior change |
| `/orch-fix-defect` | Orchestrate bug fix |
| `/orch-refine-code` | Orchestrate behavior-preserving refactor |

### Planning & Multi-Model

| Command | Description |
|---------|-------------|
| `/plan-prd` | Plan from PRD |
| `/multi-plan` | Multi-model collaborative planning |
| `/multi-workflow` | Multi-model collaborative development |
| `/multi-backend` | Backend multi-model development |
| `/multi-frontend` | Frontend multi-model development |
| `/multi-execute` | Multi-model collaborative execution |
| `/model-route` | Route task to right model |

### PRP Pipeline (Plan-Review-Promote)

| Command | Description |
|---------|-------------|
| `/prp-prd` | PRP PRD phase |
| `/prp-plan` | PRP plan phase |
| `/prp-implement` | PRP implement phase |
| `/prp-commit` | PRP commit phase |
| `/prp-pr` | PRP PR phase |

### Epic Management

| Command | Description |
|---------|-------------|
| `/epic-claim` | Claim an epic |
| `/epic-decompose` | Decompose epic into tasks |
| `/epic-publish` | Publish epic |
| `/epic-review` | Review epic |
| `/epic-sync` | Sync epic state |
| `/epic-unblock` | Unblock epic |
| `/epic-validate` | Validate epic |

### Session Management

| Command | Description |
|---------|-------------|
| `/save-session` | Save session state |
| `/resume-session` | Load most recent saved session |
| `/sessions` | Browse/search session history |
| `/checkpoint` | Mark a checkpoint |
| `/aside` | Quick side question without losing context |

### Learning & Improvement

| Command | Description |
|---------|-------------|
| `/learn` | Extract reusable patterns from session |
| `/learn-eval` | Extract patterns + self-evaluate |
| `/evolve` | Analyse instincts, suggest evolved skills |
| `/promote` | Promote project-scoped to global scope |
| `/instinct-status` | Show learned instincts with confidence |
| `/instinct-export` | Export instincts |
| `/instinct-import` | Import instincts |
| `/skill-create` | Analyse git history, generate skill |
| `/skill-health` | Skill portfolio health dashboard |

### Docs & Research

| Command | Description |
|---------|-------------|
| `/update-docs` | Update project documentation |
| `/update-codemaps` | Regenerate codemaps |
| `/ecc-guide` | Guide through ECC surface |

### Loops & Automation

| Command | Description |
|---------|-------------|
| `/loop-start` | Start recurring agent loop |
| `/loop-status` | Check running loops status |
| `/santa-loop` | Santa method adversarial loop |

### Project & Infrastructure

| Command | Description |
|---------|-------------|
| `/projects` | List known projects |
| `/harness-audit` | Audit agent harness config |
| `/pm2` | PM2 process manager init |
| `/setup-pm` | Configure package manager |
| `/project-init` | Initialize new project |
| `/security-scan` | Security scan configuration |
| `/pr` | Create pull request |
| `/review-pr` | Review pull request |
| `/prune` | Prune unused resources |
| `/auto-update` | Auto-update ECC |

### Hookify

| Command | Description |
|---------|-------------|
| `/hookify` | Create/manage hookify rules |
| `/hookify-configure` | Configure hookify |
| `/hookify-help` | Hookify help |
| `/hookify-list` | List hookify rules |

### Specialized

| Command | Description |
|---------|-------------|
| `/cost-report` | Cost tracking report |
| `/gan-build` | GAN build workflow |
| `/gan-design` | GAN design workflow |
| `/jira` | Jira integration |
| `/marketing-campaign` | Marketing campaign workflow |
| `/refactor-clean` | Remove dead code, consolidate |
| `/rust-test` | Rust TDD workflow |

---

## 4. Hooks (20)

### PreToolUse (8)

| ID | Target | Description |
|----|--------|-------------|
| `pre:bash:dispatcher` | Bash | Consolidated Bash preflight: quality, tmux, push, GateGuard |
| `pre:write:doc-file-warning` | Write | Warn about non-standard documentation files |
| `pre:edit-write:suggest-compact` | Edit\|Write | Suggest manual compaction at logical intervals |
| `pre:observe:continuous-learning` | * | Capture tool use observations for continuous learning |
| `pre:governance-capture` | Bash\|Write\|Edit\|MultiEdit | Capture governance events |
| `pre:config-protection` | Write\|Edit\|MultiEdit | Block modifications to linter/formatter config |
| `pre:mcp-health-check` | * | Check MCP server health before MCP tool execution |
| `pre:edit-write:gateguard-fact-force` | Edit\|Write\|MultiEdit | Fact-forcing gate: demand investigation before editing |

### PostToolUse (8)

| ID | Target | Description |
|----|--------|-------------|
| `post:bash:dispatcher` | Bash | Consolidated Bash postflight: logging, PR, build |
| `post:quality-gate` | Edit\|Write\|MultiEdit | Run quality gate checks after file edits |
| `post:edit:design-quality-check` | Edit\|Write\|MultiEdit | Warn when frontend drifts toward generic UI |
| `post:edit:accumulator` | Edit\|Write\|MultiEdit | Record edited JS/TS files for batch format+typecheck |
| `post:edit:console-warn` | Edit | Warn about console.log after edits |
| `post:governance-capture` | Bash\|Write\|Edit\|MultiEdit | Capture governance events from outputs |
| `post:session-activity-tracker` | * | Track per-session tool calls and file activity |
| `post:ecc-context-monitor` | * | Inject warnings on context exhaustion, cost, scope creep |

### PreCompact (1)

| ID | Target | Description |
|----|--------|-------------|
| `pre:compact` | * | Save state before context compaction |

### SessionStart (1)

| ID | Target | Description |
|----|--------|-------------|
| `session:start` | * | Load previous context and detect package manager |

### Stop (5)

| ID | Target | Description |
|----|--------|-------------|
| `stop:format-typecheck` | * | Batch format (Biome/Prettier) and typecheck edited JS/TS |
| `stop:check-console-log` | * | Check for console.log in modified files |
| `stop:session-end` | * | Persist session state after each response |
| `stop:evaluate-session` | * | Evaluate session for extractable patterns |
| `stop:cost-tracker` | * | Track token and cost metrics per session |

### SessionEnd (1)

| ID | Target | Description |
|----|--------|-------------|
| `session:end:marker` | * | Session end lifecycle marker |

---

## 5. Rules (22 dirs, ~90+ files)

### Structure
```
rules/
  common/     — 9 files (coding-style, git-workflow, testing, performance, patterns, hooks, agents, security, code-review)
  angular/    — 4 files (coding-style, hooks, patterns, security)
  cpp/        — 5 files
  dart/       — 5 files
  fsharp/     — 5 files
  golang/     — 5 files
  java/       — 5 files
  kotlin/     — 5 files
  nuxt/       — 5 files
  perl/       — 5 files
  php/        — 5 files
  python/     — 6 files (includes fastapi)
  react/      — 5 files
  ruby/       — 5 files
  rust/       — 5 files
  swift/      — 5 files
  typescript/ — 5 files
  vue/        — 5 files
  web/        — 7 files (includes performance, design-quality)
  arkts/      — 2 files
```

### Rule Types (per language)

| File | Purpose |
|------|---------|
| `coding-style.md` | Formatting, idioms, error handling |
| `testing.md` | Test framework, coverage, organization |
| `patterns.md` | Language-specific design patterns |
| `hooks.md` | PostToolUse hooks for formatters, linters |
| `security.md` | Secret management, security scanning |
| `performance.md` | (web/common) Performance optimization |
| `design-quality.md` | (web only) Design quality rules |

---

## 6. Cross-Reference: Skill → Agent Mapping

| Workflow | Skill | Agent(s) |
|----------|-------|----------|
| New feature | `orch-add-feature` | `planner`, `tdd-guide`, `code-reviewer` |
| Bug fix | `orch-fix-defect` | `planner`, `code-reviewer` |
| Refactor | `orch-refine-code` | `code-simplifier`, `refactor-cleaner` |
| Python review | `coding-standards` | `python-reviewer` |
| React review | `coding-standards` | `react-reviewer` |
| Rust review | `coding-standards` | `rust-reviewer` |
| Security audit | `security-review` | `security-reviewer` |
| ML pipeline | `mle-workflow` | `mle-reviewer` |
| Production deploy | `deployment-patterns` | `architect` |
| Codebase explore | `search-first` | `code-explorer` |
| Documentation | `knowledge-ops` | `doc-updater` |
| Testing | `tdd-workflow` | `tdd-guide` |
| Build errors | `verification-loop` | `build-error-resolver` |

---

*Generated: 2026-06-20 | ECC (Everything Claude Code)*
