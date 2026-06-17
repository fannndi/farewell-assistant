---
description: Go — universal task execution
---

# Go

Universal goal-based command. Satu command untuk semua task.

## Cara Kerja

1. **Detect** — cek project aktif dari `projects/registry.json`
2. **Context** — load `projects/context/<slug>.md`
3. **Enrich** — kalau mode on, jalankan Invoke-LLMEnrich()
4. **Execute** — AI decompose goal dan eksekusi langkah-langkah
5. **Respond** — hasil + footer

## Contoh

| Perintah | Yang Dilakukan |
|----------|----------------|
| `/go bikin CRUD user` | Decompose → backend → frontend → test |
| `/go fix auth bug` | Detect bug → fix → verify |
| `/go review code` | Code review + security scan |
| `/go deploy v1` | Verify → quality → commit |

## Constraints

Otomatis dari system:
- Profile: dari session (gratis/go)
- Project: dari registry (active)
- Mode: dari llm-mode.json (eco/on)

## Task

$ARGUMENTS
