# [ty] Respect supported lower bounds from `requires-python`

## Problem

When a `pyproject.toml` specifies `requires-python` with an unusual version specifier, ty crashes with a panic. For example, setting `requires-python = "==2.7"` (a Python 2 version) or `requires-python = "==44.44"` (a far-future version) causes ty to panic during project metadata discovery instead of handling these cases gracefully.

This affects any project whose `requires-python` doesn't map to a version that ty natively supports (Python 3.7+).

## Expected Behavior

ty should handle `requires-python` specifiers that reference Python 2 versions or unsupported future versions without panicking. For Python 2 specifiers, ty should resolve to the lowest supported Python 3 version. For completely unsupported future versions, ty should produce a clear error message explaining that no supported Python version is included.

## Files to Look At

- `crates/ty_project/src/metadata/pyproject.rs` — contains `resolve_requires_python()` which parses the `requires-python` field and converts it to a `PythonVersion`. This function directly uses the version numbers from the specifier without checking if they're actually supported by ty.
- `crates/ty_project/src/metadata.rs` — project metadata discovery that calls into `pyproject.rs` to resolve the Python version from `pyproject.toml`.
