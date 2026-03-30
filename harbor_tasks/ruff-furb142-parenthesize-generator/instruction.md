# Parenthesize generator arguments in FURB142 fixer

## Bug Description

The FURB142 rule (`for-loop-set-mutations`) rewrites `for x in iterable: s.add(expr)` into `s.update(expr for x in iterable)`. However, when `expr` itself is an unparenthesized generator expression passed to `s.add()`, the rewrite produces invalid syntax.

For example:

```python
for x in ("abc", "def"):
    s.add(c for c in x)
```

Gets rewritten to:

```python
s.update(c for c in x for x in ("abc", "def"))
```

This is ambiguous and changes the semantics because the inner `c for c in x` generator merges with the outer `for x in` comprehension, creating a single flat comprehension instead of a nested one. The inner generator expression needs to be parenthesized to preserve its scope:

```python
s.update((c for c in x) for x in ("abc", "def"))
```

Already-parenthesized generators like `s.add((c for c in x))` should not get double-parenthesized.

## Files to Modify

- `crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs`
- `crates/ruff_linter/resources/test/fixtures/refurb/FURB142.py` (add test cases)
