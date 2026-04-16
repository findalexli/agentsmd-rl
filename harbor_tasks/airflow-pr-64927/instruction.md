# Task: Fix Inefficient Python Cleanup Performance

## Problem Description

The Python cleanup function in the Airflow Breeze utility module is inefficient. It currently traverses directories using `rglob` patterns to find `.pyc` files and `__pycache__` directories, which causes it to descend into directories that don't contain Python-generated files (like `node_modules`, `.git`, `.venv`, and `.tox`).

When running cleanup operations, this wastes significant time exploring directories that never contain the files being cleaned.

## Expected Behavior

The cleanup should be optimized to:

1. **Skip `node_modules` directories** - these contain frontend dependencies, not Python files
2. **Skip hidden directories** - those starting with `.` (like `.git`, `.venv`, `.tox`)
3. **Continue removing all `.pyc` files and `__pycache__` directories** - functionality must remain unchanged
4. **Preserve error handling** - `FileNotFoundError` and `PermissionError` should still be handled gracefully (these occur when files are removed by other processes during cleanup)

## Files to Modify

Locate and fix the cleanup function within the Airflow Breeze utilities. The relevant code is in the `dev/breeze/src/airflow_breeze/utils/` directory.

## Verification

After your changes:
- Cleanup should complete faster by avoiding unnecessary directory traversal
- All `.pyc` files and `__pycache__` directories should still be removed from standard locations
- Files inside `node_modules` should remain untouched
- Files inside hidden directories (`.git`, `.venv`, etc.) should remain untouched
