# F507 misses %-format strings with zero placeholders

## Bug Description

The `F507` rule (`percent-format-positional-count-mismatch`) fails to flag %-format expressions where the format string contains **no placeholders at all**. For example:

```python
'hello' % 42           # should be flagged — no placeholders, but RHS is non-empty
'' % banana            # should be flagged
'hello' % unknown_var  # should be flagged
'hello' % get_value()  # should be flagged
'hello' % obj.attr     # should be flagged
```

All of these will raise `TypeError` at runtime because the format string expects 0 positional arguments but 1 substitution is provided. The only valid case for a zero-placeholder format string is an empty tuple `()` on the RHS (which succeeds at runtime as a no-op).

Currently, the `percent_format_positional_count_mismatch` function in `crates/ruff_linter/src/rules/pyflakes/rules/strings.rs` only handles the case where `summary.num_positional > 0`. The zero-placeholder case falls through silently regardless of what the RHS is.

## Expected Behavior

When the format string has zero placeholders (`summary.num_positional == 0`), F507 should flag any RHS expression that isn't an empty tuple literal. This catches the vast majority of bugs where a developer writes `'some string' % value` forgetting that the string has no format specifiers.

## Relevant Files

- `crates/ruff_linter/src/rules/pyflakes/rules/strings.rs` — the `percent_format_positional_count_mismatch` function
- `crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py` — test fixtures
- `crates/ruff_linter/src/rules/pyflakes/mod.rs` — test definitions
