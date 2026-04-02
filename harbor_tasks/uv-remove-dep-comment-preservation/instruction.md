# Bug: End-of-line comments lost when removing dependencies

## Summary

When removing a dependency from `pyproject.toml` using `uv remove`, end-of-line comments on **nearby** entries can be silently dropped.

## Reproduction

Given a `pyproject.toml` like:

```toml
[project]
name = "example"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "numpy>=2.4.3", # essential comment
    "requests>=2.32.5",
]
```

Running `uv remove requests` produces:

```toml
[project]
name = "example"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "numpy>=2.4.3",
]
```

The comment `# essential comment` on the `numpy` line has been silently removed. This also affects cases where the removed item is in the middle of the array — comments on the preceding entry are lost.

## Root Cause

The `remove_dependency` function in `crates/uv-workspace/src/pyproject_mut.rs` removes items from the TOML array without accounting for how `toml_edit` stores end-of-line comments. In `toml_edit`, trailing comments on one line are stored in the *prefix* of the **next** array item. When that next item is removed, its prefix (containing the previous line's comment) is discarded.

## Expected Behavior

After removing `requests`, the output should be:

```toml
dependencies = [
    "numpy>=2.4.3", # essential comment
]
```

All comments that belong to entries that are **not** being removed must be preserved.

## Scope

The fix should be contained to the `remove_dependency` function in `crates/uv-workspace/src/pyproject_mut.rs`. Consider the cases where the removed item is:
- The last item in the array
- A middle item in the array
- One of multiple adjacent matching items (e.g., two `typing-extensions` entries with different markers)
