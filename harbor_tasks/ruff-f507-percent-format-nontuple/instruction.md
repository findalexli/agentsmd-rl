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

## Test Cases

### Must trigger F507 (fail-to-pass)

- `'%s %s' % 42` → 1 F507
- `'%s %s %s' % 99` → 1 F507
- `'%s %s' % 0` → 1 F507
- `'%s %s %s' % "hello"` → 1 F507
- `'%s %s' % f"hello {name}"` → 1 F507 (f-string literal)
- `'%s %s' % b"hello"` → 1 F507 (bytes literal)
- `'%s %s' % True` → 1 F507
- `'%s %s %s' % None` → 1 F507
- `'%s %s' % 3.14` → 1 F507
- `'%s %s' % ...` → 1 F507
- `'%s %s' % -1` → at least 1 F507 (unary op)
- `'%s %s' % (1 + 2)` → at least 1 F507 (binary op)
- `'%s %s' % (not x)` → at least 1 F507
- `'%s %s' % ("a" + "b")` → at least 1 F507

### Must NOT trigger F507 (pass-to-pass)

- `'%s %s' % banana` where `banana = (1, 2)` → 0 F507
- `'%s %s' % obj.attr` → 0 F507
- `'%s %s' % get_args()` → 0 F507
- `'%s %s' % arr[0]` → 0 F507
- `'%s' % 42`, `'%s' % "hello"`, `'%s' % True`, `'%s' % 3.14` → 0 F507 (single placeholder)
- Existing tuple mismatches still fire: `'%s %s' % (1,)` → 1 F507

## Implementation Constraints

The implementation must:

- Modify `crates/ruff_linter/src/rules/pyflakes/rules/strings.rs` — specifically the function `percent_format_positional_count_mismatch`
- Not use `panic!` or `.unwrap()` in the modified code
- Not contain local `use` statements inside the modified function
- Not use `unreachable!` macro in the modified function
- Prefer `#[expect()]` over `#[allow()]` for lint suppression
- Pass `cargo fmt --all --check`
- Pass `cargo clippy --package ruff_linter --all-targets`
- Pass `cargo test -p ruff_linter -- rule_percentformat`

## Files

- Test fixture: `crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py`
- Snapshot: `crates/ruff_linter/src/rules/pyflakes/snapshots/ruff_linter__rules__pyflakes__tests__F507_F50x.py.snap`

Note: Only the Rust implementation needs to be changed. The test fixture and snapshot will update automatically when the implementation is correct.