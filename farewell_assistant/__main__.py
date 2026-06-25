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
    print("  start-project     Switch project + footer")
    print("  setup-project     Register project from path")
    print("  self-heal         Post-edit typecheck hook")
    print("  hermes            Hermes Agent: install/config/launch/status")
    print()
    print("9Router handles all models + subscriptions.")
    print()
    print("Examples:")
    print("  py -m farewell_assistant daily")
    print("  py -m farewell_assistant hermes install")
    print("  py -m farewell_assistant start-project 001")
