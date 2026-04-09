# Sort formatter diagnostics in snapshots

## Problem

The formatter's snapshot tests for unsupported syntax errors produce non-deterministic output. The `ensure_unchanged_ast` function in `crates/ruff_python_formatter/tests/fixtures.rs` iterates over a `HashMap` of unsupported syntax errors when generating diagnostic output, but `HashMap` iteration order is not guaranteed. This means the errors can appear in different orders across runs, causing spurious snapshot diffs when the underlying hash implementation changes.

You can observe this in the snapshot file `crates/ruff_python_formatter/tests/snapshots/format@expression__nested_string_quote_style.py.snap`, where the "Unsupported Syntax Errors" sections list errors in an order that doesn't correspond to their source locations.

## Expected Behavior

Errors in the snapshot output should appear in a stable, deterministic order — sorted by their source location (line number, then column). This prevents churn in snapshot files when hash internals change.

## Files to Look At

- `crates/ruff_python_formatter/tests/fixtures.rs` — the `ensure_unchanged_ast` function that processes `formatted_unsupported_syntax_errors` and generates diagnostics
- `crates/ruff_python_formatter/tests/snapshots/format@expression__nested_string_quote_style.py.snap` — the snapshot file that needs its error sections updated to reflect sorted order
