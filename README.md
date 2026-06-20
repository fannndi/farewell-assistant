# farewell-assistant

> **Zero-cost AI coding assistant. GPU-aware. Intent-driven. Handles every project.**

Python orchestrator yang menggabungkan OpenCode + 9Router + ECC menjadi satu pipeline intent-driven. Auto-classify task, chain skill yang tepat, route ke model yang optimal — semua dari satu perintah.

---

## Prerequisites

| Component | Minimum | Notes |
|-----------|---------|-------|
| Python | 3.10+ | `py --version` untuk cek |
| Node.js | 18+ | Untuk 9Router (Next.js standalone) |
| Git | 2.x | Untuk clone + update |
| GPU (optional) | 2GB VRAM | Untuk local LLM enrichment. Tanpa GPU = eco mode (no enrichment) |
| Ollama (optional) | Latest | Untuk local LLM runtime |

---

## Installation

```powershell
git clone https://github.com/fannndi/farewell-assistant.git
cd farewell-assistant
pip install httpx
```

Copy `api-key.example.txt` → `api-key.txt`, isi API key dan combo definitions.

---

## Daily Routines

### Pagi — Startup (setiap kali buka laptop)

```powershell
py -m farewell_assistant.cli start
```

Atau di dalam opencode: `/start`

**Yang dilakukan (7 step):**

| Step | Action | Detail |
|------|--------|--------|
| 1/7 | Git Pull | Sync perubahan dari device lain |
| 2/7 | Bootstrap | Clone ECC + 9Router (hanya sekali) |
| 3/7 | Update | Pull ECC + 9Router, rebuild kalau ada update |
| 4/7 | 9Router Health | Start kalau belum running |
| 5/7 | Load Config | Parse api-key.txt, generate opencode.jsonc |
| 6/7 | Pipeline Prime | Warm up intent router |
| 7/7 | Ready | Semua komponen siap |

Aman dijalankan berkali-kali — guard skip langkah yang sudah selesai.

### Siang — Ganti LLM Mode sesuai Kondisi

```powershell
# Pindahan dari dalam ke luar ( hemat battery )
py -m farewell_assistant.cli llm eco

# Balik ke meja ( plugged in )
py -m farewell_assistant.cli llm balance

# Heavy task, butuh power
py -m farewell_assistant.cli llm performance
```

### Sore — Cek Status

```powershell
# Cek semua komponen
py -m farewell_assistant.cli start

# Cek 9Router + autostart
py -m farewell_assistant.cli autostart status

# Cek GPU + Ollama + models
py -m farewell_assistant.cli llm status
```

### Malam — Cleanup (opsional)

```powershell
# Matikan autostart kalau tidak dipakai besok
py -m farewell_assistant.cli autostart disable

# Switch ke eco mode (hemat GPU)
py -m farewell_assistant.cli llm eco
```

---

## Commands

### Core

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `start` | **Satu untuk semua** — startup lengkap | `py -m farewell_assistant.cli start` |
| `workmode` | Switch PLAN/BUILD | `py -m farewell_assistant.cli workmode plan` |
| `route` | Test intent router | `py -m farewell_assistant.cli route "bikin CRUD user"` |

### LLM Management

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `llm status` | GPU + Ollama + models info | `py -m farewell_assistant.cli llm status` |
| `llm eco` | Matikan LLM (zero GPU) | `py -m farewell_assistant.cli llm eco` |
| `llm on` | Aktifkan LLM default | `py -m farewell_assistant.cli llm on` |
| `llm hot` | Switch ke 0.8B | `py -m farewell_assistant.cli llm hot` |
| `llm balance` | Switch ke 2B | `py -m farewell_assistant.cli llm balance` |
| `llm performance` | Switch ke 4B | `py -m farewell_assistant.cli llm performance` |
| `llm list` | List semua profiles | `py -m farewell_assistant.cli llm list` |
| `llm pull` | Download semua GGUF | `py -m farewell_assistant.cli llm pull` |
| `llm pull --profile hot` | Download profile spesifik | `py -m farewell_assistant.cli llm pull --profile hot` |
| `llm remove` | Hapus semua models | `py -m farewell_assistant.cli llm remove` |
| `llm auto` | Auto-detect GPU → recommend | `py -m farewell_assistant.cli llm auto` |

### Project

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `detect` | Detect project type | `py -m farewell_assistant.cli detect` |
| `detect --context` | Detect + emit context template | `py -m farewell_assistant.cli detect --context` |
| `detect /path/to/project` | Detect project di path lain | `py -m farewell_assistant.cli detect C:\myapp` |

### Autostart

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `autostart status` | Cek Scheduled Task status | `py -m farewell_assistant.cli autostart status` |
| `autostart enable` | Daftarkan autostart | `py -m farewell_assistant.cli autostart enable` |
| `autostart disable` | Hentikan autostart | `py -m farewell_assistant.cli autostart disable` |

### Self-Heal

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `self-heal --file <path>` | Post-edit typecheck | `py -m farewell_assistant.cli self-heal --file src/main.ts` |

### Di Dalam OpenCode (Slash Commands)

| Command | Fungsi |
|---------|--------|
| `/start` | Startup lengkap |
| `/workmode plan` | Switch ke PLAN (read-only) |
| `/workmode build` | Switch ke BUILD (full access) |
| `/setup <mode>` | Set LLM mode |
| `/llm-setup <mode>` | LLM config |
| `/detect` | Detect project type |
| `/enrich-check` | Test enrichment pipeline |
| `/go "task"` | Universal task execution |
| `/plan` | Create implementation plan (planner agent) |
| `/tdd` | TDD workflow |
| `/code-review` | Code review |
| `/security-scan` | Security review (OWASP) |
| `/build-fix` | Fix build errors |
| `/verify` | Run verification loop |

---

## Work Mode

Dua mode yang menentukan apa yang boleh AI lakukan:

| Mode | Tools | Skill Groups | Use Case |
|------|-------|-------------|----------|
| **PLAN** | read, bash | audit, research, explore, planning | Analisis, audit, riset |
| **BUILD** | read, bash, write, edit | orchestration, tdd, coding, security, deployment | Implementasi, fix, deploy |

**Aturan keras:**
- AI **TIDAK BOLEH** auto-switch mode — hanya user via `/workmode`
- Default: BUILD
- PLAN mode memblokir intent: build, fix, deploy
- BUILD mode boleh semua

---

## Intent Pipeline

```
User Input
    │
    ▼
┌─────────────────┐
│  Cache Check     │  ← Skip kalau sudah di-cache (TTL 1 jam)
└────────┬────────┘
         ▼
┌─────────────────┐
│ Structured Enrich│  ← Ollama (Qwen) — JSON classification
└────────┬────────┘
         ▼
┌─────────────────┐
│  Quick Classify  │  ← Fallback: Regex pattern (instant, no LLM)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Rule Check      │  ← Validasi permission vs work mode
└────────┬────────┘
         ▼
┌─────────────────┐
│  Skill Chain     │  ← 19 built-in chains berdasarkan intent+domain
└────────┬────────┘
         ▼
┌─────────────────┐
│  Model Route     │  ← Complexity → Free/Emergency combo
└────────┬────────┘
         ▼
┌─────────────────┐
│  Planning Check  │  ← High/critical → planning phase dulu
└────────┬────────┘
         ▼
       Execute
```

### Skill Chains

19 chains mapping intent+domain ke urutan skill:

| Intent | Domain | Chain | Steps |
|--------|--------|-------|-------|
| build | web | build_web | orch-add-feature → api-design → backend-patterns → database-migrations → tdd-workflow → security-review → verification-loop → git-workflow |
| build | mobile | build_mobile | orch-add-feature → dart-flutter-patterns → database-migrations → tdd-workflow → security-review → verification-loop → git-workflow |
| build | infra | build_infra | orch-add-feature → deployment-patterns → docker-patterns → kubernetes-patterns → database-migrations → verification-loop → git-workflow |
| build | data | build_data | orch-add-feature → postgres-patterns → database-migrations → tdd-workflow → verification-loop → git-workflow |
| fix | general | fix | search-first → orch-fix-defect → verification-loop |
| fix | bug | fix_bug | search-first → orch-fix-defect → ai-regression-testing → verification-loop → git-workflow |
| review | code | review_code | coding-standards → error-handling → security-review → codehealth-mcp → verification-loop |
| review | security | review_security | repo-scan → security-bounty-hunter → security-scan → verification-loop |
| deploy | general | deploy | production-audit → deployment-patterns → canary-watch → git-workflow |
| research | general | research | research-ops → documentation-lookup |
| research | deep | research_deep | research-ops → deep-research → documentation-lookup → competitive-platform-analysis |
| docs | general | docs | codebase-onboarding → article-writing → knowledge-ops |

---

## Power Profiles

GPU-aware LLM management — sesuaikan dengan kondisi hardware:

| Profile | Condition | Model | VRAM | Speed | Kapan Pakai |
|---------|-----------|-------|------|-------|-------------|
| `hot` | Outdoor, battery | Qwen3.5-0.8B | ~600MB | ~15-25 tok/s | Di luar, hemat battery |
| `eco` | Indoor, unplugged | Qwen2.5-Coder-1.5B | ~1GB | ~8-15 tok/s | Normal mobile work |
| `balance` | Plugged, AC | Qwen3.5-2B | ~1.4GB | ~5-10 tok/s | Kerja di meja |
| `performance` | Plugged, fan | Qwen3.5-4B | ~2.5GB hybrid | ~2-5 tok/s | Heavy tasks |

**Eco mode:** Enrichment dimatikan, GPU zero usage. Quick classify tetap jalan.

---

## Model Routing

Task dikirim ke cloud AI via 9Router. Routing berdasarkan complexity:

| Complexity | Primary | Emergency |
|------------|---------|-----------|
| low | Free (3 models) | Free |
| medium | Free (3 models) | Free |
| high | Free (3 models) | Emergency (2 models) |
| critical | Emergency (2 models) | Emergency |

---

## File Structure

```
farewell-assistant/
├── farewell_assistant/           # Core Python package (17 modules)
│   ├── cli.py                    # CLI dispatcher (argparse)
│   ├── config.py                 # URLs, paths, constants, model routes
│   ├── intent_router.py          # Intent → Skill Chain → Model Route
│   ├── enrichment_pipeline.py    # Structured enrichment + quick classify + cache
│   ├── skill_chain.py            # 19 built-in chains
│   ├── helpers.py                # JSON, Ollama, 9Router, GPU, LLM, parse_api_key
│   ├── workmode.py               # PLAN/BUILD mode switch
│   ├── llm_setup.py              # 4 power profiles, GGUF download, Ollama import
│   ├── detect_project.py         # Project type detection (16 types)
│   ├── start.py                  # 7-step startup orchestrator
│   ├── bootstrap.py              # First-run: clone ECC + 9Router, build
│   ├── update.py                 # Git pull ECC + 9Router, rebuild if needed
│   ├── health.py                 # 9Router/Ollama health, GPU check, model ping
│   ├── autostart.py              # Cross-platform autostart (Windows/Linux)
│   ├── self_heal.py              # Post-edit typecheck
│   ├── log.py                    # Task logging + session state
│   └── run_router.py             # Entry point for plugin
├── scripts/                      # Backward-compat PS1 wrappers → delegate to Python
├── profiles/combo/
│   └── opencode.jsonc            # Profile template
├── instructions/                 # AI rules + pipeline docs
│   ├── user-rules.md
│   └── preprocess.md
├── commands/                     # OpenCode command definitions
├── Project/
│   ├── Context/                  # Per-project context markdown
│   └── Skills/                   # Local (non-ECC) skills
├── tests/
│   ├── test_pipeline.py          # Pipeline tests (20 tests)
│   ├── test_helpers.py           # Helper tests
│   ├── test_detect.py            # Detect project tests
│   ├── test_llm.py               # LLM setup tests
│   └── test_autostart.py         # Autostart tests
├── .opencode/
│   ├── plugins/
│   │   └── intent-router.js      # Chat.message hook (configurable timeout)
│   ├── pipeline-result.json      # Runtime
│   ├── context.md                # Runtime
│   ├── llm-mode.json             # Runtime
│   ├── work-mode.json            # Runtime
│   ├── intent-cache.json         # Runtime (persisted to disk)
│   └── logs/
├── 9router/                      # Cloned (gitignored)
├── ecc/                          # ECC 270+ skills (gitignored)
├── models/                       # GGUF files (gitignored)
├── api-key.txt                   # Secrets (gitignored)
├── api-key.example.txt
├── mcp-config.example.json
├── Modelfile.qwen3.5-*.gguf
├── pyproject.toml                # Python package definition
├── CHANGELOG.md
└── logging.md                    # Task log (gitignored)
```

---

## Logs & Debug

| File | Isi |
|------|-----|
| `.opencode/logs/9router.log` | 9Router stdout |
| `.opencode/logs/9router-error.log` | 9Router stderr |
| `.opencode/9router.pid` | PID 9Router process |
| `logging.md` | Task log semua operasi (gitignored) |
| `.opencode/pipeline-result.json` | Pipeline output terakhir |
| `.opencode/intent-cache.json` | Cached intent classifications |

---

## Tech Stack

| Component | Role | Source |
|-----------|------|--------|
| Python 3.10+ | Core orchestrator | farewell-assistant |
| OpenCode | AI coding assistant | Anomaly Co. |
| 9Router | AI gateway (12 models, 4 strategies) | decolua/9router |
| ECC | 270+ skills, 64 agents | affaan-m/ECC |
| Ollama | Local LLM runtime (4 models) | ollama.ai |
| httpx | HTTP client | python-httpx |

---

## Troubleshooting

### 9Router tidak start

```powershell
# Cek apakah port sudah dipakai
netstat -ano | findstr :20128

# Cek log
type .opencode\logs\9router-error.log

# Force restart
py -m farewell_assistant.cli start
```

### Ollama tidak detected

```powershell
# Cek Ollama status
py -m farewell_assistant.cli llm status

# Start Ollama service
ollama serve

# Cek GPU info
py -m farewell_assistant.cli llm list
```

### Enrichment pipeline timeout

Default timeout 15s. Untuk model besar (performance mode: ~40-100s), set environment variable:

```powershell
$env:PIPELINE_TIMEOUT = "60000"  # 60 seconds
```

### Intent cache corrupt

Hapus file cache:

```powershell
Remove-Item .opencode\intent-cache.json
```

### Pipeline tidak jalan

```powershell
# Test route langsung
py -m farewell_assistant.cli route "bikin CRUD user dengan auth JWT"

# Force enrichment (skip cache)
py -m farewell_assistant.cli route "fix bug auth token" --force
```

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
