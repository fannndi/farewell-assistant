# farewell-assistant

Type: Lightweight 9Router orchestrator (Python)
Stack: Python 3.10+ + OpenCode + 9Router + ECC skills (271)
Focus: 9Router handle ALL models/subscriptions. OpenCode + ECC handle coding.

## Architecture

User → OpenCode (PLAN/BUILD) → 9Router /v1/chat/completions (26 models)
                                  ↑
                              ECC Skills (271, web+mobile priority)

- 9Router: model routing, combo management, subscriptions
- ECC: 271 SKILL.md, loaded by OpenCode on demand
- PLAN/BUILD: tool enforcement via work-mode.json

## Combo Strategy
Team ON → Deepseek-GO-Flash (instructor) + Free 5 model (executors) — professional
Team OFF → Free 5 model Round Robin — personal, cost efficient

## Key Files
  - cli.py          — Daily, workmode, project, self-heal, hermes (6 commands)
  - config.py       — Paths
  - helpers.py      — GPU, JSON I/O, project registry
  - workmode.py     — PLAN/BUILD switch
  - daily.py        — 9Router health + system status
  - start.py        — 9Router start/health
  - self_heal.py    — Post-edit typecheck (TS/TSX, Dart, Python, Rust, Go, Kotlin, Shell)

## CLI
  daily     — 9Router health + GPU + token usage + project status
  workmode  — Switch PLAN/BUILD
  llm       — GPU status
  project   — List/switch project
  self-heal — Post-edit typecheck
