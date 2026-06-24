---
description: Start Project — Pilih dan aktifkan project yang terdaftar
---

# Start Project

Pilih project dari daftar registered, aktivasi untuk session ini.

## Flow

| Step | Aksi | Detail |
|------|------|--------|
| 1 | **List** | Tampilkan semua project registered |
| 2 | **Pilih** | User input project code |
| 3 | **Aktifkan** | Set active di registry |
| 4 | **Footer** | Footer update: `Project: 001-service-hub` |

## Output

```
Project terdaftar:
  000 — farewell-assistant (python, AUTOMATION) ← active
  001 — farewell-ex (rust+kotlin, ANDROID+RUST)
  002 — service-hub (node, NODE)

Pilih project: /start-project <code>
```

## Cara Pakai

```powershell
py -m farewell_assistant.cli start-project      # list
py -m farewell_assistant.cli start-project 001  # activate
```

Atau di OpenCode:

```
/start-project        → AI tampilkan list
/start-project 001    → aktifkan project 001
```
