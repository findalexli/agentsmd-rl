# Task: Speed up cleanup_python_generated_files

## Problem

The `cleanup_python_generated_files()` function in `dev/breeze/src/airflow_breeze/utils/path_utils.py` is slow in large repositories. It uses `Path.rglob()` to find and remove `.pyc` files and `__pycache__` directories, which visits every directory in the tree — including `node_modules`, `.git`, `.venv`, and other directories that never contain relevant Python artifacts.

## Requirements

Optimize the function so that it can skip entire subtrees that are known to be irrelevant:

- **Skip `node_modules` directories** — these contain JavaScript dependencies, not Python bytecode.
- **Skip hidden directories** (names starting with `.`) — these include `.git`, `.venv`, `.tox`, etc.

The existing cleanup behavior must be preserved for directories that are not skipped:

- `.pyc` files must still be deleted.
- `__pycache__` directories must still be removed.
- `FileNotFoundError` must still be silently ignored.
- `PermissionError` must still be caught, with the affected path appended to the `permission_errors` list.

## Verification

After your changes, confirm that:

- `ruff check dev/breeze/src/airflow_breeze/utils/path_utils.py` passes
- `ruff format --check dev/breeze/src/airflow_breeze/utils/path_utils.py` passes
- `python -m py_compile dev/breeze/src/airflow_breeze/utils/path_utils.py` succeeds
