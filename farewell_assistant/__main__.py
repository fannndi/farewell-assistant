"""farewell-assistant — Intent-Driven AI assistant orchestrator."""
from .cli import main
import sys

if len(sys.argv) > 1:
    main()
else:
    print("farewell-assistant v1.5.0 — Intent-Driven AI assistant orchestrator")
    print()
    print("Usage: py -m farewell_assistant <command> [options]")
    print()
    print("Commands:")
    print("  daily             Daily report: pipeline prime + system health + session log")
    print("  route <text>      Run intent router on text input")
    print("  workmode          Switch work mode (plan|build)")
    print("  llm               LLM management (status|list|pull|download|remove)")
    print("  offline           Offline mode (on|off|status)")
    print("  project           Switch active project (list|<name>)")
    print("  self-heal         Post-edit typecheck hook")
    print("  enrich-check      Verify enrichment pipeline")
    print("  self-improvement  Git pull ECC + 9Router, cek dampak, update changelog")
    print()
    print("Example: py -m farewell_assistant daily")
