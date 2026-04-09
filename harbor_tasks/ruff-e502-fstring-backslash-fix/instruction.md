# Avoid syntax error from E502 fixes in f-strings and t-strings

## Problem

The E502 rule ("redundant backslash") produces incorrect auto-fixes when a backslash continuation appears after a multiline f-string (or t-string). The resulting fixed code may contain syntax errors.

For example, given code like:

```python
x = [
    "a" + \
f"""
b
""" + \
    "c"
]
```

Both backslashes are redundant (the expression is inside brackets), and ruff correctly identifies them as E502 violations. However, the auto-fix produces broken Python because the indexer doesn't correctly track line positions after multiline f-string tokens.

## Expected Behavior

When E502 removes redundant backslash continuations from code containing multiline f-strings, the resulting code should remain syntactically valid Python. All redundant backslashes adjacent to multiline f-strings should be detected and safely fixable.

## Files to Look At

- `crates/ruff_python_index/src/indexer.rs` — the source code indexer that tracks continuation lines and line start positions across tokens. The token-processing loop has a match arm that handles string tokens but may not cover all string-like token kinds.
