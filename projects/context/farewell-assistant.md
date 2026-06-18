# farewell-assistant

Type: PowerShell automation orchestrator
Path: C:/Users/FANNNDI/Documents/farewell-assistant
Stack: PowerShell 7 + OpenCode + 9Router (Next.js standalone) + ECC skills + Ollama (Qwen models)
Focus: Multi-project AI assistant — token-efficient, GPU-aware, dengan mode-based skill routing (PLAN/BUILD) dan 9Router auto-start on Windows logon.

Key files:
  - scripts/start.ps1           — daily startup + profile generation + model health report
  - scripts/autostart.ps1       — Windows Scheduled Task manager (9Router on logon + restart-on-failure)
  - scripts/llm-setup.ps1       — LLM mode config (eco/on/hot/balance/performance + auto/list/pull/remove)
  - scripts/workmode.ps1        — switch PLAN/BUILD work mode (ROLE enforcement)
  - scripts/detect-project.ps1  — project type detection from file markers
  - scripts/common/config.ps1   — centralized URLs/paths/constants
  - scripts/common/helpers.ps1  — Start-9Router (robust: PID file, log redirect, backoff), LLM, Ollama, GPU
  - scripts/common/log.ps1      — Write-TaskLog + Sync-SessionState → logging.md
  - scripts/common/start-9router-bg.ps1 — hidden wrapper for Scheduled Task
  - scripts/hooks/check-enrich.ps1 — enrichment pipeline diagnostic
  - scripts/hooks/self-heal.ps1 — auto-fix on file change
  - commands/go.md                — universal task execution template
  - commands/start.md             — boot sequence documentation
  - commands/setup.md             — LLM mode setup guide
  - commands/llm-setup.md         — LLM mode reference
  - commands/detect.md            — project type detection
  - commands/autostart.md         — 9Router autostart manager
  - commands/workmode.md          — PLAN/BUILD mode switch
  - commands/enrich-check.md      — enrichment pipeline diagnostic
  - profiles/combo/opencode.jsonc — OpenCode config template (combo-based, agent definitions, commands)
  - instructions/user-rules.md  — core rules + ROLE enforcement (mode lock, logging)
  - instructions/preprocess.md  — enrichment pipeline + footer format
  - projects/registry.json      — project index (active: farewell-assistant)
  - projects/skill-mode-index.json — skills per work mode (PLAN: 20, BUILD: 24)
  - projects/skill-index.json   — full skill catalog by kategori (6 kategori, 347 lines)
  - api-key.txt                 — NINEROUTER_API_KEY, 9ROUTER_PASSWORD, COMBO_* definitions (gitignored)

Conventions:
  - Work mode (PLAN/BUILD) adalah ROLE — AI tidak boleh auto-switch, hanya user via /workmode
  - Setiap task stage dicatat ke logging.md via Write-TaskLog
  - 9Router clone+standalone approach: build .next/standalone, run via node, PID tracked
  - Autostart: Scheduled Task AtLogon (no admin) + restart 3x @ 5min, bukan VBS di Startup
  - State files di .opencode/ (gitignored): llm-mode.json, work-mode.json, combo.json, 9router.pid, logs/

Dependencies (cloned, gitignored):
  - 9router/   — decolua/9router (Next.js AI gateway, port 20128)
  - ecc/       — affaan-m/ECC (270+ skills, 64 agents)
  - models/    — GGUF files untuk Ollama (qwen2.5-coder-1.5b, qwen3.5-0.8b/2b/4b)

GPU: MX150 2GB VRAM — mode eco (off) / on (1GB) / hot (600MB) / balance (1.4GB) / performance (2.5GB)
