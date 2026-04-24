# Bug: TOML config serialization silently drops None values

## Context

The `prime-rl` launcher writes resolved Pydantic config objects to TOML files so that downstream processes (trainer, orchestrator, inference server) can reload them. This serialization happens in three entrypoints:

- `src/prime_rl/entrypoints/rl.py` — `write_config()` and `write_subconfigs()`
- `src/prime_rl/entrypoints/sft.py` — `write_config()`
- `src/prime_rl/entrypoints/inference.py` — `write_config()`

Each of these calls `config.model_dump(exclude_none=True, mode="json")` before passing the dict to `tomli_w.dump()`.

## Problem

TOML has no native null type. By using `exclude_none=True`, any field that a user explicitly set to `None` (e.g., to disable a default or clear an inherited value) is silently dropped from the output TOML. When the downstream process loads this TOML, the missing keys fall back to their Pydantic defaults — which may not be `None`.

This means users cannot reliably override a field to `None` through the config system, even though the codebase already has a convention for it: the `BaseConfig._none_str_to_none` validator converts the string `"None"` back to Python `None` on load.

The write path does not have a corresponding conversion — `None` values are simply discarded.

## Expected behavior

When a config field is `None`, the serialized TOML should contain the string `"None"` for that key, so the load path's `_none_str_to_none` validator can restore it. This should apply to all entrypoints and handle arbitrarily nested config dicts.

Implement a helper function named `none_to_none_str` in `src/prime_rl/utils/config.py` that recursively converts Python `None` values to the string `"None"` in dictionaries. This function should:
- Convert top-level `None` values to `"None"` strings
- Recursively handle nested dictionaries at any depth
- Preserve all non-`None` values (booleans, integers, strings, lists) unchanged
- Not mutate the input dictionary (return a new dict)
- Handle edge cases: empty dicts, all-`None` dicts, and dicts with no `None` values

The entrypoints should use this `none_to_none_str` helper when serializing config to TOML, and should not use `exclude_none=True` in their `model_dump()` calls.

## Files to investigate

- `src/prime_rl/utils/config.py` — shared config utilities
- `src/prime_rl/entrypoints/inference.py`
- `src/prime_rl/entrypoints/rl.py`
- `src/prime_rl/entrypoints/sft.py`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
