# Fix DROP Query Handling for Refreshable Materialized Views

## Problem

The `ignore_drop_queries_probability` setting (used in stress tests) converts `DROP TABLE` to `TRUNCATE TABLE`. However, `TRUNCATE` does not stop the periodic refresh task of a refreshable materialized view. This causes orphaned views to keep refreshing indefinitely, consuming background pool threads and progressively overwhelming the server.

## Symptom

In stress tests with `ignore_drop_queries_probability` set to a non-zero value:
1. A refreshable materialized view is created with `REFRESH AFTER N SECONDS`
2. The final `DROP TABLE` gets converted to `TRUNCATE TABLE`
3. The view survives and keeps refreshing periodically
4. Server becomes unresponsive due to accumulated background tasks

## Requirements

The fix must ensure that when a refreshable materialized view is dropped, the periodic refresh task is properly stopped. This means the `DROP TABLE` statement must not be converted to `TRUNCATE TABLE` for refreshable materialized views.

The implementation must:
1. Detect when the table being dropped is a refreshable materialized view
2. Skip the DROP-to-TRUNCATE conversion for such views
3. Include a comment explaining why the special handling is necessary

## Implementation Notes

- The code modification should be made in the appropriate location where the DROP-to-TRUNCATE conversion decision is made
- The repository uses `dynamic_cast` for type checking in similar situations
- The comment should use backticks to wrap literal SQL and code names (e.g., `` `DROP` ``, `` `TRUNCATE` ``)
- The check should use the `isRefreshable()` method available on materialized view storage objects
- Follow the repository's code style (Allman-style braces, `tmp` subdirectory for temp files, etc.)

## Agent Configuration Rules

When implementing this fix, follow these rules from the repository's agent configuration:

- Use Allman-style braces (opening brace on a new line)
- Write function names as `f` instead of `f()` when referring to the function itself
- Wrap literal names from ClickHouse SQL language, classes, and functions inside inline code blocks
- When mentioning logical errors, say "exception" instead of "crash"
- Never use sleep in C++ code to fix race conditions
- Use `tmp` subdirectory in the current directory for temporary files, not `/tmp`