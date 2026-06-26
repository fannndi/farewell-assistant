# farewell-assistant

Type: Python CLI orchestrator
Stack: Python 3.10+ + OpenCode + 9Router + ECC skills (271)
Desc: AI coding assistant orchestrator. Manage 9Router, ECC skills, per-project session memory. Goal: hemat token via combo strategy (Team ON/OFF).

## Combo Strategy
Team ON → Deepseek-GO-Flash (instructor → fallback ke Free 5 model) — professional
Team OFF → Free 5 model Round Robin — personal, cost efficient

## Key Files
  cli.py       — Daily, workmode, project, save, self-heal
  helpers.py   — GPU, JSON I/O, project registry
  indexer.py   — Stack → skill matching, centralized manifests
  memory.py    — Session save/load per project
  daily.py     — 9Router health + token usage
  tracker.py   — Token usage from 9Router SQLite
