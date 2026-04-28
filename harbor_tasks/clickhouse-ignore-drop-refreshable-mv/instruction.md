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

The fix must be implemented in `src/Interpreters/InterpreterDropQuery.cpp`, in the code path that handles `DROP TABLE` statements.

Before the existing check for `ignore_drop_queries_probability`, the code must determine whether the table being dropped is a refreshable materialized view. If the table is a refreshable materialized view, the `DROP TABLE` statement must NOT be converted to `TRUNCATE TABLE` — the DROP must proceed normally so the periodic refresh task is properly stopped.

Relevant ClickHouse source references to consult:
- Refreshable materialized view storage: https://github.com/ClickHouse/ClickHouse/blob/master/src/Storages/StorageMaterializedView.h
- DROP query interpreter: https://github.com/ClickHouse/ClickHouse/blob/master/src/Interpreters/InterpreterDropQuery.cpp

Include a comment in the code explaining why refreshable views need special handling — specifically, that `TRUNCATE` does not stop the periodic refresh task, which would leave orphaned views consuming background pool threads.

## Agent Configuration Rules

When implementing this fix, follow these rules from the repository's agent configuration:

- Use Allman-style braces (opening brace on a new line)
- Write function names as `f` instead of `f()` when referring to the function itself
- Wrap literal names from ClickHouse SQL language, classes, and functions inside inline code blocks
- When mentioning logical errors, say "exception" instead of "crash"
- Never use sleep in C++ code to fix race conditions
- Use `tmp` subdirectory in the current directory for temporary files, not `/tmp`
