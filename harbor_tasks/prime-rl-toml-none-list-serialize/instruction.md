# Bug: TOML config serialization drops `None` values inside lists

## Context

`prime-rl` uses TOML for configuration. Since TOML has no null type, the codebase converts Python `None` values to the string `"None"` before serialization, then converts them back on load. This round-tripping is handled by `none_to_none_str()` in `src/prime_rl/utils/config.py`.

## Problem

The `none_to_none_str()` function correctly converts `None` values at the top level of a dict and recursively handles nested dicts, but it **does not handle `None` values inside lists**. When a config field contains a list with `None` elements (e.g., `[1, None, 3]`), those `None` values are passed through unconverted, which causes `tomli_w` to raise a `TypeError` because TOML cannot represent `None`.

Similarly, dicts nested inside lists are not recursed into, so `None` values in those nested dicts are also silently dropped.

## Reproduction

```python
from prime_rl.utils.config import none_to_none_str

# This works fine
print(none_to_none_str({"key": None}))  # {"key": "None"}

# This fails — None inside a list is not converted
print(none_to_none_str({"key": [None, "a"]}))  # {"key": [None, "a"]} — bug!

# Nested dicts inside lists also broken
print(none_to_none_str({"key": [{"nested": None}]}))  # None not converted
```

## Expected behavior

`none_to_none_str()` should recursively convert all `None` values to `"None"` strings, regardless of whether they appear in dicts, lists, or any nesting combination.

The fix requires a helper function named `_convert_none` that takes a value and returns it with all `None` values recursively converted to `"None"` strings. `none_to_none_str()` should call this helper to process its input.

## Files

- `src/prime_rl/utils/config.py` — contains `none_to_none_str()` and the `_convert_none` helper function