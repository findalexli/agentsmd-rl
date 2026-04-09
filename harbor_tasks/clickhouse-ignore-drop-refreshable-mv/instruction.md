# Fix DROP Query Handling for Refreshable Materialized Views

## Problem

The `ignore_drop_queries_probability` setting (used in stress tests) converts `DROP TABLE` to `TRUNCATE TABLE`. However, `TRUNCATE` does not stop the periodic refresh task of a refreshable materialized view. This causes the orphaned view to keep refreshing indefinitely, consuming background pool threads and progressively overwhelming the server.

## Symptom

In stress tests with `ignore_drop_queries_probability=0.2`:
1. A refreshable materialized view is created with `REFRESH AFTER N SECONDS`
2. The final `DROP TABLE` gets converted to `TRUNCATE TABLE`
3. The view survives and keeps refreshing periodically
4. Server becomes unresponsive due to accumulated background tasks

## Files to Modify

- `src/Interpreters/InterpreterDropQuery.cpp` - The `executeToTableImpl` function around line 199

## Required Changes

The fix should:

1. Check if the table being dropped is a refreshable materialized view
2. Skip the DROP-to-TRUNCATE conversion for refreshable views
3. Include a comment explaining why this is necessary

The key logic to add:
- Get a pointer to the table and check if it's a `StorageMaterializedView`
- Check if the view is refreshable using `isRefreshable()`
- Add `!is_refreshable_view` to the condition that decides whether to convert DROP to TRUNCATE

## Agent Configuration Rules

When implementing this fix, follow these rules from the repository's agent configuration:

- Use Allman-style braces (opening brace on a new line)
- Write function names as `f` instead of `f()` when referring to the function itself
- Wrap literal names from ClickHouse SQL language, classes, and functions inside inline code blocks
- When mentioning logical errors, say "exception" instead of "crash"
- Never use sleep in C++ code to fix race conditions
- Use `tmp` subdirectory in the current directory for temporary files, not `/tmp`
