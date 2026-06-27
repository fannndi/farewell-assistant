# farewell-assistant

AI Coding Assistant Orchestrator — Kelola tim AI, 9Router, ECC skills, dan session memory dalam satu tempat.

> "Seperti perusahaan kecil: ada Director, Team Leader, Senior Engineer, dan Junior Reviewer. Tapi kamu Bos-nya."

```bash
# Coba langsung
py -m farewell_assistant status
```

---

## Daftar Isi

- [Instalasi](#instalasi)
- [Konsep Dasar](#konsep-dasar)
- [Daily Routine](#daily-routine)
- [Team Mode](#team-mode)
- [Organization](#organization)
- [Commands Reference](#commands-reference)
- [Workflow Examples](#workflow-examples)
- [Token Optimization](#token-optimization)
- [Project Management](#project-management)
- [Architecture](#architecture)
- [Files](#files)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Instalasi

```bash
git clone https://github.com/fannndi/farewell-assistant
cd farewell-assistant
pip install -e .
```

### Requirement

| Tool | Minimal | Catatan |
|------|---------|---------|
| Python | 3.10+ | Wajib |
| Node.js | 18+ | Untuk 9Router |
| 9Router | Running on :20128 | Router untuk LLM |
| ECC | `ecc/` subdirectory | Skill library |
| api-key.txt | Root project | Lihat bawah |

### api-key.txt

Buat file `api-key.txt` di root project:

```
NINEROUTER_API_KEY=sk-your-key-here
LEADER_1=ocg/deepseek-v4-flash
LEADER_2=ds/deepseek-v4-flash
SPECIAL=oc/deepseek-v4-flash-free
WORKER_1=oc/mimo-v2.5-free
WORKER_2=oc/big-pickle
WORKER_3=oc/north-mini-code-free
WORKER_4=oc/nemotron-3-ultra-free
```

| Key | Peran |
|-----|-------|
| `LEADER_1` | Main controller (premium) |
| `LEADER_2` | Secondary controller (premium) |
| `SPECIAL` | Planner/Architect (free, dual-role: controller + worker) |
| `WORKER_1..4` | Reviewer/Helper (free models) |

Hanya 9Router API key + model mapping — **tidak ada Nvidia**, **tidak ada combo definition**. Model bisa disesuaikan tanpa edit kode.

---

## Konsep Dasar

Farewell-assistant adalah **orchestrator** yang menghubungkan:

```
9Router (LLM Router) ─── farewell-assistant ─── Opencode (AI Agent)
       │                        │                        │
   Combo DB              Sync config               Eksekusi task
   Model routing         Filter skills             Team hierarchy
   Fallback chain        Project memory            Role-based routing
```

### Cara Kerja

1. Kamu (Boss) kasih task
2. Farewell-assistent tentukan mode tim (divisi/tim/bawahan)
3. Model mapping dari `api-key.txt`:

```
DIVISI:  LEADER → SPECIAL → WORKER_1 → WORKER_2
TIM:     SPECIAL → SPECIAL → WORKER_1 → WORKER_2
BAWAHAN: WORKER_1 → WORKER_1 → WORKER_1 → WORKER_2
```

4. Agent pakai model sesuai peran (controller/specialist/reviewer/helper)
5. 9Router route request ke model sesungguhnya
6. Hasil kembali ke kamu

---

## Daily Routine

Ini rutinitas yang ideal tiap hari:

### 🔄 Pagi — `/daily`

```bash
py -m farewell_assistant daily
```

Apa yang terjadi:

```
1/4 Start 9Router
    ├─ Cek port 20128
    ├─ Kalau mati → start 9Router (standalone mode)
    └─ Tunggu sampai siap (max 30 detik)

2/4 Upstream Sync
    ├─ git pull ECC (main)
    ├─ git pull 9Router (master)
    └─ git pull awesome-opencode (main)

3/4 Generate Config
    ├─ Baca combo dari 9Router SQLite
    ├─ Baca active-skills.json (filtered skills)
    ├─ Generate opencode.jsonc dari template
    └─ Inject model + skill paths

4/4 Readiness Check
    ├─ 9Router version
    ├─ ECC status
    ├─ GitHub release
    └─ Combo report
```

**Kapan perlu:** Setiap kali mau mulai coding. Dilakukan auto saat startup opencode.

### 📋 Cek Status

```bash
py -m farewell_assistant status
```

Output:
```
Farewell: ON | 002-service-hub | BUILD | Skills: 11 | Tim | awesome: 129p/9a/61pr
```

Artinya:
- Farewell aktif
- Project: 002-service-hub
- Mode: BUILD (full akses)
- Skill: 11 (difilter dari 271)
- Tier: Tim (Team Leader leading)
- awesome-opencode: 129 plugin, 9 agent, 61 project

### 👥 Cek Tim

```bash
py -m farewell_assistant team status
```

Output: `Team: TIM (Tim: oc/deepseek-v4-flash-free)` — tau siapa yang leading.

### 🏢 Cek Organisasi

```bash
py -m farewell_assistant org
```

Menampilkan chart hierarchy, roles, workflow, priority.

---

## Team Mode

Model mapping diatur lewat `api-key.txt`. Tiap mode pilih LEADER berbeda, sisanya tetap.

| Mode | Command | LEADER | SPECIAL | WORKER | HELPER | Cocok |
|------|---------|--------|---------|--------|--------|-------|
| **DIVISI** | `/team on` | LEADER_1 | SPECIAL | WORKER_1 | WORKER_2 | Premium |
| **TIM** | `/team off` | SPECIAL | SPECIAL | WORKER_1 | WORKER_2 | Sehari-hari |
| **BAWAHAN** | `/team bawahan` | WORKER_1 | WORKER_1 | WORKER_1 | WORKER_2 | Cepat |

### Agent-to-Model (TIM mode)

```
build/team           -> SPECIAL      (controller + execution)
planner/architect    -> SPECIAL      (reasoning)
reviewers            -> WORKER_1     (code review)
docs-lookup/refactor -> WORKER_2     (lightweight)
worker-1/2/3         -> WORKER_2     (helpers)
```

### Contoh

```bash
py -m farewell_assistant team on
# [DIVISI] LEADER = LEADER_1 | SPECIAL = SPECIAL | WORKER = WORKER_1

py -m farewell_assistant team off
# [TEAM] LEADER = SPECIAL | SPECIAL = SPECIAL | WORKER = WORKER_1
```

---

## Organization

Struktur organisasi lengkap:

```
           Boss (User)
               │
    ┌──────────┼──────────┐
    │          │          │
 Director AI  Deputy     Team Leader AI ← Kamu
    │          │          │
    └──────────┴──────────┤
                 ┌────────┼────────┐
                 │        │        │
            Senior BE   Junior I  Junior II  Junior III
```

### Roles

```bash
# Lihat semua role + wewenang
py -m farewell_assistant org roles
```

Setiap role punya:
- **Title** & **Model** — siapa dan pakai model apa
- **Status** — Pegawai Tetap / Junior
- **Fokus** — area tanggung jawab
- **Authority** — wewenang spesifik
- **Kontribusi** — persentase beban kerja

### Workflow

```bash
py -m farewell_assistant org workflow
```

10 langkah dari terima Work Order sampai laporan:

```
 1. Pahami objective Director
 2. Analisis ruang lingkup
 3. Tentukan pembagian tugas
 4. Team Leader eksekusi (frontend, integrasi)
 5. Senior BE eksekusi (backend, API, DB)
 6. Junior Reviewer validasi
 7. Gabungkan hasil
 8. Hilangkan konflik
 9. Prioritaskan
10. Laporkan ke Director / User
```

### Decision Priority

```bash
py -m farewell_assistant org priority
```

Saat ada perbedaan pendapat:

```
 1. Boss (User)
 2. Director AI (ocg/deepseek-v4-flash)
 3. Deputy Director AI (ds/deepseek-v4-flash)
 4. Team Leader AI (oc/deepseek-v4-flash-free)
 5. Senior Backend Engineer (oc/mimo-v2.5-free)
 6. Junior Reviewer I (oc/big-pickle)
 7. Junior Reviewer II (oc/north-mini-code-free)
 8. Junior Reviewer III (oc/nemotron-3-ultra-free)
```

Keputusan berdasarkan **kualitas analisis**, **bukti teknis**, dan **otoritas peran** — BUKAN jumlah suara.

---

## Commands Reference

### `/daily`

All-in-one: start 9Router + sync upstream + generate config + check readiness.

```bash
py -m farewell_assistant daily
```

### `/team`

Switch mode tim.

```bash
py -m farewell_assistant team on       # Divisi — Director leads
py -m farewell_assistant team off      # Tim — Team Leader leads
py -m farewell_assistant team bawahan  # Bawahan — Workers only
py -m farewell_assistant team status   # Cek mode saat ini
```

### `/org`

Lihat struktur organisasi.

```bash
py -m farewell_assistant org           # Chart + priority
py -m farewell_assistant org chart     # Hierarchy saja
py -m farewell_assistant org roles     # Semua roles + authority
py -m farewell_assistant org workflow  # Workflow steps
py -m farewell_assistant org priority  # Decision priority
```

### `/workmode`

Switch PLAN (read-only) / BUILD (full akses).

```bash
py -m farewell_assistant workmode plan   # Read-only
py -m farewell_assistant workmode build  # Full akses
py -m farewell_assistant workmode status # Cek mode
```

### `/status`

Tampilan state saat ini.

```bash
py -m farewell_assistant status
```

Output: project aktif, mode, tier, jumlah skill, awesome stats.

### `/project`

Manage project.

```bash
py -m farewell_assistant project list   # Daftar semua project
py -m farewell_assistant project 002    # Switch ke project 002
```

### `/cool`

Browse awesome-opencode registry.

```bash
py -m farewell_assistant cool list              # Semua entries
py -m farewell_assistant cool search <q>        # Cari
py -m farewell_assistant cool info <name>       # Detail
py -m farewell_assistant cool recommend         # Rekomendasi untuk stack aktif
py -m farewell_assistant cool stats             # Statistik
```

---

## Workflow Examples

### DIVISI Mode -- Via Director

```
USER (Boss)
  |  "Bikin fitur login"
  ▼
DIRECTOR AI (LEADER_1)
  |  Memahami objective -> scope -> Work Order
  |  Output: "Implementasi auth (register/login/JWT)"
  ▼
TEAM LEADER (LEADER) + SPECIAL + WORKERS
  |  Eksekusi sesuai WO
  ▼
LAPOR -> DIRECTOR -> USER
```

### TIM Mode -- Skip Director (Personal/Hemat)

```
USER (Boss)
  |  "Bikin fitur login"
  |  (langsung, tanpa Director -- hemat token)
  ▼
TEAM LEADER (SPECIAL)
  |  Pahami task -> bagi tugas:
  |  +- SPECIAL  -> planning, architecture
  |  +- WORKER_1 -> code review, validation
  |  +- WORKER_2 -> docs, refactoring
  ▼
EXECUTION
  |  LEADER eksekusi + SPECIAL planning + WORKER review
  ▼
GABUNG HASIL
  |  LEADER kumpulkan output
  |  Resolve konflik rekomendasi
  ▼
LAPOR ke USER
  |  "Selesai. Fitur berjalan"
  ▼
USER (Boss)
  |  Review -> approve / minta revisi
  ✔  SELESAI
```

### BAWAHAN Mode -- Worker Langsung

```
USER (Boss)
  |  "Bikin fitur login"
  ▼
WORKER (WORKER_1)
  |  Eksekusi langsung
  ▼
USER (Boss)
  ✔  SELESAI
```

### Sesi Lengkap (Pagi Hari)

```bash
# 1. Daily -- start 9Router + sync semua
py -m farewell_assistant daily

# 2. Pilih mode tim
py -m farewell_assistant team tim

# 3. Cek org chart
py -m farewell_assistant org

# 4. Mulai coding -- opencode otomatis pake model sesuai mode

# 5. Cek project
py -m farewell_assistant project list

# 6. Cek status
py -m farewell_assistant status
```

---

## Token Optimization

### Skill Filtering

ECC punya **271 skills**. Farewell-assistant filter project-relevant:

| Sebelum | Sesudah | Hemat |
|---------|---------|-------|
| 271 skills di system prompt | 11 skills | ~96% |
| ~30k tokens/request | ~1.2k tokens/request | ~28.8k token |

Caranya:
1. `indexer.py` — match stack project → skill manifest
2. `active-skills.json` — hanya skill relevan
3. `_sync_opencode()` — inject filtered paths ke `opencode.jsonc`

### Role-Based Routing

| Agent | DIVISI | TIM | BAWAHAN |
|-------|--------|-----|---------|
| build/team | LEADER_1 | SPECIAL | WORKER_1 |
| planner/architect | SPECIAL | SPECIAL | WORKER_1 |
| reviewers | WORKER_1 | WORKER_1 | WORKER_1 |
| helpers (docs, worker) | WORKER_2 | WORKER_2 | WORKER_2 |

Task simpel -> model ringan (WORKER_2). Task kompleks -> model capable (SPECIAL/LEADER).

### Fallback

9Router handle fallback otomatis. Kalau model premium kena rate limit, 9Router coba model lain. Gak perlu campur tangan manual.

---

## Project Management

### Melihat Project

```bash
py -m farewell_assistant project list
```

Output:
```
001 - farewell-assistant (python, PYTHON) <- active
002 - service-hub (node, NODE)
003 - farewell-ex (unknown, UNKNOWN)
```

### Switch Project

```bash
py -m farewell_assistant project 002
```

Otomatis:
- Simpan session project sebelumnya
- Update registry active project
- Update context footer

### Register Project Baru

Farewell-assistant otomatis register project dari registry. Kalau mau manual, edit `.farewell/registry.json`.

---

## Architecture

```
farewell_assistant/           # Python package
├── cli.py                    # CLI dispatcher (8 commands)
├── daily.py                  # All-in-one daily routine
├── org.py                    # Organization hierarchy
├── workmode.py               # PLAN/BUILD mode switch
├── config.py                 # Path constants
├── helpers.py                # JSON I/O, colors, registry
├── indexer.py                # Skill matching engine
├── awesome_indexer.py        # awesome-opencode parser
├── memory.py                 # Session memory
└── __main__.py               # Entry point

.farewell/                    # State & config
├── team.json                 # {"team": "TIM", "org": {...}}
├── registry.json             # Registered projects
├── manifests/                # Per-project skill manifests
├── memory/                   # Session logs
└── context/                  # Per-project docs

.opencode/                    # OpenCode config (auto-generated)
├── opencode.jsonc            # Provider + agent + skills
├── context.md                # Session footer
├── work-mode.json            # {"mode": "build"}
└── active-skills.json        # Filtered skill paths
```

### File yang sudah dihapus

| File | Alasan |
|------|--------|
| `nvidia.py` | Nvidia provider dihapus — rate limit |
| `tracker.py` | Dead code — fungsi tidak pernah dipanggil |
| `log.py` | Dead code — tidak pernah di-import |
| `.farewell/9router-models.json` | Hardcoded combos — diganti live SQLite read |

---

## Troubleshooting

### "9Router not running"

```bash
py -m farewell_assistant daily
```

Daily otomatis start 9Router. Kalau gagal, cek:
- Node.js terinstall?
- 9Router ada di `9router/`?
- Port 20128 tidak dipakai aplikasi lain?

### Combo tidak muncul di opencode

```bash
py -m farewell_assistant daily
```

`_sync_opencode()` baca model dari `api-key.txt`. Pastikan LEADER/SPECIAL/WORKER_N sudah terisi.

### Model tidak sesuai ekspektasi

Cek `api-key.txt` — model mapping ada di sana. Edit lalu jalankan `/daily` untuk sync ulang.

### Nvidia error (sudah tidak relevan)

Nvidia sudah dihapus dari farewell-assistant dan 9Router. Kalau masih muncul error, cek `kv` table di 9Router SQLite (`%APPDATA%/9router/db/data.sqlite`) untuk entry `customModels` atau `disabledModels` scope dengan key nvidia.

---

---

## awesome-opencode Integration

Farewell-assistant terintegrasi penuh dengan [awesome-opencode](https://github.com/anomalyco/awesome-opencode) — registry plugin, theme, agent, dan project untuk Opencode.

### Data Source

Semua data dari repo `awesome-opencode/` (YAML files):

```
awesome-opencode/data/
├── plugins/    *.yaml  — Plugin OpenCode
├── themes/     *.yaml  — Tema tampilan
├── agents/     *.yaml  — Agent AI siap pakai
├── projects/   *.yaml  — Project referensi
└── resources/  *.yaml  — Resource belajar
```

### Commands

```bash
# Lihat semua entri
py -m farewell_assistant cool list

# Cari plugin/agent/project
py -m farewell_assistant cool search auth
py -m farewell_assistant cool search database

# Lihat detail
py -m farewell_assistant cool info <name>

# Rekomendasi project berdasarkan stack aktif
py -m farewell_assistant cool recommend

# Statistik
py -m farewell_assistant cool stats
```

### Auto-Recommendation

Saat `/daily` atau `/status`, farewell-assistant otomatis:

1. Baca project aktif (misal: `002-service-hub`)
2. Dapatkan stack dari manifest (misal: `["nodejs", "nestjs", "prisma"]`)
3. Cocokkan dengan awesome-opencode projects
4. Tampilkan 3 rekomendasi teratas di `.opencode/context.md`

Hasilnya muncul di footer setiap sesi:

```
# Awesome Recommendations
  - Universal LLM API Proxy: Universal multi-model proxy and library
  - opencode-agent for Cowork: Cowork plugin for Claude Code
```

### Daily Sync

```bash
py -m farewell_assistant daily
```

Setiap `/daily`, awesome-opencode di git pull (upstream sync) biar selalu up-to-date dengan registry terbaru.

### Stack Matching

Farewell-assistant punya `STACK_SKILLS` mapping di `indexer.py`:

| Stack | Skills yang cocok |
|-------|-------------------|
| python | python-patterns, fastapi-patterns, django-patterns, ... |
| nodejs | nestjs-patterns, prisma-patterns, backend-patterns, ... |
| react | react-patterns, react-testing, frontend-patterns, ... |
| docker | docker-patterns, deployment-patterns |

Ditambah `get_recommended_projects_for_stack()` di `awesome_indexer.py` yang mencocokkan stack project → rekomendasi dari awesome-opencode.

---

## License

MIT
