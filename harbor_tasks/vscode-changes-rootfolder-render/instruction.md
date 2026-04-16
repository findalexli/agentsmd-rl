# Task: Fix ruff Python Parser Crate

The ruff repository's Python parser crate (`crates/ruff_python_parser`) has code quality issues that cause failures in standard Rust tooling.

## What to Fix

After cloning the repository, the following commands fail on the parser crate:

1. `cargo fmt --all --check` — reports formatting issues
2. `cargo clippy -p ruff_python_parser -- -D warnings` — reports clippy warnings
3. `cargo check -p ruff_python_parser` — fails to compile

Additionally, `crates/ruff_python_parser/src/lib.rs` contains code patterns that should not be present:
- The string `badly_formatted` must not appear in the file
- The string `let unused=1` must not appear in the file

## Goal

Make all three commands pass (exit code 0) and ensure the above strings are absent from the file.

## Verification

Run these commands to verify the fix:
- `cargo fmt --all --check`
- `cargo clippy -p ruff_python_parser -- -D warnings`
- `cargo check -p ruff_python_parser`

And check the file content:
- `grep -q 'badly_formatted' crates/ruff_python_parser/src/lib.rs && echo "FAIL" || echo "PASS"`
- `grep -q 'let unused=1' crates/ruff_python_parser/src/lib.rs && echo "FAIL" || echo "PASS"`
