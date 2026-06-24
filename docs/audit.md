# AI Audit — WEB + MOBILE

> Untuk AI model yang kerja di project Web (React/NestJS/Django) dan Mobile (Flutter/Kotlin/Android)
> Versi: 4.1 | Target: < 250 lines

---

# 📖 GUIDEBOOK

## Data Flow (yang AI peduli)

```
User: "bikin halaman login Flutter"
  → Plugin inject footer: Farewell: ON | Project: 002-service-hub | BUILD | Turn: 1 | Chain: 7 | 80% | Eco
  → context.md ditulis:
    - Session State: project, mode, profile
    - Turn State: intent, domain, chain steps, model, blocked
  → AI baca footer + context.md + instruction files
  → AI execute step-by-step dari skill chain
  → LLM call di-routing oleh 9Router (session-pinned combo, lihat Model Routing)
  → Setiap edit → self-heal typecheck
```

## File Kunci (yang wajib AI paham)

| File | Isi | Kenapa AI Peduli |
|------|-----|------------------|
| `.opencode/context.md` | Session + Turn state | **Ini yang saya baca setiap turn** |
| `data/context/{project}.md` | Stack, dir structure, conventions | **Project knowledge** |
| `ecc/skills/{skill}/SKILL.md` | Instruksi domain-specific | **Panduan kerja saya** |
| `data/registry.json` | Project list + codes | **Tau project mana aktif** |
| `instructions/*.md` | Mode enforcement, pipeline rules | **Batas-batas saya** |
| `9router/combo.js` | Model/provider combo selection + session pinning | **Session affinity — cegah cache reset** |
| `9router/chat.js` | Dispatch request per session | **Pin ke combo yang sama di sesi yang sama** |
| `9router/requestDetail.js` | Detail per-request (tokens, model, provider) | **Sumber data cache-hit logging** |
| `9router/usageTracking.js` | Tracking usage + hitung cache-hit ratio | **Nulis ke `logs/cache-hit-ratio.csv`** |
| `logs/cache-hit-ratio.csv` | Log historis cache-hit per request | **Bukti empiris efektivitas session affinity** |

## Mode Enforcement

| Mode | Boleh | Tidak Boleh |
|------|-------|-------------|
| PLAN | read, bash, research, review, docs | write, edit, build, fix, deploy |
| BUILD | ALL | none |

---

# 📚 REFERENCE

## Intent Patterns (Quick Classify)

| Pattern | Intent | Confidence |
|---------|--------|------------|
| fix/bug/error/crash/debug | fix | 0.7 |
| optimize/improve/refactor/upgrade/migrate | fix | 0.7 |
| review/audit/check/inspect | review | 0.7 |
| deploy/release/ship | deploy | 0.7 |
| write/document/docs | docs | 0.7 |
| create/build/make/add/implement/bikin/buat | build | **0.8** |
| research/search/find | research | 0.7 |
| (none match) | ask | 0.6 |

## Domain Detection

| Keyword | Domain |
|---------|--------|
| react/vue/angular/nextjs/crud/auth/jwt/rest/express/django/fastapi/nest/spring | **web** |
| flutter/dart/kotlin/android/ios/swift/compose/mobile | **mobile** |
| apapun yang ga match | **general** |

## Skill Chains (7 yang relevan untuk WEB+MOBILE)

| Input | Chain | Steps |
|-------|-------|-------|
| build + web | **build_web** | orch-add-feature → api-design → backend-patterns → db-migrations → tdd → security-review → verification-loop → git-workflow (8) |
| build + mobile | **build_mobile** | orch-add-feature → flutter-patterns → db-migrations → tdd → security-review → verification-loop → git-workflow (7) |
| fix | **fix** | search-first → orch-fix-defect → verification-loop (3) |
| review | **review** | coding-standards → security-review → verification-loop (3) |
| deploy | **deploy** | production-audit → deployment-patterns → canary-watch → git-workflow (4) |
| research | **research** | research-ops → documentation-lookup (2) |
| ask/docs | **ask/docs** | documentation-lookup (1) |

## Model Routing

| Complexity | Primary | Heavy |
|------------|---------|-------|
| low/medium | Free | Free |
| high | Free | Emergency |
| critical | Emergency | Emergency |

**Session Affinity (9Router):** request pertama di sebuah sesi pilih combo via round-robin → request berikutnya di sesi yang sama **pin** ke combo itu (lihat `combo.js`/`chat.js`). Tujuannya cegah DeepSeek prompt-cache reset — cache provider cuma hit kalau prefix **dan** provider-nya sama. Fallback ke combo lain tetap jalan kalau combo yang dipin gagal (mis. provider down).

## Self-Heal (yang di-validasi post-edit)

| File | Tool | Catatan |
|------|------|---------|
| .ts/.tsx | `tsc --noEmit` | NestJS/React |
| .dart | `flutter analyze` | Flutter |
| .py | `ruff check` | Django/FastAPI |
| .rs | `cargo check` | Rust native (farewell-ex) |
| .kt/.kts | `kotlinc` | Android/Kotlin |
| .sh | `shellcheck` | Scripts |
| .yml/.yaml | `yamllint` | Config |
| .js | `node --check` | 9Router |

---

# ✍️ SKENARIO (11 Soal)

**Cara:** Jalankan command, bandingkan Actual vs Expected. ✅ = 1 poin, ⚠️ = 0.5, ❌ = 0.

---

### S1: Intent Classification — WEB

| # | Input | Expected Intent | Domain | Chain |
|---|-------|----------------|--------|-------|
| 1 | "bikin CRUD user dengan auth JWT" | build | web | build_web (8) |
| 2 | "fix bug login middleware" | fix | web | fix (3) |
| 3 | "deploy API ke production" | deploy | infra | deploy (4) |
| 4 | "review security auth endpoint" | review | web | review (3) |
| 5 | "refactor user service layer" | fix | general | fix (3) |

```powershell
py -m farewell_assistant route "bikin CRUD user dengan auth JWT"
py -m farewell_assistant route "fix bug login middleware"
py -m farewell_assistant route "deploy API ke production"
py -m farewell_assistant route "review security auth endpoint"
py -m farewell_assistant route "refactor user service layer"
```

---

### S2: Intent Classification — MOBILE

| # | Input | Expected Intent | Domain | Chain |
|---|-------|----------------|--------|-------|
| 6 | "bikin halaman login Flutter" | build | mobile | build_mobile (7) |
| 7 | "fix crash saat tap tombol" | fix | mobile | fix (3) |
| 8 | "optimize list view performance" | fix | general | fix (3) |
| 9 | "upgrade AGP gradle version" | fix | general | fix (3) |
| 10 | "review widget tree refactor" | review | mobile | review (3) |

```powershell
py -m farewell_assistant route "bikin halaman login Flutter"
py -m farewell_assistant route "fix crash saat tap tombol"
py -m farewell_assistant route "optimize list view performance"
py -m farewell_assistant route "upgrade AGP gradle version"
py -m farewell_assistant route "review widget tree refactor"
```

---

### S3: Permission — PLAN mode

| # | Input | Mode | Expected |
|---|-------|------|----------|
| 11 | "bikin halaman Flutter" | plan | ❌ BLOCKED |
| 12 | "fix bug login" | plan | ❌ BLOCKED |
| 13 | "review code" | plan | ✅ ALLOWED |
| 14 | "research state management" | plan | ✅ ALLOWED |

```powershell
py -m farewell_assistant workmode plan
py -m farewell_assistant route "bikin halaman Flutter"
py -m farewell_assistant route "fix bug login"
py -m farewell_assistant route "review code"
py -m farewell_assistant route "research state management"
py -m farewell_assistant workmode build
```

---

### S4: Input Sufficiency

| # | Input | Expected |
|---|-------|----------|
| 15 | "hai" | ❌ HOLD |
| 16 | "fix" | ❌ HOLD |
| 17 | "fix bug auth" | ✅ OK |
| 18 | "bikin CRUD" | ✅ OK (build always OK) |

```powershell
py -m farewell_assistant route "hai"
py -m farewell_assistant route "fix"
py -m farewell_assistant route "fix bug auth"
py -m farewell_assistant route "bikin CRUD"
```

---

### S5: Multi-Stack — Web + Mobile (service-hub)

service-hub: NestJS backend + Flutter frontend + Docker + PostgreSQL

| # | Input | Expected Intent | Domain | Gunakan |
|---|-------|----------------|--------|---------|
| 19 | "bikin order API endpoint" | build | web | build_web |
| 20 | "buat screen checkout Flutter" | build | mobile | build_mobile |
| 21 | "add redis service ke compose" | build | infra | build_infra |
| 22 | "migrate prisma schema order" | build | data | build_data |

```powershell
py -m farewell_assistant route "bikin order API endpoint"
py -m farewell_assistant route "buat screen checkout Flutter"
py -m farewell_assistant route "review prisma schema order"
```

---

### S6: Mobile + Native — Kotlin + Rust (farewell-ex)

farewell-ex: Android (Kotlin) + Rust native JNI library

| # | Input | Expected Intent | Domain | Stack |
|---|-------|----------------|--------|-------|
| 23 | "bikin screen GPU monitoring" | build | mobile | kotlin |
| 24 | "optimize sysfs read di Rust" | fix | general | rust |
| 25 | "fix JNI memory leak" | fix | mobile | kotlin |
| 26 | "review kernel module" | review | mobile | rust |

```powershell
py -m farewell_assistant route "bikin screen GPU monitoring"
py -m farewell_assistant route "optimize sysfs read di Rust"
py -m farewell_assistant route "fix JNI memory leak"
py -m farewell_assistant route "review kernel module"
```

---

### S7: Security — Auth & Input

| # | Item | How to Check |
|---|------|-------------|
| 27 | PLAN blocks build intent | `check_task_permission({intent:build}, "plan")` → allowed=False |
| 28 | PLAN blocks fix intent | `check_task_permission({intent:fix}, "plan")` → allowed=False |
| 29 | PLAN allows review | `check_task_permission({intent:review}, "plan")` → allowed=True |
| 30 | API key gitignored | `git check-ignore api-key.txt` → match |
| 31 | No sk- in .py files | `Select-String "sk-" farewell_assistant/*.py` → empty |

```powershell
git check-ignore api-key.txt
Select-String -Path "farewell_assistant/*.py" -Pattern "sk-"
```

---

### S8: Context Quality — Apa yang AI Baca

Cek `.opencode/context.md` setelah route selesai. Minimal harus ada:

| # | Field | Contoh |
|---|-------|--------|
| 32 | Project name | `farewell-assistant` |
| 33 | Project type | `python` |
| 34 | Work mode | `BUILD` |
| 35 | Intent | `build` |
| 36 | Domain | `web` |
| 37 | Complexity | `medium` |
| 38 | Chain steps | detail per step |
| 39 | Turn number | numeric |

```powershell
cat .opencode/context.md
```

---

### S9: Self-Heal — Post-Edit Validation

| # | File | Tool | Catatan |
|---|------|------|---------|
| 40 | `cli.py` | ruff | pyproject.toml ada |
| 41 | fake `.kt` | kotlinc | skip (no marker) |

```powershell
py -m farewell_assistant self-heal --file farewell_assistant/cli.py
```

---

### S10: Full Stack — Dari Input Sampai Eksekusi

| # | Step | Check |
|---|------|-------|
| 42 | Pipeline route "bikin CRUD" | ✅ build/web/medium, chain=8 |
| 43 | Pipeline route "fix bug" | ✅ fix/general/medium, chain=3 |
| 44 | Pipeline route "review code" | ✅ review/general, chain=3 |
| 45 | Switching mode | ✅ plan block, build allow |
| 46 | After all: context.md valid | ✅ Session + Turn state |
| 47 | After all: turn count naik | ✅ incremented |
| 48 | Registry codes unik | ✅ no duplicate |
| 49 | Tests pass | ✅ pytest |

```powershell
py -m pytest -q tests/ --tb=short | Select-Object -Last 3
py -c "import json; r=json.load(open('data/registry.json')); codes=[v['project_code'] for v in r['projects'].values()]; print('Codes:', codes); print('Duplicates:', [c for c in set(codes) if codes.count(c)>1] or 'NONE')"
cat .opencode/turn-count
cat .opencode/context.md
```

---

### S11: Model Routing — Session Affinity & Cache-Hit (9Router)

> Catatan: command asumsi entry point 9Router lo expose session ID via flag/param sejenis. Sesuaikan kalau beda — yang wajib dicek cuma 3: model konsisten per sesi, fallback jalan, ratio ter-log dengan benar.

| # | Check | Expected |
|---|-------|----------|
| 50 | 2 request beruntun, session ID sama → model/provider sama | ✅ pinned (no rotation) |
| 51 | Pinned combo gagal (mis. DeepSeek down) → fallback ke combo lain | ✅ fallback jalan, tetap dapat response |
| 52 | Session tanpa ID (fallback ke message hash) → tetap konsisten | ✅ hash sama → combo sama |
| 53 | Tiap request → row baru di `logs/cache-hit-ratio.csv` | ✅ row baru, kolom lengkap |
| 54 | Cache-hit ratio rata-rata untuk sesi multi-turn | ✅ ≥ 0.80 |
| 55 | Kolom `completion_tokens` (output) terisi | ✅ ada nilai > 0, bukan kosong |

```powershell
# Lihat baris terakhir log
Get-Content logs/cache-hit-ratio.csv -Tail 5

# Cek header — pastikan completion_tokens ada
Get-Content logs/cache-hit-ratio.csv -Head 1

# Rata-rata cache-hit ratio dari seluruh log
py -c "import csv; rows=list(csv.DictReader(open('logs/cache-hit-ratio.csv'))); r=[float(x['ratio']) for x in rows if x.get('ratio')]; print(f'Avg ratio: {sum(r)/len(r):.2%}' if r else 'NO DATA')"

# Cek tiap session cuma pakai 1 model (group by connectionId)
py -c "import csv,collections; rows=list(csv.DictReader(open('logs/cache-hit-ratio.csv'))); g=collections.defaultdict(set); [g[r['connectionId']].add(r['model']) for r in rows]; bad={k:v for k,v in g.items() if len(v)>1}; print(bad or 'OK: tiap session 1 model')"
```

---

**Score Card:** __/55

| Score | Status |
|-------|--------|
| 45-55 | 🟢 GREEN |
| 34-44 | 🟡 YELLOW |
| 17-33 | 🟠 ORANGE |
| <17 | 🔴 RED |
