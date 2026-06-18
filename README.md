# farewell-assistant

> **AI assistant yang bisa handle semua project. Hemat token, pakai semua potensi GPU.**

Multi-project AI assistant berbasis OpenCode + 9Router + ECC. Didesain dari nol untuk efisiensi token dan fleksibilitas workflow.

---

## Quick Start

```powershell
git clone https://github.com/fannndi/farewell-assistant.git
cd farewell-assistant
.\start.ps1
```

Itu saja. `start.ps1` akan:
1. **Git pull** — sync perubahan dari device lain
2. **Initial bootstrap** (hanya sekali) — clone ECC + 9Router, build, panduan dashboard
3. **Update check** — pull ECC + 9Router, rebuild kalau ada update, scan breaking changes
4. **9Router health** — start kalau belum running
5. **Load config** — parse api-key.txt, diff combo vs cached, generate opencode.jsonc
6. **Autostart** — register Scheduled Task kalau belum ada
7. **Launch** — opencode

Aman dijalankan setiap boot — guard skip langkah yang sudah selesai.

---

## Apa Ini?

Seperti punya asisten coding yang:
- **Tau project apa yang sedang kamu kerjakan** — auto-detect stack dan context
- **Hemat token** — instruksi hanya ~800 token (bukan 5000+)
- **Pakai GPU lokal** — enrichment via Ollama saat butuh (opsional)
- **Handle semua project** — Flutter, Go, Node, PHP, Python, Rust, .NET

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

### GPU: MX150 (2GB VRAM)

| Mode | Model | VRAM | Speed |
|------|-------|------|-------|
| eco | none | 0 | — |
| on | qwen2.5:1.5b-s | ~1GB | ~6.5 tok/s |
| hot | qwen3.5-0.8b | ~600MB | ~10 tok/s |
| balance | qwen3.5-2b | ~1.4GB | ~8 tok/s |
| performance | qwen3.5-4b | ~2.5GB | ~5 tok/s |

---

## Daily Operation

Setelah clone & first run (`.\start.ps1`), cukup satu perintah setiap hari:

```powershell
.\start.ps1
```

Atau di dalam opencode: `/start`

9Router sudah auto-start via Scheduled Task (terdaftar otomatis di step 6).

### Cek status (opsional)

```powershell
.\scripts\autostart.ps1 -Action status    # Scheduled Task + 9Router health
.\scripts\llm-setup.ps1 -Action status     # GPU + Ollama + models
.\scripts\autostart.ps1 -Action run        # Trigger task manual (test)
.\scripts\autostart.ps1 -Action disable    # Hentikan autostart
.\scripts\autostart.ps1 -Action enable     # Daftarkan ulang
```

### Logs & Debug

| File | Isi |
|------|-----|
| `.opencode/logs/9router.log` | 9Router stdout |
| `.opencode/logs/9router-error.log` | 9Router stderr |
| `.opencode/logs/autostart.log` | Log Scheduled Task runs |
| `.opencode/9router.pid` | PID 9Router process |
| `logging.md` | Task log semua operasi (gitignored) |

---

## Commands

| Command | Fungsi |
|---------|--------|
| `/start` | **Satu untuk semua** — git pull, update, health, config, autostart, launch |
| `/autostart enable\|disable\|status\|run` | Manage Scheduled Task |
| `/setup eco\|on\|hot\|balance\|performance` | Set LLM mode (alias `/llm-setup`) |
| `/llm-setup <mode>` | Full LLM config + auto/list/pull/remove |
| `/detect` | Detect project type dari directory markers |
| `/enrich-check` | Verify enrichment pipeline (diagnostic) |
| `/workmode plan\|build` | Switch work mode |
| `/go "task"` | Universal task |

---

## Auto-start (Windows)

9Router auto-start pas Windows logon via Scheduled Task. **Terdaftar otomatis** oleh `start.ps1` step 6.

- Trigger: `AtLogon` (no admin)
- Restart: 3x @ 5 menit kalau crash
- Action: `pwsh.exe -WindowStyle Hidden -File scripts/common/start-9router-bg.ps1`
- Logs: `.opencode/logs/autostart.log`
- PID tracking: `.opencode/9router.pid`
- Ollama punya autostart sendiri via `.lnk` di Startup folder

---

## File Structure

```
farewell-assistant/
├── scripts/
│   ├── start.ps1                  # ★ Konsolidasi: 7-step bootstrap + update + config + report + launch
│   ├── autostart.ps1              # Scheduled Task manager
│   ├── llm-setup.ps1              # LLM config (eco/on/hot/balance/performance)
│   ├── workmode.ps1               # Switch work mode
│   ├── detect-project.ps1         # Project type detection
│   ├── common/
│   │   ├── config.ps1             # URLs, paths, constants (port configurable via env)
│   │   ├── helpers.ps1            # Start-9Router, Ollama, GPU, LLM, Get-SkillCount, Get-ComboDetails
│   │   ├── log.ps1                # Write-TaskLog, Sync-SessionState
│   │   └── start-9router-bg.ps1   # Hidden wrapper for Scheduled Task
│   └── hooks/
│       ├── self-heal.ps1          # Post-edit typecheck (project-aware)
│       └── check-enrich.ps1       # Enrichment diagnostic
├── profiles/combo/opencode.jsonc
├── instructions/
│   ├── user-rules.md
│   └── preprocess.md
├── commands/
│   ├── start.md, autostart.md, llm-setup.md, setup.md
│   ├── workmode.md, detect.md, go.md, enrich-check.md
├── projects/
│   ├── registry.json
│   ├── skill-mode-index.json
│   ├── skill-index.json
│   └── context/
├── 9router/                       # Clone (gitignored)
├── ecc/                           # ECC skills (gitignored)
├── models/                        # GGUF files (gitignored)
├── .opencode/                     # Runtime state (gitignored)
│   ├── llm-mode.json, work-mode.json, combo.json, 9router.pid
│   ├── session-state.json, context.md
│   └── logs/
├── api-key.txt                    # Multi-key storage (gitignored)
├── api-key.example.txt
├── mcp-config.example.json
├── Modelfile.qwen2.5-coder-1.5b
├── Modelfile.qwen3.5-0.8b
├── Modelfile.qwen3.5-2b
├── Modelfile.qwen3.5-4b
├── CHANGELOG.md
├── CHANGELOG_ECC.md
├── CHANGELOG_9ROUTER.md
└── logging.md                     # Task log (gitignored)
```

---

## Comparison With opencode-setup

| Metric | opencode-setup | farewell-assistant |
|--------|---------------|-------------------|
| Total tracked files | ~150+ | ~35 |
| Scripts | 64 | 5 (+4 common, +3 hooks) |
| Commands | ~50 | 8 (custom) + ECC |
| Instructions | 19 | 2 |
| Pipeline steps | 8+ | 3 |
| Multi-project | Overcomplicated | Simple registry |
| Startup command | Manual | 1 perintah: `/start` |

---

## Operating Modes

| Mode | GPU | Enrichment | Use When |
|------|-----|------------|----------|
| `eco` | Off | Disabled | Battery, gaming, simple tasks |
| `on` | ~1GB | Active | Complex tasks, multi-project work |
| `hot` | ~600MB | Active | Outdoor, unplugged, high temp |
| `balance` | ~1.4GB | Active | Indoor, plugged, AC |
| `performance` | ~2.5GB | Active | Indoor, plugged, fan active |

Switch: `/setup eco` / `/setup on` / `/setup hot` / `/setup balance` / `/setup performance`

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
