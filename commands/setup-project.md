---
description: Setup Project — Clone project ke TEMP/ dan register dengan auto code
---

# Setup Project

Clone git project ke folder `TEMP/` (gitignored), detect type, register ke registry.

## Flow

| Step | Aksi | Detail |
|------|------|--------|
| 1 | **Clone** | `git clone <url> TEMP/<name>/` |
| 2 | **Detect** | Auto-detect type (python, node, rust, etc.) |
| 3 | **Register** | Daftar ke registry dengan auto code (001, 002, ...) |
| 4 | **Activate** | Set sebagai active project |

## Output

```
[OK] Cloned to TEMP/service-hub
[OK] service-hub terdaftar dengan code project 001
```

## Cara Pakai

```powershell
py -m farewell_assistant.cli setup-project https://github.com/user/repo.git
```

Atau di OpenCode: `/setup-project https://github.com/user/repo.git`
