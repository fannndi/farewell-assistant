#!/usr/bin/env python3
# Test the project registration fix

import json
from pathlib import Path

print("Testing project registration fix...")
print("=" * 60)

# Test 1: Check project-specific registry in farewell-ex
project_registry_file = Path("C:\\Users\\FANNNDI\\Documents\\farewell-ex\\data\\registry.json")

print(f"1. Project-specific registry exists: {project_registry_file.exists()}")
if project_registry_file.exists():
    with open(project_registry_file, "r") as f:
        reg = json.load(f)
    print(f"   Active project: {reg.get('active')}")
    print(f"   Project code: {reg['projects'][reg['active']].get('project_code')}")

print()

# Test 2: Check default registry in farewell-assistant
default_registry_file = Path("C:\\Users\\FANNNDI\\Documents\\farewell-assistant\\data\\registry.json")

print(f"2. Default registry exists: {default_registry_file.exists()}")
if default_registry_file.exists():
    with open(default_registry_file, "r") as f:
        reg = json.load(f)
    print(f"   Active project: {reg.get('active')}")
    print(f"   Project code: {reg['projects'][reg['active']].get('project_code')}")

print()
print("Fix Summary:")
print("- sync_turn_state now checks for project-specific registry in current directory")
print("- If project-specific registry exists, uses that project context")
print("- Otherwise, falls back to default registry")
print("- This allows each project to maintain its own project context")
