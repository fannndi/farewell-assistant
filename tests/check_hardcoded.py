#!/usr/bin/env python3
# Check for hardcoded farewell-assistant references

import re

with open('/Users/FANNNDI/Documents/farewell-assistant/farewell_assistant/intent_router.py', 'r') as f:
    content = f.read()

matches = re.findall(r'"farewell-assistant"', content)
print(f"Found {len(matches)} hardcoded references to 'farewell-assistant' in intent_router.py")
for match in matches[:10]:
    print(f"  - {match}")
