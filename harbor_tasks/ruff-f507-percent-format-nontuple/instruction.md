# Fix F507 false negative for non-tuple RHS in %-formatting

## Bug Description

The F507 rule (`percent-format-positional-count-mismatch`) only checks tuple right-hand sides in `%`-format expressions. This means literal non-tuple values like `'%s %s' % 42` are silently ignored, even though they are clearly bugs -- the format string expects 2 positional arguments but only 1 value is provided.

For example, none of these are flagged:

```python
'%s %s' % 42       # int literal, not a tuple -- F507 should fire
'%s %s' % 3.14     # float literal
'%s %s' % "hello"  # string literal
'%s %s' % True     # bool literal
'%s %s' % None     # None literal
'%s %s' % -1       # unary op producing int
'%s %s' % (1 + 2)  # binary op producing int
```

The rule should be extended to also flag non-tuple RHS values when the format string expects a different number of positional arguments. However, variables, attribute accesses, subscripts, and calls should NOT be flagged because they could be tuples at runtime (e.g., `x = (1, 2); '%s %s' % x` is valid).

The approach should use type inference to determine if the RHS has a known concrete type. If the resolved type is a non-tuple atom, it counts as exactly 1 positional argument. Look for existing type-inference utilities in the `ruff_python_semantic` crate.

## Files to Modify

- `crates/ruff_linter/src/rules/pyflakes/rules/strings.rs`
- `crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py` (add test cases)
