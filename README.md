# farewell-assistant

> **AI assistant yang bisa handle semua project. Hemat token, pakai semua potensi GPU.**

Multi-project AI assistant berbasis OpenCode + 9Router + ECC. Didesain dari nol untuk efisiensi token dan fleksibilitas workflow.

---

## Apa Ini?

Seperti punya asisten coding yang:
- **Tau project apa yang sedang kamu kerjakan** — auto-detect stack dan context
- **Hemat token** — instruksi hanya ~800 token (bukan 5000+)
- **Pakai GPU lokal** — enrichment via Ollama saat butuh (opsional)
- **Handle semua project** — Flutter, Go, Node, PHP, Python, Rust, .NET

```
User Input → Project Detect → Enrich (opsional) → Execute → Response
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

## Quick Setup

### First Install

```powershell
# 1. Clone this repo
git clone https://github.com/fannndi/farewell-assistant.git
cd farewell-assistant

# 2. Run setup (clones ECC + 9Router, applies profile)
.\scripts\setup.ps1

# 3. Edit api-key.txt — isi dengan key dari 9Router
#    Dashboard: http://localhost:20128/dashboard

# 4. Start
.\scripts\start.ps1 -Profile gratis
```

### Daily Startup

```powershell
# Start with free models
.\scripts\start.ps1 -Profile gratis

# Start with paid models
.\scripts\start.ps1 -Profile go

# Then open opencode
opencode
```

### Commands

| Command | Fungsi |
|---------|--------|
| `/setup` | First install |
| `/start-free` | Daily startup (free) |
| `/start-go` | Daily startup (paid) |
| `/admin` | Maintenance |
| `/llm eco` | Turn off GPU |
| `/llm on` | Turn on GPU |
| `/llm status` | Check mode |
| `/detect` | Detect project type |
| `/go "task"` | Universal task |

---

## Project Management

### Auto-Detect

```powershell
# Detect project type dari working directory
.\scripts\detect-project.ps1 -Path "C:\my-project"
```

Detects: Flutter, Node.js, Go, PHP/Laravel, Python, Rust, .NET, Ruby.

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
├── scripts/                    # 7 scripts (bukan 64)
│   ├── setup.ps1               # First install
│   ├── start.ps1               # Daily startup
│   ├── llm-adapter.ps1         # Ollama API + enrichment
│   ├── llm-mode.ps1            # Mode switch (eco/on)
│   ├── admin.ps1               # Maintenance
│   ├── detect-project.ps1      # Project auto-detect
│   └── hooks/
│       ├── check-enrich.ps1    # Enrichment verification
│       └── self-heal.ps1       # Post-edit typecheck
├── profiles/                   # OpenCode configs
│   ├── gratis/opencode.jsonc   # Free models
│   └── go/opencode.jsonc       # Paid models
├── instructions/               # AI behavior (3 files)
│   ├── user-rules.md           # Core rules
│   ├── preprocess.md           # Enrichment pipeline
│   └── footer.md               # Footer format
├── commands/                   # 5 custom commands
│   ├── setup.md
│   ├── start-free.md
│   ├── start-go.md
│   ├── admin.md
│   └── go.md
├── projects/                   # Multi-project management
│   ├── registry.json           # Project index
│   └── context/                # Per-project context
├── .opencode/                  # Runtime state (gitignored)
├── api-key.txt                 # 9Router key (gitignored)
└── Modelfile.qwen2-1.5b       # GPU model config
```

**Total: ~30 files** (dari ~150+ di project lama).

---

## Comparison With opencode-setup

| Metric | opencode-setup | farewell-assistant |
|--------|---------------|-------------------|
| Total files | ~150+ | ~30 |
| Scripts | 64 | 7 |
| Commands | ~50 | 14 (5 custom + 9 ECC) |
| Instructions loaded | 19 | 5 |
| Instruction tokens | ~5000+ | ~800 |
| Pipeline steps | 8+ | 3 |
| Multi-project | Overcomplicated | Simple registry |

---

## Operating Modes

| Mode | GPU | Enrichment | Use When |
|------|-----|------------|----------|
| `eco` | Off | Disabled | Battery, gaming, simple tasks |
| `on` | ~1GB | Active | Complex tasks, multi-project work |

Switch: `/llm eco` or `/llm on`

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
