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

After the fix, passing `{"items": [None, "hello", None]}` to `none_to_none_str()` must return `{"items": ["None", "hello", "None"]}`, and the result must serialize via `tomli_w.dumps()` without raising `TypeError`.

## Files

- `src/prime_rl/utils/config.py` — contains `none_to_none_str()`
- Your fix must not use `try`/`except` blocks anywhere in this file
- Keep the code clean — avoid comments that describe past work or refactoring decisions

## Verification

Your fix will be checked against:
- `none_to_none_str({"k": [None, "a", None]})` must equal `{"k": ["None", "a", "None"]}`
- `none_to_none_str({"k": [{"n": None, "ok": 1}]})` must equal `{"k": [{"n": "None", "ok": 1}]}`
- `none_to_none_str({"k": [[None, 1], [2, None]]})` must equal `{"k": [["None", 1], [2, "None"]]}`
- `tomli_w.dumps(none_to_none_str({"items": [None, "hello", None]}))` must not raise
- No `try`/`except` blocks in `config.py`
- Ruff linter must pass on the modified file