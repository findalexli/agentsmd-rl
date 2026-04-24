# Bug: System Python check script skips path verification on Windows

## Summary

The script `scripts/check_system_python.py` verifies that packages installed via `uv pip install --system` are functional — importable and discoverable in `PATH`. However, the "is the binary in PATH?" check is skipped entirely on Windows due to an `os.name` guard, and it relies on shelling out to the Unix `which` command, which doesn't exist on Windows.

## Problem

In `scripts/check_system_python.py`, around the section that verifies `pylint` is on the PATH after installation:

1. The check is wrapped in `if os.name != "nt":`, meaning **Windows is never tested** for PATH correctness.
2. The check uses `subprocess.run(["which", "pylint"])`, which calls the Unix `which` binary — this command does not exist on Windows.

The script should use a cross-platform approach to check if an executable is on the PATH, rather than shelling out to a Unix-specific command. The platform guard should be removed so all platforms are tested equally.

## Expected behavior

- The PATH check for installed binaries should run on **all platforms**, including Windows.
- The check should use a cross-platform mechanism rather than a Unix-specific command.

## Files to investigate

- `scripts/check_system_python.py` — the `pylint` PATH verification section after package installation

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
