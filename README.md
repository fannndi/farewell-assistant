# farewell-assistant

AI Coding Assistant Orchestrator — manage 9Router, ECC skills, team hierarchy, and per-project session memory.

```bash
$ py -m farewell_assistant daily
```

One command: starts 9Router, syncs combos, generates opencode config, checks everything.

---

## Install

```bash
pip install -e .
```

Requires: Python 3.10+, Node.js 18+, 9Router (port 20128), ECC.

---

## Commands

| Command | Description |
|---------|-------------|
| `/daily` | All-in-one: start 9Router + sync combos + generate opencode.jsonc + readiness |
| `/workmode` | Switch PLAN (read-only) / BUILD (full access) |
| `/team` | Switch team tier: divisi / tim / bawahan |
| `/org` | Show org chart, roles, workflow, decision priority |
| `/status` | Show current state (mode, team, project, skills) |
| `/project` | List or switch active project |
| `/cool` | Browse awesome-opencode plugins, themes, agents, projects |

### Examples

```bash
# Daily check (start + sync + read)
py -m farewell_assistant daily

# Team mode
py -m farewell_assistant team on      # Divisi — director leads
py -m farewell_assistant team off     # Tim — team leader + senior + junior
py -m farewell_assistant team bawahan # Workers only

# Organization
py -m farewell_assistant org          # Full org chart
py -m farewell_assistant org roles    # Role authorities
py -m farewell_assistant org workflow # Workflow steps
py -m farewell_assistant org priority # Decision priority

# Work mode
py -m farewell_assistant workmode build
py -m farewell_assistant workmode plan

# Project management
py -m farewell_assistant project list
py -m farewell_assistant project 002

# Quick state
py -m farewell_assistant status
```

---

## Organization Structure

```
Boss (User)
├── Director AI          ocg/deepseek-v4-flash
├── Deputy Director AI   ds/deepseek-v4-flash
└── Team Leader AI       oc/deepseek-v4-flash-free  ← Anda
    ├── Senior Backend Engineer   oc/mimo-v2.5-free
    ├── Junior Reviewer I         oc/big-pickle
    ├── Junior Reviewer II        oc/north-mini-code-free
    └── Junior Reviewer III       oc/nemotron-3-ultra-free
```

**Pegawai Tetap** (90% kontribusi): Team Leader + Senior Backend Engineer
**Junior Reviewer** (10% kontribusi): validasi & second opinion

Decision priority: Boss → Director → Deputy → Team Leader → Senior BE → Junior (berdasarkan bukti teknis, bukan voting)

---

## Team Modes

| Mode | root_model | senior_model | junior_model | Use case |
|------|-----------|--------------|--------------|----------|
| **DIVISI** (`/team on`) | DIRECTOR | DIRECTOR | DIRECTOR | Semua pakai model premium |
| **TIM** (`/team off`) | TEAM_LEADER | SENIOR | JUNIOR_1 | Hierarki: leader → senior → junior |
| **BAWAHAN** (`/team bawahan`) | SENIOR | SENIOR | SENIOR | Workers saja, tanpa leader |

### Agent-to-Model Mapping (TIM mode)

```
build/team/ketua-tim  → TEAM_LEADER  (round-robin: free models)
planner/architect/... → SENIOR       (round-robin: free models)
worker-1/2/3          → JUNIOR_1     (single: north-mini-code-free)
```

Token hemat: tugas sederhana → model murah, tugas kompleks → model capable.

---

## Combo Architecture

9Router combos are **read-only** from farewell-assistant. Created/managed via 9Router UI.

| Combo | Kind | Models |
|-------|------|--------|
| DIRECTOR | fallback | ocg/deepseek-v4-flash → TEAM_LEADER → SENIOR |
| DEPUTY | fallback | ds/deepseek-v4-flash → TEAM_LEADER → SENIOR |
| TEAM_LEADER | round-robin | oc/deepseek-v4-flash-free, SENIOR, JUNIOR_1/2/3 |
| SENIOR | round-robin | oc/mimo-v2.5-free, oc/deepseek-v4-flash-free, JUNIOR_1/2/3 |
| JUNIOR_1 | single | oc/north-mini-code-free |
| JUNIOR_2 | single | oc/big-pickle |
| JUNIOR_3 | single | oc/nemotron-3-ultra-free |

Combo names resolved dynamically from 9Router SQLite — no hardcoded model names.

---

## What `/daily` Does

```
1/4 Start 9Router       → if not running, starts 9Router on port 20128
2/4 Upstream            → git pull ECC (main) + 9Router (master) + awesome-opencode
3/4 Sync opencode.jsonc → reads combos from SQLite, injects models + skill paths + agent config
4/4 Readiness check     → health, ECC, GitHub, combos report
```

---

## Skill Loading (Token Optimization)

ECC has 271 skills. Farewell-assistant **filters** to project-relevant skills only:

- `active-skills.json` written per project (e.g., 11 skills for service-hub)
- `_sync_opencode()` injects filtered paths into `opencode.jsonc`
- Result: **~96% less skill token burn** per session

---

## Architecture

```
farewell_assistant/
├── cli.py              # CLI dispatcher (daily, team, org, workmode, project, cool, status)
├── daily.py            # All-in-one: start + upstream + sync + check
├── org.py              # Organization hierarchy, roles, workflow, priority
├── workmode.py         # PLAN/BUILD switch + model patching
├── config.py           # Path constants
├── helpers.py          # JSON I/O, colored output, project registry
├── indexer.py          # Project→skill matching, active-skills manifest
├── awesome_indexer.py  # awesome-opencode YAML parser + recommendation engine
├── memory.py           # Per-project session save/load
└── __main__.py         # Entry point

.farewell/
├── team.json           # {"team": "TIM", "org": {...}}
├── registry.json       # Registered projects
├── manifests/          # Per-project skill manifests
├── memory/             # Per-project session memory
└── context/            # Per-project context docs

.opencode/
├── context.md          # Auto-updated footer (read by OpenCode)
├── work-mode.json      # {"mode": "plan|build"}
├── opencode.jsonc      # Auto-generated from template + 9Router combos
└── active-skills.json  # Filtered skill paths
```

---

## Files Removed (Cleanup)

| File | Reason |
|------|--------|
| `nvidia.py` | Nvidia provider removed — rate limit issues |
| `tracker.py` | Dead code — functions never called |
| `log.py` | Dead code — never imported |
| `.farewell/9router-models.json` | Hardcoded combos — replaced by live SQLite read |

---

## API Keys

Only `api-key.txt` at project root:

```
NINEROUTER_API_KEY=sk-...
```

No Nvidia keys. No hardcoded combo definitions.

---

## Work Modes

| Mode | Behavior |
|------|----------|
| **PLAN** | Read-only. Read/Glob/Grep only. Bash forbidden. |
| **BUILD** | Full write access via edit/write tools. |

---

## License

MIT
