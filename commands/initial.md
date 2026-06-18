---
description: Initial — one-time setup for new laptop
---

# Initial

Run once after cloning project to a new laptop.

## Flow

1. Clone ECC + 9Router + npm install
2. Build 9Router standalone
3. Start 9Router + poll health (robust backoff)
4. Guide user to open dashboard, create API key + combo
5. Create api-key.txt from template
6. Validate API key + combo against 9Router API
7. Initialize state files (ECO mode, BUILD mode)
8. Detect GPU → recommendation
9. (Optional) Enable 9Router autostart on Windows logon
10. Done → run /start
