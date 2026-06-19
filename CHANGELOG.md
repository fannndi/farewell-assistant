# Changelog

Semua perubahan penting di farewell-assistant.

---

## [1.5.0] - 2026-06-19 — Pipeline Live: Plugin + Auto-Prefix + 20 Tests

### P0 — Wire Pipeline to Runtime (BREAKING: pipeline now LIVE)
- **`.opencode/plugins/intent-router.js`**: OpenCode plugin via `chat.message` hook → intercepts every user message → shells to `run-router.ps1`. **Blocking mode** (15s timeout): menunggu pipeline selesai, lalu **prepend** prefix `[Pipeline: intent/complexity/confidence% | chain]` ke user message. AI melihat hasil pipeline sebagai baris pertama setiap input.
- **`scripts/run-router.ps1`**: Clean entry point for plugin → dot-sources all pipeline modules → calls `Invoke-IntentRouter`.

### Bug Fixes (verified)
- **Input recording**: `$Input` → `$UserInput` di `Sync-TurnState` (shadowing automatic variable). `input` field sekarang terisi dengan benar.
- **Turn counter**: Persisted ke `.opencode/turn-count` file. Tidak reset setiap kali script dijalankan. Turn 1→2→3 across invocations.
- **Quick-classify threshold**: 0.7 → 0.8. Quick-classify hanya menang untuk high-confidence matches (0.8+). Structured enrichment sekarang dipakai untuk input ambiguous.
- **Planning check**: `critical` complexity sekarang juga trigger planning (sebelumnya hanya `high`).
- **Plugin error logging**: `catch(_e){}` → `console.error("[intent-router] pipeline error:", e.message)`. Error ter-log, bukan silent swallow.
- **powershell-patterns**: Skill ada di `projects/skills/` (bukan `ecc/skills/`). OpenCode benar menemukannya.
- **Auto-Prefix**: Plugin otomatis menambahkan `[Pipeline: intent/complexity/confidence% | chain_summary]` ke setiap user message. AI tidak perlu trigger pipeline manual.
- **preprocess.md**: Updated — dokumentasi auto-prefix + plugin mechanism.
- **.gitignore**: `!.opencode/plugins/` exception untuk plugin tracking.
- **`start.ps1`**: Updated Step 7/7 to prime pipeline at startup (runs `Invoke-IntentRouter` for fresh context before launch).
- **`preprocess.md`**: AI WAJIB trigger pipeline via `trigger-pipeline.ps1` before every turn.

### P1 — Fix Bugs
- **`commands/enrich-check.md` + `go.md`**: Remove `Invoke-LLMEnrich` references (function removed in v1.4.3). Update docs to reference `Invoke-IntentRouter`/`trigger-pipeline.ps1`.
- **`intent-router.ps1`**: `$Result` → `$result` (normalize casing). Intent classification priority: quick (if confident ≥0.7) > structured > quick (fallback).
- **`trigger-pipeline.ps1`**: `$Input` → `$InputText` (PS automatic variable shadowing fix).

### P2 — Dedup & Sync Documentation
- **`intent-router.ps1`**: Remove dead `Select-ModelRoute` fallback (24 lines). `$script:MODEL_ROUTES` from `config.ps1` is single source of truth.
- **`enrichment-pipeline.ps1`**: `"critical"` added to LLM schema (`low|medium|high|critical`) + whitelist. Tier now reachable.
- **`skill-chain.ps1`**: Fix PS array unrolling bug with `,` operator. All 19 chains return correct type.
- **Chain count**: 12 → 19 in all docs (context.md x3, README x2, CHANGELOG).
- **`preprocess.md`**: Fix step ordering (cache=2, enrich=3, classify=4). Add `critical` to planning check.

### P3 — Pester Testing
- **`tests/pipeline.tests.ps1`**: 20 tests across 5 `Describe` blocks:
  - `Get-QuickIntent`: 5 tests (fix, build, deploy, review, ask)
  - `Get-SkillChain`: 5 tests (build_web, build_mobile, fix, deploy, ask)
  - `Test-TaskPermission`: 4 tests (PLAN blocks build, allows review/docs, BUILD allows all)
  - `Select-ModelRoute`: 3 tests (low→Free, high→Emergency, critical→Emergency)
  - `Regression Guard`: 3 tests (functions exist, Invoke-StructuredEnrichment exists, Invoke-LLMEnrich removed)
- **`run-tests.ps1`**: Test runner (invokes Pester on all test files).
- **`tests/test-helper.ps1`**: Bootstrap (dot-sources config/helpers/enrichment/skill-chain/intent-router).
- **Result**: 20/20 passed, 889ms.

### Verification
```
run-router.ps1 "bikin CRUD user" → intent=build source=quick chain=5 ✓
run-router.ps1 "fix bug"         → intent=fix  source=quick chain=3 ✓
Pester suite                      → 20/20 passed, 889ms ✓
```

---

### Fixed — P0 Critical
- **context.md race condition**: Hapus context.md write dari `Sync-SessionState` (log.ps1). Sekarang hanya `Sync-TurnState` yang manage context.md → tidak ada overwrite mid-session.
- **Preprocess.md pipeline flow**: Update steps 1-9 → match actual code (Cache Check step 2, Quick Classify fallback step 4).
- **Critical complexity**: Tambah `"critical"` ke `Select-ModelRoute` → Emergency/Emergency/Emergency.

### Fixed — P1 High
- **Get-QuickIntent**: Tambah `domain` + `stack` detection (web/mobile/infra/data/ai_ml/automation + python/nodejs/flutter/powershell/etc).
- **Dead code removed**: `Parse-ApiKeyFile` (helpers.ps1), `$script:PIPELINE` (config.ps1), duplicate `Stop-OllamaModels` (llm-setup.ps1).
- **$currentCombos scope bug**: Initialize `$currentCombos = @{}` dan `$comboNamesFromFile = @()` sebelum if block.

### Fixed — P2 Medium
- **Hardcoded ports**: Replace `20128` di helpers.ps1 → pakai `$script:ROUTER_PORT` (configurable).
- **Started field**: Baca dari `session-state.json` (session start), bukan current turn time.
- **Footer indicator**: Tambah "Pipeline Status" section ke context.md (enrichment, classification, skill chain, model route status).

### Fixed — P3 Low
- **Duplicate regex**: Hapus `broken|broken` → `broken` di quick intent.
- **Invoke-LLMEnrich**: Mark sebagai DEPRECATED di comment.

### Changed
- **llm-mode.json**: Mode balance aktif (qwen3.5-2b, 1.4GB VRAM)
- **$script:MODEL_ROUTES**: Sekarang dipakai oleh `Select-ModelRoute` (bukan dead code lagi)

---

## [1.4.1] - 2026-06-19 - Precision Context System: Bridge Pipeline → AI

### Problem
Pipeline (enrichment + intent router + skill chain) menghasilkan data kaya per-turn — tapi tidak pernah sampai ke AI. Footer lama 83% noise. AI harus re-classify intent sendiri.

### Added — Precision Context
- **intent-router.ps1**: `Sync-TurnState` — menulis pipeline result ke 2 file:
  - `.opencode/pipeline-result.json` (structured, machine-readable): intent, domain, stack, complexity, confidence, chain, model route, turn count
  - `.opencode/context.md` (AI-readable, injected via instructions): Session State + Turn State
- **Turn counter**: Track nomor turn per sesi
- **Turn state**: Intent, complexity, confidence, stack, chain summary, model route, planning status, blocked tools

### Changed — Context Injection
- **opencode.jsonc template**: +`pipeline-result.json` dan `projects/context/{context_file}.md` ke instructions array
- **start.ps1**: +`{context_file}` variable substitution dari registry.json
- **preprocess.md**: Replace footer format lama (6 field, 2 actionable) → Precision Context System

### Changed — Footer
- **Lama**: `Session: farewell-assistant | Kategori: AUTOMATION | Mode: eco | GPU: off | Work: BUILD | Skills: ON - 24`
- **Baru**: `Intent: build | Chain: 4 steps | Model: Free | Work: BUILD | Turn: 12`
- **Impact**: 3x lebih informatif, 100% actionable

### Architecture — Data Flow
```
User Input
  → Invoke-IntentRouter (classify + route)
  → Sync-TurnState (tulis ke pipeline-result.json + context.md)
  → AI reads context.md (lihat semua data)
  → AI execute (dengan konteks lengkap)
```

---

## [1.4.0] - 2026-06-19 - Intent-Driven Architecture (Phase 1-4)

### Added — Phase 1: Structured Enrichment
- **enrichment-pipeline.ps1**: `Invoke-StructuredEnrichment` — Ollama (`qwen2.5:1.5b`) mengklasifikasi intent sebagai JSON terstruktur: `{intent, domain, stack, complexity, confidence}`.
- **Get-QuickIntent**: Pattern-based fallback tanpa LLM (regex matching untuk fix/build/review/deploy/research/docs).
- **Intent cache**: Skip enrichment kalau input sama sudah di-cache.

### Added — Phase 2: Intent Router + Skill Chains
- **intent-router.ps1**: `Invoke-IntentRouter` — pipeline lengkap: classify → permission check → skill chain → model route.
- **skill-chain.ps1**: `Get-SkillChain` — mapping intent+domain → urutan skill. 19 built-in chains: build_web, build_mobile, build_infra, build_data, build_automation, build_ai_ml, build, fix_bug, fix_security, fix, review_code, review_security, review, deploy, research, research_deep, docs, docs_code, ask.
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

