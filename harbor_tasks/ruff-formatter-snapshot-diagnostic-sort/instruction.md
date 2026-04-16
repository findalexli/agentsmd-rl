# Sort formatter diagnostics in snapshots

## Problem

The formatter's snapshot tests for unsupported syntax errors produce non-deterministic output. Errors appear in different orders across test runs due to unsorted collection iteration, causing spurious snapshot diffs that don't reflect actual behavioral changes.

You can observe this in the snapshot file `crates/ruff_python_formatter/tests/snapshots/format@expression__nested_string_quote_style.py.snap`, where the "Unsupported Syntax Errors" sections list errors in an order that doesn't correspond to their source locations (e.g., errors on line 30 appear before errors on line 28).

## Expected Behavior

1. **Sorted error output**: Errors in the snapshot output must appear in a stable, deterministic order — sorted by their source location (line number, then column). This prevents churn in snapshot files when underlying data structure internals change.

2. **Implementation requirements**: When modifying the test code in `crates/ruff_python_formatter/tests/fixtures.rs` to achieve sorted output, your changes must satisfy these constraints:
   - The sorting logic must use a `.sort*`, `.sort_by`, or `.sort_by_key` method call
   - If the code iterates over `formatted_unsupported_syntax_errors` using `.values().map()`, the resulting `diagnostics` collection must be sorted afterward
   - No `panic!` or `.unwrap()` calls in the sorting/error-processing section
   - No local `use` statements (local imports) inside the modified function

3. **Snapshot update**: The snapshot file `crates/ruff_python_formatter/tests/snapshots/format@expression__nested_string_quote_style.py.snap` must be updated to reflect the new sorted order, with errors appearing in ascending order by line number within each "Unsupported Syntax Errors" section.

## Files to Look At

- `crates/ruff_python_formatter/tests/fixtures.rs` — test fixture code that processes `formatted_unsupported_syntax_errors` and generates diagnostics
- `crates/ruff_python_formatter/tests/snapshots/format@expression__nested_string_quote_style.py.snap` — the snapshot file that needs its error sections updated to reflect sorted order
