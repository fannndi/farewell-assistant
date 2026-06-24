# farewell-assistant

> **Zero-cost AI coding orchestrator. Local LLM + 9Router gateway. Intent-driven.**

Orchestrator Python yang menjembatani OpenCode + Local LLM (Ollama qwen2.5-coder-1.5b) + 9Router (6 model combos) + ECC (162 whitelisted skills). Setiap input user auto-classify intent → chain skill → route ke model optimal.

---

## Architecture (2-Layer)

```
┌──────────────────────────────────────────────────────────────────┐
│ L1: Pipeline (farewell_assistant/)                                │
│                                                                   │
│ User Input                                                        │
│   → Plugin intent-router.js intercept                             │
│     → Python pipeline:                                            │
│       → Ollama enrichment + regex fallback → classify intent      │
│       → Permission check (PLAN blocks write)                      │
│       → Skill chain (23 chains) + whitelist filter (162 skills)   │
│       → Write pipeline-result.json + context.md                   │
│     → Plugin inject footer ke chat                                │
│     → AI execute chain step-by-step                               │
│                                                                   │
│ Footer: Farewell: ON | Project: XXX | BUILD | Turn: N | Chain: N │
│         | 85% | LLM:qwen2.5-coder-1.5b                           │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│ L2: OpenCode Runtime (opencode.jsonc)                             │
│                                                                   │
│ 9Router Provider (6 model combos):                                │
│   Free       → deepseek-v4-flash-free, mimo-v2.5-free             │
│   Emergency  → north-mini-code-free                               │
│   Deepseek-API  → ds/deepseek-v4-flash/pro                        │
│   Deepseek-GO   → ocg/deepseek-v4-flash/pro                       │
│                                                                   │
│ ECC Skills (162 whitelisted dari 271 total):                      │
│   Web frontend, backend, mobile, rust, kotlin, security,          │
│   TDD, verification, git, database, infra, deployment             │
│                                                                   │
│ Sub-agents via 9Router:                                           │
│   planner (Emergency), code-reviewer (Emergency),                 │
│   security-reviewer (Free), tdd-guide (Free),                     │
│   build-error-resolver (Emergency), doc-updater (Emergency)       │
└──────────────────────────────────────────────────────────────────┘
```

---

## Daily Workflow

### Sesi Baru (pagi hari)

```powershell
# Buka farewell-assistant workspace
cd ~/Documents/farewell-assistant
opencode

# Di OpenCode:
/daily
```

`/daily` menjalankan:
1. Pipeline prime (warm up intent router)
2. Git pull self (farewell-assistant update)
3. Reset turn counter
4. Log session ke `session-log.md`
5. Tampilkan daily report:

```
╔══════════════════════════════════════════════════╗
║            Daily Report — 2026-06-24            ║
╠══════════════════════════════════════════════════╣
║  SYSTEM HEALTH                                   ║
║    Ollama      : ✅ Running (qwen2.5-coder-1.5b) ║
║    GPU         : ✅ MX150 (49°C, 1109/2048MB)   ║
║    Mode        : BUILD                            ║
║                                                  ║
║  EXTERNAL COMPONENTS                              ║
║    ECC         : ✅ up to date (162/271 whitelist)║
║    9Router     : ✅ up to date                    ║
║                                                  ║
║  PROJECT STATUS                                   ║
║    Active      : farewell-assistant               ║
║    Projects    : 3 registered                     ║
║                                                  ║
║  LAST SESSION                                     ║
║    Date        : 2026-06-23                       ║
║    Turns       : 47                               ║
║    Topics      : whitelist, single-LLM, README    ║
║                                                  ║
║  PENDING ITEMS                                    ║
║    ◷ P1-1 Split helpers.py — CARRY_OVER           ║
║                                                  ║
║  RECENT COMMITS                                   ║
║    584e986 refactor: single LLM model             ║
║    24d0ac9 feat: skill whitelist                  ║
╚══════════════════════════════════════════════════╝
```

### Project Baru

```powershell
# Register project dari path lokal
/setup-project C:\Users\You\Documents\my-project
  → detect type (Flutter/Python/Rust/etc)
  → register di registry.json (auto code)
  → buat junction .opencode/
```

### Ganti Project Aktif

```powershell
# Dari terminal project
cd C:\Users\You\Documents\my-project
opencode
/start-project 001   # atau code yang didapat
  → set active project
  → load context
  → pipeline siap
```

---

## Skenario ECC + 9Router

### ECC Skill Chains (otomatis via pipeline)

| Input | Intent | Chain | Skills |
|-------|--------|-------|--------|
| "bikin CRUD user auth JWT" | build/web | build_web (8) | orch-add-feature, api-design, backend-patterns, db-migrations, tdd, security, verify, git |
| "fix error 500 login" | fix/web | fix_web (5) | search-first, orch-fix-defect, regression-testing, verify, git |
| "review security auth" | review/web | review_web (5) | coding-standards, error-handling, security-review, codehealth-mcp, verify |
| "refactor service layer" | fix/refactor | fix_refactor (4) | search-first, orch-refine-code, verify, git |
| "research best practices" | research | research (2) | research-ops, documentation-lookup |
| "deploy microservice" | deploy | deploy (4) | production-audit, deployment-patterns, canary-watch, git |

### 9Router Sub-Agents (manual via /commands)

| Command | Agent | Model | Task |
|---------|-------|-------|------|
| `/plan` | planner | Emergency | Implementation plan + risk |
| `/code-review` | code-reviewer | Emergency | Full code review |
| `/tdd` | tdd-guide | Free | TDD workflow |
| `/security-scan` | security-reviewer | Free | OWASP security review |
| `/build-fix` | build-error-resolver | Emergency | Debug build errors |
| `/update-docs` | doc-updater | Emergency | Update documentation |

### Hybrid Flow: Ollama + 9Router

```
Input: "review security auth module"
  → Pipeline (Ollama local): classify → review/security chain
  → Step 1-2: AI execute (coding-standards, error-handling)
  → Step 3: AI trigger /security-scan → 9Router sub-agent
  → Step 4-5: AI execute (codehealth-mcp, verify)
```

---

## Commands

### CLI (py -m farewell_assistant.cli)

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `daily` | Daily report + pipeline prime | `daily` |
| `route` | Test intent router | `route "bikin CRUD"` |
| `workmode` | Switch PLAN/BUILD | `workmode plan` |
| `llm` | LLM management | `llm status` |
| `project` | List/switch project | `project 001` |
| `self-heal` | Post-edit typecheck | `self-heal --file foo.py` |
| `enrich-check` | Test pipeline | `enrich-check` |
| `self-improvement` | Git pull ECC + 9Router + cek dampak | `self-improvement` |

### OpenCode Slash Commands

| Command | Fungsi |
|---------|--------|
| `/daily` | Daily report + pipeline prime |
| `/start-project <code>` | Activate project |
| `/setup-project <path>` | Register new project |
| `/project <code>` | Switch/list project |
| `/workmode plan\|build` | Switch work mode |
| `/self-improvement` | Git pull ECC + 9Router, cek dampak |
| `/go <task>` | Universal task execution |
| `/plan` | Implementation plan (Emergency) |
| `/tdd` | TDD workflow (Free) |
| `/code-review` | Full code review (Emergency) |
| `/security-scan` | OWASP security review (Free) |
| `/build-fix` | Debug build errors (Emergency) |
| `/verify` | Verification loop |
| `/update-docs` | Update documentation (Emergency) |

---

## File Structure

```
farewell-assistant/
├── farewell_assistant/          # Core Python (15 modules)
│   ├── cli.py                   # CLI dispatcher (8 commands)
│   ├── config.py                # Paths, constants
│   ├── daily.py                 # Daily report engine
│   ├── intent_router.py         # Classify → chain → route → persist
│   ├── enrichment_pipeline.py   # Ollama + regex classify
│   ├── skill_chain.py           # 23 built-in chains
│   ├── helpers.py               # JSON, LLM, GPU, project registry
│   ├── llm_setup.py             # Single model (qwen2.5-coder-1.5b)
│   ├── self_improvement.py      # Git pull ECC/9Router + cek dampak
│   ├── health.py                # Ollama health, GPU check
│   ├── self_heal.py             # Post-edit typecheck
│   ├── workmode.py              # PLAN/BUILD mode switch
│   ├── log.py                   # Task logging
│   ├── start.py                 # Pipeline prime + daily
│   └── run_router.py            # Plugin entry point
├── instructions/                # AI rules (3 files)
├── data/                        # Context, whitelist, registry, memory
│   ├── skill-whitelist.json     # 162 whitelisted skills
│   ├── skill-mode-index.json    # Skill index by mode
│   ├── memory/daily-memory.json # Daily session memory
│   └── context/                 # Project context files
├── .opencode/                   # Runtime state + plugin
├── docs/                        # Documentation
├── ecc/                         # 271 ECC skills (gitignored, whitelist manajemen)
├── 9router/                     # AI gateway (gitignored, 6 model combos)
├── self-improvement.md          # Self-evolving audit framework
├── pyproject.toml
└── README.md
```

## Tech Stack

| Component | Role | Detail |
|-----------|------|--------|
| Python 3.10+ | Core orchestrator | farewell-assistant (15 modules) |
| OpenCode | AI coding assistant | Anomaly Co. |
| Ollama | Local LLM runtime | qwen2.5-coder-1.5b |
| 9Router | Multi-model gateway | 6 combos, Free/Emergency/Deepseek |
| ECC | Skill library | 162 whitelisted / 271 total |
| NVIDIA MX150 | GPU accelerator | 2GB VRAM |

## Cost: **$0** (Ollama lokal, 9Router free tier, ECC open source)

## License: MIT
