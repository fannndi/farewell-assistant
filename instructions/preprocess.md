# Preprocess Pipeline — Intent-Driven Architecture

Setiap user input setelah Session Init:

```
1. INPUT           → User input masuk ke pipeline
2. CACHE CHECK     → Skip enrichment kalau input sudah di-cache
3. STRUCTURED ENRICH → Ollama (qwen3.5-2b) klasifikasi intent sebagai JSON
4. QUICK CLASSIFY  → Fallback pattern-based kalau enrichment gagal (tanpa LLM)
5. RULE CHECK      → Validasi permission vs work mode (PLAN/BUILD)
6. SKILL CHAIN     → Bangun urutan skill berdasarkan intent + domain
7. MODEL ROUTE     → Pilih model combo berdasarkan complexity
8. PLANNING CHECK  → Apakah task perlu planning phase dulu?
9. EXECUTE         → Jalankan skill chain dengan model yang dipilih
```

---

## Pipeline Detail

### Step 1: Input

```
User: "bikin CRUD user dengan auth JWT"
```

### Step 2: Cache Check

Intent disimpan di session cache. Kalau input sama muncul lagi, langsung lanjut ke Step 5 (skip enrichment + quick classify).

### Step 3: Structured Enrichment

Ollama (model sesuai active profile: eco=qwen2.5:1.5b, balance=qwen3.5:2b, performance=qwen3.5:4b) mengklasifikasi dengan **JSON output**:

```
Input: "bikin CRUD user dengan auth JWT"
→
{
  "intent": "build",
  "domain": "web",
  "stack": ["fastapi", "postgresql"],
  "complexity": "medium",
  "confidence": 0.85
}
```

**Skip conditions:** mode == eco, input < 3 kata, pertanyaan umum

### Step 4: Quick Classification (Fallback)

Pattern-based (tanpa LLM, instan). Hanya jalan jika Step 3 (Structured Enrichment) gagal atau di-skip:

| Pattern | Intent | Confidence |
|---------|--------|------------|
| fix/bug/error/crash | fix | 0.7 |
| review/audit/check/inspect | review | 0.7 |
| deploy/release/ship/publish | deploy | 0.7 |
| research/search/find | research | 0.7 |
| write/document/docs/readme | docs | 0.7 |
| create/build/make/add/implement/bikin/buat/tambah | build | 0.8 |

### Step 5: Rule Check

| Work Mode | Allowed | Blocked |
|-----------|---------|---------|
| PLAN | research, docs, review, ask | build, fix, deploy |
| BUILD | ALL | NONE |

### Step 6: Skill Chain

Mapping intent + domain → **urutan skill yang dieksekusi berurutan**:

#### BUILD Chains

| Domain | Chain | Steps |
|--------|-------|-------|
| web | build_web | orch-add-feature → api-design → backend-patterns → database-migrations → tdd-workflow → security-review → verification-loop → git-workflow |
| mobile | build_mobile | orch-add-feature → dart-flutter-patterns → database-migrations → tdd-workflow → security-review → verification-loop → git-workflow |
| infra | build_infra | orch-add-feature → deployment-patterns → docker-patterns → kubernetes-patterns → database-migrations → verification-loop → git-workflow |
| data | build_data | orch-add-feature → postgres-patterns → database-migrations → tdd-workflow → verification-loop → git-workflow |
| automation | build_automation | orch-add-feature → powershell-patterns → tdd-workflow → verification-loop → git-workflow |
| ai_ml | build_ai_ml | orch-add-feature → pytorch-patterns → mle-workflow → tdd-workflow → verification-loop → git-workflow |

#### FIX Chains

| Intent | Chain | Steps |
|--------|-------|-------|
| fix (general) | fix | search-first → orch-fix-defect → verification-loop |
| fix (security) | fix_security | repo-scan → security-review → safety-guard → verification-loop → git-workflow |
| fix (bug) | fix_bug | search-first → orch-fix-defect → ai-regression-testing → verification-loop → git-workflow |

#### REVIEW Chains

| Intent | Chain | Steps |
|--------|-------|-------|
| review (code) | review_code | coding-standards → error-handling → security-review → codehealth-mcp → verification-loop |
| review (security) | review_security | repo-scan → security-bounty-hunter → security-scan → verification-loop |

#### DEPLOY Chain

| Intent | Chain | Steps |
|--------|-------|-------|
| deploy | deploy | production-audit → deployment-patterns → canary-watch → git-workflow |

#### RESEARCH Chains

| Intent | Chain | Steps |
|--------|-------|-------|
| research | research | research-ops → documentation-lookup |
| research (deep) | research_deep | research-ops → deep-research → documentation-lookup → competitive-platform-analysis |

#### DOCS Chains

| Intent | Chain | Steps |
|--------|-------|-------|
| docs | docs | codebase-onboarding → article-writing → knowledge-ops |
| docs (code) | docs_code | codebase-onboarding → code-tour → architecture-decision-records → article-writing |

### Step 7: Model Route

| Complexity | Primary | Secondary | Heavy |
|------------|---------|-----------|-------|
| low | Free | Free | Free |
| medium | Free | Free | Free |
| high | Free | Emergency | Emergency |
| critical | Emergency | Emergency | Emergency |

**Free combo:** deepseek-v4-flash-free, mimo-v2.5-free, mmf/mimo-auto (3 models, fast)
**Emergency combo:** big-pickle, north-mini-code-free (2 models, stronger reasoning)

### Step 8: Planning Check

Kalau complexity == "high" OR complexity == "critical" AND intent == "build":
- Aktifkan planning phase dulu (planner agent)
- Decompose task → acceptance criteria → implementasi

Kalau complexity < "high":
- Langsung eksekusi

### Step 9: Execute

Skill chain dijalankan berurutan. Setiap skill:
1. Terima input dari skill sebelumnya
2. Load context dari session
3. Ejekusi dengan model route yang dipilih
4. Output → input ke skill berikutnya

### ⚡ Execution: AI WAJIB Trigger Pipeline

Pipeline (Invoke-IntentRouter) adalah **PowerShell function**, bukan mekanisme internal AI. AI WAJIB menjalankan pipeline secara eksplisit sebelum memproses setiap user input:

**Setiap kali menerima input baru, AI harus:**
1. Jalankan pipeline: jalankan `powershell -ExecutionPolicy Bypass -File "{project}\\scripts\\common\\trigger-pipeline.ps1" -InputText "<user_input>"`
2. Baca `.opencode/pipeline-result.json` untuk intent classification
3. Baca `.opencode/context.md` untuk turn state
4. Lanjutkan eksekusi berdasarkan hasil pipeline

**PENTING:** File pipeline-result.json dan context.md hanya update jika AI menjalankan pipeline. Jangan gunakan data stale. Pipeline harus di-trigger setiap turn.

### 🔄 Auto-Prefix (Plugin)

**Plugin `.opencode/plugins/intent-router.js`** secara otomatis:
1. Menjalankan `Invoke-IntentRouter` via `run-router.ps1` di `chat.message` hook
2. Menambahkan prefix `[Pipeline: intent/complexity/confidence% | chain_summary]` ke user message
3. AI akan melihat prefix ini sebagai baris pertama dari setiap user input

**AI tidak perlu trigger pipeline manual** — plugin sudah melakukannya.
Prefix otomatis muncul di prompt AI sebagai:

```
[Pipeline: build/high/80% | orch-add-feature → ...]
User: bikin CRUD user dengan auth JWT
```

---

## Performance Profile

Enrichment menggunakan model lokal yang sesuai power profile:

| Profile | Model | VRAM | Speed | Enrichment Time |
|---------|-------|------|-------|-----------------|
| Hot | Qwen3.5-0.8B | 600MB | 15-25 tok/s | ~4-7s |
| Eco | Qwen2.5-Coder-1.5B | 1GB | 8-15 tok/s | ~7-13s |
| Balance | Qwen3.5-2B | 1.4GB | 5-10 tok/s | ~10-20s |
| Performance | Qwen3.5-4B | 2.5GB hybrid | 2-5 tok/s | ~40-100s |

**Eco mode:** Enrichment dimatikan (hemat GPU). Quick classification tetap jalan.

---

## Kapan Enrichment Berguna

| Input | Enrich? | Alasan |
|-------|---------|--------|
| "bikin CRUD penduduk desa" | Ya | Domain + stack detection |
| "buat API inventory system" | Ya | Complex task decomposition |
| "fix bug auth token expiry" | Ya | Context enrichment |
| "hai" | Tidak | Terlalu sederhana |
| "apa itu closure?" | Tidak | Pertanyaan umum |
| "fix typo line 45" | Tidak | Simple task |

---

## Mode Behavior

| Mode | Skill Groups | Tools | Behavior |
|------|-------------|-------|----------|
| PLAN | audit, research, explore, planning | read, bash | Read-only, tidak edit file |
| BUILD | orchestration, tdd, coding, security, deployment, agent_eng | read, bash, write, edit | Implementasi, test, commit |

Default: BUILD.

---

## Context Injection (Precision Context System)

Setiap turn, pipeline menghasilkan context yang di-inject ke AI melalui 2 file:

### 1. `pipeline-result.json` (machine-readable)
Ditulis oleh `Invoke-IntentRouter` setelah klasifikasi:
```json
{
  "intent": "build",
  "domain": "web",
  "stack": ["javascript", "react"],
  "complexity": "medium",
  "confidence": 0.95,
  "chain": ["orch-add-feature", "api-design", "backend-patterns"],
  "model_primary": "Free",
  "needs_planning": false,
  "turn": 12
}
```

### 2. `context.md` (AI-readable, injected via instructions array)
Berisi session state + turn state yang diupdate setiap turn:
```markdown
# Session State

- **Project:** farewell-assistant
- **Mode:** balance
- **Work:** BUILD

# Turn State

- **Intent:** build
- **Complexity:** medium
- **Confidence:** 95%(structured)
- **Stack:** javascript, react
- **Chain:** orch-add-feature → api-design → backend-patterns
- **Model:** Free/Free
- **Planning:** no
- **Turn:** 12
```

### 3. Plugin Auto-Prefix (single consistent indicator)
Plugin `.opencode/plugins/intent-router.js` menambahkan **satu baris footer konsisten** ke setiap user message:
```
Intent: build | Complexity: medium (95%) | Domain: web | Chain: 3 steps | Model: Free | Turn: 12 | Mode: balance
```

**Format konsisten** dipakai di SEMUA tempat — plugin prefix, context.md, dan dokumentasi. AI melihat footer ini sebagai baris pertama dari setiap user input.

### Data Flow

```
User Input
  → Plugin chat.message hook
    → Run run-router.ps1 (classify + route)
    → Write pipeline-result.json + context.md
    → Prepend footer ke user message
  → AI reads: footer + context.md + pipeline-result.json
  → AI execute (dengan konteks lengkap)
```

---

## ROLE Enforcement

Work mode (plan/build) adalah **role** yang ditentukan user. AI **DILARANG** mengganti mode sendiri.

### Aturan Keras
1. AI **TIDAK BOLEH** auto-switch work mode - hanya user yang bisa via /workmode
2. Jika user minta eksekusi (/go, edit, write) tapi mode = PLAN -> **HENTIKAN** dan minta user switch mode
3. Jika user minta analisa/audit tapi mode = BUILD -> **TETAP EKSEKUSI** (BUILD bisa semua)
4. Mode switch hanya melalui /workmode plan atau /workmode build - tidak ada cara lain

### Refusal Pattern
```
User: /go bikin CRUD user
AI:   "Anda sedang dalam PLAN mode. Untuk eksekusi, gunakan /workmode build terlebih dahulu."
```

### Logging Rule
AI **WAJIB** log setiap task stage ke file logging.md (project root, gitignored):
```
[timestamp] STAGE: <nama_stage> | ACTION: <apa yg dilakukan> | RESULT: <success/fail> | FILES: <file yg disentuh>
```
