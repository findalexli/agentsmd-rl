# Fix DROP handling for refreshable materialized views in ClickHouse

## Problem

When the `ignore_drop_queries_probability` setting is active in ClickHouse stress tests, `DROP TABLE` queries may be randomly converted to `TRUNCATE TABLE`. However, for **refreshable materialized views**, this conversion causes a serious issue:

- `TRUNCATE TABLE` does not stop the periodic refresh task of a refreshable materialized view
- The view continues refreshing indefinitely in the background
- This consumes background pool threads and can progressively overwhelm the server
- Under TSan (ThreadSanitizer), where operations are 5–15× slower, this leads to complete server unresponsiveness

## Observed Behavior

When a refreshable materialized view is dropped while `ignore_drop_queries_probability` is non-zero, the query is converted to TRUNCATE instead of DROP. This leaves the refresh task running, causing resource exhaustion and server unresponsiveness.

## Expected Fix

The DROP-to-TRUNCATE conversion must be suppressed for refreshable materialized views. The fix must ensure that:

1. Regular tables: DROP may still be converted to TRUNCATE based on the probability setting
2. Refreshable materialized views: DROP is never converted to TRUNCATE, ensuring the refresh task is properly stopped

## What the Tests Check

The automated tests verify the fix by checking for the presence of:

- The `StorageMaterializedView` header include directive (`#include <Storages/StorageMaterializedView.h>`)
- A comment with the text `TRUNCATE` and `refresh` explaining the rationale
- Logic to detect whether a table is a refreshable materialized view
- The condition controlling the DROP-to-TRUNCATE conversion excludes refreshable views

## Implementation Location

The relevant source file is `src/Interpreters/InterpreterDropQuery.cpp` in the `executeToTableImpl()` method.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `mypy (Python type checker)`
