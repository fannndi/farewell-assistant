# farewell-assistant

> **Zero-cost AI coding assistant. Intent-driven. Multi-provider. GPU-aware.**

Python orchestrator yang menggabungkan OpenCode + 9Router + NVIDIA NIM + ECC menjadi satu pipeline intent-driven. Auto-classify task, chain skill yang tepat, route ke model yang optimal — semua dari satu perintah. Supports cloud models (DeepSeek, Gemma, Poolside) dan local LLM (Ollama).

---

## Prerequisites

| Component | Minimum | Notes |
|-----------|---------|-------|
| Python | 3.10+ | `py --version` untuk cek |
| Node.js | 18+ | Untuk 9Router (Next.js standalone) |
| Git | 2.x | Untuk clone + update |
| GPU (optional) | 2GB VRAM | Untuk local LLM enrichment. Tanpa GPU = eco mode (no enrichment) |
| Ollama (optional) | Latest | Untuk local LLM runtime |
| NVIDIA API Key (optional) | build.nvidia.com | Untuk DeepSeek V4 Flash/Pro |

---

## Installation

```powershell
git clone https://github.com/fannndi/farewell-assistant.git
cd farewell-assistant
pip install httpx
```

Copy `api-key.example.txt` → `api-key.txt`, isi API key:

| Key | Dapat dari | Wajib? |
|-----|-----------|--------|
| `NINEROUTER_API_KEY` | `http://localhost:20128/dashboard` | Wajib |
| `NVIDIA_FLASH_KEY` | `build.nvidia.com/settings/api-keys` | Opsional (DeepSeek V4 Flash) |
| `NVIDIA_PRO_KEY` | `build.nvidia.com/settings/api-keys` | Opsional (DeepSeek V4 Pro) |

---

## Quick Start

```powershell
# Startup lengkap (7 steps)
py -m farewell_assistant.cli start
```

Atau di dalam OpenCode: `/start`

---

## Daily Routines

### Pagi — Startup

```powershell
py -m farewell_assistant.cli start
```

**7 steps:**

| Step | Action | Detail |
|------|--------|--------|
| 1/7 | Git Pull | Sync perubahan dari device lain |
| 2/7 | Bootstrap | Clone ECC + 9Router (hanya sekali) |
| 3/7 | Update | Pull ECC + 9Router, rebuild kalau ada update |
| 4/7 | 9Router Health | Start kalau belum running |
| 5/7 | Load Config | Parse api-key.txt, generate opencode.jsonc |
| 6/7 | Pipeline Prime | Warm up intent router |
| 7/7 | Ready | Semua komponen siap |

### Siang — Ganti LLM Mode

```powershell
# Hemat battery (outdoor)
py -m farewell_assistant.cli llm eco

# Normal (indoor)
py -m farewell_assistant.cli llm balance

# Heavy task (plugged)
py -m farewell_assistant.cli llm performance
```

### Sore — Cek Status

```powershell
py -m farewell_assistant.cli start
py -m farewell_assistant.cli autostart status
py -m farewell_assistant.cli llm status
```

---

## Architecture

```
┌──────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│   OpenCode   │────▶│   Pipeline Engine    │────▶│    Skill Chain   │
│  (Opencode)  │     │  (Intent Router)     │     │   (19 chains)    │
└──────────────┘     └──────────┬──────────┘     └──────────────────┘
                                │
                                ▼
                      ┌─────────────────┐
                      │   9Router API    │
                      │  localhost:20128 │
                      └────────┬────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │  Free Combo  │   │ NVIDIA Combo │   │Emergency Combo│
    │ (r-r+fallback)│   │ (round-robin)│   │  (fallback)  │
    └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
           │                  │                   │
           ▼                  ▼                   ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │ OpenRouter   │   │ NVIDIA NIM   │   │ Free Tier    │
    │ 10 free models│   │DeepSeek V4   │   │ fallback     │
    └──────────────┘   │Flash + Pro   │   └──────────────┘
                       └──────────────┘
```

---

## Available Models

### Cloud Models (via 9Router)

#### Free Combo — 10 OpenRouter models

| Model | ID | Speed | Context | 
|-------|-----|-------|---------|
| Owl Alpha (2.7T) | `openrouter/owl-alpha` | 18 t/s | 1M |
| Nemotron 3 Super (386B) | `nvidia/nemotron-3-super` | 21 t/s | 1M |
| Poolside Laguna M.1 (610B) | `poolside/laguna-m.1` | 13 t/s | 262K |
| Poolside Laguna XS.2 (98.4B) | `poolside/laguna-xs.2` | 90 t/s | 262K |
| Cohere North Mini Code (13.7B) | `cohere/north-mini-code` | 121 t/s | 256K |
| Gemma 4 31B | `google/gemma-4-31b-it` | 35 t/s | 262K |
| Nemotron 3 Nano Omni (30B) | `nvidia/nemotron-3-nano-omni` | reasoning | 256K |
| Nemotron 3 Nano (30B A3B) | `nvidia/nemotron-3-nano-30b` | 162 t/s | 256K |
| OpenRouter Auto | `openrouter/free` | auto-select | auto |

#### NVIDIA Combo — round-robin Flash + Pro

| Model | Size | Context | Speed | Rate Limit |
|-------|------|---------|-------|------------|
| DeepSeek V4 Flash | 284B MoE | 1M tokens | Fast | 40 RPM (shared) |
| DeepSeek V4 Pro | MoE | 1M tokens | Slower | 40 RPM (shared) |

**Scheduling:** round-robin (bergantian). Request 1 → Flash, Request 2 → Pro, Request 3 → Flash...

### Local Models (via Ollama) — 4 power profiles

| Profile | Model | VRAM | Speed |
|---------|-------|------|-------|
| Hot | Qwen3.5-0.8B | 600MB | 15-25 tok/s |
| Eco | Qwen2.5-Coder-1.5B | 1GB | 8-15 tok/s |
| Balance | Qwen3.5-2B | 1.4GB | 5-10 tok/s |
| Performance | Qwen3.5-4B | 2.5GB | 2-5 tok/s |

---

## Commands

### Core

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `start` | Startup lengkap (7 steps) | `py -m farewell_assistant.cli start` |
| `daily` | Daily session + session log | `py -m farewell_assistant.cli daily` |
| `route` | Test intent router | `py -m farewell_assistant.cli route "bikin CRUD user"` |
| `workmode` | Switch PLAN/BUILD | `py -m farewell_assistant.cli workmode plan` |

### LLM Management

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `llm status` | GPU + Ollama + models | `py -m farewell_assistant.cli llm status` |
| `llm eco` | Matikan LLM (zero GPU) | `py -m farewell_assistant.cli llm eco` |
| `llm hot` | Switch ke 0.8B | `py -m farewell_assistant.cli llm hot` |
| `llm balance` | Switch ke 2B | `py -m farewell_assistant.cli llm balance` |
| `llm performance` | Switch ke 4B | `py -m farewell_assistant.cli llm performance` |
| `llm list` | List semua profiles | `py -m farewell_assistant.cli llm list` |
| `llm pull` | Download semua GGUF | `py -m farewell_assistant.cli llm pull` |
| `llm remove` | Hapus semua models | `py -m farewell_assistant.cli llm remove` |
| `llm auto` | Auto-detect GPU → recommend | `py -m farewell_assistant.cli llm auto` |

### Project

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `project` | Switch/list active project | `py -m farewell_assistant.cli project 002` |
| `setup-project` | Clone git ke TEMP/ + register | `py -m farewell_assistant.cli setup-project https://...` |
| `start-project` | List + activate project | `py -m farewell_assistant.cli start-project` |
| `detect` | Detect project type (16 types) | `py -m farewell_assistant.cli detect ./myapp` |

### Autostart

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `autostart status` | Cek Scheduled Task | `py -m farewell_assistant.cli autostart status` |
| `autostart enable` | Daftarkan autostart | `py -m farewell_assistant.cli autostart enable` |
| `autostart disable` | Hentikan autostart | `py -m farewell_assistant.cli autostart disable` |

### Self-Heal

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `self-heal --file <path>` | Post-edit typecheck | `py -m farewell_assistant.cli self-heal --file src/main.ts` |

### OpenCode Slash Commands

| Command | Fungsi |
|---------|--------|
| `/start` | Startup lengkap |
| `/workmode plan|build` | Switch work mode |
| `/setup <mode>` | Set LLM mode |
| `/llm-setup <mode>` | LLM config |
| `/detect` | Detect project type |
| `/enrich-check` | Test enrichment pipeline |
| `/go "task"` | Universal task execution |
| `/plan` | Create implementation plan |
| `/tdd` | TDD workflow |
| `/code-review` | Code review |
| `/security-scan` | Security review (OWASP) |
| `/build-fix` | Fix build errors |
| `/verify` | Run verification loop |
| `/project <code>` | Switch active project |

---

## Work Mode

| Mode | Tools | Skill Groups | Use Case |
|------|-------|-------------|----------|
| **PLAN** | read, bash | audit, research, explore, planning | Analisis, audit, riset |
| **BUILD** | read, bash, write, edit | orchestration, tdd, coding, security, deployment | Implementasi, fix, deploy |

**Rules:**
- AI **TIDAK BOLEH** auto-switch mode
- Default: BUILD
- PLAN mode blocks: build, fix, deploy
- BUILD mode: full access

---

## Model Routing

| Complexity | Primary | Secondary | Heavy |
|------------|---------|-----------|-------|
| low | `9router/Free` | `9router/Free` | `9router/Free` |
| medium | `9router/Free` | `9router/Free` | `9router/Free` |
| high | `9router/nvidia` | `9router/Emergency` | `9router/Emergency` |
| critical | `9router/nvidia` | `9router/Emergency` | `9router/Emergency` |

**Current agent assignments (all agents → `9router/nvidia`):**
- Build (default), Planner, Code-Reviewer, Security-Reviewer
- TDD-Guide, Build-Error-Resolver, Doc-Updater

---

## Intent Pipeline

```
User Input → Cache Check → Structured Enrich → Quick Classify → Rule Check
→ Skill Chain → Model Route → Planning Check → Execute
```

### 19 Skill Chains

| Intent | Domain | Chain | Steps |
|--------|--------|-------|-------|
| build | web | build_web | 8 steps |
| build | mobile | build_mobile | 7 steps |
| build | infra | build_infra | 7 steps |
| build | data | build_data | 6 steps |
| fix | general | fix | 3 steps |
| fix | bug | fix_bug | 5 steps |
| review | code | review_code | 5 steps |
| review | security | review_security | 4 steps |
| deploy | general | deploy | 4 steps |
| research | general | research | 2 steps |
| research | deep | research_deep | 4 steps |
| docs | general | docs | 3 steps |

---

## File Structure

```
farewell-assistant/
├── farewell_assistant/          # Core Python package (17 modules)
│   ├── cli.py                   # CLI dispatcher (argparse, 12 commands)
│   ├── config.py                # URLs, paths, constants, model routes
│   ├── intent_router.py         # Intent → Skill Chain → Model Route
│   ├── enrichment_pipeline.py   # Structured enrichment + quick classify + cache
│   ├── skill_chain.py           # 19 built-in chains
│   ├── helpers.py               # JSON, Ollama, 9Router, GPU, LLM helpers
│   ├── workmode.py              # PLAN/BUILD mode switch
│   ├── llm_setup.py             # 4 power profiles, GGUF download
│   ├── detect_project.py        # Project type detection (16 types)
│   ├── start.py                 # 7-step startup orchestrator
│   ├── bootstrap.py             # First-run: clone ECC + 9Router
│   ├── update.py                # Git pull, rebuild if needed
│   ├── health.py                # 9Router/Ollama health, GPU check
│   ├── autostart.py             # Cross-platform autostart
│   ├── self_heal.py             # Post-edit typecheck
│   ├── log.py                   # Task logging + session state
│   └── run_router.py            # Entry point for intent-router plugin
├── instructions/                # AI rules + pipeline docs
├── commands/                    # OpenCode command definitions
├── profiles/
│   └── combo/opencode.jsonc     # Profile template (model combo routing)
├── data/
│   ├── context/                 # Per-project context markdown
│   ├── skills/                  # Local (non-ECC) skills
│   ├── session/                 # Session state
│   ├── memory/                  # Persistent memory
│   └── llm/                     # GGUF model files
├── tests/                       # Pytest test suite (5 modules)
├── .opencode/                   # Runtime state + plugins
│   ├── plugins/intent-router.js # Chat.message hook
│   ├── logs/                    # 9Router logs
│   └── *.json                   # Pipeline, cache, mode state
├── 9router/                     # AI gateway (cloned, gitignored)
├── ecc/                         # 270+ skills (cloned, gitignored)
├── models/                      # GGUF files (gitignored)
├── api-key.txt                  # Secrets (gitignored)
├── api-key.example.txt          # Template for API keys
├── pyproject.toml               # Python package definition
├── logging.md                   # Task log (gitignored)
└── CHANGELOG.md
```

---

## Config — How NVIDIA Combo Works

9Router combo system mengelompokkan beberapa model jadi satu endpoint:

```
Config: model "9router/nvidia"
  ↓
9Router: lookup combo "nvidia" di DB
  → models: ["nvidia/deepseek-ai/deepseek-v4-flash", "nvidia/deepseek-ai/deepseek-v4-pro"]
  → strategy: "round-robin"
  ↓
Request 1 → Flash, Request 2 → Pro, Request 3 → Flash...
  ↓
Forward ke https://integrate.api.nvidia.com/v1/chat/completions
```

Provider connections disimpan di 9Router dashboard (`http://localhost:20128`), bukan di file config. Aman dari git leak.

---

## Logs & Debug

| File | Isi |
|------|-----|
| `.opencode/logs/9router.log` | 9Router stdout |
| `.opencode/logs/9router-error.log` | 9Router stderr |
| `.opencode/9router.pid` | PID 9Router process |
| `logging.md` | Task log (gitignored) |
| `.opencode/pipeline-result.json` | Pipeline output |
| `.opencode/intent-cache.json` | Cached intent classifications |

---

## Troubleshooting

### 9Router tidak start
```powershell
netstat -ano | findstr :20128
type .opencode\logs\9router-error.log
py -m farewell_assistant.cli start
```

### Ollama tidak detected
```powershell
py -m farewell_assistant.cli llm status
ollama serve
```

### Pipeline timeout
```powershell
$env:PIPELINE_TIMEOUT = "60000"
```

### Intent cache corrupt
```powershell
Remove-Item .opencode\intent-cache.json
```

---

## Tech Stack

| Component | Role | Source |
|-----------|------|--------|
| Python 3.10+ | Core orchestrator | farewell-assistant |
| OpenCode | AI coding assistant | Anomaly Co. |
| 9Router | AI gateway (model routing + combo) | GitHub |
| NVIDIA NIM | DeepSeek V4 Flash/Pro (cloud) | build.nvidia.com |
| OpenRouter | 10 free cloud models | openrouter.ai |
| ECC | 270+ skills, 64 agents | GitHub |
| Ollama | Local LLM runtime (4 models) | ollama.ai |
| httpx | HTTP client | python-httpx |

---

## Cost

| Component | Cost |
|-----------|------|
| OpenCode | Free |
| 9Router | Free |
| NVIDIA NIM (DeepSeek V4) | Free (prototyping tier, 40 RPM) |
| OpenRouter Free Tier | Free |
| ECC | Free |
| Ollama | Free |
| **Total** | **$0** |

---

## License

MIT