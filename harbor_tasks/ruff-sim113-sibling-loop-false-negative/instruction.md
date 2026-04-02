# SIM113 false negative when same counter variable is reused in sibling loops

Ruff's `SIM113` rule (`enumerate-for-loop`) suggests replacing manual index counters with `enumerate()`. However, it produces a false negative when the same counter variable is reused across sibling loops within the same function.

For example:

```python
def func():
    i = 0
    for val in [1, 2, 3]:
        print(f"{i}: {val}")
        i += 1

    i = 0
    for val in [1, 2, 3]:
        print(f"{i}: {val}")
        i += 1
```

Both loops should be flagged with SIM113 (each independently could use `enumerate()`), but currently only the first loop is flagged. The second loop is silently skipped.

Similarly, this pattern is missed:

```python
def func():
    for i, val in enumerate([1, 2, 3]):
        print(f"{i}: {val}")

    i = 0
    for val in [1, 2, 3]:
        print(f"{i}: {val}")
        i += 1
```

The second loop should be flagged, but it is not.

## Affected code

The core logic lives in `crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs`, specifically in the `enumerate_for_loop` function. The function checks whether the counter variable is used outside the for loop — if so, it suppresses the diagnostic. The problem is in how "outside references" are determined: references from a previous sibling loop using the same variable name are incorrectly treated as references to the current loop's counter, causing the check to bail out.

## What needs to happen

1. Fix the reference-checking logic so that only references within the current counter's lifetime are considered when deciding whether the variable is used outside the loop
2. Add test cases covering sibling loops with the same counter variable and the enumerate-then-manual pattern
3. Update the relevant snapshot files
