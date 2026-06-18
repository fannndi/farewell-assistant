---
description: Verify enrichment pipeline (local LLM preprocessor)
---

# Enrich Check

Diagnostic command untuk validasi enrichment pipeline end-to-end.

## Cara Kerja

1. **Detect mode** — baca `llm-mode.json`
2. **GPU check** — tampilkan VRAM info
3. **Test enrich** — kirim input ke `Invoke-LLMEnrich()`
4. **Compare** — input vs output untuk cek apakah enrichment aktif

## Mode

- Mode `eco` → enrichment disabled (skip, tampilkan instruksi)
- Mode selain eco → test jalankan enrichment

## Contoh

| Perintah | Yang Dilakukan |
|----------|----------------|
| `/enrich-check test input` | Test enrichment dengan "test input" |
| `/enrich-check bikin API` | Test enrichment dengan input complex |

## Task

$ARGUMENTS
