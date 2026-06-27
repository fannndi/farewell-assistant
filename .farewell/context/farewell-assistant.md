# farewell-assistant

Type: Python CLI orchestrator
Stack: Python 3.10+ + OpenCode + 9Router + ECC skills (271) + awesome-opencode registry
Desc: AI coding assistant orchestrator. Manage 9Router, ECC skills, awesome-opencode registry, per-project session memory. Goal: hemat token via combo strategy (Team ON/OFF).

## Team Hierarchy
**Divisi** (team=ON): `ocg/deepseek-v4-flash` leader + Free workers
**Tim** (team=OFF): `oc/deepseek-v4-flash-free` leader + Free workers
  /team divisi|tim  — Switch team tier (Divisi=ON, Tim=OFF)
  /workmode build|plan|status — Switch work mode

## Key Files
  cli.py            — Daily, workmode, project, cool, save, self-heal
  helpers.py        — JSON I/O, project registry, colored output
  indexer.py        — Stack → ECC skill matching, centralized manifests
  awesome_indexer.py — YAML parser → awesome-opencode plugin/agent/project matching
  daily.py          — 9Router health + token usage + awesome-opencode upstream sync
  memory.py         — Session save/load per project
  tracker.py        — Token usage from 9Router SQLite
  9Router models: .farewell/9router-models.json

## Commands
  /cool list        — List all awesome-opencode entries
  /cool search <q>  — Search plugins/themes/agents/projects
  /cool info <name> — Show details for a specific entry
  /cool recommend   — Recommend projects matching current stack
  /cool stats       — Show total counts per category
  /team on|off      — Switch combo strategy (enforces model swap)
