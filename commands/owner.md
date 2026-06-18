---
description: Owner — daily maintenance
---

# Owner

Daily maintenance for project owner. Run after /start.

## Flow

1. Pull ECC + 9Router updates (rebuild 9Router standalone kalau source berubah, bukan hanya package.json)
2. Analyze changelog for breaking changes or adjustments needed
3. Doctor check (ECC exist, 9Router exist + standalone build, config, health, Ollama status)
4. Ensure 9Router running (start kalau tidak)
5. Summary with recommendations
