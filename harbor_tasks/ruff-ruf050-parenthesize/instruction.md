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

## Required Changes

### 1. Rust Implementation (`crates/ruff_linter/src/rules/ruff/rules/unnecessary_if.rs`)

The fix needs to detect when the extracted expression spans multiple lines at the top level (outside of any brackets/parens) and either:
- Preserve the existing parentheses from the `if` condition, or
- Add new parentheses around the expression

The existing handling for walrus operators (named expressions) already adds parentheses using a `format!` macro. The walrus operator handling must be preserved while generalizing to any multiline expression.

The following literal strings must be present in the modified source code:
- `parenthesized_range` - for tracking existing parentheses in the condition
- `has_top_level_line_break` - for detecting multiline expressions at the top level
- `condition_as_expression` - for the expression output function
- `line_break` or `multiline` or `multi_line` - for identifying expressions spanning multiple lines
- `needs_parens` or `nesting` or `spans_multiple` - for determining when parentheses are required
- `is_named_expr` - for preserving walrus operator handling
- `format!` with `"({}` - the format string pattern used for parenthesizing expressions

### 2. Test Cases (`crates/ruff_linter/resources/test/fixtures/ruff/RUF050.py`)

Add test cases covering multiline expressions that need parentheses:

**Multiline arithmetic expression (BinOp):**
- An `if` statement where the condition is a binary operation (like `+`) split across multiple lines
- The condition should be an expression like `id(0) + 0` with the operator and second operand on a new line
- When the fix is applied, the output should preserve the parentheses: `(\n    id(0)\n    + 0\n)`

**Multiline function call (Call):**
- An `if` statement where the condition is a function call split across multiple lines
- The call should have a name identifier as the function, with at least two integer arguments
- Example pattern: `Call(name, [int, int, ...])`
- When the fix is applied, the output should preserve the call structure

**Existing test cases must be preserved:**
- Walrus operator tests (containing `x := ` patterns)
- Basic function call tests (containing `foo()` patterns)
- `pass` statements in if bodies

The fixture file must remain syntactically valid Python and include all existing test cases plus the new multiline expression cases.
