"""Simple entry script - runs intent router with --input argument.
Used by OpenCode plugin via run-router.ps1."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="run_router",
        description="Invoke intent router with a text input.",
    )
    parser.add_argument("--input", required=True, help="User input text")
    parser.add_argument("--context", default="", help="Project context")
    parser.add_argument("--force", action="store_true", help="Force enrichment")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    from farewell_assistant.intent_router import invoke_intent_router

    result = invoke_intent_router(args.input, args.context, force=args.force)

    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        from farewell_assistant.intent_router import show_intent_router_result
        show_intent_router_result(result)

    # Exit code: 0 for success, 1 for blocked
    if result.get("success"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
