# farewell-assistant

Lightweight Python orchestrator for **9Router** + **OpenCode** + **ECC skills**.

9Router handles ALL models, subscriptions, and combos. OpenCode handles coding. ECC skills (271) provide expert guidance per domain.

## Architecture

```
User → OpenCode (PLAN/BUILD) → 9Router /v1/chat/completions (26 models)
                                  ↑
                              ECC Skills (271, web+mobile priority)
```

- **9Router**: model routing, combo management, API keys, subscriptions
- **OpenCode**: AI coding agent with ECC skills integration
- **ECC**: 271 SKILL.md files loaded on demand by OpenCode

## Model Strategy

| Mode | Combo | Use |
|------|-------|-----|
| Team ON | Deepseek-GO-Flash (instructor) + Free 5 (executors) | Professional: architecture, planning, security, complex logic |
| Team OFF | Free Round Robin (5 models) | Personal: typo, CRUD, exploration |

Team status shown in footer: `Farewell: ON | 001-project | BUILD | Team: ON`

## CLI Commands

| Command | Description |
|---------|-------------|
| `daily` | 9Router health + GPU + project status |
| `workmode` | Switch PLAN/BUILD |
| `project` | List/switch active project |
| `start-project <code>` | Activate project + footer |
| `setup-project <path>` | Register project from path + index skills |
| `self-heal` | Post-edit typecheck hook |
| `hermes` | Hermes Agent: install/config/launch/status |

## Quick Start

```powershell
py -m farewell_assistant daily        # Check 9Router + system health
py -m farewell_assistant workmode build  # Switch to BUILD mode
py -m farewell_assistant start-project 001  # Activate farewell-assistant
```

## Project Lifecycle

1. `/setup-project <git|path>` → register + index skills → `.farewell/skills/`
2. `/start-project <code>` → activate project + footer
3. Work in OpenCode with ECC skills filtered to project stack
4. `/daily` for health check

## Dependencies

- Python 3.10+
- 9Router (Next.js standalone) at `9router/`
- ECC skills at `ecc/skills/` (271 files)
- Hermes Agent (optional) at `hermes-agent/`
