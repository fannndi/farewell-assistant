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
    print("  start-project     Activate project + skill index + footer")
    print("  setup-project     Register project: <path> [--stack python flutter] [--reindex]")
    print("  self-heal         Post-edit typecheck hook")
    print("  hermes            Hermes Agent: install/config/launch/status")
    print()
    print("9Router handles all models + subscriptions. ECC skills (271) indexed per project.")
    print()
    print("Examples:")
    print("  py -m farewell_assistant setup-project ..\my-app --stack python react")
    print("  py -m farewell_assistant start-project 001")
