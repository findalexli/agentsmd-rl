# Fix broken_add Function

## Problem

The `broken_add` function in `math_ops.py` has a bug where it ignores the second argument and only returns the first argument.

## Expected Behavior

`broken_add(a, b)` should return `a + b`, not just `a`.

## Files to Look At

- `math_ops.py` — Contains the broken `broken_add` function
