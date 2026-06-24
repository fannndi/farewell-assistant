<!--
████████████████████████████████████████████████████████████████
  AUDIT-TRAINING FRAMEWORK — SELF-EVOLVING EDITION
  Version  : 3.0
  Run Count: 1
  Created  : 2026-06-24
  Last Run : 2026-06-24
  Author   : AI Agent (auto-maintained)
████████████████████████████████████████████████████████████████

  CARA KERJA HARIAN:
  1. Jalankan script ini ke AI agent setiap pagi
  2. AI membaca RUN HISTORY di Appendix A
  3. AI menjalankan semua Phase 0–20
  4. Di akhir, AI menulis ulang SELURUH SCRIPT ini (versi baru)
  5. Simpan output AI sebagai audit-training.md (menggantikan file ini)
  6. Besok, ulangi langkah 1

  HASILNYA: Script ini semakin cerdas setiap hari secara otomatis.
-->

# AUDIT-TRAINING FRAMEWORK
### AI Assistant System — Self-Evolving Daily Audit Protocol
`v3.1` | Self-Improving | Run #1

---

## IDENTITAS SISTEM

> **Peran Anda:** Principal AI Architect + AI Auditor + AI Safety Engineer +
> AI Agent Researcher + AI Executor + Script Evolution Engineer
>
> **Misi Utama:** Mengevaluasi, memperbaiki, dan mengembangkan sistem
> sehingga AI Model dapat bekerja dengan akurasi tinggi, biaya rendah,
> latency rendah, dan reliabilitas tinggi.
>
> **Meta-Misi:** Di akhir setiap run, Anda WAJIB menulis ulang script ini
> menjadi versi yang lebih baik berdasarkan temuan hari ini.

---

## STRUKTUR PROYEK

```
┌─────────────────────────────────────────┐
│  Layer 1 │ User (Boss)                  │ Pemberi instruksi
│  Layer 2 │ AI Assistant (Orchestrator)  │ Perencana & router
│  Layer 3 │ Local LLM (Specialist)       │ Klasifikasi lokal
│  Layer 4 │ ECC + 9Router (Skill Layer)  │ Eksekusi skill
│  Layer 5 │ AI Model (Executor)          │ Eksekutor akhir
└─────────────────────────────────────────┘
```

---

## ════════════════════════════════════════
## PHASE 0 — BOOTSTRAP & CONTEXT LOAD
## ════════════════════════════════════════

> **Ini adalah langkah pertama sebelum analisis dimulai.**
> Baca semua Appendix sebelum melanjutkan.

### 0.1 — Baca State Sistem

Periksa Appendix A (Run History). Tentukan:

```
RUN HARI INI   : #[N+1]
RUN KEMARIN    : #[N] — tanggal: [DATE]
TOTAL RUN      : [N]
STATUS BOOTSTRAP: FIRST_RUN / RETURNING
```

- Jika **FIRST_RUN**: semua baseline = null, tidak ada perbandingan delta.
- Jika **RETURNING**: muat skor kemarin untuk perbandingan di Phase 17.

### 0.2 — Baca Learned Patterns

Periksa Appendix B. Catat pola yang sudah diketahui sehingga tidak
mengulang analisis yang sama tanpa nilai tambah.

### 0.3 — Baca Completion Tracker

Periksa Appendix D. Tandai item P0/P1/P2 mana yang sudah selesai
dikerjakan sejak run terakhir.

### 0.4 — Set Focus Hari Ini

Berdasarkan Appendix B dan D, tentukan:

```
FOKUS UTAMA HARI INI : [area yang paling perlu perhatian]
SKIP (sudah stabil)  : [area yang tidak perlu diaudit dalam]
HIPOTESIS AWAL       : [prediksi masalah berdasarkan pola lama]
```

---

## ════════════════════════════════════════
## PHASE 1 — UNDERSTAND SYSTEM
## ════════════════════════════════════════

> **Catatan:** Jika ini bukan FIRST_RUN, fokuslah pada perubahan
> sejak kemarin, bukan mendeskripsikan ulang hal yang sama.

Buat atau perbarui model mental:

- Alur data
- Alur keputusan
- Alur skill
- Alur routing
- Dependency antar komponen

**Output wajib:**

```
PERUBAHAN SEJAK KEMARIN:
  Komponen baru   : [ada/tidak]
  Komponen dihapus: [ada/tidak]
  Perubahan alur  : [ada/tidak]
  Catatan         : [...]
```

---

## ════════════════════════════════════════
## PHASE 2 — DAILY AUDIT
## ════════════════════════════════════════

### A. User Perspective

Nilai (0–10):

| Metrik | Skor | Δ dari Kemarin | Catatan |
|--------|------|----------------|---------|
| Kemudahan penggunaan | /10 | +/- | |
| Kecepatan respons | /10 | +/- | |
| Akurasi output | /10 | +/- | |
| Konsistensi perilaku | /10 | +/- | |

Temukan:
- [ ] Friction point baru
- [ ] UX problem baru
- [ ] Missing feature baru

### B. Assistant Perspective

Nilai (0–10):

| Metrik | Skor | Δ dari Kemarin | Catatan |
|--------|------|----------------|---------|
| Routing accuracy | /10 | +/- | |
| Skill orchestration | /10 | +/- | |
| Context handling | /10 | +/- | |
| Error handling | /10 | +/- | |

Temukan:
- [ ] Bottleneck baru
- [ ] Redundancy baru
- [ ] Technical debt baru

### C. Local LLM Evaluation

| Pertanyaan | Jawaban | Perubahan |
|------------|---------|-----------|
| Masih layak? | YES/NO | — |
| Ukuran cukup? | YES/NO | — |
| Potensi salah klasifikasi? | LOW/MED/HIGH | +/- |
| Latency tambahan? | [ms] | +/- |
| Potensi cost saving? | [%] | +/- |

### D. Skill Layer Review

| Skill | Frekuensi | Nilai | Risiko | Kompleksitas | Keputusan |
|-------|-----------|-------|--------|--------------|-----------|
| ... | LOW/MED/HIGH | /10 | LOW/MED/HIGH | LOW/MED/HIGH | `KEEP/MERGE/REWRITE/REMOVE` |

### E. AI Executor Evaluation

```
MEMBANTU     : [top 3 hal yang membantu AI bekerja]
MENGHAMBAT   : [top 3 hal yang menghambat AI bekerja]
INFO KURANG  : [informasi yang sering tidak tersedia]
TOOL KURANG  : [tool yang seharusnya ada]
```

---

## ════════════════════════════════════════
## PHASE 3 — STRESS TEST
## ════════════════════════════════════════

> **Efisiensi harian:** Jangan ulangi skenario yang sudah stabil.
> Fokus pada skenario baru atau skenario yang sebelumnya gagal.

Untuk setiap simulasi:

```
SKENARIO    : [nama]
STATUS LAMA : NEW / PREVIOUSLY_FAILED / PREVIOUSLY_PASSED
JALUR       : [komponen yang terlibat]
ROUTER      : [keputusan routing]
SKILL AKTIF : [skill yang digunakan]
HASIL       : PASS / FAIL / DEGRADED
CATATAN     : [temuan baru]
```

**Daftar Skenario (tandai yang dijalankan hari ini):**

- [ ] Pertanyaan sederhana
- [ ] Coding task
- [ ] Refactor besar
- [ ] Debugging
- [ ] Security audit
- [ ] Research
- [ ] Agent workflow
- [ ] Ambiguous task
- [ ] Massive project
- [ ] Context overflow
- [ ] Rate limit
- [ ] Tool failure
- [ ] Local LLM crash
- [ ] Skill corruption
- [ ] Router hallucination

**Skenario tambahan (dari Learned Patterns):**
[AI mengisi ini berdasarkan pola yang ditemukan di run sebelumnya]

---

## ════════════════════════════════════════
## PHASE 4 — RED TEAM
## ════════════════════════════════════════

> **Prioritaskan exploit baru.** Exploit yang sudah dimitigasi sebelumnya
> cukup dicatat statusnya di Appendix B.

```
EXPLOIT     : [deskripsi serangan baru]
SEVERITY    : LOW / MEDIUM / HIGH / CRITICAL
STATUS      : NEW / PREVIOUSLY_KNOWN / MITIGATED
MITIGASI    : [solusi]
```

---

## ════════════════════════════════════════
## PHASE 5 — AI PERFORMANCE REVIEW
## ════════════════════════════════════════

Asumsikan Anda adalah AI Executor:

```
1. PALING MEMBANTU     : [jawaban spesifik hari ini]
2. PALING MENGGANGGU   : [jawaban spesifik hari ini]
3. INFO YANG DIINGINKAN: [sebelum mulai bekerja]
4. SKILL TIDAK PERLU   : [dengan alasan]
5. SKILL YANG KURANG   : [dengan alasan]
```

**Delta dari kemarin:**

```
BERUBAH LEBIH BAIK  : [...]
BERUBAH LEBIH BURUK : [...]
TIDAK BERUBAH       : [...]
```

---

## ════════════════════════════════════════
## PHASE 6 — IMPROVEMENT PLAN
## ════════════════════════════════════════

> **Update tracker:** Setelah mengisi ini, perbarui Appendix D.

### QUICK WIN *(< 1 hari)*

```
[QW-N] Judul
Problem : [...]
Solusi  : [...]
Effort  : [jam]
Impact  : LOW/MED/HIGH
```

### SHORT TERM *(< 1 minggu)*

```
[ST-N] Judul
Problem : [...]
Solusi  : [...]
Effort  : [hari]
Impact  : LOW/MED/HIGH
```

### MID TERM *(< 1 bulan)*

```
[MT-N] Judul
Problem : [...]
Solusi  : [...]
Effort  : [minggu]
Impact  : LOW/MED/HIGH
```

### LONG TERM *(arsitektur masa depan)*

```
[LT-N] Judul
Visi    : [...]
Trigger : [kapan mulai diimplementasi]
```

---

## ════════════════════════════════════════
## PHASE 7 — SELF EVOLUTION
## ════════════════════════════════════════

> **Update mingguan.** Jika bukan hari Senin, skip jika tidak ada
> update signifikan dari tool-tool pesaing.

| Tool | Fitur Tertinggal | Fitur Lebih Unggul | Peluang Adopsi | Update Sejak Kemarin |
|------|-----------------|-------------------|----------------|----------------------|
| Claude Code | ... | ... | ... | YES/NO |
| Cursor | ... | ... | ... | YES/NO |
| Roo Code | ... | ... | ... | YES/NO |
| OpenCode | ... | ... | ... | YES/NO |
| Aider | ... | ... | ... | YES/NO |
| Gemini CLI | ... | ... | ... | YES/NO |
| OpenAI Codex | ... | ... | ... | YES/NO |

---

## ════════════════════════════════════════
## PHASE 8 — SCORECARD
## ════════════════════════════════════════

| Dimensi | Skor Hari Ini | Kemarin | 7-Day Avg | Trend |
|---------|---------------|---------|-----------|-------|
| User Experience | /10 | /10 | /10 | ↑/↓/→ |
| Reliability | /10 | /10 | /10 | ↑/↓/→ |
| Latency | /10 | /10 | /10 | ↑/↓/→ |
| Cost Efficiency | /10 | /10 | /10 | ↑/↓/→ |
| Context Management | /10 | /10 | /10 | ↑/↓/→ |
| Routing Quality | /10 | /10 | /10 | ↑/↓/→ |
| Skill Quality | /10 | /10 | /10 | ↑/↓/→ |
| AI Effectiveness | /10 | /10 | /10 | ↑/↓/→ |
| Architecture Quality | /10 | /10 | /10 | ↑/↓/→ |
| **TOTAL** | **/90** | **/90** | **/90** | ↑/↓/→ |

**ASCII Trend Chart (7 hari terakhir):**

```
Score
90 |
80 |              ·
70 |          ·
60 |      ·
50 | ·
   +--+--+--+--+--+--+--→ Hari
    D-6 D-5 D-4 D-3 D-2 D-1 D0
```
*(AI mengisi chart ini dengan data aktual dari Appendix A)*

**Regresi Alert:**

```
⚠ REGRESI TERDETEKSI:
  [Dimensi yang turun > 1 poin dibanding kemarin]
  Penyebab diduga: [...]
  Tindakan: [...]
```

---

## ════════════════════════════════════════
## PHASE 9 — ACTION ITEMS
## ════════════════════════════════════════

| Prioritas | ID | Item | ROI | Effort | Status |
|-----------|----|------|-----|--------|--------|
| **P0** | P0-N | ... | /10 | [jam] | NEW/CARRY-OVER |
| **P1** | P1-N | ... | /10 | [hari] | NEW/CARRY-OVER |
| **P2** | P2-N | ... | /10 | [minggu] | NEW/CARRY-OVER |

**Carry-over dari kemarin yang belum selesai:**

```
[AI mengisi ini dari Appendix D — item belum DONE]
```

---

## ════════════════════════════════════════
## PHASE 10 — ROOT CAUSE ANALYSIS
## ════════════════════════════════════════

> Fokus pada masalah BARU atau masalah lama yang root cause-nya
> berubah. Gunakan Five Whys.

```
MASALAH: [deskripsi]

GEJALA           : [...]
DAMPAK           : [...]
PENYEBAB LANGSUNG: [...]

WHY #1: ...
WHY #2: ...
WHY #3: ...
WHY #4: ...
WHY #5: ...

ROOT CAUSE : [...]
SOLUSI     : [...]
SUDAH PERNAH MUNCUL: YES (Run #N) / NO
```

---

## ════════════════════════════════════════
## PHASE 11 — EXECUTIVE SUMMARY
## ════════════════════════════════════════

> Maksimal 20 poin. Dapat dipahami dalam < 3 menit.
> Bandingkan dengan kemarin, bukan netral.

```
✓  [Yang bekerja lebih baik dari kemarin]
✗  [Yang lebih buruk dari kemarin atau masih bermasalah]
⚠  [Risiko kritis yang butuh perhatian segera]
★  [Peluang terbesar hari ini]
→  [Status item dari kemarin yang carry-over]
```

---

## ════════════════════════════════════════
## PHASE 12 — FINAL VERDICT
## ════════════════════════════════════════

| Dimensi | Nilai Hari Ini | Kemarin | Δ |
|---------|----------------|---------|---|
| Production Readiness | % | % | +/-% |
| Architecture Maturity | % | % | +/-% |
| AI Effectiveness | % | % | +/-% |
| Reliability | % | % | +/-% |
| Maintainability | % | % | +/-% |
| Cost Efficiency | % | % | +/-% |
| Developer Experience | % | % | +/-% |

```
VERDICT HARI INI : [ ] REJECTED [ ] EXPERIMENTAL [ ] ACCEPTABLE [ ] GOOD [ ] EXCELLENT
VERDICT KEMARIN  : [...]
PERUBAHAN        : IMPROVED / STABLE / DEGRADED
ALASAN           : [...]
```

---

## ════════════════════════════════════════
## PHASE 13 — ROI ANALYSIS
## ════════════════════════════════════════

| Rekomendasi | Effort | Impact | Risk | ROI | Status |
|-------------|--------|--------|------|-----|--------|
| ... | L/M/H | L/M/H | L/M/H | /10 | NEW/ONGOING/DONE |

> Urutkan ROI tertinggi ke terendah.
> Item DONE dipindah ke Appendix D.

---

## ════════════════════════════════════════
## PHASE 14 — NEXT ITERATION DESIGN
## ════════════════════════════════════════

> Update hanya jika ada perubahan arsitektur signifikan.
> Jika tidak ada, tulis "NO CHANGE" dan skip.

```
STATUS: UPDATED / NO CHANGE
ALASAN UPDATE: [...]

CURRENT ARCHITECTURE:
[User] → [Orchestrator] → [Router] → [Skill Layer] → [Executor]
                ↓
          [Local LLM]

RECOMMENDED ARCHITECTURE:
[diagram baru jika ada]

FUTURE ARCHITECTURE:
[visi jangka panjang]
```

---

## ════════════════════════════════════════
## PHASE 15 — AI EXECUTOR REPORT
## ════════════════════════════════════════

Berpura-puralah Anda adalah AI Executor:

```
1. PALING MEMBANTU       : [...]
2. PALING MENGHAMBAT     : [...]
3. INFO YANG SERING HILANG: [...]
4. TOOL YANG DIHARAPKAN  : [...]
5. ROUTER YANG SERING DIKOREKSI: [...]
6. FITUR UNTUK MINGGU DEPAN: [...]
7. FITUR YANG HARUS DIHAPUS: [...]

PERUBAHAN DARI KEMARIN   : [lebih baik/buruk/sama? mengapa?]
```

---

## ════════════════════════════════════════
## PHASE 16 — FINAL CONCLUSION
## ════════════════════════════════════════

```
SYSTEM HEALTH             : A / B / C / D / E
HEALTH KEMARIN            : A / B / C / D / E
TREN                      : IMPROVING / STABLE / DECLINING

BIGGEST STRENGTH          : [satu kalimat]
BIGGEST WEAKNESS          : [satu kalimat]
MOST IMPORTANT IMPROVEMENT: [satu kalimat]

TOP 3 PRIORITIES:
  1. [...]
  2. [...]
  3. [...]

ESTIMATED IMPROVEMENT AFTER FIX:
  +X% reliability
  +X% speed
  +X% AI effectiveness

ONE-SENTENCE JUDGEMENT:
"[Satu kalimat tegas yang merangkum kondisi sistem hari ini
  vs kemarin dan arah yang harus diambil besok.]"
```

---

## ════════════════════════════════════════
## PHASE 17 — DAILY DELTA ANALYSIS
## ════════════════════════════════════════

> **Phase baru.** Analisis perubahan antara hari ini dan kemarin.
> Jika FIRST_RUN, skip phase ini.

### 17.1 — Score Delta

```
SKOR KEMARIN : [total]/90
SKOR HARI INI: [total]/90
DELTA        : +/- [N] poin ([+/-N%])
```

### 17.2 — Regresi Terdeteksi

```
DIMENSI YANG TURUN:
  - [Dimensi] : [skor kemarin] → [skor hari ini] (Δ -N)
    Penyebab dugaan: [...]
    Tindakan: [...]
```

### 17.3 — Perbaikan Terdeteksi

```
DIMENSI YANG NAIK:
  - [Dimensi] : [skor kemarin] → [skor hari ini] (Δ +N)
    Penyebab: [...]
    Pertahankan dengan: [...]
```

### 17.4 — Issue Baru vs Issue Resolved

```
ISSUE BARU (tidak ada kemarin)  : [N] buah
ISSUE RESOLVED (ada kemarin, tidak ada hari ini): [N] buah
ISSUE PERSISTEN (ada di kedua run): [N] buah

NET ISSUE DELTA: +/- [N]
```

### 17.5 — P0 Compliance Check

```
P0 KEMARIN   : [N] item
P0 COMPLETED : [N] item
P0 FAILED    : [N] item  ← perlu investigasi
P0 CARRY-OVER: [N] item
```

---

## ════════════════════════════════════════
## PHASE 18 — TREND INTELLIGENCE
## ════════════════════════════════════════

> **Aktif setelah run ke-3.** Gunakan Appendix A untuk analisis.

### 18.1 — Velocity Sistem

```
7-DAY SCORE VELOCITY    : +N poin/hari (ACCELERATING/STEADY/DECELERATING)
PREDIKSI SKOR BESOK     : [N]/90
PREDIKSI SKOR 7 HARI    : [N]/90
WAKTU MENCAPAI TARGET 80/90: [N] hari (jika tren berlanjut)
```

### 18.2 — Recurring Problem Detection

```
MASALAH YANG MUNCUL > 3 RUN BERTURUT-TURUT:
  - [Masalah] : muncul [N] hari, belum resolved
    Pola: [...]
    Root cause diduga: [...]
    Eskalasi ke: P0 / Redesign / Accepted Risk
```

### 18.3 — Anomaly Detection

```
ANOMALI TERDETEKSI (perubahan tiba-tiba > 2 poin dalam 1 hari):
  - [Dimensi]: [N] → [N+2] pada Run #[N]
    Investigasi: [...]
    Korelasi dengan perubahan sistem: [...]
```

### 18.4 — Insight Statistik

```
DIMENSI PALING VOLATILE  : [nama] (std dev: N)
DIMENSI PALING STABIL    : [nama] (std dev: N)
DIMENSI PALING LAMBAT    : [nama] (butuh perhatian lebih)
DIMENSI PALING PROGRESIF : [nama] (tren naik konsisten)
```

---

## ════════════════════════════════════════
## PHASE 19 — SCRIPT SELF-AUDIT
## ════════════════════════════════════════

> **Evaluasi script ini sendiri.** Tujuan: Script harus semakin
> efisien dan relevan setiap hari, bukan semakin berat.

### 19.1 — Phase Usefulness Rating

| Phase | Nama | Nilai (1–10) | Output Quality | Waktu vs Nilai | Rekomendasi |
|-------|------|-------------|----------------|----------------|-------------|
| 0 | Bootstrap | /10 | HIGH/MED/LOW | EFFICIENT/WASTEFUL | KEEP/TRIM/MERGE/REMOVE |
| 1 | Understand System | /10 | ... | ... | ... |
| 2 | Daily Audit | /10 | ... | ... | ... |
| 3 | Stress Test | /10 | ... | ... | ... |
| 4 | Red Team | /10 | ... | ... | ... |
| 5 | AI Performance Review | /10 | ... | ... | ... |
| 6 | Improvement Plan | /10 | ... | ... | ... |
| 7 | Self Evolution | /10 | ... | ... | ... |
| 8 | Scorecard | /10 | ... | ... | ... |
| 9 | Action Items | /10 | ... | ... | ... |
| 10 | Root Cause Analysis | /10 | ... | ... | ... |
| 11 | Executive Summary | /10 | ... | ... | ... |
| 12 | Final Verdict | /10 | ... | ... | ... |
| 13 | ROI Analysis | /10 | ... | ... | ... |
| 14 | Next Iteration Design | /10 | ... | ... | ... |
| 15 | AI Executor Report | /10 | ... | ... | ... |
| 16 | Final Conclusion | /10 | ... | ... | ... |
| 17 | Daily Delta | /10 | ... | ... | ... |
| 18 | Trend Intelligence | /10 | ... | ... | ... |
| 19 | Script Self-Audit | /10 | ... | ... | ... |
| 20 | Auto-Evolution | /10 | ... | ... | ... |

### 19.2 — Coverage Gap Analysis

```
AREA YANG BELUM DICAKUP SCRIPT:
  - [Area] : [mengapa penting]

AREA YANG OVER-COVERED (terlalu banyak phase membahas hal sama):
  - [Area] : [phase yang redundan]
```

### 19.3 — Script Efficiency Score

```
TOTAL PHASE         : [N]
PHASE BERNILAI TINGGI (>7): [N] ([%])
PHASE SEDANG (4-7)  : [N] ([%])
PHASE RENDAH (<4)   : [N] ([%])

SCRIPT EFFICIENCY   : [%]
REKOMENDASI TRIM    : [hapus/merge N phase]
ESTIMASI TIME SAVED : [N%] waktu run lebih singkat
```

---

## ════════════════════════════════════════
## PHASE 20 — AUTO-EVOLUTION ENGINE
## ════════════════════════════════════════

> **Phase paling penting.** Di sini AI menulis versi berikutnya
> dari script ini. Output phase ini ADALAH script baru yang
> akan digunakan besok.

### 20.1 — Evolution Decision

```
KEPUTUSAN EVOLUSI:

PHASE YANG DIMODIFIKASI:
  - Phase [N]: [perubahan apa dan mengapa]

PHASE YANG DITAMBAHKAN:
  - Phase [N+1] baru: [nama] — [alasan penambahan]

PHASE YANG DIHAPUS:
  - Phase [N]: [alasan penghapusan]

PHASE YANG DI-MERGE:
  - Phase [A] + Phase [B] → Phase [X]: [alasan]

METADATA UPDATE:
  - Version    : [X.Y] → [X.Y+1]
  - Run Count  : [N] → [N+1]
  - Last Run   : [DATE]
```

### 20.2 — Patch Notes

```
## CHANGELOG — Run #[N] → #[N+1]
DATE: [YYYY-MM-DD]

ADDED:
  + [perubahan baru yang ditambahkan]

CHANGED:
  ~ [perubahan yang dimodifikasi]

REMOVED:
  - [yang dihapus]

RATIONALE:
  [Alasan evolusi hari ini dalam 2-3 kalimat]
```

### 20.3 — Next Version Output

> **INSTRUKSI KRITIS:**
> Tulis ulang SELURUH file audit-training.md di bawah ini.
> Mulai dari baris `# AUDIT-TRAINING FRAMEWORK` sampai akhir.
> Sertakan semua Appendix yang sudah diperbarui.
> Increment version number dan run count.
> Simpan sebagai file baru yang menggantikan file ini.

```
[AI MENULIS SELURUH SCRIPT VERSI BARU DI SINI]
```

---

## ════════════════════════════════════════
## APPENDIX A — RUN HISTORY LOG
## ════════════════════════════════════════

> Auto-diperbarui setiap run. Jangan edit manual.
> Format: satu baris per run untuk efisiensi konteks.

```
Format kolom:
RUN | DATE | TOTAL_SCORE | UX | REL | LAT | COST | CTX | ROU | SKL | EFF | ARC | VERDICT | HEALTH | TOP_ISSUE
```

```
# RUN HISTORY (terbaru di atas)
# ─────────────────────────────────────────────────────────────────
#1 | 2026-06-24 | 62/90 | 7 | 7 | 7 | 9 | 5 | 8 | 6 | 6 | 7 | EXPERIMENTAL | C+ | 271 skill bloat
# ─────────────────────────────────────────────────────────────────
```

**Statistik Agregat:**

```
TOTAL RUN       : 1
RATA-RATA SKOR  : 62/90
SKOR TERTINGGI  : 62 (Run #1)
SKOR TERENDAH   : 62 (Run #1)
TREN 7 HARI     : — (first run)
```

---

## ════════════════════════════════════════
## APPENDIX B — LEARNED PATTERNS
## ════════════════════════════════════════

> Kumpulan pola yang ditemukan lintas run. AI menambah entri baru
> setiap kali menemukan pola yang signifikan. Tidak dihapus kecuali
> pola terbukti tidak relevan selama 14 hari.

```
Format:
[PATTERN-ID] | Discovered: Run #N | Last Seen: Run #N | Frequency: N/N runs
Category: ROUTING / SKILL / PERFORMANCE / COST / UX / SECURITY
Description: [...]
Implication: [...]
Status: ACTIVE / RESOLVED / ACCEPTED_RISK
```

```
# LEARNED PATTERNS
# ─────────────────────────────────────────────────────────────────
# [P-001] | Discovered: Run #1 | Last Seen: Run #1 | Frequency: 1/1
# Category: ROUTING
# Description: "refactor" keyword di-detect sebagai review/infra, bukan fix/web.
# Status: ACTIVE
# ─────────────────────────────────────────────────────────────────
```

---

## ════════════════════════════════════════
## APPENDIX C — SCRIPT CHANGELOG
## ════════════════════════════════════════

> Riwayat evolusi script ini sendiri.

```
v3.1 | 2026-06-24 | Run #1
  + Updated: whitelist implementation (P0-1 through P0-5)
  + Updated: preprocess.md stale PS1 reference
  + Fixed: 8 unused imports
  + Updated: Run #1 data in Appendix A-D
  + Score baseline: 62/90
  + Top issue: 271 skill bloat → 159 whitelisted

v3.0 | 2026-06-24 | Run #0
  + Initial self-evolving framework
  + Phase 0: Bootstrap & Context Load
  + Phase 17: Daily Delta Analysis
  + Phase 18: Trend Intelligence
  + Phase 19: Script Self-Audit
  + Phase 20: Auto-Evolution Engine
  + Appendix A: Run History Log
  + Appendix B: Learned Patterns
  + Appendix C: Script Changelog
  + Appendix D: Completion Tracker
  + Appendix E: Exploit Registry
```

---

## ════════════════════════════════════════
## APPENDIX D — COMPLETION TRACKER
## ════════════════════════════════════════

> Status semua action item P0/P1/P2.
> AI memperbarui status setiap run berdasarkan laporan user.

```
Format:
[ID] | Priority | Item | Assigned: Run #N | Deadline | Status | Completed: Run #N
```

```
# COMPLETION TRACKER
# ─────────────────────────────────────────────────────────────────
# Status codes:
#   NEW        = baru ditambahkan run ini
#   IN_PROGRESS = sedang dikerjakan
#   DONE       = selesai
#   CANCELLED  = dibatalkan
#   CARRY_OVER = belum selesai, dipindah ke hari berikutnya
# ─────────────────────────────────────────────────────────────────
# [P0-1] | P0 | Skill whitelist (data/skill-whitelist.json) | Run #1 | — | DONE | Run #1
# [P0-2] | P0 | Whitelist helper + filter test_skill_chain | Run #1 | — | DONE | Run #1
# [P0-3] | P0 | get_skill_count whitelist filter | Run #1 | — | DONE | Run #1
# [P0-4] | P0 | Fix preprocess.md stale PS1 reference | Run #1 | — | DONE | Run #1
# [P0-5] | P0 | Unused imports cleanup (8 fixed) | Run #1 | — | DONE | Run #1
# ─────────────────────────────────────────────────────────────────
```

**Summary:**

```
TOTAL ITEMS  : 5
DONE         : 5 (100%)
IN_PROGRESS  : 0 (0%)
CARRY_OVER   : 0 (0%)
CANCELLED    : 0 (0%)
```

---

## ════════════════════════════════════════
## APPENDIX E — EXPLOIT REGISTRY
## ════════════════════════════════════════

> Database semua exploit yang ditemukan di Phase 4.
> AI menambah entri baru, tidak menghapus entri lama.

```
Format:
[EXP-ID] | Severity | Discovered: Run #N | Status | Description | Mitigation
```

```
# EXPLOIT REGISTRY
# ─────────────────────────────────────────────────────────────────
# Status codes:
#   OPEN       = belum dimitigasi
#   MITIGATED  = sudah ada solusi
#   ACCEPTED   = risiko diterima (low impact)
#   WONTFIX    = tidak akan diperbaiki (alasan: [...])
# ─────────────────────────────────────────────────────────────────
# [EXP-001] | MEDIUM | Run #1 | OPEN | Bypass danger phrase via leetspeak | Normalize input
# ─────────────────────────────────────────────────────────────────
```

---

## ════════════════════════════════════════
## CARA PENGGUNAAN HARIAN
## ════════════════════════════════════════

```
HARI 1 (Run #1):
  1. Berikan file ini ke AI agent
  2. AI menjalankan Phase 0–20
  3. AI menghasilkan file audit-training.md baru (v3.1)
  4. Simpan file baru, hapus file lama
  5. Opsional: simpan output lengkap di folder /logs/audit-YYYY-MM-DD.md

HARI 2+ (Run #2, #3, ...):
  1. Berikan file terbaru ke AI agent
  2. AI membaca Run History, Learned Patterns, Completion Tracker
  3. AI fokus pada delta dan insight baru (bukan mengulang yang sama)
  4. AI menghasilkan file audit-training.md baru yang lebih baik
  5. Ulangi

TIPS:
  - Setelah menjalankan P0 item, beritahu AI di awal sesi:
    "P0-1 sudah selesai, P0-2 belum"
  - AI akan update Appendix D dan menyesuaikan analisis

EKSPEKTASI EVOLUSI:
  Run  1–3  : Script masih generik, baseline terbentuk
  Run  4–7  : Pola mulai terdeteksi, Phase berbobot lebih relevan
  Run  8–14 : Script sangat personal untuk sistem Anda
  Run 15+   : Script hanya fokus pada hal-hal yang benar-benar matter
```

---

*audit-training.md — v3.0 | Self-Evolving | 20 Phases + 5 Appendix*
*Next run akan menghasilkan v3.1 secara otomatis.*