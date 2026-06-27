# farewell-assistant

Type: Python CLI orchestrator
Stack: Python 3.10+ + OpenCode + 9Router + ECC skills (271) + awesome-opencode registry
Desc: AI coding assistant orchestrator. Manage 9Router, ECC skills, awesome-opencode registry, per-project session memory. Goal: hemat token via combo strategy (Team ON/OFF).

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

## Team Tiers
**Divisi** (team=ON): `ocg/deepseek-v4-flash` leader + Free workers
**Tim** (team=OFF): `oc/deepseek-v4-flash-free` leader + Free workers
**Bawahan** (team=BAWAHAN): Workers langsung tanpa leader
  /team divisi|tim|bawahan  — Switch team tier
  /workmode build|plan|status — Switch work mode
  /org chart|roles|workflow|priority — Show full org hierarchy

## Key Files
  cli.py            — Daily, workmode, project, cool, save, self-heal, org
  helpers.py        — JSON I/O, project registry, colored output
  org.py            — Organizational hierarchy (roles, decision priority, workflow)
  indexer.py        — Stack → ECC skill matching, centralized manifests
  awesome_indexer.py — YAML parser → awesome-opencode plugin/agent/project matching
  daily.py          — 9Router health + token usage + awesome-opencode upstream sync
  memory.py         — Session save/load per project
  tracker.py        — Token usage from 9Router SQLite
  9Router models: .farewell/9router-models.json

## Commands
  /org              — Show org chart, roles, workflow, decision priority
  /cool list        — List all awesome-opencode entries
  /cool search <q>  — Search plugins/themes/agents/projects
  /cool info <name> — Show details for a specific entry
  /cool recommend   — Recommend projects matching current stack
  /cool stats       — Show total counts per category
  /team on|off      — Switch combo strategy (enforces model swap)
