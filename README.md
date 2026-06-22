# farewell-assistant

> **Zero-cost AI coding assistant. Intent-driven. Multi-provider. GPU-aware.**

Python orchestrator yang menggabungkan OpenCode + 9Router + ECC menjadi satu pipeline intent-driven. Auto-classify task, chain skill yang tepat, route ke model yang optimal — semua dari satu perintah.

---

## Workflow Utama

### Diagram Alur Kerja

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   STEP 1: Register Project                                               │
│   ┌──────────────────────────────────────────────────────┐              │
│   │  Buka farewell-assistant workspace:                  │              │
│   │    cd ~/Documents/farewell-assistant                 │              │
│   │    opencode                                          │              │
│   │                                                      │              │
│   │  Ketik:                                              │              │
│   │    /setup-project C:\Users\You\Documents\my-project  │              │
│   │                                                      │              │
│   │  Yang terjadi:                                       │              │
│   │    1. Detect project type (Flutter/NestJS/Python...) │              │
│   │    2. Register di registry.json (auto code 003)      │              │
│   │    3. Buat junction .opencode/ → farewell-assistant   │              │
│   └──────────────────────────────────────────────────────┘              │
│                              │                                           │
│                              ▼                                           │
│   STEP 2: Buka Workspace Project + Start                                 │
│   ┌──────────────────────────────────────────────────────┐              │
│   │  Buka terminal baru di folder project:               │              │
│   │    cd C:\Users\You\Documents\my-project              │              │
│   │    opencode                                          │              │
│   │                                                      │              │
│   │  Ketik:                                              │              │
│   │    /start-project 003                                │              │
│   │                                                      │              │
│   │  Yang terjadi:                                       │              │
│   │    1. Set my-project sebagai active project          │              │
│   │    2. Load context dari registry                     │              │
│   │    3. Pipeline siap menerima input                   │              │
│   └──────────────────────────────────────────────────────┘              │
│                              │                                           │
│                              ▼                                           │
│   STEP 3: Farewell ON — Pipeline Menangani Semua Input                    │
│   ┌──────────────────────────────────────────────────────┐              │
│   │  User ketik: "bikin crud user dengan auth JWT"       │              │
│   │                                                      │              │
│   │  Plugin intercept → pipeline jalankan:               │              │
│   │    Input → Local LLM (Enrich) → Rule Check           │              │
│   │    → Select Model → Execute with Precision Input     │              │
│   │                                                      │              │
│   │  Output:                                             │              │
│   │  ┌────────────────────────────────────────────┐     │              │
│   │  │ Farewell: ON | Project: 003-my-project     │     │              │
│   │  │ BUILD | Turn: 1 | Chain: 8 | 80% | Eco     │     │              │
│   │  │                                            │     │              │
│   │  │ User: bikin crud user dengan auth JWT       │     │              │
│   │  └────────────────────────────────────────────┘     │              │
│   └──────────────────────────────────────────────────────┘              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Apa yang Terjadi di Balik Layar

```
User Input (di workspace project manapun)
  │
  ▼
┌─────────────────┐
│ OpenCode Plugin │ ← intercept setiap pesan via chat.message hook
│ (intent-router) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Local LLM      │ ← Ollama enrich → JSON intent/classify
│  (qwen2.5 1.5B) │    Skip jika eco mode atau input < 3 kata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Rule Check     │ ← PLAN mode? → Block build/fix/deploy
│  (PLAN/BUILD)   │    BUILD mode? → Lanjut
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Select Model   │ ← Complexity → model combo
│  + Skill Chain  │    low/medium → Free | high → Emergency
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execute        │ ← AI model eksekusi dengan presisi
│  (AI Model)     │    Precision rules: max 2 tanya, YAGNI, terse
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Footer Output  │ ← "Farewell: ON | Project: XXX | ..."
│  (di chat)      │
└─────────────────┘
```

---

## Prerequisites

| Component | Minimum | Notes |
|-----------|---------|-------|
| Python | 3.10+ | `py --version` |
| Node.js | 18+ | Untuk 9Router |
| Git | 2.x | Untuk clone + update |
| Ollama (optional) | Latest | Untuk local LLM enrichment |

---

## Installation

```powershell
git clone https://github.com/fannndi/farewell-assistant.git
cd farewell-assistant
pip install httpx
pip install -e .
```

Copy `api-key.example.txt` → `api-key.txt`, isi API key dari dashboard 9Router (`http://localhost:20128/dashboard`).

---

## Quick Start

### 1. Start farewell-assistant (sekali saja per hari)

```powershell
py -m farewell_assistant.cli daily
```

Atau di dalam OpenCode: `/daily`

### 2. Register Project

```powershell
# Dari farewell-assistant workspace
/setup-project C:\Users\You\Documents\my-project
```

### 3. Buka Project + Gunakan

```powershell
# Buka terminal baru di folder project
cd C:\Users\You\Documents\my-project
opencode
/start-project 003  # atau code yang didapat
```

Sekarang setiap input di-handle oleh farewell-assistant!

---

## Daily Routines

### Pagi — Startup

```powershell
py -m farewell_assistant.cli daily
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

---

## Architecture

### Bagaimana Pipeline Bekerja

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  farewell-assistant (root)                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ .opencode/                                               │   │
│  │ ├── plugins/intent-router.js  ← plugin untuk OpenCode    │   │
│  │ ├── pipeline-result.json      ← output pipeline terakhir │   │
│  │ ├── context.md                ← state session saat ini    │   │
│  │ ├── work-mode.json            ← PLAN atau BUILD          │   │
│  │ └── llm-mode.json             ← eco/balance/performance  │   │
│  │                                                          │   │
│  │ farewell_assistant/                                      │   │
│  │ ├── cli.py                  ← 12 CLI commands            │   │
│  │ ├── intent_router.py        ← classify + route           │   │
│  │ ├── enrichment_pipeline.py  ← Ollama enrichment          │   │
│  │ ├── skill_chain.py          ← 19 built-in chains         │   │
│  │ └── start.py                ← startup orchestrator       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                              │ junction (.opencode/)              │
│                              ▼                                    │
│  my-project/ (workspace lain)                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ .opencode/ ──→ farewell-assistant/.opencode/            │   │
│  │                                                          │   │
│  │ Plugin baca pipeline-result.json dari junction           │   │
│  │ Pipeline tulis hasil ke junction                         │   │
│  │ User tidak perlu tau ada junction                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Model Routing

| Complexity | Primary | Secondary | Heavy |
|------------|---------|-----------|-------|
| low | Free | Free | Free |
| medium | Free | Free | Free |
| high | Free | Emergency | Emergency |
| critical | Emergency | Emergency | Emergency |

---

## Commands

### Core

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `daily` | Startup lengkap + session log | `py -m farewell_assistant.cli daily` |
| `start` | Startup lengkap (7 steps) | `py -m farewell_assistant.cli start` |
| `route` | Test intent router | `py -m farewell_assistant.cli route "bikin CRUD user"` |
| `workmode` | Switch PLAN/BUILD | `py -m farewell_assistant.cli workmode plan` |

### Project

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `setup-project` | Register project + buat junction | `setup-project C:\project` |
| `start-project` | Activate project by code | `start-project 003` |
| `project` | Switch/list project | `project 002` |
| `detect` | Detect project type | `detect ./myapp` |

### LLM

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `llm status` | GPU + Ollama + models | `llm status` |
| `llm eco` | Matikan LLM (zero GPU) | `llm eco` |
| `llm balance` | Switch ke 2B model | `llm balance` |
| `llm auto` | Auto-detect GPU → recommend | `llm auto` |

### OpenCode Slash Commands

| Command | Fungsi |
|---------|--------|
| `/start` | Startup lengkap |
| `/daily` | Daily session + log |
| `/workmode plan|build` | Switch work mode |
| `/start-project 003` | Activate project |
| `/setup-project C:\path` | Register project |
| `/project 002` | Switch active project |
| `/go "task"` | Universal task execution |
| `/plan` | Create implementation plan |
| `/tdd` | TDD workflow |
| `/code-review` | Code review |
| `/security-scan` | Security review |
| `/verify` | Run verification loop |

---

## Work Mode

| Mode | Tools | Use Case |
|------|-------|----------|
| **PLAN** | read, bash | Analisis, audit, riset — TIDAK BOLEH write/edit |
| **BUILD** | read, bash, write, edit | Implementasi, fix, deploy — FULL ACCESS |

**Aturan keras:** AI **TIDAK BOLEH** auto-switch mode. Hanya user yang bisa via `/workmode`.

---

## File Structure

```
farewell-assistant/
├── farewell_assistant/          # Core Python package
│   ├── cli.py                   # CLI dispatcher (12 commands)
│   ├── config.py                # URLs, paths, constants
│   ├── intent_router.py         # Intent → Skill Chain → Model Route
│   ├── enrichment_pipeline.py   # Ollama enrichment + quick classify
│   ├── skill_chain.py           # 19 built-in chains
│   ├── helpers.py               # JSON, Ollama, 9Router, GPU helpers
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
│   └── rules/                   # Core execution rules
├── profiles/                    # Profile templates
├── data/                        # Context, skills, session, memory
├── .opencode/                   # Runtime state + plugins
├── 9router/                     # AI gateway (cloned, gitignored)
├── ecc/                         # 270+ skills (cloned, gitignored)
├── api-key.txt                  # Secrets (gitignored)
├── pyproject.toml               # Python package definition
└── CHANGELOG.md
```

---

## Tech Stack

| Component | Role | Source |
|-----------|------|--------|
| Python 3.10+ | Core orchestrator | farewell-assistant |
| OpenCode | AI coding assistant | Anomaly Co. |
| 9Router | AI gateway (model routing + combo) | GitHub |
| ECC | 270+ skills, 64 agents | GitHub |
| Ollama | Local LLM runtime | ollama.ai |

---

## Cost

| Component | Cost |
|-----------|------|
| OpenCode | Free |
| 9Router | Free |
| ECC | Free |
| Ollama | Free |
| **Total** | **$0** |

---

## License

MIT
