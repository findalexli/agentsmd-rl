# Fix panic in UP012 rule caused by octal escape handling

## Problem

Running `ruff check --select UP012` on Python files containing certain string literals with octal escape sequences causes ruff to panic with a thread crash. For example, checking a file containing `"$IMURAW\0".encode("ascii")` triggers an internal panic.

Additionally, strings that combine octal escapes with named Unicode escapes (like `\N{DIGIT ONE}`) may incorrectly trigger UP012 when they shouldn't.

## Expected Behavior

- `ruff check --select UP012` should never panic regardless of the string contents.
- Strings containing named Unicode escapes (`\N{...}`) should not trigger UP012, since `\N{...}` is not valid in byte literals.
- Octal escape values should be correctly validated against byte range limits.

## Files to Look At

- `crates/ruff_linter/src/rules/pyupgrade/rules/unnecessary_encode_utf8.rs` — the UP012 rule implementation

## Development Guidelines

When modifying the code, follow the conventions in `/workspace/ruff/AGENTS.md`:

1. **Error Handling**: Avoid `panic!()`, `unreachable!()`, and `.unwrap()`. Instead, encode constraints in the type system.
2. **Imports**: Keep all Rust imports at the top of the file, never inside function bodies.

## Repository Quality Standards

All changes must pass the following repo-wide checks:
- `cargo clippy --package ruff_linter --all-targets -- -D warnings` must pass without warnings
- `cargo fmt --check` must pass (code must be properly formatted)
- `cargo check --workspace` must pass (entire workspace must compile)
