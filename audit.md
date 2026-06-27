# AUDIT PROMPT — farewell-assistant v2.0.1

> Prompt ini ditujukan untuk AI Executor (OpenCode via 9Router — gunakan combo
> `SENIOR`/`TEAM_LEADER`, bukan `JUNIOR_*`, karena scope-nya cross-file dan butuh
> reasoning, bukan task ringan). Hasil analisis sumber: source code lengkap
> `farewell_assistant/`, `scripts/`, `.farewell/`, `instructions/rules.md`,
> `opencode.template.jsonc`, `pyproject.toml`, `.github/workflows/test.yml`.
> Repro dilakukan nyata (clean venv, simulasi regex) — bukan asumsi/tebakan.

---

## 1. Peran & Tujuan

Kamu bertindak sebagai **Senior Backend Engineer** (sesuai `org.py` — fokus
backend/infra) yang menerima Work Order audit dari Boss. Tugasmu:

1. **Verifikasi** setiap temuan di bawah terhadap kondisi repo **saat ini**
   (working tree lokal Fandi, bukan snapshot zip yang dipakai untuk audit ini —
   bisa saja sudah berubah).
2. **Fix** temuan yang statusnya `CONFIRMED BUG` — langsung eksekusi, sesuai
   `instructions/rules.md` ("Bug fix: langsung eksekusi tanpa hold").
3. **Jangan auto-fix** temuan berstatus `NEEDS DECISION` — itu butuh keputusan
   arsitektur dari Boss dulu (treat sebagai NEW task: HOLD → PLAN → APPROVE).
4. **Catat semua kerjaan** di tabel Audit Log (Section 7) — ini WAJIB, bukan
   opsional. Update tabel itu setiap kali satu temuan selesai diproses.

## 2. Aturan Main

- Ikuti `instructions/rules.md`: YAGNI, ultra terse, jangan refactor di luar
  scope temuan yang disebut.
- Tiap fix HARUS punya cara verifikasi konkret (command yang bisa dijalankan,
  bukan "seharusnya sudah benar").
- Kalau fix butuh ubah `opencode.jsonc` / `opencode.template.jsonc`, jangan
  commit hasil generate (`opencode.jsonc` sudah di `.gitignore` — itu benar,
  jangan diubah).
- Jangan sentuh `9router/`, `ecc/`, `awesome-opencode/` (upstream clone, bukan
  punya kita).
- Commit hanya kalau Boss minta.

## 3. Cara Kerja per Temuan

```
1. Buka file:line yang disebut → konfirmasi masih ada / masih sama
2. Reproduksi (jalankan command repro yang dicantumkan, kalau ada)
3. Kalau CONFIRMED → terapkan fix yang disarankan (atau lebih baik kalau ada)
4. Verifikasi ulang dengan command yang sama → harus lolos
5. Isi baris di tabel Audit Log
```

---

## 4. P0 — Blocker (merusak instalasi fresh / fungsi inti)

### P0-1: Dependency `yaml` tidak dideklarasikan → CLI crash total di fresh install

- **File**: `pyproject.toml:10` (`dependencies = []`) vs
  `farewell_assistant/awesome_indexer.py:3` (`import yaml`)
- **Root cause**: `awesome_indexer.py` import PyYAML di top-level. Modul ini
  diimport dari `cli.py` di dalam `_write_context_footer()`
  (`from .awesome_indexer import get_recommended_projects_for_stack`), dan
  `_write_context_footer()` dipanggil **unconditional** di baris pertama
  `main()` (`cli.py:264`) — sebelum argparse bahkan jalan. Artinya SEMUA
  command (termasuk `--help`, `project list`) kena.
- **Repro yang sudah dijalankan** (venv bersih, hanya install `httpx pytest`
  sesuai `.github/workflows/test.yml`):
  ```
  ModuleNotFoundError: No module named 'yaml'
    File ".../cli.py", line 220, in _write_context_footer
      from .awesome_indexer import get_recommended_projects_for_stack
    File ".../awesome_indexer.py", line 3, in <module>
      import yaml
  ```
- **Dampak**: README bilang instalasi cukup `pip install -e .` lalu langsung
  jalan — pada kenyataannya itu crash di environment yang belum kebetulan
  punya PyYAML terinstal global (kemungkinan besar di laptop Fandi PyYAML
  sudah ada lewat tool lain, jadi bug ini "tersembunyi" secara lokal).
- **CI ikut kena**: `.github/workflows/test.yml` hanya install `httpx pytest`
  (bukan `pyyaml`), dan step "Test CLI" menjalankan
  `python -m farewell_assistant.cli project list` — yang lewat `main()` juga.
  **Cek langsung tab Actions di GitHub repo** — kemungkinan run terbaru RED.
  Catatan tambahan: `httpx` sendiri di-install tapi tidak pernah dipakai di
  source manapun (`grep -rn httpx farewell_assistant/ scripts/ tests/` kosong)
  — kemungkinan sisa dependency yang tidak relevan lagi.
- **Fix**:
  ```toml
  # pyproject.toml
  dependencies = ["pyyaml>=6.0"]
  ```
  Lalu update `.github/workflows/test.yml` step "Install dependencies":
  ```yaml
  run: |
    python -m pip install --upgrade pip
    pip install -e . pytest
  ```
  (pakai `pip install -e .` supaya dependency dari `pyproject.toml` ikut
  terinstall, sekaligus menghapus kebutuhan `httpx` yang tidak terpakai).
- **Verifikasi**: ulangi repro di atas (venv bersih + `pip install -e .` saja,
  tanpa install yaml manual) → `farewell-assistant project list` harus jalan
  tanpa traceback.

---

### P0-2: `/team on|off|bawahan` menghancurkan role-based model routing

Ini bug paling kritis karena **langsung kontra dengan tujuan utama project**
(hemat token via routing per-role: DIRECTOR/TEAM_LEADER vs SENIOR vs JUNIOR).

- **File**: `farewell_assistant/workmode.py:40-67` (`set_models()`), dipanggil
  dari `farewell_assistant/cli.py` di `cmd_team()` (baris ~27-43).
- **Root cause**: `set_models(model_key, small_key, tier)` cuma terima 2 nilai
  model. Regex Step 1-nya:
  ```python
  content = re.sub(
      r'(\s{4,}"model"\s*:\s*)"[^"]*"',
      lambda m: f'{m.group(1)}"{model_key}"',
      content,
  )
  ```
  ini match **SEMUA** baris `"model": ...` yang indent ≥4 spasi — artinya
  semua agent block di `opencode.jsonc` (`build`, `team`, `planner`,
  `architect`, semua `*-reviewer`, `worker-1/2/3`, `ketua-tim`,
  `backend-reviewer`, `frontend-reviewer`) ikut ditimpa jadi `model_key` yang
  sama. Sementara `daily.py:_sync_opencode()` (baris ~150-180) justru
  menghitung 4 nilai BERBEDA (`root_model`, `small_model`, `senior_model`,
  `junior_model`) persis untuk membedakan role ini.
- **Bug kedua yang lebih parah**: replacement-nya `f'...{model_key}"'` —
  TANPA prefix `"9router/"`. Template aslinya selalu `"9router/${...}"`. Jadi
  sesudah `/team` jalan, semua field model jadi string TELANJANG (mis.
  `"TEAM_LEADER"`) bukan `"9router/TEAM_LEADER"`.
- **Repro yang sudah dijalankan** (simulasi pakai regex asli dari file,
  terhadap hasil real `_sync_opencode()` mode TIM):
  ```
  SEBELUM /team off (hasil _sync_opencode, benar):
    "model": "9router/TEAM_LEADER"   <- build, team
    "model": "9router/SENIOR"        <- planner, architect, *-reviewer (x14)
    "model": "9router/JUNIOR_1"      <- worker-1, worker-2, worker-3

  SESUDAH set_models("TEAM_LEADER","SENIOR") dipanggil (apa yang cmd_team lakukan):
    "model": "TEAM_LEADER"           <- SEMUA 24 baris, prefix 9router/ HILANG
  ```
- **Dampak nyata**: setiap kali switch tier (`/team on/off/bawahan`) setelah
  `/daily`, seluruh sub-agent (planner, reviewer, worker) ikut pakai model
  tier teratas — fitur "Role-Based Routing" yang didokumentasikan panjang di
  README (tabel `build/team → DIRECTOR/TEAM_LEADER/SENIOR`, dst) **tidak
  berjalan** di praktiknya. Kemungkinan juga merusak resolusi provider di
  opencode (model id tanpa prefix provider) — bagian ini **belum** diverifikasi
  end-to-end (tidak ada instance opencode/9Router live saat audit ini ditulis),
  jadi WAJIB diverifikasi langsung oleh executor.
- **Saran arah fix** (butuh keputusan desain, bukan one-liner):
  - Opsi A (disarankan): hapus pendekatan regex blind-replace di
    `set_models()`. Sebagai gantinya, panggil ulang `_sync_opencode()` dari
    `daily.py` setiap kali `/team` berganti tier — karena fungsi itu SUDAH
    benar menghitung `root/small/senior/junior` dari combo SQLite secara live.
    `cmd_team()` di `cli.py` tinggal: set `team.json` → panggil
    `_sync_opencode()` → print status. Hilangkan `set_models()`/
    `_switch_default_agent()` kalau memang sudah ter-cover oleh template
    regenerate (cek juga apakah `default_agent` perlu dipertahankan terpisah
    untuk PLAN/BUILD mode — itu domain `workmode.py`, jangan dicampur).
  - Opsi B (kalau Opsi A ternyata merusak alur `workmode.py` yang sudah benar
    untuk `default_agent`): perbaiki regex `set_models()` agar scoped per
    nama agent (mis. pisahkan tiga grup: `{build, team}` → root,
    `{planner, architect, *-reviewer, docs-lookup, refactor-cleaner,
    ketua-tim, backend-reviewer, frontend-reviewer}` → senior,
    `{worker-1, worker-2, worker-3}` → junior), dan SELALU sisipkan prefix
    `"9router/"` di replacement.
- **Verifikasi**: jalankan `daily`, lalu `team off`, lalu
  `cat opencode.jsonc | grep -A1 '"model"'` — pastikan `build`/`team` pakai
  model TEAM_LEADER, semua `*-reviewer`/`planner`/`architect` pakai SENIOR,
  `worker-1/2/3` pakai JUNIOR_1, dan **semua** value diawali `9router/`.

---

## 5. P1 — Functional Bug (skill matching & cost optimization)

### P1-1: Skill matching by stack salah arah substring + fallback tidak guna

- **File**: `farewell_assistant/indexer.py:27-33` (`_find_matching_skills`),
  `indexer.py:45-57` (`write_active_skills_manifest`).
- **Bug 1 (arah substring terbalik)**: baris 31
  ```python
  if keyword in s.lower():
  ```
  ini cek apakah `keyword` (mis. `"nodejs"`) adalah substring dari `s`
  (mis. `"node"`) — itu mustahil benar kalau `s` lebih pendek dari `keyword`.
  **Bukti nyata**: `.farewell/manifests/002-service-hub.json` punya
  `"stack": ["node", "dart"]`, tapi `"skills"` di manifest yang sama TIDAK
  ADA satupun dari `nestjs-patterns`, `prisma-patterns`, `backend-patterns`,
  `database-migrations` — padahal service-hub (ServisGadget) adalah backend
  NestJS + Prisma + PostgreSQL + Redis. `"dart"` cocok (karena equal-string
  dengan key `"dart"`), `"node"` tidak pernah cocok dengan key `"nodejs"`.
- **Bug 2 (fallback pakai project_code, bukan stack asli)**: baris 47
  ```python
  skills = _find_matching_skills([project_code.split("-")[0] ...])
  ```
  Ini pakai `project_code` (mis. `"002"`) sebagai keyword pencarian — bukan
  field `"stack"` yang sudah ada di manifest. `"002"` tidak akan pernah cocok
  keyword apapun di `STACK_SKILLS`, jadi fallback ini cuma hasilkan
  `COMMON_SKILLS` doang, useless untuk kasus manifest kosong/rusak.
- **Bug 3 (field `stack` di manifest dead data)**: `grep -rn` membuktikan
  field `"stack"` di file manifest manapun **tidak pernah dibaca** oleh kode
  manapun — hanya `"skills"` yang dibaca (`indexer.py:42`). `stack` yang
  dipakai untuk `cool recommend` (`cli.py:175,240`) malah di-derive ulang dari
  prefix nama skill (`s.split("-")[0]`), bukan dari field manifest. Jadi field
  `stack` di semua 5 file manifest itu murni dekoratif.
- **Fix**:
  1. Ganti arah pengecekan jadi dua arah / pakai alias map, mis.:
     ```python
     if keyword in s.lower() or s.lower() in keyword:
     ```
     atau lebih robust: tambahkan alias eksplisit (`"node": "nodejs"`,
     `"ts": "react"`/dst sesuai kebutuhan) supaya tidak fragile ke variasi
     penamaan.
  2. Ubah `write_active_skills_manifest` agar fallback pakai
     `data.get("stack", [])` dari manifest (baca manifest mentah dulu, jangan
     cuma `get_project_skills` yang sudah memfilter ke `"skills"`), bukan
     `project_code`.
  3. Regenerate ulang `002-service-hub.json` (dan manifest lain yang
     terdampak) setelah fix, lalu manual-review apakah skill list-nya sudah
     masuk akal untuk masing-masing project (terutama 002 — pastikan
     nestjs/prisma/backend-patterns muncul).
- **Verifikasi**: hapus `"skills"` dari `002-service-hub.json` (sisakan
  `"stack": ["node","dart"]`), jalankan ulang generator manifest → cek hasil
  sekarang mengandung `nestjs-patterns`/`prisma-patterns`/`backend-patterns`.

---

## 6. P2 — Data Integrity / Context yang Disuntik ke AI

Ini kategori serius karena file-file ini **langsung masuk ke
`instructions` array opencode** (`opencode.template.jsonc` baris berisi
`.farewell/context/farewell-assistant.md`) — kalau isinya salah, AI executor
beroperasi dengan informasi yang salah tentang project-nya sendiri, di SETIAP
sesi.

### P2-1: `.farewell/context/service-hub.md` salah total

- **File**: `.farewell/context/service-hub.md`
- **Isi saat ini**: "Type: Node.js backend service ... API gateway for
  multiple services. Manages routing, auth, and service discovery."
- **Fakta sebenarnya** (per deskripsi project Fandi): service-hub adalah
  **ServisGadget** — marketplace dua sisi servis gadget, backend
  NestJS/TypeScript/Prisma/PostgreSQL/Redis, frontend Flutter/Riverpod, tim
  3 orang (Fandi/Andriyan/Nissa), Fandi pegang backend. Tidak ada satupun
  kata "Prisma", "PostgreSQL", "Flutter", "marketplace", atau "gadget" di
  file context ini.
- **Fix**: tulis ulang `service-hub.md` sesuai deskripsi project yang benar
  (stack lengkap, tujuan bisnis, siapa pegang apa). Minta konfirmasi isi
  final ke Boss sebelum final-write (karena ini deskripsi proyek nyata,
  bukan sekadar bug teknis).
- **Verifikasi**: baca ulang file, cocokkan ke deskripsi project asli — tidak
  ada klaim yang salah/menyesatkan.

### P2-2: `.farewell/context/farewell-assistant.md` reference file yang sudah dihapus

- **File**: `.farewell/context/farewell-assistant.md`, bagian "Key Files"
  masih menyebut `tracker.py — Token usage from 9Router SQLite`.
- **Kontradiksi**: `README.md` tabel "File yang sudah dihapus" bilang
  `tracker.py` sudah dihapus ("Dead code — fungsi tidak pernah dipanggil").
- **Dampak**: AI executor yang baca context ini bisa coba `read`/`edit`
  `tracker.py` yang sudah tidak ada, atau salah paham arsitektur saat ini.
- **Fix**: hapus baris referensi `tracker.py` dari "Key Files", sinkronkan
  daftar file dengan isi `farewell_assistant/` yang sebenarnya saat ini
  (`__init__.py, __main__.py, cli.py, config.py, daily.py, helpers.py,
  indexer.py, awesome_indexer.py, memory.py, org.py, workmode.py`).
- **Verifikasi**: `grep -n tracker .farewell/context/farewell-assistant.md`
  harus kosong.

### P2-3: `.api-key.example.txt` kontradiksi README & arsitektur v2

- **File**: `.api-key.example.txt`
- **Isi saat ini**: masih ada `NVIDIA_API_KEY_FLASH`/`NVIDIA_API_KEY_PRO`,
  dan hardcode `COMBO_FREE=...`, `COMBO_DEEPSEEK-API-FLASH=...`, dst.
- **Kontradiksi**: README section "api-key.txt" bilang eksplisit "Hanya
  9Router API key — **tidak ada Nvidia**, **tidak ada combo hardcoded**" —
  karena v2 baca combo secara live dari SQLite (`daily.py:_load_combos()`).
- **Dampak**: orang yang setup project baru ikut contoh ini akan bingung
  (atau salah konfigurasi) karena formatnya beda total dari yang benar-benar
  dibaca kode saat ini.
- **Fix**: sederhanakan jadi cuma:
  ```
  NINEROUTER_API_KEY=sk-your-key-here
  ```
  (sesuai contoh di README), hapus semua baris Nvidia & `COMBO_*`.
- **Verifikasi**: bandingkan isi file dengan section "api-key.txt" di
  README — harus identik formatnya.

---

## 7. P3 — Dead Code / Cleanup (tidak urgent, tapi noise di codebase)

### P3-1: `check_db.py` rusak — `NameError` di baris pertama yang jalan

- **File**: `check_db.py:5` — pakai `os.environ.get(...)` tapi `import os`
  tidak ada di file ini (hanya `import sqlite3, json` + `from pathlib import
  Path`).
- **Fix**: tambahkan `import os` di baris atas.
- **Verifikasi**: `python check_db.py` tidak lagi error `NameError: name 'os'
  is not defined` (boleh tetap gagal di langkah lain kalau DB tidak ada, itu
  expected).

### P3-2: `_CONTEXT_COUNTER` auto-checkpoint tidak pernah jalan

- **File**: `farewell_assistant/cli.py:9` (`_CONTEXT_COUNTER = 0`),
  `cli.py:248-259` (increment + `% 5 == 0` check di `_write_context_footer`).
- **Root cause**: tiap invocation CLI = proses Python baru → variable global
  ini selalu reset ke 0 lalu jadi 1 sebelum dicek modulo 5. `1 % 5 == 0` tidak
  pernah `True` dalam pola pemakaian normal (satu command = satu proses).
  Auto-save session "tiap 5 panggilan" yang dimaksud kode ini efektif dead
  code.
- **Fix opsi**: kalau fitur ini memang diinginkan, counter harus persisted ke
  disk (mis. file kecil di `.farewell/`) supaya bertahan antar-proses — bukan
  in-memory global. Kalau tidak terlalu penting, hapus saja logic ini
  (YAGNI) supaya tidak menyesatkan pembaca kode.
- **Verifikasi**: keputusan ada di Boss — kategori ini masuk **NEEDS
  DECISION**, jangan auto-fix tanpa konfirmasi (lihat Section 8).

### P3-3: `org.py` — definisi Role duplikat (copy-paste)

- **File**: `farewell_assistant/org.py` — `DEPUTY` didefinisikan dua kali
  (baris 47 & 96), `TEAM_LEADER` dua kali (baris 62 & 111), `SENIOR_BACKEND`
  dua kali (baris 80 & 129). Isinya identik sehingga tidak menyebabkan bug
  fungsional saat ini, tapi ini jelas leftover copy-paste yang berisiko kalau
  suatu saat hanya satu copy yang diedit.
- **Fix**: hapus blok duplikat (baris 96-145, definisi kedua), sisakan satu
  saja per Role.
- **Verifikasi**: `grep -c "^DEPUTY = Role" farewell_assistant/org.py` harus
  hasil `1`, begitu juga untuk `TEAM_LEADER` dan `SENIOR_BACKEND`. Jalankan
  `farewell-assistant org roles` → output harus identik dengan sebelum fix.

### P3-4: `session-counter.json` — state file orphan

- **File**: `.farewell/session-counter.json` (isi `{"n": 17}`)
- **Temuan**: tidak ada satupun kode Python yang membaca/menulis file ini
  (`grep -rn "session.counter" farewell_assistant/` kosong). Kemungkinan
  besar sisa dari `tracker.py`/`log.py` yang sudah dihapus (lihat tabel
  README), dan tidak ter-cover di `.gitignore` sehingga ikut tracked di git
  sebagai noise.
- **Fix**: hapus file ini (`git rm .farewell/session-counter.json`) kecuali
  ada rencana fitur yang akan memakainya lagi — kalau iya, ini masuk
  **NEEDS DECISION**, jangan hapus dulu.

---

## 8. P4 — Perlu Konfirmasi Boss (JANGAN auto-fix, cukup laporkan)

### P4-1: Asumsi Windows-only (`APPDATA`) di beberapa tempat

- **File**: `daily.py:_ensure_9router()` & `_load_combos()`,
  `check_db.py:5`, `scripts/9router-diagnostic.py`,
  `scripts/check-9router-usage.py` — semua pakai
  `os.environ.get("APPDATA", "")` untuk lokasi SQLite 9Router.
- **Pertanyaan untuk Boss**: apakah farewell-assistant memang didesain
  Windows-only (konsisten dengan `py -m farewell_assistant` di semua contoh
  README), atau perlu fallback Linux/macOS (`XDG_DATA_HOME`/`~/.local/share`)
  mengingat sebagian workflow lain (kernel build) sudah pindah ke native
  Ubuntu? Tunggu jawaban sebelum ubah apapun di area ini.

### P4-2: Fitur cost/token budget tracking belum ada implementasinya

- **Temuan**: `.gitignore` sudah punya entry `.farewell/cost-budget.json` dan
  `.farewell/cost-log.csv` (di bagian "Cost tracking (local state, per-user)")
  — tapi tidak ada satupun modul Python di snapshot ini yang menulis/membaca
  file tersebut.
- **Pertanyaan untuk Boss**: apakah modul ini sedang dikerjakan di
  branch/working-copy lain yang belum masuk snapshot audit ini, atau memang
  belum diimplementasikan? Kalau belum, ini bukan "bug" — cukup dicatat
  sebagai gap yang konsisten dengan rencana "menambahkan fitur token/cost
  budget tracking" yang sedang berjalan.

### P4-3: `awesome_indexer.load_all_entries()` parse ulang semua YAML tanpa cache

- **File**: `awesome_indexer.py:14-30` — setiap panggilan glob + parse ulang
  seluruh direktori `data/{plugins,themes,agents,projects,resources}/*.yaml`.
  Dipanggil minimal 2x dalam satu invocation `status` (sekali di
  `_write_context_footer()` yang selalu jalan, sekali lagi di `cmd_status()`).
  Dengan skala "129 plugin, 9 agent, 61 project" (dari contoh README), ini
  overhead I/O berulang di setiap command, termasuk command yang tidak
  related (`workmode status`, `--help`, dst, karena `_write_context_footer`
  selalu jalan).
- **Pertanyaan untuk Boss**: worth it untuk simple in-process cache (load
  sekali per invocation, simpan di module-level variable) atau biarkan
  karena tiap invocation toh proses baru jadi cache antar-proses tidak relevan
  (dan cache file-based nambah kompleksitas invalidation pas upstream
  `awesome-opencode` di-`git pull` tiap `/daily`)? Bukan bug fungsional, cuma
  efisiensi — putuskan dulu sebelum diubah.

---

## 9. Audit Log (isi tabel ini selagi jalan, JANGAN dikosongkan)

| # | Temuan | File:Line | Severity | Status | Verifikasi Dilakukan | Catatan |
|---|--------|-----------|----------|--------|----------------------|---------|
| P0-1 | Missing `yaml` dependency | pyproject.toml:10 | Blocker | | | |
| P0-2 | `set_models` collapse role routing | workmode.py:40-67 | Blocker | | | |
| P1-1 | Stack-skill substring & fallback salah | indexer.py:27-57 | High | | | |
| P2-1 | `service-hub.md` salah deskripsi | .farewell/context/service-hub.md | High | | | |
| P2-2 | `farewell-assistant.md` ref `tracker.py` | .farewell/context/farewell-assistant.md | Medium | | | |
| P2-3 | `.api-key.example.txt` kontradiksi README | .api-key.example.txt | Medium | | | |
| P3-1 | `check_db.py` NameError | check_db.py:5 | Low | | | |
| P3-2 | `_CONTEXT_COUNTER` dead logic | cli.py:9,248-259 | Low | | | |
| P3-3 | `org.py` Role duplikat | org.py:47-145 | Low | | | |
| P3-4 | `session-counter.json` orphan | .farewell/session-counter.json | Low | | | |
| P4-1 | Asumsi Windows-only `APPDATA` | daily.py, check_db.py, scripts/*.py | Info | NEEDS DECISION | - | tunggu jawaban Boss |
| P4-2 | Cost-budget tracking belum ada kode | .gitignore vs (tidak ada modul) | Info | NEEDS DECISION | - | tunggu jawaban Boss |
| P4-3 | `awesome_indexer` tanpa cache | awesome_indexer.py:14-30 | Info | NEEDS DECISION | - | tunggu jawaban Boss |

**Status valid**: `CONFIRMED` / `FIXED` / `NOT REPRODUCIBLE` / `NEEDS DECISION`
/ `WONTFIX (+alasan)`.

## 10. Deliverable yang Diharapkan

1. Tabel Audit Log di Section 9 terisi penuh untuk P0-P3 (P4 cukup
   dilaporkan, tunggu jawaban Boss).
2. Diff/patch untuk setiap temuan `FIXED`.
3. Ringkasan akhir (≤10 baris): berapa yang fixed, berapa yang butuh
   keputusan Boss, ada efek samping yang ditemukan saat fix (terutama untuk
   P0-2 — wajib laporkan hasil tes opencode.jsonc setelah fix).
