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
NINEROUTER_API_KEY=sk-5aeb03e2d6fefe6e-oedccr-a35926e4
```

Hanya 9Router API key — **tidak ada Nvidia**, **tidak ada combo hardcoded**.

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
2. Farewell-assistant tentukan mode tim (divisi/tim/bawahan)
3. Agent pake combo sesuai peran (DIRECTOR/TEAM_LEADER/SENIOR/JUNIOR)
4. 9Router route request ke model sesungguhnya lewat combo fallback chain
5. Hasil kembali ke kamu

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

Ada 3 mode tim. Pilih sesuai kebutuhan:

| Mode | Command | Root Model | Senior Model | Junior Model | Cocok Untuk |
|------|---------|-----------|--------------|--------------|-------------|
| **DIVISI** | `/team on` | DIRECTOR | DIRECTOR | DIRECTOR | Project besar, butuh premium |
| **TIM** | `/team off` | TEAM_LEADER | SENIOR | JUNIOR_1 | Sehari-hari, hemat token |
| **BAWAHAN** | `/team bawahan` | SENIOR | SENIOR | SENIOR | Task kecil, cepat |

### DIVISI (ON) — Mode Perusahaan

Semua agent pake DIRECTOR combo (ocg/deepseek-v4-flash → fallback ke TEAM_LEADER → SENIOR).

```bash
py -m farewell_assistant team on
# Output: [DIVISI] Ketua Divisi leading: DIRECTOR
```

**Alur:** User → Director → Team Leader → Senior BE → Junior → Lapor ke Director → User

Cocok untuk: project besar, butuh kualitas maksimal, budget token gak masalah.

### TIM (OFF) — Mode Personal/Hemat

Agent dibagi peran:
- **build/team** → TEAM_LEADER combo (oc/deepseek-v4-flash-free round-robin)
- **planner/code-reviewer/dll** → SENIOR combo (oc/mimo-v2.5-free round-robin)
- **worker-1/2/3** → JUNIOR_1 combo (oc/north-mini-code-free single)

```bash
py -m farewell_assistant team off
# Output: [TEAM] Ketua Tim leading: TEAM_LEADER
```

**Alur:** User → Team Leader → Senior BE + Junior → Lapor ke User

Cocok untuk: sehari-hari, hemat token, task kompleksitas sedang.

### BAWAHAN — Mode Worker

Semua agent pake SENIOR combo. Tanpa leader.

```bash
py -m farewell_assistant team bawahan
# Output: [KARYAWAN] Workers mode: SENIOR
```

**Alur:** User → Worker → User

Cocok untuk: task kecil, cepat, token minimal.

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

### DIVISI Mode — Via Director

```
USER (Boss)
  │  "Bikin fitur login untuk service-hub"
  ▼
DIRECTOR AI (ocg/deepseek-v4-flash)
  │  Memahami objective → scope → Work Order
  │  Output: "WO-003: Implementasi auth (register/login/JWT)"
  ▼
TEAM LEADER + SENIOR BE + JUNIORS
  │  Eksekusi sesuai WO
  ▼
LAPOR → DIRECTOR → USER
```

### TIM Mode — Skip Director (Personal/Hemat)

```
USER (Boss)
  │  "Bikin fitur login untuk service-hub"
  │  (langsung, tanpa Director — hemat token)
  ▼
TEAM LEADER (oc/deepseek-v4-flash-free)
  │  Pahami task → bagi tugas:
  │  ├─ Senior BE  → backend auth (API, DB, JWT)
  │  ├─ Junior I   → validasi bug/edge cases
  │  ├─ Junior II  → review code style
  │  └─ Junior III → review arsitektur
  ▼
SENIOR BE (oc/mimo-v2.5-free)
  │  Eksekusi backend:
  │  1. Buat model User + migration
  │  2. Buat endpoint register/login/me
  │  3. Implementasi JWT + middleware
  │  4. Tulis unit test
  ▼
JUNIOR REVIEWERS
  │  Validasi: bug, style, architecture
  ▼
GABUNG HASIL
  │  Team Leader kumpulkan output
  │  Resolve konflik rekomendasi
  ▼
LAPOR ke USER
  │  "Selesai. 3 file: auth.ts, db.py, test_auth.py"
  │  Coverage: 92%
  ▼
USER (Boss)
  │  Review → approve / minta revisi
  ✔  SELESAI
```

### BAWAHAN Mode — Worker Langsung

```
USER (Boss)
  │  "Bikin fitur login"
  ▼
WORKER (SENIOR combo)
  │  Eksekusi langsung
  ▼
USER (Boss)
  ✔  SELESAI
```

### Sesi Lengkap (Pagi Hari)

```bash
# 1. Daily — start 9Router + sync semua
py -m farewell_assistant daily

# 2. Pilih mode tim
py -m farewell_assistant team tim

# 3. Cek org chart
py -m farewell_assistant org

# 4. Mulai coding — opencode otomatis pake model sesuai mode
#    (build/team → TEAM_LEADER, reviewer → SENIOR, worker → JUNIOR_1)

# 5. Kalau perlu ganti project
py -m farewell_assistant project 001

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

| Agent | Divisi | Tim | Bawahan |
|-------|--------|-----|---------|
| build/team | DIRECTOR | TEAM_LEADER | SENIOR |
| planner/reviewer | DIRECTOR | SENIOR | SENIOR |
| worker | DIRECTOR | JUNIOR_1 | SENIOR |

Task simpel → model murah (JUNIOR). Task kompleks → model capable (SENIOR/TEAM_LEADER).

### Combo Fallback Chain

```
DIRECTOR → TEAM_LEADER → SENIOR → JUNIOR_1/2/3
```

Kalau model premium rate-limited, turun otomatis ke free models. Gak perlu campur tangan manual.

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

`_sync_opencode()` baca combo dari 9Router SQLite. Pastikan combo sudah dibuat di 9Router UI.

### Model rate-limited

Combo punya fallback chain. DIRECTOR → TEAM_LEADER → SENIOR → JUNIOR. Kalau model mahal kena limit, turun otomatis ke free model. Gak perlu manual.

### Nvidia error

Nvidia sudah dihapus sepenuhnya dari farewell-assistant. Tapi kalau masih terdaftar di 9Router (providerConnections table), hapus manual lewat 9Router UI → Settings → Providers.

---

## License

MIT
