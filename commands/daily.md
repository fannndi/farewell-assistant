---
description: Daily — Session start dengan log (ganti /start untuk daily workflow)
---

# Daily

Session start ringan dengan logging ke `session-log.md` (gitignored).
Full 7-step startup — 9Router ON, combo diakses via OpenCode UI.

## Flow

| Step | Aksi | Detail |
|------|------|--------|
| 1/7 | **Git Pull Self** | Sync dari device lain |
| 2/7 | **Initial Bootstrap** | Guard: hanya sekali setelah fresh clone |
| 3/7 | **Update Check** | Git pull ECC + 9Router, rebuild jika update |
| 4/7 | **9Router Health** | Health check → start kalau belum running |
| 5/7 | **Load Configuration** | Parse api-key.txt, combos |
| 6/7 | **Pipeline + Launch** | Prime intent pipeline |
| 7/7 | **Ready + Log** | Log session ke session-log.md |

## Output ke session-log.md

```markdown
## 2026-06-21 09:00 UTC

- **Project:** farewell-ex
- **LLM Mode:** eco
- **Work Mode:** BUILD
- **Turn:** 0
---
```

## Cara Pakai

```powershell
py -m farewell_assistant.cli daily
```

Atau di OpenCode: `/daily`
