# Changelog

Semua perubahan penting di farewell-assistant.

---

## [1.3.2] - 2026-06-19 - Fix combo handling + regex

### Fixed
- **Combo handling**: `COMBO_Free=model1,model2,...` diganti `COMBO_0=NamaCombo`. Sekarang value adalah nama combo dari dashboard 9Router, bukan raw model IDs. 9Router menerima `model: "Free"` → detek combo → fallback internal.
- **Regex parsing**: `^([A-Z_]+)=` tidak bisa match `COMBO_0` karena digit `0` tidak di `[A-Z_]`. Fix ke `[A-Z_0-9]` di 3 file (`start.ps1` x2, `start-9router-bg.ps1`).
- **Combo ordering**: Sort keys di `start.ps1` untuk deterministic ordering COMBO_0 → COMBO_1.
- **Combo display badge**: Ganti dari index key ke nama combo.

### Changed
- `api-key.example.txt`: Update format dokumentasi combo baru (numeric index + combo name).
- `api-key.txt`: (gitignored) format baru — user perlu update manual.

### Notes
- `api-key.txt` gitignored — setelah pull, jalankan `/start` untuk regenerate profile.
- Profile di `%USERPROFILE%\.config\opencode\opencode.jsonc` sudah regenerate dengan `"model": "9router/Free"` dan `"small_model": "9router/Emergency"`.

---

## [1.3.1] - 2026-06-17 - Fix standalone static, dashboard

### Fixed
- **9Router dashboard**: Static JS files nggak ke-copy pas build standalone -> dashboard cuma "Loading..."
- **start.ps1**: +Auto-copy `.next/static` ke `.next/standalone/.next/static` setelah build
- **admin.ps1**: +Static copy + password env sebelum restart 9Router

### Added
- `api-key.txt`: +`9ROUTER_PASSWORD` untuk login dashboard 9Router
- `start.ps1`: Pass `INITIAL_PASSWORD` dari api-key.txt ke standalone server

---

## [1.3.0] - 2026-06-17 - Single Profile + Combo Setup

### Changed
- **Profiles**: Hapus `profiles/gratis/` & `profiles/go/`. Ganti dengan `profiles/combo/` - template dengan placeholder `${COMBO_0}`, `${COMBO_1}`, `${COMBO_MODELS}`
- **start.ps1**: Hapus semua logic `-Profile`, wizard pilih profile, persist profile
- **start.ps1**: +Step baru **Combo Setup** - fetch combo dari 9Router API, input combo interaktif (loop), simpan ke `.opencode/combo.json`
- **start.ps1**: Apply profile - substitute `${COMBO_0}`, `${COMBO_1}`, `${COMBO_MODELS}` dengan combo user
- **start.ps1**: Auto-run `opencode` di akhir
- **setup.ps1**: Hapus `-Profile` param, simplifikasi
- **commands/**: `start-free.md` & `start-go.md` >> merge jadi `start.md`

### Added
- **profiles/combo/opencode.jsonc** - single default profile template
- **start.ps1** - Combo Setup: fetch remote combos dari 9Router, input loop, simpan

---

## [1.2.0] - 2026-06-17 - Single-Command Daily Flow

### Changed
- **start.ps1** - Kini jadi satu-satunya command yang perlu dijalankan tiap hari:
  - Auto-clone ECC & 9Router jika belum ada (ganti setup.ps1)
  - Auto-install npm dependencies
  - Update check + changelog sync otomatis
- **README.md** - Simplified workflow, tambah section changelog

### Added
- `CHANGELOG_ECC.md` - Tracked dari upstream affaan-m/ECC
- `CHANGELOG_9ROUTER.md` - Tracked dari upstream decolua/9router
- **start.ps1** Step 5: auto-sync changelog files dari upstream

---

## [1.1.0] - 2026-06-17 - Update Repo & Auto-Check

### Changed
- **ECC** remote >> `github.com/affaan-m/ECC` (upstream)
- **9Router** remote >> `github.com/decolua/9router` (replaces broken `9router/9router`)
- `setup.ps1` clone URLs updated sesuai remote baru

### Added
- **start.ps1** - Update Check: otomatis cek ECC & 9Router untuk update baru tiap startup
- **admin.ps1** - Changelog diff: setelah pull, tampilkan daftar commit baru dari upstream

---

## [1.0.0] - 2026-06-17 - Initial Release

### Architecture
- Built from scratch on OpenCode + 9Router + ECC
- 3-step pipeline: Project Detect >> Enrich >> Execute
- Multi-project support via registry + context files
- Smart enrichment: auto-skip untuk input sederhana

### Scripts (7)
- **setup.ps1** - First install: clone ECC, 9Router, apply profile
- **start.ps1** - Daily startup: health check, apply profile
- **llm-adapter.ps1** - Ollama API wrapper + smart enrichment
- **llm-mode.ps1** - Mode switch: eco / on / status
- **admin.ps1** - Maintenance: pull repos, doctor check
- **detect-project.ps1** - Auto-detect project type (Flutter, Node, Go, PHP, Python, Rust, .NET, Ruby)
- **hooks/check-enrich.ps1** - Enrichment verification
- **hooks/self-heal.ps1** - Post-edit typecheck

### Profiles (2)
- **gratis** - Free models via 9Router
- **go** - Paid models via 9Router

### Instructions (3 files, ~800 tokens)
- **user-rules.md** - Core rules (presisi, max 2 tanya)
- **preprocess.md** - Enrichment pipeline (smart-skip)
- **footer.md** - Footer format (1 baris)

### Commands (14)
- Custom (5): setup, start-free, start-go, admin, go, llm, detect
- ECC (9): plan, tdd, code-review, security-scan, build-fix, verify, update-docs

### Agents (7)
- build, planner, code-reviewer, security-reviewer, tdd-guide, build-error-resolver, doc-updater

### Multi-Project
- `projects/registry.json` - project index
- `projects/context/<slug>.md` - per-project context files
- `detect-project.ps1` - auto-detect project type

### Design Principles
- Every file must justify its existence
- Token-efficient: ~800 tokens instruction (vs ~5000+ in old system)
- GPU-smart: enrichment only when it adds value
- Simple: 3-step pipeline (vs 8+ steps)
- Modular: each component independent

