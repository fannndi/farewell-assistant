# farewell-assistant

Lightweight Python orchestrator — **9Router** + **ECC skills** + **OpenCode**.

9Router handles ALL models, subscriptions, combos. ECC skills (271) provide expert guidance per domain.

## Architecture

```
User → OpenCode (PLAN/BUILD) → 9Router /v1/chat/completions (26 models)
                                  ↑
                              ECC Skills (271, per-project indexed)
```

## Per-Project Setup

Every project has its own `.farewell/` directory with isolated context.

```
C:/Users/.../service-hub/
├── .farewell/
│   ├── manifest.json       ← skill index (10 skills for this project)
│   ├── memory/             ← session history per project
│   └── context/            ← project context files
└── (project files)
```

## Flow (Game-like Checkpoints)

```bash
# Session 1
cd ~/project
fa setup-project .            # register + index skills → .farewell/
fa start-project <code>       # continue: inject "Last: ..." dari memory
# ... kerja ...
fa save "refactored auth, added tests"   # checkpoint

# Session 2 (besok)
fa start-project <code>       # continue: "Last: refactored auth, added tests"
# ... lanjut kerja ...
fa save "deployed to staging"
```

## Commands

| Command | Description |
|---------|-------------|
| `daily` | 9Router health + GPU + token usage + project status |
| `workmode` | Switch PLAN/BUILD |
| `start-project <code>` | Activate project → inject context + memory |
| `setup-project <path>` | Register project + index skills + create `.farewell/` |
| `save <summary>` | Save session checkpoint to memory |
| `self-heal` | Post-edit typecheck hook |

## Model Strategy

| Mode | Combo | Use Case |
|------|-------|----------|
| **Team ON** | `Deepseek-GO-Flash` (instructor) + `Free` (executor) | Professional: architecture, planning, security |
| **Team OFF** | `Free` (Round Robin 5 model) | Personal: typo, CRUD, exploration |

Team indicator in footer: `Farewell: ON | 001-project | BUILD | Team: ON | Skills: 12`

## Dependencies

- Python 3.10+
- [9Router](https://github.com/decolua/9router) — local AI gateway (Next.js standalone)
- ECC skills — 271+ SKILL.md files
- [OpenCode](https://opencode.ai) — AI coding agent
