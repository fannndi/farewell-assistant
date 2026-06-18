# Preprocess Pipeline

Setiap user input setelah Session Init:

```
1. BACA projects/registry.json       → project aktif
2. BACA projects/context/<slug>.md   → konteks project
3. EXTRACT kategori dari registry:
   - Ambil unique values dari registry → active → kategori
   - Sort by importance: WEB > MOBILE > AI_ML > DATA > INFRA > AUTOMATION
   - Simpan ke session state untuk footer
4. READ MODE + GPU:
   - Baca .opencode/llm-mode.json → ambil mode
   - Infer GPU: eco → off, on → on
5. READ WORK MODE:
   - Baca .opencode/work-mode.json → ambil mode (plan / build)
   - PLAN mode: gunakan skill audit, research, explore
   - BUILD mode: gunakan skill orchestration, tdd, coding, security
6. COUNT SKILLS:
   - Baca projects/skill-mode-index.json → skills[work_mode]
   - Hitung total = sum semua skill di semua group
   - Status: ON jika count > 0, OFF jika count = 0
7. ENRICHMENT CHECK:
   - Mode == eco?           → SKIP
   - Input < 5 kata?        → SKIP
   - Pertanyaan umum?       → SKIP ("apa itu", "jelaskan", "what is", "how to")
   - Selain itu             → Jalankan Invoke-LLMEnrich()
8. JAWAB user dengan context + work mode
9. APPEND footer (lihat Footer section di bawah)
```

## Kapan Enrichment Berguna

| Input | Enrich? | Alasan |
|-------|---------|--------|
| "bikin CRUD penduduk desa" | Ya | Domain + stack detection |
| "buat API inventory system" | Ya | Complex task decomposition |
| "fix bug auth token expiry" | Ya | Context enrichment |
| "hai" | Tidak | Terlalu sederhana |
| "apa itu closure?" | Tidak | Pertanyaan umum |
| "fix typo line 45" | Tidak | Simple task |

## Kategori Validasi

System harus validasi bahwa kategori di footer hanya berasal dari project aktif:

- `farewell-assistant` → hanya `AUTOMATION`
- `service-hub` → `AUTOMATION - DATA - INFRA - MOBILE - WEB`
- Tidak ada project → jangan tampilkan footer

## Mode Behavior

| Mode | Skill Groups | Allowed Tools | Behavior |
|------|-------------|---------------|----------|
| PLAN | audit, research, explore, planning | read, bash | Read-only, tidak edit file |
| BUILD | orchestration, tdd, coding, security, deployment | read, bash, write, edit | Implementasi, test, commit |

Default: BUILD.

---

## Footer Format

Setelah setiap respons (kecuali Session Init), append 1 baris:

```
Session: farewell-assistant | Kategori: AUTOMATION | Mode: eco | GPU: off | Work: BUILD | Skills: ON - 23
```

### Dynamic Rendering

Footer **harus** di-render secara dinamis berdasarkan registry + mode state:

1. Baca `projects/registry.json` → ambil field `active`
2. Baca `projects/<active>/kategori` → ambil semua unique values
3. Sorted by importance: `WEB > MOBILE > AI_ML > DATA > INFRA > AUTOMATION`
4. Baca `.opencode/llm-mode.json` → ambil field `mode`
5. Infer GPU: mode == "on" → `GPU: on`, mode == "eco" → `GPU: off`
6. Baca `.opencode/work-mode.json` → ambil field `mode`
7. Baca `projects/skill-mode-index.json` → hitung total skill sesuai work mode
8. Render: `Session: <active> | Kategori: <sorted kategori> | Mode: <mode> | GPU: <gpu> | Work: <work mode> | Skills: ON - <count>`

### Behavioral Impact

Footer ini bukan sekadar display — mempengaruhi behavior AI:

| Mode | GPU | Work | Skills | AI Behavior |
|------|-----|------|--------|-------------|
| eco | off | BUILD | ON - 23 | Self-reliant, 23 skill aktif, execute mode |
| eco | off | PLAN | ON - 20 | Read-only, 20 skill aktif, audit mode |
| on | on | BUILD | ON - 23 | Local LLM + 23 skill, full power |
| on | on | PLAN | ON - 20 | Local LLM + 20 skill, analyze mode |

Footer bersifat informatif, sekaligus behavioral switch.

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

