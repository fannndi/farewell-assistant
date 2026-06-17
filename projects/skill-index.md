# Skill & Feature Index

> Indexed: 2026-06-17 | ECC v2.0.0 | 271 skills, 67 agents, 92 commands

---

## RELEVAN — Langsung Dipakai

### 🔴 HIGH Priority

| # | Skill | Kegunaan di Project Ini |
|---|-------|-------------------------|
| 1 | `agent-architecture-audit` | Debug agent stack, detect wrapper regression |
| 2 | `agentic-engineering` | Eval-first execution, model routing by complexity |
| 3 | `agentic-os` | Bangun multi-agent persistent OS di atas OpenCode |
| 4 | `autonomous-agent-harness` | Continuous agent loop, scheduled tasks, memory |
| 5 | `orch-pipeline` | Shared engine untuk orch-* commands |
| 6 | `orch-add-feature` | Tambah feature baru end-to-end |
| 7 | `orch-fix-defect` | Fix bug: reproduce → fix → review → commit |
| 8 | `configure-ecc` | Install wizard ECC ke project baru |
| 9 | `config-gc` | Bersihkan config ECC yang redundant |
| 10 | `context-budget` | Audit context window consumption |
| 11 | `customize-opencode` | Edit opencode.jsonc, .opencode/ configs |

### 🟡 MEDIUM Priority

| # | Skill | Kegunaan di Project Ini |
|---|-------|-------------------------|
| 12 | `agent-harness-construction` | Design agent tool definitions & observation |
| 13 | `parallel-execution-optimizer` | Parallel agents, batched tool calls |
| 14 | `dmux-workflows` | Multi-agent tmux parallel sessions |
| 15 | `team-agent-orchestration` | Kanban, merge gates, ownership |
| 16 | `claude-devfleet` | Dispatch parallel agents in worktrees |
| 17 | `git-workflow` | Branching, commits, merge conventions |
| 18 | `github-ops` | Issue/PR/CI management via gh CLI |
| 19 | `windows-desktop-e2e` | E2E testing via pywinauto |
| 20 | `automation-audit-ops` | Audit automation inventory |
| 21 | `deployment-patterns` | CI/CD pipeline, Docker, health checks |
| 22 | `orch-change-feature` | Alter existing feature behavior |
| 23 | `orch-refine-code` | Behavior-preserving refactor |
| 24 | `orch-build-mvp` | Build MVP from spec doc |

### 🟢 LOW Priority

| # | Skill | Kegunaan di Project Ini |
|---|-------|-------------------------|
| 25 | `continuous-agent-loop` | Quality gates + recovery controls |
| 26 | `ralphinho-rfc-pipeline` | RFC-driven multi-agent DAG |
| 27 | `eval-harness` | Formal eval framework untuk sessions |
| 28 | `safety-guard` | Prevent destructive ops |
| 29 | `gateguard` | Fact-forcing gate sebelum edit/write |
| 30 | `agent-eval` | Head-to-head coding agent comparison |
| 31 | `agent-introspection-debugging` | Self-debugging untuk agent failures |
| 32 | `ai-regression-testing` | Catch AI blind spots |
| 33 | `team-builder` | Compose & dispatch parallel teams |
| 34 | `prompt-optimizer` | Optimize prompt → match ECC components |
| 35 | `search-first` | Research-before-coding workflow |
| 36 | `blueprint` | Multi-session build plan |

---

## AGENTS RELEVAN

| Agent | Kegunaan |
|-------|----------|
| `architect` | System design, scalability decisions |
| `code-architect` | Feature architecture dari existing patterns |
| `planner` | Step breakdown, risk analysis |
| `loop-operator` | Autonomous loop execution, stall detection |
| `harness-optimizer` | Tune agent config untuk reliability/cost |
| `tdd-guide` | Red-Green-Refactor untuk semua code |
| `code-reviewer` | Code quality reviews |
| `security-reviewer` | Vulnerability detection, OWASP |
| `agent-evaluator` | 5-axis quality rubric scoring |
| `spec-miner` | Extract behavioral specs dari codebase |
| `silent-failure-hunter` | Cari swallowed errors |
| `build-error-resolver` | Fix build/type errors |
| `doc-updater` | Update documentation |
| `chief-of-staff` | Communication triage |
| `code-explorer` | Codebase analysis |

---

## COMMANDS RELEVAN

| Command | Kegunaan |
|---------|----------|
| `/plan` | Requirements → step-by-step plan |
| `/checkpoint` | Workflow checkpoints dengan verifikasi |
| `/model-route` | Model tier recommendation by complexity |
| `/quality-gate` | Formatter/lint quality gate |
| `/loop-start` | Start autonomous loop |
| `/loop-status` | Inspect active loop state |
| `/orch-add-feature` | Research → Plan → TDD → Review → Commit |
| `/orch-fix-defect` | Reproduce → Fix → Review → Commit |
| `/orch-build-mvp` | Spec → running vertical slice |
| `/orch-change-feature` | Alter existing feature |
| `/orch-refine-code` | Behavior-preserving refactor |
| `/security-scan` | AgentShield scan |
| `/save-session` | Save session state |
| `/resume-session` | Resume prior session |
| `/cost-report` | Token/cost tracking |
| `/harness-audit` | Harness config audit + scorecard |

---

## MCP SERVERS RELEVAN

| Server | Kegunaan |
|--------|----------|
| `memory` | Persistent memory across sessions |
| `omega-memory` | Multi-agent coordination + knowledge graph |
| `sequential-thinking` | Chain-of-thought reasoning |
| `nexus` | Local cost/privacy proxy |
| `devfleet` | Multi-agent parallel dispatch |
| `token-optimizer` | 95%+ context reduction |
| `longhand` | Lossless session history → SQLite |
| `github` | PR/issue ops |

---

## HOOKS RELEVAN

| Hook | Phase | Pattern |
|------|-------|---------|
| `pre:bash:dispatcher` | PreToolUse | Security gate sebelum bash |
| `pre:governance-capture` | PreToolUse | Secret/policy audit trail |
| `pre:edit-write:gateguard-fact-force` | PreToolUse | Block edit tanpa investigasi |
| `session:start` | SessionStart | Load previous context |
| `post:quality-gate` | PostToolUse | Verification setelah edit |
| `post:session-activity-tracker` | PostToolUse | Track tool calls |
| `post:ecc-context-monitor` | PostToolUse | Context exhaustion watchdog |
| `stop:session-end` | Stop | Persist state |
| `stop:cost-tracker` | Stop | Token/cost metrics |

---

## TIDAK RELEVAN

### Mobile Dev (~15 skills)
Android-clean-architecture, dart-flutter-patterns, flutter-dart-code-review, swiftui-patterns, swift-concurrency-6-2, swift-actor-persistence, swift-protocol-di-testing, compose-multiplatform-patterns, ios-icon-gen, liquid-glass-design, foundation-models-on-device

### Web Frameworks (~30 skills)
react-patterns, react-testing, react-performance, vue-patterns, nuxt4-patterns, angular-developer, laravel-patterns, laravel-security, laravel-tdd, laravel-verification, laravel-plugin-discovery, django-patterns, django-security, django-tdd, django-celery, django-verification, nestjs-patterns, backend-patterns, frontend-patterns, prisma-patterns, bun-runtime, nextjs-turbopack, vite-patterns, ui-to-vue, nodejs-keccak256

### Video/Media/Design (~15 skills)
video-editing, remotion-video-creation, fal-ai-media, manim-video, taste, ui-demo, videodb, motion-ui, motion-foundations, motion-patterns, motion-advanced, frontend-design-direction, make-interfaces-feel-better, design-system, frontend-a11y, accessibility, seo, frontend-slides, blender-motion-state-inspection

### Content/Social/Marketing (~15 skills)
content-engine, article-writing, brand-voice, brand-discovery, crosspost, social-publisher, x-api, lead-intelligence, connections-optimizer, social-graph-ranker, investor-materials, investor-outreach, marketing-campaign, market-research, competitive-platform-analysis, benchmark-methodology, competitive-report-structure

### Industry Domain (~25 skills)
carrier-relationship-management, customs-trade-compliance, energy-procurement, inventory-demand-planning, logistics-exception-management, production-scheduling, quality-nonconformance, returns-reverse-logistics, healthcare-cdss-patterns, healthcare-emr-patterns, healthcare-eval-harness, healthcare-phi-compliance, hipaa-compliance, ito-basket-compare, ito-data-atlas-agent, ito-market-intelligence, ito-trade-planner, prediction-market-oracle-research, prediction-market-risk-review

### Language-Specific (~40 skills)
python-patterns, python-testing, fastapi-patterns, pytorch-patterns, golang-patterns, golang-testing, rust-patterns, rust-testing, java-coding-standards, springboot-*, quarkus-*, kotlin-*, jpa-patterns, cpp-coding-standards, cpp-testing, perl-patterns, perl-security, perl-testing, csharp-testing, fsharp-testing, dotnet-patterns, tinystruct-patterns

### Blockchain/DeFi (~3 skills)
defi-amm-security, evm-token-decimals, nodejs-keccak256

### Scientific (~5 skills)
scientific-db-pubmed-database, scientific-db-uspto-database, scientific-pkg-gget, scientific-thinking-literature-review, scientific-thinking-scholar-evaluation

### Infra/Network (~10 skills)
kubernetes-patterns, uncloud, homelab-vlan-segmentation, homelab-pihole-dns, homelab-network-readiness, cisco-ios-patterns, network-bgp-diagnostics, network-config-validation, network-interface-health, clickhouse-io

### Ops/Business (~10 skills)
email-ops, messages-ops, google-workspace-ops, customer-billing-ops, finance-billing-ops, unified-notifications-ops, recsys-pipeline-architect, ml-adoption-playbook, mle-workflow, hexagonal-architecture

---

## GAP

| # | Gap | Solusi |
|---|-----|--------|
| 1 | Tidak ada PowerShell-specific skill | Buat custom skill `powershell-patterns` |
| 2 | Tidak ada Windows automation skill | Port `windows-desktop-e2e` + extend untuk PS1 |
| 3 | ECC hooks tidak ter-wire ke OpenCode | Adapt hooks.json → opencode config |
| 4 | `self-heal.ps1` tidak auto-trigger | Wire ke PostToolUse hook |
| 5 | Token estimation crude (Length/4) | Gunakan `token-optimizer` MCP atau tiktoken |
| 6 | Tidak ada skill untuk local LLM management | Buat skill `local-llm-ops` (Ollama, model switching, VRAM tracking) |
| 7 | Tidak ada skill untuk 9Router management | Buat skill `9router-ops` (gateway management, model registry) |
