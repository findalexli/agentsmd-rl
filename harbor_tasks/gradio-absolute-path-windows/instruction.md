# Fix: Absolute path detection issue on Windows with Python 3.14

## Problem

The `safe_join` function in `gradio/utils.py` has a path traversal vulnerability on Windows when running Python 3.14. In Python 3.14, `os.path.isabs` no longer treats paths starting with `/` as absolute on Windows. This means a path like `/etc/passwd` would bypass the `os.path.isabs` check and could be joined with the allowed directory, potentially allowing unauthorized file access.

## Root Cause

The `safe_join` function relies solely on `os.path.isabs(filename)` to detect absolute paths. On Windows with Python 3.14, paths starting with a forward slash (`/`) are no longer considered absolute by `os.path.isabs`. The function needs an explicit check for paths starting with `/` to maintain security across all Python versions and platforms.

## Expected Fix

Add an explicit check in the `safe_join` function for paths that start with `/`, in addition to the existing `os.path.isabs` check, to ensure such paths are rejected regardless of Python version or platform behavior.

## Files to Investigate

- `gradio/utils.py` -- the `safe_join` function
