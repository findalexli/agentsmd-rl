# TOML Config Serialization Writes Literal "None" Strings

## Problem

When the RL, SFT, and inference entrypoints write resolved configs to disk as TOML files, the output contains literal `"None"` string values wherever a config field has a Python `None` value. This makes the TOML files semantically incorrect (TOML has no null type, and the string `"None"` is not a valid TOML value).

## Expected Behavior

When writing a config with optional/nullable fields that are `None`, those fields should not appear in the TOML output at all, rather than being serialized as the string `"None"`.

## Affected Code

The entrypoints in `src/prime_rl/entrypoints/` call helper functions from `src/prime_rl/utils/config.py` to convert the config dict before writing it with `tomli_w.dump`. Those helpers currently convert `None` values to `"None"` strings. The fix should instead use Pydantic's `exclude_none` parameter on `model_dump` calls to prevent `None` fields from appearing in the dict in the first place, and the legacy conversion helpers should be removed.

## Validation

After fixing, running the entrypoints to write config files should produce TOML output with no `"None"` string literals and no fields present for values that were `None` in the original config.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
