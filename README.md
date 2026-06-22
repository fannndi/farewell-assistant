# farewell-assistant

> **Zero-cost AI coding assistant. Intent-driven. Multi-provider. GPU-aware.**

Python orchestrator yang menggabungkan OpenCode + 9Router + ECC menjadi satu pipeline intent-driven. Auto-classify task, chain skill yang tepat, route ke model yang optimal — semua dari satu perintah.

---

## Prerequisites

| Component | Minimum | Notes |
|-----------|---------|-------|
| Python | 3.10+ | `py --version` untuk cek |
| Node.js | 18+ | Untuk 9Router (Next.js standalone) |
| Git | 2.x | Untuk clone + update |
| Ollama (optional) | Latest | Untuk local LLM enrichment |

---

## Installation

```powershell
git clone https://github.com/fannndi/farewell-assistant.git
cd farewell-assistant
pip install httpx
```

Copy `api-key.example.txt` → `api-key.txt`, isi API key dari dashboard 9Router (`http://localhost:20128/dashboard`).

---

## Quick Start

```powershell
py -m farewell_assistant.cli start
```

Atau di dalam OpenCode: `/start`

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
                      ┌────────┴────────┐
                      ▼                 ▼
              ┌──────────────┐  ┌──────────────┐
              │  Cloud       │  │  Local       │
              │  LLM Models  │  │  Ollama      │
              └──────────────┘  └──────────────┘
```

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
| `llm auto` | Auto-detect GPU → recommend | `py -m farewell_assistant.cli llm auto` |

### Project

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `project` | Switch/list active project | `py -m farewell_assistant.cli project 002` |
| `setup-project` | Register project dari path lokal | `py -m farewell_assistant.cli setup-project C:\project` |
| `start-project` | List + activate project | `py -m farewell_assistant.cli start-project` |
| `detect` | Detect project type | `py -m farewell_assistant.cli detect ./myapp` |

### Autostart

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `autostart status` | Cek Scheduled Task | `py -m farewell_assistant.cli autostart status` |
| `autostart enable` | Daftarkan autostart | `py -m farewell_assistant.cli autostart enable` |
| `autostart disable` | Hentikan autostart | `py -m farewell_assistant.cli autostart disable` |

### OpenCode Slash Commands

| Command | Fungsi |
|---------|--------|
| `/start` | Startup lengkap |
| `/workmode plan|build` | Switch work mode |
| `/setup <mode>` | Set LLM mode |
| `/project <code>` | Switch active project |
| `/go "task"` | Universal task execution |
| `/plan` | Create implementation plan |
| `/tdd` | TDD workflow |
| `/code-review` | Code review |
| `/security-scan` | Security review (OWASP) |
| `/verify` | Run verification loop |

---

## Work Mode

| Mode | Tools | Use Case |
|------|-------|----------|
| **PLAN** | read, bash | Analisis, audit, riset |
| **BUILD** | read, bash, write, edit | Implementasi, fix, deploy |

---

## Intent Pipeline

```
User Input → Cache Check → Structured Enrich → Quick Classify → Rule Check
→ Skill Chain → Model Route → Planning Check → Execute
```

Pipeline otomatis mengklasifikasi intent (build/fix/review/deploy/research/docs), memilih skill chain yang sesuai, dan meroute ke model combo optimal.

---

## File Structure

```
farewell-assistant/
├── farewell_assistant/          # Core Python package (17 modules)
├── instructions/                # AI rules + pipeline docs
├── profiles/                    # Profile templates
├── data/                        # Context, skills, session, memory
├── tests/                       # Pytest test suite
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
