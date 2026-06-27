# farewell-assistant

Lightweight 9Router orchestrator — start, sync, and check 9Router + ECC in one command.

```
$ py -m farewell_assistant daily
```

```
  ========================================
  Daily Readiness
  ========================================
  [OK] 9Router v0.5.12 (port 20128)
  [OK] ECC: up to date
  [OK] GitHub: v0.5.12
  [OK] Nvidia (direct): 2/2 models, 40 RPM
  [..]   Free                 (-)        <- oc/deepseek-v4-flash-free ...
  [..]   Deepseek-API-Flash   (-)        <- ds/deepseek-v4-flash, Free
  [..]   Deepseek-GO-Flash    (-)        <- ocg/deepseek-v4-flash, Free
  [..]   Ollama               (-)        <- ollama/gpt-oss:120b ...
  [OK] 4 combos, 13 models
  ========================================
```

One command does it all: starts 9Router, pulls ECC/9Router updates, syncs OpenCode config, checks everything.

---

## Install

```bash
pip install -e .
```

Or run directly:
```bash
python -m farewell_assistant daily
```

Requires: Python 3.10+, Node.js, 9Router, ECC.

---

## Commands

| Command | Description |
|---------|-------------|
| `daily` | **All-in-one**: start 9Router + pull ECC/9Router + sync opencode.jsonc + readiness check |
| `workmode` | Switch PLAN/BUILD mode |
| `team` | Toggle Team mode (ON = premium models, OFF = free models) |
| `status` | Show current state (mode, team, project, skills) |
| `project` | List or switch active project |

### Examples

```bash
# All-in-one daily check (start + pull + sync + check)
py -m farewell_assistant daily

# Work mode
py -m farewell_assistant workmode build   # BUILD mode
py -m farewell_assistant workmode plan    # PLAN mode (read-only)
py -m farewell_assistant workmode status

# Team mode
py -m farewell_assistant team on
py -m farewell_assistant team off

# Project management
py -m farewell_assistant project list
py -m farewell_assistant project 002

# Quick state
py -m farewell_assistant status
```

---

## Architecture

```
farewell_assistant/
├── cli.py              # 5 commands (daily, workmode, team, status, project)
├── daily.py            # All-in-one: start + upstream + sync + check
├── config.py           # Paths
├── helpers.py          # JSON, colors, project registry
├── workmode.py         # PLAN/BUILD + opencode default_agent sync
├── indexer.py          # ECC skill matching
├── nvidia.py           # Direct Nvidia API client
└── helpers.py          # JSON, colors, project registry
```

### What `/daily` does (all in one)

```
1/4 Start 9Router       → if not running, starts 9Router on port 20128
2/4 Upstream            → git pull ECC (main) + 9Router (master)
3/4 Sync opencode.jsonc → generates providers from 9Router DB combos + Nvidia
4/4 Readiness check     → health, ECC, GitHub, Nvidia, combos
```

### 9Router combos → opencode.jsonc

Auto-generated from 9Router SQLite DB (`combos` table):
- `Free` (round-robin)
- `Deepseek-API-Flash`
- `Deepseek-GO-Flash`
- `Ollama`

Plus **Nvidia Direct** provider (bypasses 9Router):
- `deepseek-ai/deepseek-v4-flash` (40.env: NVIDIA_API_KEY_FLASH)
- `deepseek-ai/deepseek-v4-pro` (env: NVIDIA_API_KEY_PRO)

---

## Setup

```bash
git clone https://github.com/fannndi/farewell-assistant
cd farewell-assistant
pip install -e .
```

### Required
- Python 3.10+
- Node.js 18+
- 9Router (local, port 20128)
- ECC repo (`ecc/` subdirectory)

### API Keys (`api-key.txt`)
```
NINEROUTER_API_KEY=...
NVIDIA_API_KEY_FLASH=nvapi-...
NVIDIA_API_KEY_PRO=...
```

---

## Work Modes

| Mode | Behavior |
|------|----------|
| **PLAN** | Read-only. Read/Glob/Grep only. Bash forbidden. |
| **BUILD** | Full write access via edit/write tools. |

Switch: `py -m farewell_assistant workmode plan|build`

---

## Team Mode

| Mode | Models |
|------|--------|
| **ON** (Team) | Premium models via 9Router + Nvidia |
| **OFF** (Solo) | Free models only |

```bash
py -m farewell_assistant team on
py -m farewell_assistant team off
```

---

## Project Management

```bash
# List projects
py -m farewell_assistant project list

# Switch project
py -m farewell_assistant project 002
```

---

## Files

```
.farewell/
├── team.json           # {"team": "ON|OFF"}
├── registry.json       # Registered projects
├── work-mode.json      # {"mode": "plan|build", "updated_at": "..."}
├── context.md          # Auto-generated footer for OpenCode
├── manifests/          # Per-project skill manifests
└── memory/             # Per-project session memory

.opencode/
├── context.md          # Auto-updated footer (read by OpenCode)
├── work-mode.json      # {"mode": "plan|build"}
└── opencode.jsonc      # Auto-generated providers from 9Router + Nvidia
```

---

## License

MIT