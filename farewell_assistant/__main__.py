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
    print("  route <text>  Run intent router on text input")
    print("  workmode      Switch work mode (plan|build)")
    print("  llm           LLM management (status|list|pull|download|remove)")
    print("  project       Switch active project (list|<name>)")
    print("  self-heal     Post-edit typecheck hook")
    print("  enrich-check  Verify enrichment pipeline")
    print()
    print("Example: py -m farewell_assistant route 'bikin CRUD user'")
