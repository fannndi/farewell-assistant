# Project Knowledge — farewell-assistant

> Zero-cost AI coding assistant. GPU-aware, intent-driven, handles every project.
> Version: 1.5.0 | License: MIT

---

## 1. Overview

farewell-assistant is a Python orchestrator that integrates:
- **OpenCode** — AI coding CLI
- **9Router** — AI model gateway (localhost proxy)
- **ECC** — 270+ specialized skill files
- **Ollama** — Local LLM inference (GPU optional)

Pipeline: User input → Intent classification → Permission check → Skill chain → Model route → Execution.

Cost: **$0** (all free models via 9Router combos).

---

## 2. Architecture

```
User Input
  → intent-router.js (OpenCode plugin, chat.message hook)
    → run-router.ps1 → py -m farewell_assistant.run_router
      → invoke_intent_router()
        → Quick classify (regex fallback) or Structured enrich (Ollama JSON)
        → Rule check (PLAN blocks build/fix/deploy)
        → Skill chain selection (19 chains)
        → Model route (complexity → Free/Emergency)
        → Planning check (high/critical needs planner)
        → Write context.md + pipeline-result.json
  → AI reads footer + context → Executes skill chain
```

### Key Files (Runtime Flow)
| File | Role |
|------|------|
| `.opencode/plugins/intent-router.js` | Plugin hook — fires on every user message |
| `farewell_assistant/run_router.py` | CLI entry for plugin |
| `farewell_assistant/intent_router.py` | Main pipeline orchestrator |
| `farewell_assistant/enrichment_pipeline.py` | Intent classification + cache |
| `farewell_assistant/skill_chain.py` | 19 built-in chains |
| `.opencode/context.md` | AI-readable per-turn context |
| `.opencode/pipeline-result.json` | Machine-readable per-turn data |

---

## 3. Module Reference

### Core Pipeline
| Module | Lines | Purpose |
|--------|-------|---------|
| `intent_router.py` | 298 | Main orchestrator: classify→permission→chain→route→planning |
| `enrichment_pipeline.py` | 322 | Structured enrichment (Ollama JSON), quick classify (regex), cache with TTL |
| `skill_chain.py` | 183 | 19 chains mapping intent+domain to skill sequences |
| `workmode.py` | 87 | PLAN/BUILD mode switch, ROLE enforcement |

### LLM & Models
| Module | Lines | Purpose |
|--------|-------|---------|
| `llm_setup.py` | 507 | 4 profiles (hot/eco/balance/performance), GGUF download, Ollama import |

### Startup & Health
| Module | Lines | Purpose |
|--------|-------|---------|
| `start.py` | 181 | 7-step orchestrator: git pull → bootstrap → update → health → config → pipeline → ready |
| `bootstrap.py` | 117 | First-run: clone ECC + 9Router, npm install, build |
| `update.py` | 82 | Git pull ECC + 9Router, rebuild if updated |
| `health.py` | 104 | 9Router/Ollama health, GPU info, ping combo models |

### Utilities
| Module | Lines | Purpose |
|--------|-------|---------|
| `config.py` | 74 | Central config: paths, ports, model routes, enrichment settings |
| `helpers.py` | 569 | JSON R/W, Ollama control, 9Router start/stop, GPU detect, token estimation, API key parser |
| `autostart.py` | 206 | Windows schtasks / Linux systemd autostart |
| `self_heal.py` | 82 | Post-edit typecheck (TypeScript, Dart, Python) |
| `log.py` | 81 | Task logging to logging.md, session state sync |

### Entry Points
| Module | Lines | Purpose |
|--------|-------|---------|
| `__init__.py` | 3 | Package marker, `__version__ = "1.5.0"` |
| `__main__.py` | 24 | `py -m farewell_assistant` — prints help |
| `cli.py` | 157 | Argparse dispatcher: 8 subcommands |
| `run_router.py` | 39 | Plugin CLI entry point |

**Total: ~3,100+ lines across 18 modules.**

---

## 4. CLI Commands

### Subcommands (`py -m farewell_assistant <cmd>`)
| Command | Description |
|---------|-------------|
| `start` | Full startup: git pull → bootstrap → health → config → pipeline prime |
| `route <input>` | Classify input → show chain + model route |
| `workmode [plan\|build]` | Switch or display work mode |
| `llm [eco\|hot\|balance\|performance\|list\|status]` | LLM profile management |
| `detect [--register]` | Detect project type + optional register to registry |
| `autostart [install\|remove\|status]` | System autostart (Windows/Linux) |
| `self-heal` | Post-edit typecheck |
| `enrich-check <input>` | Test enrichment pipeline |
| `project [list\|<name>]` | Switch active project |

### OpenCode Slash Commands (15)
`/start`, `/go`, `/workmode`, `/setup`, `/llm-setup`, `/detect`, `/enrich-check`, `/autostart`, `/status`, `/route`, `/self-heal`, `/update`, `/help`, `/version`, `/projects`

---

## 5. LLM Profiles

### 4 Profiles (GPU-aware)
| Profile | Model | VRAM | Speed | Use Case |
|---------|-------|------|-------|----------|
| **hot** | Qwen3.5-0.8B | 600MB | 15-25 tok/s | Simple tasks, fast response |
| **eco** | Qwen2.5-Coder-1.5B | 1GB | 8-15 tok/s | Default, code-focused |
| **balance** | Qwen3.5-2B | 1.4GB | 5-10 tok/s | Balanced accuracy/speed |
| **performance** | Qwen3.5-4B | 2.5GB hybrid | 2-5 tok/s | Complex reasoning |

### Model Routing
| Complexity | Primary | Secondary | Heavy |
|------------|---------|-----------|-------|
| low | Free | Free | Free |
| medium | Free | Free | Free |
| high | Free | Emergency | Emergency |
| critical | Emergency | Emergency | Emergency |

**Free combo:** deepseek-v4-flash-free, mimo-v2.5-free, mmf/mimo-auto
**Emergency combo:** big-pickle, north-mini-code-free

---

## 6. Skill Chains (19 Built-in)

### BUILD Chains
| Domain | Chain | Steps |
|--------|-------|-------|
| web | build_web | orch-add-feature → api-design → backend-patterns → database-migrations → tdd-workflow → security-review → verification-loop → git-workflow |
| mobile | build_mobile | orch-add-feature → dart-flutter-patterns → database-migrations → tdd-workflow → security-review → verification-loop → git-workflow |
| infra | build_infra | orch-add-feature → deployment-patterns → docker-patterns → kubernetes-patterns → database-migrations → verification-loop → git-workflow |
| data | build_data | orch-add-feature → postgres-patterns → database-migrations → tdd-workflow → verification-loop → git-workflow |
| automation | build_automation | orch-add-feature → powershell-patterns → tdd-workflow → verification-loop → git-workflow |
| ai_ml | build_ai_ml | orch-add-feature → pytorch-patterns → mle-workflow → tdd-workflow → verification-loop → git-workflow |

### FIX Chains
| Intent | Chain | Steps |
|--------|-------|-------|
| fix (general) | fix | search-first → orch-fix-defect → verification-loop |
| fix (security) | fix_security | repo-scan → security-review → safety-guard → verification-loop → git-workflow |
| fix (bug) | fix_bug | search-first → orch-fix-defect → ai-regression-testing → verification-loop → git-workflow |

### REVIEW Chains
| Intent | Chain | Steps |
|--------|-------|-------|
| review (code) | review_code | coding-standards → error-handling → security-review → codehealth-mcp → verification-loop |
| review (security) | review_security | repo-scan → security-bounty-hunter → security-scan → verification-loop |

### DEPLOY / RESEARCH / DOCS Chains
| Intent | Chain | Steps |
|--------|-------|-------|
| deploy | deploy | production-audit → deployment-patterns → canary-watch → git-workflow |
| research | research | research-ops → documentation-lookup |
| research (deep) | research_deep | research-ops → deep-research → documentation-lookup → competitive-platform-analysis |
| docs | docs | codebase-onboarding → article-writing → knowledge-ops |
| docs (code) | docs_code | codebase-onboarding → code-tour → architecture-decision-records → article-writing |

---

## 7. Plugin System

### intent-router.js (99 lines)
- Hook: `chat.message` — fires on every user message
- Runs: `run-router.ps1` → `py -m farewell_assistant.run_router`
- Output: footer prepended to user message
- Footer format: `Farewell: ON | Project: {project} | BUILD | Turn: 12 | Chain: 8 | 85% | Balance`

### Data Flow
```
User msg → Plugin hook → run_router.py
  → invoke_intent_router()
    → Write .opencode/pipeline-result.json
    → Write .opencode/context.md
    → Return footer string
  → Plugin prepend footer to msg
  → AI sees: footer + context → Executes
```

---

## 8. Data Directory Structure

```
data/
├── registry.json              # Project index (farewell-assistant + others)
├── skill-mode-index.json      # PLAN/BUILD skill group definitions
├── skill-index.json           # Full 270+ skill catalog
├── context/                   # Per-project context files
│   ├── farewell-assistant.md  # Self-context
│   ├── farewell-ex.md         # Rust+Kotlin project
│   └── service-hub.md         # NestJS+Flutter project
├── skills/                    # Local (non-ECC) skills
│   └── powershell-patterns/
└── llm/                       # Modelfiles for Ollama
    ├── Modelfile.qwen2.5-coder-1.5b
    ├── Modelfile.qwen3.5-0.8b
    ├── Modelfile.qwen3.5-2b
    └── Modelfile.qwen3.5-4b
```

---

## 9. Configuration

### api-key.txt (gitignored)
```ini
NINEROUTER_API_KEY=sk-...
9ROUTER_PASSWORD=farewell-9router-2026
COMBO_Free=oc/deepseek-v4-flash-free,oc/mimo-v2.5-free,mmf/mimo-auto
MODELS_Free=deepseek-v4-flash-free,mimo-v2.5-free,mimo-auto
COMBO_Emergency=oc/big-pickle,oc/north-mini-code-free
MODELS_Emergency=big-pickle,north-mini-code-free
```

### config.py Constants
| Constant | Value | Description |
|----------|-------|-------------|
| OLLAMA_PORT | 11434 | Ollama API port |
| ROUTER_PORT | 20128 | 9Router API port |
| HEADROOM_PORT | 8787 | Headroom proxy port |
| ROUTER_DIR | `9router/` | 9Router source |
| ECC_DIR | `ecc/` | ECC skills |
| DATA_DIR | `data/` | Project data |
| STATE_DIR | `.opencode/` | Runtime state |
| LOG_DIR | `.opencode/logs/` | Log files |

---

## 10. 9Router Integration

### What 9Router Does
- AI model gateway/proxy
- Routes requests to multiple providers (OpenCode, MMF, Codex)
- Combo load-balancing (round-robin, fallback)
- Usage tracking + billing
- Headroom context compression (optional)

### How farewell-assistant Uses It
1. **Startup** (`start.py`): starts 9Router + headroom proxy
2. **Health check**: verifies `localhost:20128/api/health`
3. **Model routing**: sends requests through 9Router combos
4. **Dashboard**: `http://localhost:20128` (password: `farewell-9router-2026`)

### Headroom (Context Compression)
- Auto-starts with 9Router
- Port 8787, health check: `GET /health`
- Compress endpoint: `POST /v1/compress` with model field
- Fail-open: if down, requests pass unmodified

---

## 11. Test Coverage

### Python Tests (198 tests)
| Test File | Tests | Coverage |
|-----------|-------|----------|
| test_pipeline.py | 19 | Quick intent, chains, permissions, model routes, cache, turn state |
| test_enrichment_full.py | 25 | Hash, cache, quick intent, sufficiency |
| test_helpers.py | 7 | API key parse, color, token estimate |
| test_helpers_full.py | 15 | Extended helper coverage |
| test_detect.py | 9 | Project detection |
| test_detect_full.py | 15 | All 10+ markers |
| test_llm.py | 4 | Profiles |
| test_llm_full.py | 12 | Profiles, map, mode switch, GGUF |
| test_workmode.py | 2 | Switch + defs |
| test_workmode_full.py | 8 | Defs, switch, status |
| test_integration.py | 8 | Full pipeline integration |
| test_bootstrap.py | 2 | Bootstrap check |
| test_health.py | 3 | GPU, Ollama |
| test_log.py | 2 | Write task log |
| test_autostart.py | 1 | Show status |
| test_self_heal.py | 6 | Run check, has marker |

### JavaScript Tests (20 tests)
| Test File | Tests | Coverage |
|-----------|-------|----------|
| test_plugin.js | 20 | Plugin functions, footer format, cache logic |

**Total: 218 tests**

---

## 12. Tech Stack & Dependencies

### Python
- **Runtime:** Python 3.10+ (3.11 tested)
- **Core:** httpx>=0.27 (HTTP client)
- **Standard lib:** json, os, subprocess, pathlib, platform, time, re, shutil

### External Services
- **Ollama** — Local LLM inference (port 11434)
- **9Router** — AI gateway (port 20128)
- **Headroom** — Context compression (port 8787)
- **ECC** — 270+ skill files (cloned on first run)

### Node.js (for 9Router)
- Node 18+ (standalone build)
- npm (dependency install)

### Build
- **pyproject.toml:** `pip install -e .` (editable mode)
- **Version:** 1.5.0

---

## 13. Daily Commands Quick Reference

```bash
# Morning
py -m farewell_assistant start        # Full startup

# During session
/workmode build                       # Switch to BUILD mode
/llm eco                              # Switch LLM profile
/detect --register                    # Detect + register project
/enrich-check "bikin CRUD user"       # Test intent pipeline

# Status
py -m farewell_assistant llm status   # LLM + GPU status
py -m farewell_assistant project list # List registered projects

# Cleanup
py -m farewell_assistant autostart remove  # Remove autostart
```

---

*Generated: 2026-06-20 | farewell-assistant v1.5.0*
