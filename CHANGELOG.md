# Changelog

Semua perubahan penting di farewell-assistant.

---

## [1.3.0] — 2026-06-17 — Single Profile + Combo Setup

### Changed
- **Profiles**: Hapus `profiles/gratis/` & `profiles/go/`. Ganti dengan `profiles/combo/` — template dengan placeholder `${COMBO_0}`, `${COMBO_1}`, `${COMBO_MODELS}`
- **start.ps1**: Hapus semua logic `-Profile`, wizard pilih profile, persist profile
- **start.ps1**: +Step baru **Combo Setup** — fetch combo dari 9Router API, input combo interaktif (loop), simpan ke `.opencode/combo.json`
- **start.ps1**: Apply profile — substitute `${COMBO_0}`, `${COMBO_1}`, `${COMBO_MODELS}` dengan combo user
- **start.ps1**: Auto-run `opencode` di akhir
- **setup.ps1**: Hapus `-Profile` param, simplifikasi
- **commands/**: `start-free.md` & `start-go.md` → merge jadi `start.md`

### Added
- **profiles/combo/opencode.jsonc** — single default profile template
- **start.ps1** — Combo Setup: fetch remote combos dari 9Router, input loop, simpan

---

## [1.2.0] — 2026-06-17 — Single-Command Daily Flow

### Changed
- **start.ps1** — Kini jadi satu-satunya command yang perlu dijalankan tiap hari:
  - Auto-clone ECC & 9Router jika belum ada (ganti setup.ps1)
  - Auto-install npm dependencies
  - Update check + changelog sync otomatis
- **README.md** — Simplified workflow, tambah section changelog

### Added
- `CHANGELOG_ECC.md` — Tracked dari upstream affaan-m/ECC
- `CHANGELOG_9ROUTER.md` — Tracked dari upstream decolua/9router
- **start.ps1** Step 5: auto-sync changelog files dari upstream

---

## [1.1.0] — 2026-06-17 — Update Repo & Auto-Check

### Changed
- **ECC** remote → `github.com/affaan-m/ECC` (upstream)
- **9Router** remote → `github.com/decolua/9router` (replaces broken `9router/9router`)
- `setup.ps1` clone URLs updated sesuai remote baru

### Added
- **start.ps1** — Update Check: otomatis cek ECC & 9Router untuk update baru tiap startup
- **admin.ps1** — Changelog diff: setelah pull, tampilkan daftar commit baru dari upstream

---

## [1.0.0] — 2026-06-17 — Initial Release

### Architecture
- Built from scratch on OpenCode + 9Router + ECC
- 3-step pipeline: Project Detect → Enrich → Execute
- Multi-project support via registry + context files
- Smart enrichment: auto-skip untuk input sederhana

### Scripts (7)
- **setup.ps1** — First install: clone ECC, 9Router, apply profile
- **start.ps1** — Daily startup: health check, apply profile
- **llm-adapter.ps1** — Ollama API wrapper + smart enrichment
- **llm-mode.ps1** — Mode switch: eco / on / status
- **admin.ps1** — Maintenance: pull repos, doctor check
- **detect-project.ps1** — Auto-detect project type (Flutter, Node, Go, PHP, Python, Rust, .NET, Ruby)
- **hooks/check-enrich.ps1** — Enrichment verification
- **hooks/self-heal.ps1** — Post-edit typecheck

### Profiles (2)
- **gratis** — Free models via 9Router
- **go** — Paid models via 9Router

### Instructions (3 files, ~800 tokens)
- **user-rules.md** — Core rules (presisi, max 2 tanya)
- **preprocess.md** — Enrichment pipeline (smart-skip)
- **footer.md** — Footer format (1 baris)

### Commands (14)
- Custom (5): setup, start-free, start-go, admin, go, llm, detect
- ECC (9): plan, tdd, code-review, security-scan, build-fix, verify, update-docs

### Agents (7)
- build, planner, code-reviewer, security-reviewer, tdd-guide, build-error-resolver, doc-updater

### Multi-Project
- `projects/registry.json` — project index
- `projects/context/<slug>.md` — per-project context files
- `detect-project.ps1` — auto-detect project type

### Design Principles
- Every file must justify its existence
- Token-efficient: ~800 tokens instruction (vs ~5000+ in old system)
- GPU-smart: enrichment only when it adds value
- Simple: 3-step pipeline (vs 8+ steps)
- Modular: each component independent
