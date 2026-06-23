#!/usr/bin/env python3
"""Comprehensive test of the project registration fix."""

import json
import os
from pathlib import Path
import sys

# Add the project to the path
sys.path.insert(0, str(Path(__file__).parent))

from farewell_assistant.intent_router import sync_turn_state

def test_project_registration_fix():
    """Test that the project registration fix works correctly."""
    
    print("=" * 80)
    print("Testing Project Registration Fix")
    print("=" * 80)
    
    # Test result
    test_result = {
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
    
    # Store original directory
    original_cwd = Path.cwd()
    
    try:
        # Test 1: Run in farewell-assistant project directory
        print("\n" + "=" * 80)
        print("Test 1: Running in farewell-assistant project")
        print("=" * 80)
        
        farewell_assistant_dir = Path("C:\\Users\\FANNNDI\\Documents\\farewell-assistant")
        
        # Backup current .opencode if it exists
        backup_dir = None
        if (farewell_assistant_dir / ".opencode").exists():
            backup_dir = Path("backup_opencode")
            if backup_dir.exists():
                import shutil
                shutil.rmtree(backup_dir)
            shutil.copytree(farewell_assistant_dir / ".opencode", backup_dir)
        
        os.chdir(farewell_assistant_dir)
        
        # Run sync_turn_state
        sync_turn_state(test_result, "test input")
        
        # Check results
        pipeline_result_path = Path(".opencode") / "pipeline-result.json"
        if pipeline_result_path.exists():
            with open(pipeline_result_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print(f"Pipeline Result:")
            print(f"  - Project: {data.get('project')}")
            print(f"  - Project Code: {data.get('project_code')}")
            
            # In farewell-assistant, the active project is "service-hub"
            if data.get("project") == "service-hub":
                print("✓ PASS: Correctly detected 'service-hub' as active project in farewell-assistant")
            else:
                print(f"✗ FAIL: Expected 'service-hub', got '{data.get('project')}'")
        else:
            print("✗ FAIL: pipeline-result.json not created")
        
        # Restore .opencode
        if backup_dir and backup_dir.exists():
            shutil.rmtree(".opencode")
            shutil.copytree(backup_dir, ".opencode")
            shutil.rmtree(backup_dir)
        
        # Test 2: Run in farewell-ex project directory
        print("\n" + "=" * 80)
        print("Test 2: Running in farewell-ex project")
        print("=" * 80)
        
        farewell_ex_dir = Path("C:\\Users\\FANNNDI\\Documents\\farewell-ex")
        
        # Backup current .opencode if it exists
        if (farewell_assistant_dir / ".opencode").exists():
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.copytree(farewell_assistant_dir / ".opencode", backup_dir)
        
        os.chdir(farewell_ex_dir)
        
        # Run sync_turn_state
        sync_turn_state(test_result, "test input")
        
        # Check results
        pipeline_result_path = Path(".opencode") / "pipeline-result.json"
        if pipeline_result_path.exists():
            with open(pipeline_result_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print(f"Pipeline Result:")
            print(f"  - Project: {data.get('project')}")
            print(f"  - Project Code: {data.get('project_code')}")
            
            # In farewell-ex, the active project should be "farewell-ex"
            if data.get("project") == "farewell-ex":
                print("✓ PASS: Correctly detected 'farewell-ex' as active project in farewell-ex")
            else:
                print(f"✗ FAIL: Expected 'farewell-ex', got '{data.get('project')}'")
        else:
            print("✗ FAIL: pipeline-result.json not created")
        
        # Restore .opencode
        if backup_dir and backup_dir.exists():
            shutil.rmtree(".opencode")
            shutil.copytree(backup_dir, ".opencode")
            shutil.rmtree(backup_dir)
        
        # Test 3: Run in directory without project registry
        print("\n" + "=" * 80)
        print("Test 3: Running in directory without project registry")
        print("=" * 80)
        
        # Create a temp directory without registry
        temp_dir = Path("C:\\Users\\FANNNDI\\Documents\\temp-test")
        temp_dir.mkdir(exist_ok=True)
        
        # Backup current .opencode if it exists
        if (farewell_assistant_dir / ".opencode").exists():
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.copytree(farewell_assistant_dir / ".opencode", backup_dir)
        
        os.chdir(temp_dir)
        
        # Run sync_turn_state
        sync_turn_state(test_result, "test input")
        
        # Check results
        pipeline_result_path = Path(".opencode") / "pipeline-result.json"
        if pipeline_result_path.exists():
            with open(pipeline_result_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print(f"Pipeline Result:")
            print(f"  - Project: {data.get('project')}")
            print(f"  - Project Code: {data.get('project_code')}")
            
            # In temp directory, should fallback to default registry
            # which has "service-hub" as active project
            if data.get("project") == "service-hub":
                print("✓ PASS: Correctly used default registry (service-hub) in temp directory")
            else:
                print(f"✗ FAIL: Expected 'service-hub', got '{data.get('project')}'")
        else:
            print("✗ FAIL: pipeline-result.json not created")
        
        # Restore .opencode and cleanup
        if backup_dir and backup_dir.exists():
            shutil.rmtree(".opencode")
            shutil.copytree(backup_dir, ".opencode")
            shutil.rmtree(backup_dir)
        
        # Cleanup temp directory
        for file_path in temp_dir.glob(".*"):
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
        
    finally:
        # Restore original directory
        os.chdir(original_cwd)
    
    print("\n" + "=" * 80)
    print("Fix Summary")
    print("=" * 80)
    print("The fix ensures that:")
    print("1. sync_turn_state checks for project-specific registry in current directory")
    print("2. If project-specific registry exists, uses that project's context")
    print("3. Otherwise, uses the default registry (service-hub in this case)")
    print("4. This allows each project to maintain its own project context")
    print("=" * 80)

if __name__ == "__main__":
    test_project_registration_fix()
