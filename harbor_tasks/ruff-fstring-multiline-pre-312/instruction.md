# Avoid emitting multi-line f-string elements before Python 3.12

## Problem

When running `ruff format` with `--target-version` set to Python 3.11 or earlier, the formatter can emit non-triple-quoted f-strings with replacement fields that span multiple lines. This is invalid syntax before Python 3.12 — PEP 701 (which allows multi-line f-string expressions) was only introduced in Python 3.12.

For example, a compact f-string like:
```python
if f"aaaaaaaaaaa {[ttttteeeeeeeeest,]} more {aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}":
    pass
```

gets formatted to something like:
```python
if f"aaaaaaaaaaa {
    [
        ttttteeeeeeeeest,
    ]
} more {aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}":
    pass
```

which is a syntax error on Python 3.10 or 3.11.

## Expected Behavior

When targeting Python versions before 3.12, the formatter should keep originally-flat replacement fields flat in non-triple-quoted f-strings. Replacement fields that are already multiline in the source should be preserved as-is. Triple-quoted f-strings and Python 3.12+ targets should continue to allow multiline expansion.

## Files to Look At

- `crates/ruff_python_formatter/src/other/interpolated_string_element.rs` — handles formatting of f-string replacement field elements, including the multiline expansion decision
