# farewell-assistant

> **AI assistant yang bisa handle semua project. Hemat token, pakai semua potensi GPU.**

Multi-project AI assistant berbasis OpenCode + 9Router + ECC. Didesain dari nol untuk efisiensi token dan fleksibilitas workflow.

---

## Apa Ini?

Seperti punya asisten coding yang:
- **Tau project apa yang sedang kamu kerjakan** - auto-detect stack dan context
- **Hemat token** - instruksi hanya ~800 token (bukan 5000+)
- **Pakai GPU lokal** - enrichment via Ollama saat butuh (opsional)
- **Handle semua project** - Flutter, Go, Node, PHP, Python, Rust, .NET

```
User Input >> Project Detect >> Enrich (opsional) >> Execute >> Response
    │              │                  │                │
    │              │                  │                └─ Cloud AI (9Router)
    │              │                  └─ Local GPU (MX150, qwen2.5:1.5b)
    │              └─ registry.json + context/<slug>.md
    └─ "bikin CRUD user"
```

---

## Arsitektur

### Pipeline: 3 Langkah

| Step | Fungsi | Keterangan |
|------|--------|------------|
| 1. Project Detect | Load project context | Registry + auto-detect |
| 2. Enrichment | Preprocess input (opsional) | Local GPU, smart-skip |
| 3. Execute | Cloud AI kerja | Via 9Router |

### Enrichment: Kapan?

| Input | Enrich? | Alasan |
|-------|---------|--------|
| "bikin CRUD penduduk desa" | Ya | Complex task, domain detection |
| "buat API inventory system" | Ya | Task decomposition |
| "fix bug auth token" | Ya | Context enrichment |
| "hai" | Tidak | Terlalu sederhana |
| "apa itu closure?" | Tidak | Pertanyaan umum |

### GPU: MX150 (2GB VRAM)

| Task | Model | VRAM | Speed |
|------|-------|------|-------|
| Input enrichment | qwen2.5:1.5b-s | ~1GB | ~6.5 tok/s |
| Code review (future) | qwen2.5:1.5b-s | ~1GB | ~6.5 tok/s |

Mode: `eco` (GPU off) atau `on` (GPU active, ~1GB VRAM).

---

## After Clone — First-Time Setup

```powershell
# Prerequisites: Node.js 18+, git, npm
git clone https://github.com/fannndi/farewell-assistant.git
cd farewell-assistant
```

Jalankan satu perintah — sisanya diarahkan oleh script:

```powershell
.\scripts\initial.ps1
```

| Step | Aksi | Catatan |
|------|------|---------|
| 1/10 | Clone ECC + 9Router | Otomatis, butuh internet |
| 2/10 | npm install + build 9Router | ~1-2 menit (Next.js standalone) |
| 3/10 | Start 9Router | Health-check sampai responsive (~20-45s) |
| 4/10 | **Dashboard** | Buka `http://localhost:20128/dashboard` — set password, buat API key + combo |
| 5/10 | Validasi key + combo | Script cek langsung ke 9Router API |
| 6/10 | Init state | eco mode + build work mode |
| 7/10 | Deteksi GPU | Rekomendasi model (LLM lokal) |
| 8/10 | MCP config | Auto-copy template ke `.opencode/mcp-config.json` |
| 9/10 | Autostart | Prompt [y/N] — register Scheduled Task |
| 10/10 | Summary | Status semua komponen |

**Setelah selesai:** edit `api-key.txt` — isi combo models sesuai yang dibuat di dashboard:

```
COMBO_0=oc/deepseek-v4-flash-free,oc/mimo-v2.5-free
```

Lalu jalankan daily start:

```powershell
.\scripts\start.ps1
```

---

## Daily Routine — Pagi Hari Setelah Buka Laptop

### Kalau autostart ENABLED

9Router sudah running otomatis via Scheduled Task (`FarewellAssistant-9Router`).
Cukup buka terminal dan:

```powershell
.\scripts\start.ps1
```

Selesai. Langsung masuk opencode.

### Kalau autostart TIDAK aktif

```powershell
.\scripts\start.ps1
```

Start.ps1 akan:
1. Cek 9Router health → start kalau belum running (build standalone + backoff ~45s)
2. Load `api-key.txt` → set env + extract combo
3. Generate `opencode.jsonc` dari template (dengan combo model)
4. Cek LLM mode → start Ollama kalau bukan `eco`
5. Sync session state → launch opencode

### Cek status (opsional)

```powershell
.\scripts\autostart.ps1 -Action status    # Scheduled Task + 9Router health
.\scripts\llm-setup.ps1 -Action status     # GPU + Ollama + models
```

---

## Owner Notes — Maintenance Berkala

```powershell
.\scripts\owner.ps1
```

Jalankan secara berkala (seminggu sekali atau setelah ada notifikasi update).

### Yang Dilakukan owner.ps1

| Langkah | Aksi |
|---------|------|
| 1/4 | **Pull ECC + 9Router** — source change detection (hash src/ + cli/ + package.json), rebuild standalone kalau ada commit baru, npm install kalau package.json berubah |
| 2/4 | **Changelog analysis** — scan breaking keywords, kasih warning kalau ada migration/deprecation |
| 3/4 | **Doctor check** — ECC exist?, 9Router exist + standalone build?, config?, health?, Ollama? |
| 4/4 | **Ensure 9Router running** — auto-start kalau mati + summary |

### Manual Override

```powershell
.\scripts\autostart.ps1 -Action status     # Cek state + health
.\scripts\autostart.ps1 -Action run         # Trigger task manual
.\scripts\autostart.ps1 -Action disable     # Hentikan autostart
.\scripts\autostart.ps1 -Action enable      # Daftarkan ulang

.\scripts\llm-setup.ps1 -Action pull        # Download GGUF models (butuh ~1-2.5GB)
.\scripts\llm-setup.ps1 -Action remove      # Hapus semua model lokal
.\scripts\detect-project.ps1 -EmitContext   # Generate context template untuk project baru
```

### Logs & Debug

| File | Isi |
|------|-----|
| `.opencode/logs/9router.log` | 9Router stdout |
| `.opencode/logs/9router-error.log` | 9Router stderr |
| `.opencode/logs/autostart.log` | Log Scheduled Task runs |
| `.opencode/9router.pid` | PID 9Router process |
| `logging.md` | Task log semua operasi (gitignored) |

### Dashboard 9Router

Buka `http://localhost:20128/login` di browser.
Password ada di `api-key.txt` (baris `9ROUTER_PASSWORD`).

### Commands

| Command | Fungsi |
|---------|--------|
| `/start` | Daily startup + auto-setup |
| `/owner` | Maintenance + pull update |
| `/autostart enable` | Register Windows Scheduled Task (9Router on logon) |
| `/autostart status` | Cek state scheduled task + 9Router health |
| `/autostart disable` | Unregister scheduled task |
| `/setup eco` | Turn off GPU (alias `/llm-setup eco`) |
| `/setup on` | Turn on GPU (alias `/llm-setup on`) |
| `/setup status` | Check mode (alias `/llm-setup status`) |
| `/llm-setup <mode>` | Full LLM config (eco/on/hot/balance/performance/auto/list/pull/remove) |
| `/detect` | Detect project type dari directory markers |
| `/enrich-check` | Verify enrichment pipeline (diagnostic) |
| `/workmode plan\|build` | Switch work mode |
| `/initial` | One-time install untuk new laptop |
| `/go "task"` | Universal task |

---

## Project Management

### Auto-Detect

```powershell
# Detect project type dari working directory (atau path tertentu)
.\scripts\detect-project.ps1                          # current dir
.\scripts\detect-project.ps1 -Path "C:\my-project"   # specific path
.\scripts\detect-project.ps1 -Path "..." -EmitContext  # + emit context template
```

Detects: Flutter, Node (Next/Nuxt/Vue/React/Express/NestJS/Svelte), Go, PHP/Laravel/Symfony, Python, Rust, .NET, Ruby, Java/Kotlin, Elixir.

### Multi-Project

Setiap project punya context file di `projects/context/<slug>.md`:

```markdown
# servisgadget
Type: Flutter + Laravel API
Stack: Flutter (Riverpod), Laravel 11, MySQL
Focus: Service hub toko gadget
Key:
  - lib/features/admin/
  - backend/app/Http/Controllers/
```

Registry di `projects/registry.json` track project aktif.

---

## File Structure

```
farewell-assistant/
├── scripts/                       # PowerShell automation
│   ├── initial.ps1                # One-time install (clone ECC+9Router, build, init state)
│   ├── start.ps1                  # Daily startup (health + load config + apply profile + launch)
│   ├── owner.ps1                  # Maintenance (pull updates, changelog, doctor, restart)
│   ├── autostart.ps1              # Windows Scheduled Task manager (enable/disable/status/run)
│   ├── llm-setup.ps1              # LLM config (eco/on/hot/balance/performance + auto/list/pull/remove)
│   ├── workmode.ps1               # Switch work mode (plan/build/status)
│   ├── detect-project.ps1         # Project type detection from markers
│   ├── common/
│   │   ├── config.ps1             # Centralized URLs, paths, constants
│   │   ├── helpers.ps1            # Write helpers, JSON state, Ollama, Start-9Router (robust), LLM
│   │   ├── log.ps1                # Write-TaskLog → logging.md
│   │   └── start-9router-bg.ps1   # Hidden wrapper for Scheduled Task
│   └── hooks/
│       ├── check-enrich.ps1       # Enrichment diagnostic command
│       ├── self-heal.ps1          # Post-edit typecheck (project-aware)
│       └── hook-registry.json     # Hook metadata
├── profiles/
│   └── combo/opencode.jsonc       # Single profile template (combo-based)
├── instructions/                  # AI behavior
│   ├── user-rules.md              # Core rules + ROLE enforcement
│   └── preprocess.md              # Enrichment pipeline + footer format
├── commands/                      # Custom command docs
│   ├── initial.md, start.md, owner.md, autostart.md
│   ├── setup.md (alias llm-setup), llm-setup.md
│   ├── workmode.md, detect.md, go.md, enrich-check.md
├── projects/                      # Multi-project management
│   ├── registry.json              # Project index
│   ├── skill-mode-index.json      # Skills per work mode
│   └── context/                   # Per-project context
├── 9router/                       # 9Router (gitignored, cloned by /initial)
├── ecc/                           # ECC skills (gitignored, cloned by /initial)
├── models/                        # GGUF model files (gitignored)
├── .opencode/                     # Runtime state (gitignored)
│   ├── llm-mode.json, work-mode.json, combo.json, 9router.pid
│   ├── session-state.json, context.md
│   ├── mcp-config.json
│   └── logs/                      # 9router.log, 9router-error.log, autostart.log
├── api-key.txt                    # Multi-key storage (gitignored)
├── api-key.example.txt            # Template (committed)
├── Modelfile.qwen2.5-coder-1.5b   # GPU model configs (eco/on)
├── Modelfile.qwen3.5-0.8b         # hot
├── Modelfile.qwen3.5-2b           # balance
├── Modelfile.qwen3.5-4b           # performance
├── CHANGELOG.md                   # Project changelog
├── CHANGELOG_ECC.md               # ECC upstream (auto-sync via /owner)
├── CHANGELOG_9ROUTER.md           # 9Router upstream (auto-sync via /owner)
└── logging.md                     # Task log (gitignored)
```

**Total tracked: ~40 files** (9router/, ecc/, models/, .opencode/ gitignored).

---

## Comparison With opencode-setup

| Metric | opencode-setup | farewell-assistant |
|--------|---------------|-------------------|
| Total tracked files | ~150+ | ~40 |
| Scripts | 64 | 8 (+3 common, +3 hooks) |
| Commands | ~50 | 16 (custom + ECC) |
| Instructions loaded | 19 | 4 |
| Instruction tokens | ~5000+ | ~800 |
| Pipeline steps | 8+ | 3 |
| Multi-project | Overcomplicated | Simple registry |
| 9Router autostart | Manual | Scheduled Task (logon + restart-on-failure) |

---

## Auto-start Setup (Windows)

9Router bisa auto-start pas Windows logon via Scheduled Task (no admin required).

```powershell
# Register scheduled task
.\scripts\autostart.ps1 -Action enable

# Cek state
.\scripts\autostart.ps1 -Action status

# Trigger manual (test)
.\scripts\autostart.ps1 -Action run

# Unregister
.\scripts\autostart.ps1 -Action disable
```

**Cara kerja:**
- Scheduled Task `FarewellAssistant-9Router` trigger `AtLogon` (user context)
- Action: `pwsh.exe -WindowStyle Hidden -File scripts\common\start-9router-bg.ps1`
- Restart-on-failure: 3x dengan interval 5 menit
- Logs: `.opencode\logs\autostart.log`, `9router.log`, `9router-error.log`
- PID tracking: `.opencode\9router.pid` (precision kill, no regex false-positive)
- Stale VBS di Startup folder auto-dihapus pas `enable`

Ollama punya autostart sendiri via `.lnk` di Startup folder (tidak dikelola farewell).

---

## Changelogs

| File | Source | Auto-Sync |
|------|--------|-----------|
| `CHANGELOG.md` | farewell-assistant sendiri | Manual |
| `CHANGELOG_ECC.md` | [affaan-m/ECC](https://github.com/affaan-m/ECC) | ✅ tiap `start.ps1` |
| `CHANGELOG_9ROUTER.md` | [decolua/9router](https://github.com/decolua/9router) | ✅ tiap `start.ps1` |

Update manual: `.\scripts\owner.ps1` (pull ECC + 9Router, rebuild standalone kalau source berubah, sync changelogs, doctor check)

---

## Operating Modes

| Mode | GPU | Enrichment | Use When |
|------|-----|------------|----------|
| `eco` | Off | Disabled | Battery, gaming, simple tasks |
| `on` | ~1GB | Active | Complex tasks, multi-project work |
| `hot` | ~600MB | Active | Outdoor, unplugged, high temp |
| `balance` | ~1.4GB | Active | Indoor, plugged, AC |
| `performance` | ~2.5GB | Active | Indoor, plugged, fan active |

Switch: `/setup eco` / `/setup on` / `/setup hot` / `/setup balance` / `/setup performance` / `/setup auto`

---

## Tech Stack

| Component | Role | Source |
|-----------|------|--------|
| OpenCode | AI coding assistant | Anomaly Co. |
| 9Router | AI gateway (free models) | Local |
| ECC | 270+ skills, 64 agents | affaan-m/ECC |
| Ollama | Local LLM runtime | ollama.ai |
| qwen2.5:1.5b-s | Enrichment model | Qwen |

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

