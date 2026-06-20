# farewell-assistant

Type: Python AI assistant orchestrator
Path: C:/Users/FANNNDI/Documents/farewell-assistant
Stack: Python 3.10+ + OpenCode + 9Router (Next.js standalone) + ECC skills + Ollama (Qwen models)
Focus: Intent-Driven AI assistant — structured enrichment, automatic skill chains, dynamic model routing. GPU-aware power profiles. 9Router auto-start on Windows logon.

Key files (Python core):
  - farewell_assistant/cli.py           — CLI dispatcher (argparse, 7 subcommands)
  - farewell_assistant/config.py        — URLs, paths, constants, model routes
  - farewell_assistant/intent_router.py — Intent → permission check → skill chain → model route
  - farewell_assistant/enrichment_pipeline.py — Structured enrichment (JSON intent via Ollama) + quick classify + cache
  - farewell_assistant/skill_chain.py   — Skill chain builder (19 built-in chains)
  - farewell_assistant/helpers.py       — JSON state, Ollama, 9Router, GPU, LLM, parse_api_key
  - farewell_assistant/workmode.py      — PLAN/BUILD mode switch (ROLE enforcement)
  - farewell_assistant/llm_setup.py     — 4 power profiles, GGUF download, Ollama import
  - farewell_assistant/detect_project.py — Project type detection (16 types)
  - farewell_assistant/start.py         — 7-step startup orchestrator
  - farewell_assistant/bootstrap.py     — First-run: clone ECC + 9Router, build
  - farewell_assistant/update.py        — Git pull ECC + 9Router, rebuild if needed
  - farewell_assistant/health.py        — 9Router/Ollama health, GPU check, model ping
  - farewell_assistant/autostart.py     — Cross-platform autostart (Windows schtasks / Linux systemd)
  - farewell_assistant/self_heal.py     — Post-edit typecheck (TS/TSX, Dart, Python)
  - farewell_assistant/log.py           — Task logging + session state sync
  - farewell_assistant/run_router.py    — Entry point for plugin (CLI)

Backward-compat PS1 wrappers:
  - scripts/run-router.ps1    → py -m farewell_assistant.run_router
  - scripts/workmode.ps1      → py -m farewell_assistant.cli workmode
  - scripts/llm-setup.ps1     → py -m farewell_assistant.cli llm
  - scripts/detect-project.ps1 → py -m farewell_assistant.cli detect

Runtime context files (written per-turn):
  - .opencode/pipeline-result.json — Machine-readable pipeline output (intent, domain, chain, model, turn)
  - .opencode/context.md           — AI-readable context (Session State + Turn State)
  - .opencode/llm-mode.json        — Current LLM mode (eco/hot/balance/performance)
  - .opencode/work-mode.json       — Current work mode (plan/build)
  - .opencode/intent-cache.json    — Persisted intent cache (survives restart)
  - .opencode/session-state.json   — Session metadata + task history
  - profiles/combo/opencode.jsonc  — OpenCode config template (combo-based, agent definitions, commands)

Static files:
  - instructions/user-rules.md  — core rules + ROLE enforcement (mode lock, logging)
  - instructions/preprocess.md  — enrichment pipeline + footer format
  - data/registry.json          — project index (active: farewell-assistant)
  - data/skill-mode-index.json  — skills per work mode (PLAN: ~20, BUILD: ~30)
  - data/skill-index.json       — full skill catalog by kategori (6 kategori, 271+ skills)
  - data/context/*.md           — per-project context files
  - data/skills/                — local (non-ECC) skills
  - api-key.txt                 — NINEROUTER_API_KEY, 9ROUTER_PASSWORD, COMBO_* definitions (gitignored)

Conventions:
  - Precision Context System: pipeline writes to pipeline-result.json + context.md → AI reads
  - Intent-Driven Pipeline: Input → Quick Classify → Structured Enrich → Rule Check → Skill Chain → Model Route → Execute
  - Work mode (PLAN/BUILD) adalah ROLE — AI tidak boleh auto-switch, hanya user via /workmode
  - Skill chains: 19 built-in chains mapping intent+domain → sequential skill execution
  - Model routing: low/medium complexity → Free combo, high/critical → Emergency combo
  - Power profiles: hot (0.8B) → eco (1.5B) → balance (2B) → performance (4B)
  - Setiap task stage dicatat ke logging.md via write_task_log
  - 9Router clone+standalone approach: build .next/standalone, run via node, PID tracked
  - Autostart: Scheduled Task AtLogon (no admin) + restart 3x @ 5min
  - State files di .opencode/ (gitignored): llm-mode.json, work-mode.json, combo.json, 9router.pid, logs/

Dependencies (cloned, gitignored):
  - 9router/   — decolua/9router (Next.js AI gateway, port 20128)
  - ecc/       — affaan-m/ECC (270+ skills, 64 agents)
  - models/    — GGUF files untuk Ollama (qwen2.5-coder-1.5b, qwen3.5-0.8b/2b/4b)

GPU: MX150 2GB VRAM — hot (600MB) / eco (1GB) / balance (1.4GB) / performance (2.5GB hybrid)

Pipeline: Input → Quick Classify → Structured Enrich (Ollama) → Rule Check → Skill Chain → Model Route → Execute
Enrichment: JSON output {intent, domain, stack, complexity, confidence}
Skill Chains: 19 built-in (build_web, build_mobile, fix_bug, review_code, deploy, etc.)
Model Routes: complexity → Free combo (low/medium) or Emergency combo (high/critical)
