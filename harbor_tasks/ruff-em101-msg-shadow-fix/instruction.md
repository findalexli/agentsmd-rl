# EM101 auto-fix shadows existing `msg` variable

## Problem

When ruff applies the auto-fix for rule `EM101` ("Exception must not use a string literal, assign to variable first"), it always names the extracted variable `msg`. If there is already a variable called `msg` in the same scope, the fix silently clobbers it, changing the program's behavior.

For example, given:

```python
def f():
    msg = "."
    try:
        raise RuntimeError("!")
    except RuntimeError:
        return msg
```

After applying the EM101 fix, `msg` gets reassigned to `"!"`, so the `except` block now returns `"!"` instead of `"."`. The fix should use a fresh name like `msg_0` when `msg` is already taken.

## Expected Behavior

- When `msg` is not already bound in the current scope, the fix should still use `msg` as the variable name.
- When `msg` is already bound, the fix should pick a fresh name that does not shadow the existing binding (e.g., `msg_0`, `msg_1`, etc.).
- The fix should handle cases where multiple `msg_N` names are already taken by incrementing the suffix.

## Files to Look At

- `crates/ruff_linter/src/rules/flake8_errmsg/rules/string_in_exception.rs` — the `generate_fix` function that produces the EM101 auto-fix
- `crates/ruff_linter/src/fix/edits.rs` — shared fix editing utilities
- `crates/ruff_linter/src/rules/ruff/rules/mutable_fromkeys_value.rs` — contains a `fresh_binding_name` utility that already solves a similar problem for a different rule
