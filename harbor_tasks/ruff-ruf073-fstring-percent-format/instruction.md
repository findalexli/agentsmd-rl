# Missing lint rule: `%` operator used on f-strings

## Bug Description

Ruff currently has no rule to flag the use of the `%` (modulo/percent-format) operator when the left-hand side is an **f-string**. This is almost always a mistake — f-strings already support interpolation via `{...}` expressions, so applying `%`-formatting on top is redundant and confusing.

For example, none of the following are flagged today:

```python
f"{banana}" % banana
f"hello %s %s" % (1, 2)
f"value: {x}" % {"key": "value"}
f"{'nested'} %s" % 42
f"no placeholders" % banana
```

Existing `F50x` rules only handle plain string literals with `%`-formatting. There is no Ruff rule that catches the case where an f-string is used with `%`.

## Expected Behavior

A new `ruff`-namespace rule should detect when the `%` binary operator has an f-string on its left side and emit a diagnostic. The rule should:

1. Only fire when the LHS of `%` is an f-string (not regular strings, byte strings, or non-string types)
2. Fire regardless of what the RHS is (variable, tuple, dict, literal)
3. Not interfere with existing `F50x` rules for plain string `%`-formatting
4. Be a preview rule (not stable yet)

## Relevant Files

- `crates/ruff_linter/src/checkers/ast/analyze/expression.rs` — where binary-op expressions are dispatched to rule checks
- `crates/ruff_linter/src/codes.rs` — rule code registration
- `crates/ruff_linter/src/rules/ruff/rules/mod.rs` — ruff rules module
- `crates/ruff_linter/src/rules/ruff/mod.rs` — test definitions for ruff rules

Look at neighboring rules in the `ruff` namespace (e.g., `RUF070`–`RUF072`) for the patterns used to register and test new rules.
