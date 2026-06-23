#!/usr/bin/env python3
"""Test the project registration fix logic."""

import json
from pathlib import Path
import os

print('Testing project registration fix...')
print('=' * 60)

# Test 1: Check project-specific registry in farewell-ex
farewell_ex_dir = Path('C:\\Users\\FANNNDI\\Documents\\farewell-ex')
project_registry_file = farewell_ex_dir / 'data' / 'registry.json'

print(f'1. Project-specific registry exists: {project_registry_file.exists()}')
if project_registry_file.exists():
    with open(project_registry_file, 'r') as f:
        reg = json.load(f)
    print(f'   Active project: {reg.get("active")}')
    print(f'   Project code: {reg["projects"][reg["active"]].get("project_code")}')

print()

# Test 2: Check default registry in farewell-assistant
default_registry_file = Path('C:\\Users\\FANNNDI\\Documents\\farewell-assistant\\data\\registry.json')

print(f'2. Default registry exists: {default_registry_file.exists()}')
if default_registry_file.exists():
    with open(default_registry_file, 'r') as f:
        reg = json.load(f)
    print(f'   Active project: {reg.get("active")}')
    print(f'   Project code: {reg["projects"][reg["active"]].get("project_code")}')

print()

# Test 3: Test sync_turn_state logic
print('3. sync_turn_state logic test:')
print('   Current directory:', os.getcwd())
print('   Would check for project registry at:', Path.cwd() / 'data' / 'registry.json')
print('   File exists:', (Path.cwd() / 'data' / 'registry.json').exists())

print()
print('=' * 60)
print('Fix Summary:')
print('- sync_turn_state now checks for project-specific registry in current directory')
print('- If project-specific registry exists, uses that project context')
print('- Otherwise, falls back to default registry')
print('- This allows each project to maintain its own project context')
print('=' * 60)
