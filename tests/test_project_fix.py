#!/usr/bin/env python3
"""Test script to verify the project registration fix."""

import json
import os
from pathlib import Path

# Add current directory to path to import farewell_assistant modules
import sys
sys.path.insert(0, str(Path(__file__).parent))

from farewell_assistant.intent_router import sync_turn_state
from farewell_assistant import config

def test_project_detection():
    """Test that project detection works correctly when running in different repos."""
    
    print("=" * 80)
    print("Testing Project Registration Fix")
    print("=" * 80)
    
    # Mock a successful pipeline result
    result = {
        "success": True,
        "intent": {
            "intent": "build",
            "domain": "web",
            "complexity": "medium",
            "confidence": 0.85,
            "stack": ["python"]
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
    
    # Test Case 1: In farewell-ex project (has project-specific registry)
    print("\n" + "=" * 80)
    print("Test Case 1: Running in farewell-ex project")
    print("=" * 80)
    
    # Temporarily change to farewell-ex directory
    original_cwd = Path.cwd()
    farewell_ex_dir = Path("C:\\Users\\FANNNDI\\Documents\\farewell-ex")
    
    try:
        os.chdir(farewell_ex_dir)
        
        # Sync turn state
        sync_turn_state(result, "bikin CRUD user dengan auth JWT")
        
        # Read the generated pipeline-result.json
        pipeline_result_path = Path(".opencode") / "pipeline-result.json"
        if pipeline_result_path.exists():
            with open(pipeline_result_path, "r", encoding="utf-8") as f:
                pipeline_data = json.load(f)
            
            print(f"Pipeline Result (farewell-ex):")
            print(f"  - Project: {pipeline_data.get('project')}")
            print(f"  - Project Code: {pipeline_data.get('project_code')}")
            print(f"  - Expected: farewell-ex, 001")
            
            # Check if project is correctly set
            project_correct = (
                pipeline_data.get("project") == "farewell-ex" and
                pipeline_data.get("project_code") == "001"
            )
            
            if project_correct:
                print("PASS: Project correctly detected and registered in farewell-ex")
            else:
                print(f"FAIL: Project not correctly detected")
                print(f"  - Got: project={pipeline_data.get('project')}, code={pipeline_data.get('project_code')}")
        else:
            print("FAIL: pipeline-result.json not created in farewell-ex")
            
    finally:
        # Restore original directory
        os.chdir(original_cwd)
    
    # Test Case 2: In farewell-assistant project (no project-specific registry)
    print("\n" + "=" * 80)
    print("Test Case 2: Running in farewell-assistant project")
    print("=" * 80)
    
    # Temporarily change to farewell-assistant directory
    farewell_assistant_dir = Path("C:\\Users\\FANNNDI\\Documents\\farewell-assistant")
    
    try:
        os.chdir(farewell_assistant_dir)
        
        # Sync turn state
        sync_turn_state(result, "bikin CRUD user dengan auth JWT")
        
        # Read the generated pipeline-result.json
        pipeline_result_path = Path(".opencode") / "pipeline-result.json"
        if pipeline_result_path.exists():
            with open(pipeline_result_path, "r", encoding="utf-8") as f:
                pipeline_data = json.load(f)
            
            print(f"Pipeline Result (farewell-assistant):")
            print(f"  - Project: {pipeline_data.get('project')}")
            print(f"  - Project Code: {pipeline_data.get('project_code')}")
            print(f"  - Expected: service-hub, 002 (from original registry)")
            
            # Check if project is correctly set
            project_correct = (
                pipeline_data.get("project") == "service-hub" and
                pipeline_data.get("project_code") == "002"
            )
            
            if project_correct:
                print("PASS: Project correctly detected and registered in farewell-assistant")
            else:
                print(f"FAIL: Project not correctly detected")
                print(f"  - Got: project={pipeline_data.get('project')}, code={pipeline_data.get('project_code')}")
        else:
            print("FAIL: pipeline-result.json not created in farewell-assistant")
            
    finally:
        # Restore original directory
        os.chdir(original_cwd)
    
    # Test Case 3: In project without registry (should fallback to default)
    print("\n" + "=" * 80)
    print("Test Case 3: Running in directory without project registry")
    print("=" * 80)
    
    # Temporarily change to temp directory
    temp_dir = Path("C:\\Users\\FANNNDI\\Documents\\test-temp")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        os.chdir(temp_dir)
        
        # Sync turn state
        sync_turn_state(result, "bikin CRUD user dengan auth JWT")
        
        # Read the generated pipeline-result.json
        pipeline_result_path = Path(".opencode") / "pipeline-result.json"
        if pipeline_result_path.exists():
            with open(pipeline_result_path, "r", encoding="utf-8") as f:
                pipeline_data = json.load(f)
            
            print(f"Pipeline Result (no registry):")
            print(f"  - Project: {pipeline_data.get('project')}")
            print(f"  - Project Code: {pipeline_data.get('project_code')}")
            print(f"  - Expected: farewell-assistant, (no code)")
            
            # Check if project is correctly set (should fallback to default)
            project_correct = (
                pipeline_data.get("project") == "farewell-assistant"
            )
            
            if project_correct:
                print("PASS: Project correctly fallback to default when no registry found")
            else:
                print(f"FAIL: Project not correctly fallback")
                print(f"  - Got: project={pipeline_data.get('project')}")
        else:
            print("FAIL: pipeline-result.json not created in temp directory")
            
    finally:
        # Cleanup and restore original directory
        for file_path in temp_dir.glob(".*"):
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir() and file_path.name != "." and file_path.name != "..":
                import shutil
                shutil.rmtree(file_path)
        
        os.chdir(original_cwd)
    
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print("The fix ensures that when running the pipeline in different projects:")
    print("1. If a project-specific registry exists, it uses that project context")
    print("2. If no project-specific registry exists, it uses the default registry")
    print("3. The footer will now correctly show the actual project being worked on")
    print("=" * 80)

if __name__ == "__main__":
    test_project_detection()
