#!/usr/bin/env python3
"""Test script to reproduce the project registration issue."""

import json
import os
from pathlib import Path

# Add current directory to path to import farewell_assistant modules
import sys
sys.path.insert(0, str(Path(__file__).parent))

from farewell_assistant.intent_router import sync_turn_state
from farewell_assistant import config

def test_project_registration():
    """Test that project registration works correctly in different repos."""
    
    # Test Case 1: Default farewell-assistant repo
    print("=" * 60)
    print("Test Case 1: Default farewell-assistant repo")
    print("=" * 60)
    
    # Mock a successful pipeline result
    result = {
        "success": True,
        "intent": {
            "intent": "build",
            "domain": "web",
            "complexity": "medium",
            "confidence": 0.85
        },
        "skill_chain": [
            {"name": "orch-add-feature", "desc": "Add new feature", "mode_hint": ""}
        ],
        "model_route": {
            "primary": "Free",
            "secondary": "Free",
            "heavy": "Free"
        },
        "needs_planning": False,
        "work_mode": "build",
        "profile": "eco",
        "turn": 1,
        "blocked": [],
        "chain_summary": "orch-add-feature",
        "task_warning": None,
        "post_steps": None,
        "degraded": None
    }
    
    # Sync turn state
    sync_turn_state(result, "bikin CRUD user dengan auth JWT")
    
    # Read the generated pipeline-result.json
    pipeline_result_path = config.STATE_DIR / "pipeline-result.json"
    if pipeline_result_path.exists():
        with open(pipeline_result_path, "r", encoding="utf-8") as f:
            pipeline_data = json.load(f)
        
        print(f"Pipeline Result:")
        print(f"  - Project: {pipeline_data.get('project')}")
        print(f"  - Project Code: {pipeline_data.get('project_code')}")
        print(f"  - Intent: {pipeline_data.get('intent')}")
        print(f"  - Turn: {pipeline_data.get('turn')}")
        
        # Check if project is correctly set
        if pipeline_data.get("project") == "farewell-assistant":
            print("✓ Test Case 1 PASSED: Project correctly set to 'farewell-assistant'")
        else:
            print(f"✗ Test Case 1 FAILED: Project incorrectly set to '{pipeline_data.get('project')}'")
    else:
        print("FAIL: Test Case 1 FAILED: pipeline-result.json not created")
    
    print()
    
    # Test Case 2: Test with project context
    print("=" * 60)
    print("Test Case 2: Test project context from registry")
    print("=" * 60)
    
    # Create a mock registry with different project
    registry_path = config.DATA_DIR / "registry.json"
    registry_backup = None
    
    try:
        # Backup current registry
        if registry_path.exists():
            with open(registry_path, "r", encoding="utf-8") as f:
                registry_backup = f.read()
        
        # Create a new registry with farewell-ex project
        test_registry = {
            "projects": {
                "farewell-ex": {
                    "project_code": "001",
                    "type": "rust+kotlin",
                    "last_used": "2026-06-22",
                    "context_file": "farewell-ex.md",
                    "path": "C:\\Users\\FANNNDI\\Documents\\farewell-ex",
                    "dominan": "ANDROID+RUST",
                    "is_local": True,
                    "kategori": {}
                }
            },
            "active": "farewell-ex",
            "_next_code": "002"
        }
        
        # Write test registry
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(test_registry, f, indent=2)
        
        # Run sync again
        sync_turn_state(result, "bikin CRUD user dengan auth JWT")
        
        # Read the updated pipeline-result.json
        if pipeline_result_path.exists():
            with open(pipeline_result_path, "r", encoding="utf-8") as f:
                pipeline_data = json.load(f)
            
            print(f"Pipeline Result:")
            print(f"  - Project: {pipeline_data.get('project')}")
            print(f"  - Project Code: {pipeline_data.get('project_code')}")
            print(f"  - Expected: farewell-ex")
            
            # Check if project is correctly set from registry
            if pipeline_data.get("project") == "farewell-ex":
                print("PASS: Test Case 2 PASSED: Project correctly set to 'farewell-ex' from registry")
            else:
                print(f"FAIL: Test Case 2 FAILED: Project incorrectly set to '{pipeline_data.get('project')}'")
        else:
            print("FAIL: Test Case 2 FAILED: pipeline-result.json not created")
            
    finally:
        # Restore original registry
        if registry_backup:
            with open(registry_path, "w", encoding="utf-8") as f:
                f.write(registry_backup)
        elif registry_path.exists():
            # If there was no original registry, delete it
            os.remove(registry_path)
    
    print()
    
    # Test Case 3: Test without registry (should fallback to default)
    print("=" * 60)
    print("Test Case 3: Test without registry (fallback to default)")
    print("=" * 60)
    
    # Remove registry if it exists
    if registry_path.exists():
        os.remove(registry_path)
    
    # Run sync again
    sync_turn_state(result, "bikin CRUD user dengan auth JWT")
    
    # Read the pipeline-result.json
    if pipeline_result_path.exists():
        with open(pipeline_result_path, "r", encoding="utf-8") as f:
            pipeline_data = json.load(f)
        
        print(f"Pipeline Result:")
        print(f"  - Project: {pipeline_data.get('project')}")
        print(f"  - Project Code: {pipeline_data.get('project_code')}")
        print(f"  - Expected: farewell-assistant (fallback)")
        
        # Check if project is correctly set (should fallback to default)
        if pipeline_data.get("project") == "farewell-assistant":
            print("PASS: Test Case 3 PASSED: Project correctly set to 'farewell-assistant' (fallback)")
        else:
            print(f"FAIL: Test Case 3 FAILED: Project incorrectly set to '{pipeline_data.get('project')}'")
    else:
        print("FAIL: Test Case 3 FAILED: pipeline-result.json not created")

if __name__ == "__main__":
    test_project_registration()
