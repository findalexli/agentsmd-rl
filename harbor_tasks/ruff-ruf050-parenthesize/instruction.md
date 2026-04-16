# Fix RUF050 parenthesization of multiline expressions

## Bug Description

The RUF050 rule (`unnecessary-if`) rewrites empty `if` statements like `if cond: pass` into just the condition expression when the condition has side effects. However, the auto-fix does not correctly handle multiline expressions that need parentheses to remain valid as standalone expression statements.

For example:

```python
if (
    id(0)
    + 0
):
    pass
```

The current fixer extracts just the inner expression without ensuring it has parentheses, potentially producing invalid Python where continuation lines become incorrectly indented statements.

## Required Changes

### 1. Rust Implementation (RUF050 rule)

Modify the RUF050 rule implementation to detect when an `if` condition is a multiline expression and ensure it is properly parenthesized when extracted as a standalone expression statement.

The fix must preserve existing handling for walrus operators (named expressions like `(x := foo())`), which already requires parentheses. The solution must not break existing walrus operator support.

The following literal strings must be present in the modified Rust source code:
- `parenthesized_range` - for tracking existing parentheses in the condition
- `has_top_level_line_break` - for detecting multiline expressions at the top level
- `condition_as_expression` - for the expression output function
- `line_break` or `multiline` or `multi_line` - for identifying expressions spanning multiple lines
- `needs_parens` or `nesting` or `spans_multiple` - for determining when parentheses are required
- `is_named_expr` - for preserving walrus operator handling
- `format!` with `"({}` - the format string pattern used for parenthesizing expressions
- `unnecessary_if` - the rule module name
- `StmtIf` - the AST node type for if statements
- `has_side_effects` - for checking if condition has side effects
- `Edit` - for creating code edits
- `Fix` - for creating fixes

### 2. Test Cases (RUF050.py fixture)

Add test cases to the RUF050.py fixture file covering multiline expressions that need parentheses:

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
