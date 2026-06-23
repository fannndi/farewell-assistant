# Project Registration Fix Summary

## Problem Description

When using `/start-project` in repositories other than the main farewell-assistant repository, the footer was not showing the correct project context. For example, when running `/start-project` in the `farewell-ex` or `service-hub` repositories, the footer would still show `farewell-assistant` as the project name instead of the actual project being worked on.

## Root Cause

The issue was in the `sync_turn_state` function in `farewell_assistant/intent_router.py`. This function hardcodes the project name as `"farewell-assistant"` and always reads from the default registry file (`farewell_assistant/data/registry.json`).

When running the pipeline in a different project repository:
1. The pipeline would create a pipeline-result.json in that project's `.opencode` directory
2. But the project context would be incorrectly set to `"farewell-assistant"`
3. The footer would show the wrong project name

## Solution

The fix ensures that the pipeline detects which project is being worked on by checking for a project-specific registry file in the current directory.

### Key Changes

1. **Updated `sync_turn_state` function** (`farewell_assistant/intent_router.py`):
   - Added logic to check for a project-specific registry file in the current directory: `current_dir / "data" / "registry.json"`
   - If the project-specific registry exists, use that for project context
   - If not, fall back to the default registry
   - This ensures each project maintains its own project context

2. **Updated helper functions** (`farewell_assistant/helpers.py`):
   - Modified `read_project_active()` to accept an optional `registry_file` parameter
   - Modified `read_project_code()` to accept an optional `registry_file` parameter
   - Both functions now read from the specified registry file or fall back to the default

3. **Updated `_get_project_info` function** (`farewell_assistant/intent_router.py`):
   - Modified to accept an optional `registry_file` parameter
   - Ensures project info is read from the correct registry

### How It Works

1. When the pipeline runs in any repository, it first checks for a project-specific registry file
2. If found, it uses that registry's active project as the project context
3. If not found, it falls back to the default registry (which has the original project's context)
4. This allows each project to maintain its own project context and footer information

## Files Modified

1. `farewell_assistant/intent_router.py`:
   - Updated `sync_turn_state()` function
   - Updated `_get_project_info()` function

2. `farewell_assistant/helpers.py`:
   - Updated `read_project_active()` function
   - Updated `read_project_code()` function

## Testing

The fix has been tested to ensure:
- When running in `farewell-assistant` project: correctly uses `service-hub` as the active project
-.When running in `farewell-ex` project: correctly uses `farewell-ex` as the active project
- When running in a directory without a project registry: falls back to the default registry

## Impact

This fix ensures that:
- Each project maintains its own project context
- The footer correctly shows the project being worked on
- `/start-project` works correctly in any repository
- Users can distinguish between different projects when using the pipeline

## Example

**Before the fix:**
- Running `/start-project` in `farewell-ex` would show: `Farewell: ON | Project: farewell-assistant | BUILD | Turn: 1 | Chain: 8 | 95% | Eco`
- This was incorrect - it should have shown the `farewell-ex` project context

**After the fix:**
- Running `/start-project` in `farewell-ex` shows: `Farewell: ON | Project: 001-farewell-ex | BUILD | Turn: 1 | Chain: 8 | 95% | Eco`
- This is correct - it shows the proper project context for `farewell-ex`
