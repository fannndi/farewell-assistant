# Changelog

Semua perubahan penting di farewell-assistant.

---

## [1.4.0] - 2026-06-19 - Intent-Driven Architecture (Phase 1-4)

### Added — Phase 1: Structured Enrichment
- **enrichment-pipeline.ps1**: `Invoke-StructuredEnrichment` — Ollama (`qwen2.5:1.5b`) mengklasifikasi intent sebagai JSON terstruktur: `{intent, domain, stack, complexity, confidence}`.
- **Get-QuickIntent**: Pattern-based fallback tanpa LLM (regex matching untuk fix/build/review/deploy/research/docs).
- **Intent cache**: Skip enrichment kalau input sama sudah di-cache.

### Added — Phase 2: Intent Router + Skill Chains
- **intent-router.ps1**: `Invoke-IntentRouter` — pipeline lengkap: classify → permission check → skill chain → model route.
- **skill-chain.ps1**: `Get-SkillChain` — mapping intent+domain → urutan skill. 12 built-in chains: build_web, build_mobile, build_infra, build_data, build_automation, build_ai_ml, fix, fix_bug, fix_security, review, review_code, review_security, deploy, research, docs.
- **Chain validation**: `Test-SkillChain` cek skill existence di disk.

### Added — Phase 3: Dynamic Model Routing
- **config.ps1**: `MODEL_ROUTES` — routing complexity → combo (low/medium → Free, high → Emergency, critical → Emergency).
- **Select-ModelRoute**: Dynamic model selection berdasarkan complexity + profile.
- **Intent cache**: Session-scoped cache untuk enrichment results.

### Changed — Phase 4: Pipeline Integration
- **preprocess.md**: Full rewrite — Intent-Driven Pipeline (9 steps). Skill chain tables untuk semua intent+domain. Performance profile table.
- **config.ps1**: +`ENRICHMENT`, `PIPELINE`, skill chain paths. Port configurable via env vars.
- **helpers.ps1**: +`Get-SkillCount`, `Get-ComboDetails` shared functions (Phase 1 dari audit fix).

### Architecture
```
Input → Quick Classify → Structured Enrich (Ollama) → Cache → Rule Check
  → Skill Chain Builder → Model Route → Planning Check → Execute
```

---

## [1.3.4] - 2026-06-19 - Audit fix: critical bugs, docs sync, redundant deps

### Fixed (Critical)
- **llm-setup.ps1**: `ROOT_DIR` computation wrong — `Split-Path -Parent` dipanggil 2x dari `scripts/`, hasilnya parent folder project. Fix ke 1 level.
- **check-enrich.ps1**: `$Input` parameter name shadowing PowerShell automatic variable. Rename ke `$InputText`.
- **check-enrich.ps1**: Wrong file reference `llm-mode.ps1` → `llm-setup.ps1`.

### Fixed (Docs sync)
- **preprocess.md**: BUILD skill count 23 → 24 (actual count). Plus behavioral impact table + footer example.
- **preprocess.md**: Missing skill groups di step 5 (planning, deployment, agent_eng).
- **preprocess.md**: Dynamic rendering path `projects/<active>/kategori` → `projects/registry.json → projects[active].kategori`.
- **context.md**: Remove ghost file refs (`initial.ps1`, `owner.ps1`). Add missing files (`skill-index.json`, hooks/, commands/).
- **go.md**: Profile reference `gratis/go` → `Free/Emergency combo`.
- **api-key.example.txt**: Remove plaintext default password `123456` → `CHANGE_ME`.
- **registry.json**: Update `last_used` dates `2026-06-17` → `2026-06-19`.

### Added (Shared functions)
- **helpers.ps1**: `Get-SkillCount` — centralized skill counting, replaces 3x duplicate logic in start.ps1, log.ps1, workmode.ps1.
- **helpers.ps1**: `Get-ComboDetails` — read combo models from 9Router SQLite, replaces inline Node.js script in start.ps1.
- **commands/workmode.md**: New command doc file (was ghost).
- **commands/enrich-check.md**: New command doc file (was ghost).

### Changed
- **config.ps1**: Port 20128/11434 now configurable via `$env:ROUTER_PORT` / `$env:OLLAMA_PORT`.
- **mcp-config.example.json**: Remove retired `sequential-thinking` MCP (ECC 2.0.0), keep context7/github/memory.
- **.gitignore**: Remove redundant `!projects/context/.gitkeep` (no-op). Remove `.opencode/.gitignore` (whole dir already ignored by root).

### Cleanup
- **context/farewell-assistant.md**: +hook scripts, +skill-index.json, +all command docs to "Key files" list.
- **CHANGELOG.md 1.0.0**: Fix internal count errors (8 vs 7 scripts, 7 vs 5 custom commands).

---

## [1.3.3] - 2026-06-19 - Full Status Report + Model Health Ping

### Added
- **start.ps1**: Full status report setelah `/start` — tampilan rapi: SYSTEM, 9ROUTER, LLM & GPU, COMBOS & PROFILE, MODEL HEALTH, DEPENDENCIES, AUTOSTART, WORK MODE.
- **Model health ping**: Ping tiap model di setiap combo via 9Router API (10s timeout per model). Tampilkan status (✓/✗), HTTP code, response time.
- **Combo model list**: Read combo models dari 9Router SQLite (`better-sqlite3`) via Node.js script — tahu model apa saja di dalam tiap combo.
- **Duration tracking**: Hitung waktu total dari awal script sampai selesai.

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

### Scripts (8)
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

### Instructions (2 files)
- **user-rules.md** - Core rules + ROLE enforcement
- **preprocess.md** - Enrichment pipeline + footer format

### Commands (16)
- Custom (7): setup, start-free, start-go, admin, go, llm, detect
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

