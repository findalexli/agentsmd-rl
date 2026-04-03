# Freeze the in-tree Python SDK

## Problem

The Python SDK at `src/pyodide/internal/workers-api/` has been migrated to a separate repository ([cloudflare/workers-py](https://github.com/cloudflare/workers-py)) and is now installed from PyPI. The in-tree copy must be kept for backward compatibility but should not be modified going forward. Currently there is nothing preventing accidental changes to these files.

## What needs to happen

1. **Create a freeze test** at `src/pyodide/internal/test_frozen_sdk.py` that uses SHA-256 hashes to verify none of the SDK files under `internal/workers-api/` have been modified. The test should hash each file and compare against known-good values. If a file was changed, the test should fail with a clear message directing developers to `cloudflare/workers-py`.

2. **Register the test in Bazel** — add a `py_test` target in `src/pyodide/BUILD.bazel` so the freeze test runs as part of the normal test suite.

3. **Add a deprecation comment** to `src/pyodide/internal/workers-api/src/workers/__init__.py` making it clear that this module is frozen and new features belong in `workers-py`. Update the freeze test's expected hash for `__init__.py` to reflect this addition.

4. **Update the agent documentation** — `src/pyodide/AGENTS.md` currently describes `internal/workers-api/` as a "Python SDK package (`pyproject.toml` + `uv.lock` managed)". This is no longer accurate. Update the documentation to reflect that the SDK is frozen and now lives in a separate repository.

## Files to Look At

- `src/pyodide/internal/workers-api/` — the frozen SDK directory
- `src/pyodide/BUILD.bazel` — Bazel build file where the test target should be added
- `src/pyodide/AGENTS.md` — agent documentation describing this directory's components
- `src/pyodide/internal/workers-api/src/workers/__init__.py` — main module entry point
