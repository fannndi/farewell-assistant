---
description: Verify enrichment pipeline (local LLM preprocessor)
---

# Enrich Check

Diagnostic command untuk validasi pipeline Intent-Driven end-to-end.

## Cara Kerja

1. **Detect mode** — baca `llm-mode.json`
2. **GPU check** — tampilkan VRAM info
3. **Run pipeline** — jalankan `py -m farewell_assistant.cli route --force`
4. **Show result** — tampilkan intent, domain, complexity, confidence, skill chain, model route

## Mode

- Mode `eco` → enrichment disabled (skip, tampilkan instruksi)
- Mode selain eco → test jalankan pipeline lengkap

## Contoh

| Perintah | Yang Dilakukan |
|----------|----------------|
| `/enrich-check fix auth bug` | Test pipeline dengan intent fix |
| `/enrich-check bikin CRUD user` | Test pipeline dengan input complex |

## Task

$ARGUMENTS
