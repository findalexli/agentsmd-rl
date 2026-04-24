# Fix DROP Query Handling for Refreshable Materialized Views

## Problem

When the `ignore_drop_queries_probability` setting is enabled in stress tests, `DROP TABLE` statements are converted to `TRUNCATE TABLE`. However, for refreshable materialized views, this conversion causes a critical issue: `TRUNCATE` does not stop the periodic refresh task. This leaves orphaned views that continue refreshing indefinitely, consuming background pool threads and eventually overwhelming the server.

## Symptom

In stress tests with `ignore_drop_queries_probability` enabled:
1. A refreshable materialized view is created with `REFRESH AFTER N SECONDS`
2. The `DROP TABLE` statement gets converted to `TRUNCATE TABLE`
3. The view survives and keeps refreshing periodically
4. The server becomes unresponsive due to accumulated background tasks

## Requirements

The fix must ensure that when a refreshable materialized view is being dropped, the `DROP TABLE` statement is NOT converted to `TRUNCATE TABLE`.

The implementation should:
1. Check if the table being dropped is a refreshable materialized view
2. Skip the DROP-to-TRUNCATE conversion for such views
3. Include a comment explaining why refreshable views need special handling

## Agent Configuration Rules

When implementing this fix, follow these rules from the repository's agent configuration:

- Use Allman-style braces (opening brace on a new line)
- Write function names as `f` instead of `f()` when referring to the function itself
- Wrap literal names from ClickHouse SQL language, classes, and functions inside inline code blocks
- When mentioning logical errors, say "exception" instead of "crash"
- Never use sleep in C++ code to fix race conditions
- Use `tmp` subdirectory in the current directory for temporary files, not `/tmp`
