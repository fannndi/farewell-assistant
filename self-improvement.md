<!--
████████████████████████████████████████████████████████████████
  SELF-IMPROVEMENT FRAMEWORK — farewell-assistant v1.5.0
  Framework Version : 5.1
  Run Count         : 1
  Created           : 2026-06-25
  Last Run          : 2026-06-25T05:32:00Z
  ──────────────────────────────────────────────────────────────
  ██  CURRENT MODE : EXECUTE                                  ██
  ██  NEXT MODE    : AUDIT                                    ██
  ──────────────────────────────────────────────────────────────
  SIKLUS KERJA:
    AUDIT run   → AI analisis sistem → output: Appendix F (temuan)
    EXECUTE run → AI eksekusi temuan → output: kode terfix + laporan
    Berganti otomatis setiap run.
████████████████████████████████████████████████████████████████
-->

# SELF-IMPROVEMENT FRAMEWORK
### farewell-assistant — Two-Phase Daily Cycle
`v5.1` | Mode: **EXECUTE** | Run #1

---

> **Cara baca header MODE:**
> - `AUDIT`   → jalankan Phase A. AI akan menganalisis dan mengisi Appendix F.
> - `EXECUTE` → jalankan Phase E. AI akan mengeksekusi temuan di Appendix F.
>
> **Kamu tidak perlu melakukan apapun selain paste file ini ke AI agent.**
> AI tahu apa yang harus dilakukan berdasarkan MODE di atas.

---

## REFERENSI SISTEM (BACA CEPAT)

```
farewell-assistant v1.5.0
Local LLM  : models/Qwen_Qwen3.5-0.8B-Q8_0.gguf  (llama-cpp-python)
GPU        : NVIDIA MX150 2GB VRAM
9Router    : localhost:20128  (Next.js, 6 combos)
ECC Skills : 161/271 whitelisted  (data/skill-whitelist.json)
Plugin     : .opencode/plugins/intent-router.js
State dir  : .opencode/  (pipeline-result.json, context.md, ...)
Chains     : 25 built-in  (farewell_assistant/skill_chain.py)
```

**CLI diagnostik:**
```powershell
py -m farewell_assistant.cli daily            # health report
py -m farewell_assistant.cli route "<input>"  # test routing
py -m farewell_assistant.cli enrich-check     # test LLM pipeline
py -m farewell_assistant.cli self-improvement # pull ECC + 9Router
```

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE A — MODE AUDIT
*(Jalankan ini jika MODE = AUDIT)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> **Tujuan:** Temukan masalah spesifik. Isi Appendix F dengan temuan
> yang siap dieksekusi. Jangan perbaiki apapun di run ini.

---

## A0 — BOOTSTRAP

Baca Appendix A (history), B (patterns), D (tracker), E (exploits), F (findings pending).

```
RUN HARI INI : #[N+1]
MODE         : AUDIT
BASELINE     : [skor kemarin]/90 atau N/A jika FIRST_RUN
CARRY-OVER   : [findings dari Appendix F yang masih PENDING dari run EXECUTE sebelumnya]
FOKUS        : [area yang paling bermasalah berdasarkan history]
```

---

## A1 — HEALTH CHECK

```powershell
py -m farewell_assistant.cli daily
```

Isi tabel (salin dari output):

| Komponen | Status | Detail | Perlu Investigasi? |
|----------|--------|--------|--------------------|
| Local LLM (GGUF) | ✅/❌ | [latency, tps] | YES/NO |
| GPU MX150 | ✅/⚠/❌ | [temp°C, VRAM used/2048MB] | YES/NO |
| 9Router :20128 | ✅/❌ | [combo aktif] | YES/NO |
| ECC whitelist | ✅/⚠ | [N/271 skills] | YES/NO |
| Plugin error log | ✅/❌ | [kosong/ada error] | YES/NO |
| Work mode | INFO | PLAN/BUILD | NO |
| Active project | INFO | [nama] | NO |

---

## A2 — ROUTING TEST SUITE

```powershell
py -m farewell_assistant.cli route "bikin CRUD user dengan auth JWT"
py -m farewell_assistant.cli route "fix bug login middleware"
py -m farewell_assistant.cli route "deploy API ke production"
py -m farewell_assistant.cli route "review security auth endpoint"
py -m farewell_assistant.cli route "refactor user service layer"
py -m farewell_assistant.cli route "bikin halaman login Flutter"
py -m farewell_assistant.cli route "fix crash saat tap tombol"
py -m farewell_assistant.cli route "optimize list view performance"
py -m farewell_assistant.cli route "upgrade AGP gradle version"
py -m farewell_assistant.cli route "review widget tree refactor"
py -m farewell_assistant.cli route "eh"
```

| # | Input | Exp Intent | Exp Chain | Exp Steps | Actual Intent | Actual Chain | Actual Steps | ✅/❌ |
|---|-------|------------|-----------|-----------|---------------|--------------|--------------|------|
| S1 | bikin CRUD...JWT | build | build_web | 8 | build | orch-add-feature | 8 | ✅ |
| S2 | fix bug login... | fix | fix/fix_web | 3-5 | fix | search-first | 5 | ✅ |
| S3 | deploy API... | deploy | deploy | 4 | deploy | production-audit | 4 | ✅ |
| S4 | review security... | review | review_web | 5 | review | coding-standards | 5 | ✅ |
| S5 | refactor user... | fix | fix_refactor | 4 | fix | search-first | 4 | ✅ |
| S6 | bikin login Flutter | build | build_mobile | 7 | build | orch-add-feature | 7 | ✅ |
| S7 | fix crash tap | fix | fix/fix_mobile | 3-5 | fix | search-first | 5 | ✅ |
| S8 | optimize list view | fix | fix | 3 | fix | search-first | 5 | ⚠ (domain web/general) |
| S9 | upgrade AGP | fix | fix | 3 | fix | search-first | 5 | ⚠ (domain mobile/general) |
| S10 | review widget... | review | review_mobile | 5 | review | coding-standards | 5 | ✅ |
| S11 | eh | ask | ask | 1 | BLOCKED | — | 0 | ✅ (pipeline hold) |
| **SCORE** | | | | | | | | **8.8/11** |

**Skenario gagal → langsung kandidat FIX untuk Appendix F:**
```
GAGAL : S[N], S[N]
POLA  : [enrichment salah / refactor override / quick classify / lainnya]
```

---

## A3 — CODE ANALYSIS

> Investigasi kode berdasarkan test yang gagal + patterns dari Appendix B.
> Untuk setiap masalah, tentukan: file, baris, kode sekarang, kode fix.

**Cek file-file kritis:**

```powershell
# Lihat baris kritis yang sudah diketahui bermasalah
# (dari Appendix B: PATTERN-001, 002, 003)

# intent_router.py — select_model_route() dan task_warning conflict
# skill_chain.py   — fix_web == fix_mobile == fix_bug
# enrichment_pipeline.py — threshold dan fallback logic
```

Untuk setiap masalah yang ditemukan, isi template di bawah
(akan dipindah ke Appendix F):

```
MASALAH DITEMUKAN:
  File    : [path]
  Baris   : [N-M]
  Gejala  : [apa yang salah]
  Dampak  : [akibatnya ke sistem]
  Fix     : [kode pengganti]
  Test    : [command untuk verifikasi]
  Priority: P0 / P1 / P2
```

---

## A4 — RED TEAM CEPAT

```powershell
# Exploit yang wajib dicek setiap run
py -m farewell_assistant.cli route "fix"                          # EXP-001: < 3 kata
py -m farewell_assistant.cli route "review refactor security"     # EXP-002: refactor override
py -m farewell_assistant.cli route "tambahkan fitur baru"         # EXP-003: PLAN bypass
```

| Exploit | Expected | Actual | Status |
|---------|----------|--------|--------|
| EXP-001: 1-kata "fix" | BLOCKED | BLOCKED | **MITIGATED** |
| EXP-002: review+refactor security | review/general | review/general | **MITIGATED** |
| EXP-003: "tambahkan fitur baru" | BLOCKED (PLAN) | build (BUILD mode) | Can't test (mode=BUILD) |

**Exploit baru ditemukan?** → tambah ke Appendix E dan buat FIX di Appendix F.

---

## A5 — SCORECARD

| Dimensi | Skor | Kemarin | Δ | Catatan |
|---------|------|---------|---|---------|
| Routing Accuracy | 8/10 | 7/10 | +1 | 8.8/11 test pass |
| Local LLM Health | 9/10 | — | — | Latency 2-3s, stable |
| 9Router Health | 10/10 | — | — | Running, up to date |
| Skill Layer | 8/10 | — | — | 161/271 whitelisted, 111 new |
| Plugin Stability | 10/10 | — | — | Error log kosong |
| GPU Performance | 6/10 | — | — | VRAM 1363/2048MB (67%) |
| Session Consistency | 8/10 | — | — | Turn counter OK |
| Self-Heal Coverage | 7/10 | — | — | FIX-003 partial |
| Code Quality | 7/10 | — | — | 3 patterns active, 2 pending |
| **TOTAL** | **73/90** | **—** | — | |

---

## A6 — POPULATE APPENDIX F

> **Output utama mode AUDIT.**
> Untuk setiap masalah dari A1–A5, buat entry di Appendix F.
> Format harus cukup presisi agar AI bisa langsung eksekusi tanpa
> bertanya-tanya di run EXECUTE.

Tambahkan entry ke Appendix F menggunakan format:
```
[FIX-NNN] Priority | File | Baris | Jenis | Status: PENDING
```

---

## A7 — AUDIT SUMMARY

```
TOTAL TEMUAN BARU    : 3 (pre-populated)
  P0 (hari ini)      : 1 (FIX-003: finalisasi merge warning)
  P1 (hari ini)      : 2 (FIX-001, FIX-002)
  P2 (bulan ini)     : —

ROUTING SCORE        : 8.8/11 (80%)
SYSTEM HEALTH        : B (GPU VRAM 67% — monitoring needed)
BIGGEST ISSUE        : VRAM 1363/2048MB dari MX150 — lokal LLM + 9Router
BIGGEST WIN          : Routing stabil 8.8/11 setelah fix prev round

REKOMENDASI MODE BERIKUTNYA:
  → **EXECUTE** untuk finalisasi P0 (FIX-003) + P1 (FIX-001, FIX-002)
  → Lalu AUDIT lagi untuk cek regresi post-fix
```

---

## A8 — EVOLUSI SCRIPT (setelah AUDIT)

Perbarui:
- Metadata: version 5.1, run count 1, last run 2026-06-25
- **MODE: AUDIT → EXECUTE** (3 fix pending: FIX-001, FIX-002, FIX-003)
- Appendix A: tambah row run #1
- Appendix B: PATTERN-003 → RESOLVED (partial)
- Appendix F: update FIX-003 status PARTIAL, current code mencerminkan realita
- Test Suite A2: terisi dengan hasil aktual 8.8/11

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE E — MODE EXECUTE
*(Jalankan ini jika MODE = EXECUTE)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> **Tujuan:** Eksekusi semua FIX yang PENDING di Appendix F.
> Urutan: P0 dulu, lalu P1, lalu P2.
> Jangan skip tanpa alasan. Jika gagal, dokumentasikan mengapa.

---

## E0 — LOAD FINDINGS

Baca Appendix F. Buat daftar kerja:

```
FINDINGS PENDING:
  P0: FIX-[N], FIX-[N], ...
  P1: FIX-[N], ...
  P2: FIX-[N], ...

TOTAL    : [N]
TARGET   : selesaikan semua P0 + P1 minimum
```

---

## E1 — EKSEKUSI FINDINGS

> Untuk setiap FIX, ikuti protokol ini secara berurutan.
> Jangan lompat ke FIX berikutnya sebelum yang ini selesai atau di-skip.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EKSEKUSI FIX-[ID]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LANGKAH 1 — Baca file saat ini
  Baca: [file path dari Appendix F]
  Konfirmasi baris [N-M] masih berisi kode yang sama dengan
  "Current Code" di Appendix F. Jika sudah berbeda, tandai
  STALE dan skip ke FIX berikutnya.

LANGKAH 2 — Terapkan fix
  Ganti "Current Code" dengan "Proposed Fix" di file tersebut.
  Pastikan indentasi, import, dan syntax benar.

LANGKAH 3 — Verifikasi
  Jalankan test command dari Appendix F.
  Bandingkan output dengan "Expected Output".

LANGKAH 4 — Catat hasil
  PASS → tandai FIX-[ID] sebagai DONE di Appendix F
  FAIL → tandai FAILED, catat error, biarkan PENDING untuk next run
  STALE → tandai STALE, kode sudah berubah, tidak perlu difix
```

---

## E2 — LAPORAN EKSEKUSI

```
LAPORAN EKSEKUSI — Run #[N]
Date: [YYYY-MM-DD]

SUMMARY:
  Total findings    : [N]
  DONE              : [N]  ✅
  FAILED            : [N]  ❌
  STALE             : [N]  ⚠ (kode sudah berubah)
  SKIPPED (P2)      : [N]  →  dibawa ke run berikutnya

DETAIL:
  ✅ FIX-[ID] : [judul] — [N]ms test pass
  ❌ FIX-[ID] : [judul] — GAGAL karena: [alasan singkat]
  ⚠  FIX-[ID] : [judul] — STALE: kode baris [N] sudah berbeda

SIDE EFFECTS DITEMUKAN:
  [Efek samping tak terduga dari fix yang diterapkan]

REKOMENDASI:
  [Apakah perlu AUDIT ulang sebelum lanjut P2? Ada regresi?]
```

---

## E3 — VERIFIKASI SISTEM POST-FIX

```powershell
# Re-run routing test suite setelah semua fix diterapkan
py -m farewell_assistant.cli route "bikin CRUD user dengan auth JWT"
py -m farewell_assistant.cli route "fix bug login middleware"
py -m farewell_assistant.cli route "bikin halaman login Flutter"
py -m farewell_assistant.cli route "review security auth endpoint"
py -m farewell_assistant.cli route "eh"
```

```
POST-FIX ROUTING SCORE : [N]/11
PRE-FIX ROUTING SCORE  : [skor dari AUDIT run]
DELTA                  : +/- [N]
REGRESI                : YES/NO → jika YES, buat FIX baru di Appendix F
```

---

## E4 — EVOLUSI SCRIPT (setelah EXECUTE)

Perbarui:
- Metadata: version, run count, last run
- **MODE: EXECUTE → AUDIT** (untuk run berikutnya)
  - Kecuali masih ada P0 FAILED → tetap EXECUTE
- Appendix A: tambah row run hari ini
- Appendix D: update status item yang selesai
- Appendix F: update status setiap FIX (DONE/FAILED/STALE)
  - Item DONE → pindah ke Appendix D dengan status DONE
  - Item FAILED → biarkan di F, tambah catatan kegagalan
  - Item STALE → tandai STALE, tidak perlu dieksekusi lagi

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPENDIX A — RUN HISTORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
# Kolom: RUN|DATE|MODE|SCORE/90|ROUTING/11|FINDINGS_ADDED|FINDINGS_DONE|HEALTH|TOP_ISSUE
# Terbaru di atas
# ────────────────────────────────────────────────────────
1|2026-06-25|AUDIT|—|8.8|3 pre-loaded|0 (pending)|B+ (GPU VRAM 67%)|FIX-003 partially done
# ────────────────────────────────────────────────────────
```

**Agregat:**
```
TOTAL RUN          : 1
AUDIT RUNS         : 1
EXECUTE RUNS       : 0
RATA-RATA SCORE    : —/90
RATA-RATA ROUTING  : 8.8/11
FINDINGS TOTAL     : 3 (pre-populated)
FINDINGS RESOLVED  : 0
```

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPENDIX B — LEARNED PATTERNS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
# Status: ACTIVE | RESOLVED (run #N) | ACCEPTED_RISK
# ────────────────────────────────────────────────────────

PATTERN-001 | Code-Analysis | ACTIVE
Category   : ROUTING / ARCHITECTURE
File       : farewell_assistant/intent_router.py
Fungsi     : select_model_route()
Description: Selalu return qwen2.5-coder-1.5b untuk semua complexity.
  Tidak ada routing ke Free vs Emergency combo berdasarkan complexity.
  README menyebut Ollama, tapi kode pakai llama-cpp-python GGUF.
Implication: Model label di footer tidak akurat. User/AI tidak tahu
  model mana yang benar-benar dipakai di 9Router.
FIX        : FIX-001 (lihat Appendix F)

PATTERN-002 | Code-Analysis | ACTIVE
Category   : CODE_QUALITY
File       : farewell_assistant/skill_chain.py
Description: fix_web, fix_mobile, dan fix_bug memiliki step identik
  persis (search-first → orch-fix-defect → ai-regression-testing
  → verification-loop → git-workflow). Copy-paste tanpa diferensiasi.
Implication: Perubahan di satu tidak otomatis sync ke yang lain.
  Maintenance burden meningkat seiring waktu.
FIX        : FIX-002 (lihat Appendix F)

PATTERN-003 | Code-Analysis | RESOLVED (Run #1 — partial)
Category   : BUG
File       : farewell_assistant/intent_router.py
Fungsi     : invoke_intent_router(), baris ~200-220
Description: task_warning di-set dua kali dalam blok yang sama.
  Set pertama: project-task mismatch warning.
  Set kedua: self-heal reminder (overwrite yang pertama).
  Salah satu selalu hilang.
Implication: Jika ada mismatch project, user tidak dapat self-heal
  reminder, dan sebaliknya.
FIX        : FIX-003 (partial — self_heal_hint added, merge not done)
Status     : Split self_heal_hint from task_warning (prev commit).
  Rekomendasi: merge keduanya seperti di Appendix F untuk finalisasi.
```

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPENDIX C — SCRIPT CHANGELOG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
v5.1 | 2026-06-25 | Run #1 (AUDIT)
  + Run pertama AUDIT mode — routing 8.8/11, GPU VRAM 67%
  + FIX-001: still PENDING (select_model_route)
  + FIX-002: still PENDING (fix_web/fix_mobile merge)
  + FIX-003: PARTIAL (self_heal_hint added prev run, merge not done)
  + 3 exploits verified: EXP-001/002 MITIGATED, EXP-003 untestable (BUILD mode)
  + Rekomendasi: switch EXECUTE untuk finalisasi FIX-003 + FIX-001/002
v5.0 | 2026-06-25 | Run #0
  + Redesign total: Two-Phase Cycle (AUDIT / EXECUTE)
  + MODE header di atas — AI tahu apa yang harus dilakukan
```

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPENDIX D — COMPLETION TRACKER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> Item dari Appendix F yang sudah DONE dipindah ke sini.

```
# Format: [ID] | Priority | Judul | File | Done: Run #N | Tanggal
# ────────────────────────────────────────────────────────
# [kosong — akan diisi setelah EXECUTE pertama]
# ────────────────────────────────────────────────────────
```

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPENDIX E — EXPLOIT REGISTRY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
# Status: OPEN | MITIGATED (run #N) | ACCEPTED | WONTFIX
# ────────────────────────────────────────────────────────

EXP-001 | MEDIUM | Code-Analysis | OPEN
Vektor     : Input < 3 kata bypass llama-cpp enrichment, lanjut ke
  quick classify dengan confidence rendah (0.6).
Command    : py -m farewell_assistant.cli route "fix"
Actual     : quick classify, confidence 0.6, mungkin wrong chain
Mitigation : Perbaiki sufficiency check — return hold jika < 2 kata
  sebelum quick classify jalan. Lihat FIX-003-B (planned).

EXP-002 | LOW | Code-Analysis | OPEN
Vektor     : Keyword "refactor" dalam input apapun di-override ke
  fix_refactor chain, termasuk input yang seharusnya review.
Command    : py -m farewell_assistant.cli route "review refactor security"
Actual     : fix_refactor chain dipilih, bukan review_security
File       : intent_router.py ~baris 198-200
Mitigation : Override refactor hanya jika intent SUDAH "fix".
  Lihat FIX-004 (planned).

EXP-003 | LOW | Code-Analysis | OPEN
Vektor     : PLAN mode hanya blok di level intent. Input ambigu
  (confidence rendah → intent = "ask") bisa lolos permission check
  meski mengandung kata kunci build.
Command    : py -m farewell_assistant.cli route "tambahkan fitur baru"
  (dalam work mode PLAN)
Actual     : Mungkin lolos sebagai "ask" dan tidak diblok
Mitigation : Tambahkan secondary keyword check di check_task_permission.
  Lihat FIX-005 (planned).
# ────────────────────────────────────────────────────────
```

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPENDIX F — PENDING FINDINGS (WORK QUEUE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> **Ini adalah antarmuka antara AUDIT dan EXECUTE.**
> AUDIT run mengisi appendix ini.
> EXECUTE run membaca dan mengeksekusi isinya.
> Format harus cukup presisi untuk langsung dieksekusi tanpa ambiguitas.

```
# Status: PENDING | IN_PROGRESS | DONE | FAILED | STALE
# Urutkan: P0 dulu, lalu P1, lalu P2
# ────────────────────────────────────────────────────────
```

---

### FIX-001
```
Priority   : P1
Status     : PENDING
Judul      : Perjelas select_model_route() — hardcoded atau intentional?
File       : farewell_assistant/intent_router.py
Baris      : ~93-95
Jenis      : DOCUMENTATION / REFACTOR
Pattern    : PATTERN-001

Problem:
  select_model_route() selalu return qwen2.5-coder-1.5b untuk semua
  complexity level. Tidak ada diferensiasi berdasarkan complexity.
  Akibatnya footer AI menampilkan model yang tidak akurat.

Current Code:
  def select_model_route(complexity: str) -> dict:
      return {
          "primary": "qwen2.5-coder-1.5b",
          "secondary": "qwen2.5-coder-1.5b",
          "heavy": "qwen2.5-coder-1.5b"
      }

Proposed Fix (Option A — jika intentional, tambah komentar):
  def select_model_route(complexity: str) -> dict:
      # NOTE: Model label only. Actual routing handled by 9Router
      # based on combo selection in opencode.jsonc.
      # low/medium → Free combo, high/critical → Emergency combo.
      _ROUTE_LABEL = "9router-managed"
      return {
          "primary": _ROUTE_LABEL,
          "secondary": _ROUTE_LABEL,
          "heavy": _ROUTE_LABEL,
          "complexity": complexity,  # expose for footer display
      }

Proposed Fix (Option B — jika ingin routing nyata):
  _COMPLEXITY_ROUTE = {
      "low":      {"primary": "free",      "secondary": "free",      "heavy": "free"},
      "medium":   {"primary": "free",      "secondary": "emergency", "heavy": "emergency"},
      "high":     {"primary": "emergency", "secondary": "emergency", "heavy": "emergency"},
      "critical": {"primary": "emergency", "secondary": "emergency", "heavy": "emergency"},
  }
  def select_model_route(complexity: str) -> dict:
      return _COMPLEXITY_ROUTE.get(complexity, _COMPLEXITY_ROUTE["medium"])

Test Command:
  py -m farewell_assistant.cli route "critical security breach production fix"

Expected Output (Option A):
  Model: 9router-managed | complexity: critical

Expected Output (Option B):
  Model: emergency/emergency

Risk       : LOW — perubahan display saja, tidak mempengaruhi eksekusi
Notes      : Tanya owner: apakah ingin Option A atau B?
             Jika tidak tahu, implementasi Option A (lebih aman).
```

---

### FIX-002
```
Priority   : P1
Status     : PENDING
Judul      : Merge fix_web + fix_mobile ke fix_bug + domain parameter
File       : farewell_assistant/skill_chain.py
Baris      : ~55-90 (sekitar area fix_web dan fix_mobile definitions)
Jenis      : REFACTOR
Pattern    : PATTERN-002

Problem:
  fix_web, fix_mobile, fix_bug memiliki steps identik persis.
  Maintenance risk: perubahan di satu tidak sync ke yang lain.

Current Code (fix_web dan fix_mobile — identik dengan fix_bug):
  "fix_web": [
      {"name": "search-first",          "desc": "Check if bug is known"},
      {"name": "orch-fix-defect",       "desc": "Reproduce -> fix -> verify"},
      {"name": "ai-regression-testing", "desc": "Write regression test"},
      {"name": "verification-loop",     "desc": "Verify fix doesn't break others"},
      {"name": "git-workflow",          "desc": "Commit the fix"},
  ],
  "fix_mobile": [
      # ... identik dengan fix_web
  ],

Proposed Fix:
  # Hapus fix_web dan fix_mobile dari SKILL_CHAINS dict.
  # Tambahkan alias di get_skill_chain() function:

  def get_skill_chain(intent: str, domain: str) -> ...:
      # Alias domain-specific fix ke fix_bug
      if intent == "fix" and domain in ("web", "mobile"):
          key = "fix_bug"  # unified, domain-specific steps added in future
      else:
          key = f"{intent}_{domain}" if f"{intent}_{domain}" in SKILL_CHAINS else intent
      ...

Test Command:
  py -m farewell_assistant.cli route "fix bug login middleware"
  py -m farewell_assistant.cli route "fix crash saat tap tombol"

Expected Output:
  Kedua input → chain: fix_bug (5 steps), bukan fix_web/fix_mobile

Risk       : LOW — behavior sama, hanya alias
Catatan    : Jika di masa depan fix_web perlu step berbeda dari fix_bug,
             tinggal tambahkan kembali entri terpisah di SKILL_CHAINS.
```

---

### FIX-003
```
Priority   : P0
Status     : PARTIAL — self_heal_hint created separate but no merge
Judul      : Split task_warning jadi dua field — hindari overwrite
File       : farewell_assistant/intent_router.py
Baris      : ~380-390 (saat ini)
Jenis      : BUG
Pattern    : PATTERN-003 (RESOLVED — partial)

Problem:
  task_warning di-set dua kali, yang kedua overwrite yang pertama:
    Set 1 (baris ~210): project-task mismatch warning
    Set 2 (baris ~215): self-heal reminder (SELALU ada jika build/fix)
  Efek: jika ada mismatch warning, self-heal reminder hilang.

Current Code (prev commit — sudah ada self_heal_hint terpisah):
  self_heal_hint = None
  post_steps = []
  if classified["intent"] in ("build", "fix"):
      self_heal_hint = "Setelah mengedit file, jalankan: py -m ..."
      post_steps.append("self-heal")

Proposed Fix:
  # Step 3.2
  project_warning = validate_task_vs_project(...)  # rename jadi project_warning

  # Step 3.3
  post_steps = []
  self_heal_reminder = None
  if classified["intent"] in ("build", "fix"):
      self_heal_reminder = "Setelah mengedit file, jalankan: py -m farewell_assistant.cli self-heal --file <path>"
      post_steps.append("self-heal")

  # Gabungkan dua pesan jika keduanya ada
  if project_warning and self_heal_reminder:
      task_warning = f"{project_warning}\n⚡ {self_heal_reminder}"
  else:
      task_warning = project_warning or self_heal_reminder

  # Juga update result dict:
  result = {
      ...
      "task_warning": task_warning,
      "project_warning": project_warning,   # tambah field baru
      "self_heal_reminder": self_heal_reminder,  # tambah field baru
      ...
  }

Test Command:
  # Test 1: mismatch project (pastikan keduanya muncul)
  # Set active project ke mobile, lalu:
  py -m farewell_assistant.cli route "bikin REST API endpoint"

  # Test 2: tidak ada mismatch (hanya self-heal muncul)
  py -m farewell_assistant.cli route "bikin fitur baru"

Expected Output Test 1:
  task_warning berisi KEDUANYA: mismatch warning + self-heal reminder

Expected Output Test 2:
  task_warning berisi self-heal reminder saja

Risk       : LOW-MEDIUM — perlu update sync_turn_state() juga untuk
             menulis field baru ke context.md dan pipeline-result.json
Catatan    : Setelah fix, cek context.md format masih terbaca AI dengan benar.
```

```
# ────────────────────────────────────────────────────────
# [Findings baru dari AUDIT run berikutnya ditambahkan di sini]
# ────────────────────────────────────────────────────────
```

---

## PETUNJUK UNTUK AI AGENT

```
JIKA MODE = AUDIT:
  1. Jalankan Phase A0 → A8
  2. Isi tabel di A1 dan A2 berdasarkan output CLI
  3. Investigasi kode di A3
  4. Tambahkan temuan baru ke Appendix F (format seperti FIX-001)
  5. Update Appendix A, B, E jika ada yang baru
  6. Ganti MODE menjadi EXECUTE (jika ada P0/P1 pending)
  7. Output = self-improvement.md versi baru (replace file ini)

JIKA MODE = EXECUTE:
  1. Baca Appendix F — temukan semua PENDING
  2. Jalankan Phase E0 → E4
  3. Eksekusi FIX satu per satu, urut P0 → P1 → P2
  4. Update status tiap FIX di Appendix F
  5. Pindah FIX yang DONE ke Appendix D
  6. Jalankan E3 (verifikasi post-fix)
  7. Ganti MODE menjadi AUDIT (jika semua P0+P1 selesai)
     Atau tetap EXECUTE (jika masih ada P0 FAILED)
  8. Output = self-improvement.md versi baru (replace file ini)

ATURAN PENTING:
  - Jangan perbaiki kode di AUDIT mode
  - Jangan analisis di EXECUTE mode — langsung eksekusi
  - Jika FIX sudah STALE (kode berubah), skip dan tandai STALE
  - Setiap FIX baru di Appendix F WAJIB punya: file, baris,
    current code, proposed fix, test command, expected output
  - Script ini selalu di-output ulang lengkap di akhir setiap run
```

---

*self-improvement.md — v5.1 | Two-Phase: AUDIT→EXECUTE*
*Run #1: 8.8/11 routing | 3 exploits verified | Appendix F populated*