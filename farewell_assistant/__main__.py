"""farewell-assistant v2 — Lightweight 9Router orchestrator."""

from .cli import main
import sys

if len(sys.argv) > 1:
    main()
else:
    print("farewell-assistant v2.0.0 - Lightweight 9Router orchestrator")
    print()
    print("Commands:")
    print("  daily             Daily: 9Router health + system status")
    print("  workmode          Switch work mode (plan|build)")
    print("  llm               Show LLM/GPU status")
    print("  project           List or switch active project")
    print("  self-heal         Post-edit typecheck hook")
    print()
    print("9Router handles all models + subscriptions.")
    print("Hermes Agent integration coming in v2.1.")
    print()
    print("Example: py -m farewell_assistant daily")
