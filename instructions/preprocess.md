# Preprocess Pipeline

Setiap user input setelah Session Init:

```
1. BACA projects/registry.json       → project aktif
2. BACA projects/context/<slug>.md   → konteks project
3. ENRICHMENT CHECK:
   - Mode == eco?           → SKIP
   - Input < 20 kata?       → SKIP
   - Pertanyaan umum?       → SKIP ("apa itu", "jelaskan", "what is", "how to")
   - Selain itu             → Jalankan Invoke-LLMEnrich()
4. JAWAB user dengan context
5. APPEND footer
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
