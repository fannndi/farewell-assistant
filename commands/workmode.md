---
description: Switch work mode: plan / build / status
---

# Workmode

Switch PLAN/BUILD work mode. Mode ini adalah ROLE — AI tidak boleh auto-switch.

## Cara Kerja

1. **Read** — baca mode saat ini dari `.opencode/work-mode.json`
2. **Switch** — update mode ke `plan` atau `build` (atau `status` untuk info)
3. **Sync** — `Sync-SessionState` update footer + context
4. **Show** — tampilkan skill groups untuk mode baru

## Contoh

| Perintah | Yang Dilakukan |
|----------|----------------|
| `/workmode plan` | Switch ke PLAN mode (read-only) |
| `/workmode build` | Switch ke BUILD mode (full access) |
| `/workmode status` | Tampilkan mode saat ini |

## Role Enforcement

- AI **DILARANG** auto-switch mode
- PLAN mode: tools = read, bash (NO write/edit)
- BUILD mode: tools = read, bash, write, edit (full)
- Hanya user yang bisa switch via `/workmode`

## Task

$ARGUMENTS
