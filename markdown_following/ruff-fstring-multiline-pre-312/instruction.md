# Avoid emitting multi-line f-string elements before Python 3.12

## Problem

When running `ruff format` with `--target-version` set to Python 3.11 or earlier, the formatter can emit non-triple-quoted f-strings with replacement fields that span multiple lines. This is invalid syntax before Python 3.12 — PEP 701 (which allows multi-line f-string expressions) was only introduced in Python 3.12.

For example, a compact f-string like:
```python
if f"aaaaaaaaaaa {[ttttteeeeeeeeest,]} more {aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}":
    pass
```

gets formatted to something like:
```python
if f"aaaaaaaaaaa {
    [
        ttttteeeeeeeeest,
    ]
} more {aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}":
    pass
```

which is a syntax error on Python 3.10 or 3.11.

## Expected Behavior

When targeting Python versions before 3.12, the formatter should keep originally-flat replacement fields flat in non-triple-quoted f-strings. Replacement fields that are already multiline in the source should be preserved as-is. Triple-quoted f-strings and Python 3.12+ targets should continue to allow multiline expansion.

Specifically:
- **Pre-3.12 with flat fields**: A compact list inside braces like `{[ttttteeeeeeeeest]}` must remain inline (must NOT expand to `{\n    [`)
- **Pre-3.12 with already-multiline fields**: If the source already contains a multiline replacement field (e.g., `{\n    aaa...\n}`), that multiline field is preserved, but other originally-flat fields in the same f-string must still stay flat
- **Python 3.12+**: Multiline expansion is allowed (PEP 701), so fields may be expanded

## Files to Modify

- `crates/ruff_python_formatter/src/other/interpolated_string_element.rs` — handles formatting of f-string replacement field elements, including the multiline expansion decision

## Code Quality Requirements

Per the repository's AGENTS.md guidelines, the modified file must not use `.unwrap()`, `panic!`, or `unreachable!` in production code (these patterns are allowed only in test code marked with `#[cfg(test)]`).

The solution must also pass `cargo clippy -p ruff_python_formatter -- -D warnings` and `cargo fmt --all --check`.
