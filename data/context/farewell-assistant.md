# farewell-assistant

Type: Lightweight 9Router orchestrator (Python)
Path: C:/Users/FANNNDI/Documents/farewell-assistant
Stack: Python 3.10+ + OpenCode + 9Router (Next.js standalone) + ECC skills
Focus: Minimal orchestrator — 9Router handles ALL models + subscriptions.
       OpenCode + ECC skills handle coding. PLAN/BUILD mode via work-mode.json.
       Hermes Agent integration planned (v2.1).

## Architecture

User → OpenCode (PLAN/BUILD tools) → 9Router /v1/chat/completions
                                        ↑
                                    ECC Skills (270+)

- 9Router: ALL model routing, combo management, API keys, subscriptions
- ECC skills: 270+ SKILL.md files, loaded directly by OpenCode
- PLAN/BUILD: tool-level enforcement via work-mode.json

## Key Files

  - farewell_assistant/cli.py          — CLI dispatcher (6 subcommands)
  - farewell_assistant/config.py       — Paths, constants (minimal)
  - farewell_assistant/helpers.py      — JSON I/O, GPU info, project registry
  - farewell_assistant/workmode.py     — PLAN/BUILD mode switch
  - farewell_assistant/daily.py        — 9Router health + system status
  - farewell_assistant/start.py        — 9Router start/health check
  - farewell_assistant/self_heal.py    — Post-edit typecheck (TS/TSX, Dart, Python)
  - farewell_assistant/hermes.py       — Hermes Agent bridge (install/config/sync)
  - farewell_assistant/llm_setup.py    — GPU + model status
  - farewell_assistant/log.py          — Task logging
  - farewell_assistant/self_improve.py — Git pull ECC + 9Router

## Removed (v2.0)

  - enrichment_pipeline.py  (0.8B LLM enrichment — negative value)
  - intent_router.py         (replaced by 9Router)
  - skill_chain.py           (static chains — OpenCode + AI handle skill selection)
  - models.py                (local LLM — 9Router handles all models)
  - preprocess.md            (old pipeline description)

## CLI Commands

  - daily             9Router health + system status
  - workmode          Switch PLAN/BUILD mode
  - llm               Show GPU/model status
  - project           List/switch active project
  - self-heal         Post-edit typecheck
  - hermes            Hermes Agent bridge (install/config/sync-skills/launch/status)

## Combo Profiles (9Router)

Models and subscriptions via 9Router combo (Free/Emergency).
api-key.txt defines: NINEROUTER_API_KEY, COMBO_*, MODELS_*

## Hermes Agent (v2.1 planned)

Components:
  - hermes_install.sh/ps1 — official installer
  - ~/.hermes/ — config, skills, state
  - ECC skills via external_dirs (no conversion needed)
  - 9Router as OpenAI-compatible provider
