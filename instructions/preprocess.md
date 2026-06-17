# Preprocess Pipeline

Setiap user input setelah Session Init:

```
1. BACA projects/registry.json       → project aktif
2. BACA projects/context/<slug>.md   → konteks project
3. EXTRACT kategori dari registry:
   - Ambil unique values dari registry → active → kategori
   - Sort by importance: WEB > MOBILE > AI_ML > DATA > INFRA > AUTOMATION
   - Simpan ke session state untuk footer
4. ENRICHMENT CHECK:
   - Mode == eco?           → SKIP
   - Input < 20 kata?       → SKIP
   - Pertanyaan umum?       → SKIP ("apa itu", "jelaskan", "what is", "how to")
   - Selain itu             → Jalankan Invoke-LLMEnrich()
5. JAWAB user dengan context
6. APPEND footer (Profile | Session | Kategori)
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
