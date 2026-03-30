# Parenthesize expression in RUF050 fix

## Bug Description

The RUF050 rule (`unnecessary-if`) rewrites empty `if` statements like `if cond: pass` into just the condition expression `cond` when the condition has side effects. However, the auto-fix does not correctly handle multiline expressions that need parentheses to remain valid as standalone expression statements.

For example:

```python
if (
    id(0)
    + 0
):
    pass
```

The current fixer extracts just the inner expression `id(0)\n    + 0` without wrapping it in parentheses, producing invalid Python:

```python
id(0)
    + 0
```

This is a syntax error because without parentheses, the `+ 0` on the next line is treated as a separate (improperly indented) statement.

The fix needs to detect when the extracted expression spans multiple lines at the top level (outside of any brackets/parens) and either:
- Preserve the existing parentheses from the `if` condition, or
- Add new parentheses around the expression

The existing handling for walrus operators (named expressions) already adds parentheses, but this needs to be generalized to any multiline expression.

## Files to Modify

- `crates/ruff_linter/src/rules/ruff/rules/unnecessary_if.rs`
- `crates/ruff_linter/resources/test/fixtures/ruff/RUF050.py` (add test cases)
