---
description: Go — universal task execution
---

# Go

Universal goal-based command. Satu command untuk semua task.

## Cara Kerja

1. **Pipeline** — trigger `Invoke-IntentRouter` via `trigger-pipeline.ps1`
2. **Context** — load `projects/context/<slug>.md` + `pipeline-result.json`
3. **Execute** — AI decompose goal dan eksekusi langkah-langkah
4. **Respond** — hasil

## Contoh

| Perintah | Yang Dilakukan |
|----------|----------------|
| `/go bikin CRUD user` | Decompose → backend → frontend → test |
| `/go fix auth bug` | Detect bug → fix → verify |
| `/go review code` | Code review + security scan |
| `/go deploy v1` | Verify → quality → commit |

## Constraints

Otomatis dari system:
- Profile: dari session (Free/Emergency combo)
- Project: dari registry (active)
- Mode: dari llm-mode.json (eco/on)

## Task

$ARGUMENTS
