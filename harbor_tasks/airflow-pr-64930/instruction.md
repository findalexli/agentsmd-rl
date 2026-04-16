# Task: Optimize cleanup_python_generated_files Performance

The `cleanup_python_generated_files()` function in `dev/breeze/src/airflow_breeze/utils/path_utils.py` is slow when cleaning up `.pyc` files and `__pycache__` directories.

## Problem

The current implementation uses `rglob()` which traverses the entire directory tree, including directories that will never contain relevant Python bytecode files:

- Hidden directories (`.git`, `.venv`, etc.) contain their own Python environments and should not be cleaned
- `node_modules` directories from JavaScript tooling contain no relevant `.pyc` files

This causes unnecessary disk I/O and slows down the cleanup operation, especially in large repositories with many dependencies.

## Expected Behavior

The cleanup function should:
1. Still remove `.pyc` files in regular directories
2. Still remove `__pycache__` directories in regular locations
3. Skip hidden directories entirely (any directory starting with `.`)
4. Skip `node_modules` directories entirely

## Files to Modify

- `dev/breeze/src/airflow_breeze/utils/path_utils.py`

Look at the `cleanup_python_generated_files()` function around line 415.
