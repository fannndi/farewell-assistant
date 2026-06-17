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
9. APPEND footer (Session | Kategori | Mode | GPU | Work | Skills)
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
