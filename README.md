# farewell-assistant

> **Zero-cost AI coding orchestrator. Single LLM. Intent-driven.**

Orchestrator Python yang menjembatani OpenCode + Local LLM + ECC skill chains. Setiap input user: auto-classify intent → chain skill → route ke model lokal — semua dari satu perintah.

---

## Workflow

```
User ketik di OpenCode
  → Plugin intent-router.js intercept
    → Python pipeline:
      → classify intent (Ollama qwen2.5-coder-1.5b + regex fallback)
      → check permission (PLAN blocks write)
      → select skill chain (23 chains by intent+domain)
      → filter by whitelist (162 active skills)
      → write pipeline-result.json + context.md
  → Plugin inject footer ke chat
  → AI execute chain step-by-step
```

**Footer output:**
```
Farewell: ON | Project: XXX | BUILD | Turn: 1 | Chain: 8 | 85% | LLM:qwen2.5-coder-1.5b
```

---

## Quick Start

```powershell
git clone https://github.com/fannndi/farewell-assistant.git
cd farewell-assistant
pip install httpx
pip install -e .
```

```powershell
# Setup LLM (sekali)
py -m farewell_assistant.cli llm pull

# Pipeline prime
py -m farewell_assistant.cli route "bikin CRUD user"
```

Di OpenCode, pipeline otomatis jalan tiap input.

---

## Commands

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `route` | Test intent router | `route "bikin CRUD user"` |
| `workmode` | Switch PLAN/BUILD | `workmode plan` |
| `llm status` | GPU + Ollama info | `llm status` |
| `llm pull` | Download + import model | `llm pull` |
| `project` | List/switch project | `project 001` |
| `self-heal` | Post-edit typecheck | `self-heal --file foo.py` |
| `enrich-check` | Test pipeline | `enrich-check` |

---

## Work Mode

| Mode | Tools | Use Case |
|------|-------|----------|
| **PLAN** | read, bash | Analisis, audit, riset — no write/edit |
| **BUILD** | read, bash, write, edit | Implementasi, fix — full access |

---

## File Structure

```
farewell-assistant/
├── farewell_assistant/          # Core Python (13 modules)
│   ├── cli.py                   # CLI dispatcher (6 commands)
│   ├── config.py                # Paths, constants
│   ├── intent_router.py         # Classify → chain → route → persist
│   ├── enrichment_pipeline.py   # Ollama enrichment + quick classify
│   ├── skill_chain.py           # 23 built-in chains
│   ├── helpers.py               # JSON, LLM, GPU, project registry
│   ├── llm_setup.py             # Single model (qwen2.5-coder-1.5b)
│   ├── workmode.py              # PLAN/BUILD mode switch
│   ├── health.py                # Ollama health, GPU check
│   ├── self_heal.py             # Post-edit typecheck
│   ├── log.py                   # Task logging
│   ├── start.py                 # Pipeline prime
│   └── run_router.py            # Plugin entry point
├── instructions/                # AI rules (2 files)
├── data/                        # Context, whitelist, skills
│   ├── skill-whitelist.json     # 162 whitelisted skills
│   └── context/                 # Project context files
├── .opencode/                   # Runtime state + plugin
├── docs/                        # Documentation
└── pyproject.toml
```

## Tech Stack

| Component | Role | Source |
|-----------|------|--------|
| Python 3.10+ | Core orchestrator | farewell-assistant |
| OpenCode | AI coding assistant | Anomaly Co. |
| Ollama | Local LLM runtime | ollama.ai |
| qwen2.5-coder-1.5b | Classification + execution | HuggingFace |
| ECC | 162 skills (whitelisted) | GitHub |

## Cost: **$0** (semua lokal, no API calls)

## License: MIT
