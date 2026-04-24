# Memory Leak in MySQL Adapter — Per-Query Allocation Growth

## Problem

The `bun:sql` MySQL adapter leaks native (Zig) memory on every query execution. The JavaScript heap remains stable, but RSS grows monotonically until the process is killed by the OOM killer on Linux. This happens with any query pattern — simple SELECTs, parameterized queries, wide tables — and is proportional to the number of columns and query executions.

## Symptoms

- RSS grows ~3.5 KB per column per query execution (e.g., a 50-column table leaks ~175 KB per query)
- After 5,000 queries on a 50-column table, RSS should remain stable instead of growing by ~17 MB
- `Bun.gc(true)` does not reclaim the leaked memory (it's native, not JS heap)
- The leak occurs with prepared statement re-execution (same query run multiple times)

## Affected Components

The MySQL protocol implementation lives in:
- `src/sql/mysql/protocol/ColumnDefinition41.zig` — Column definition decoding and cleanup
- `src/sql/mysql/protocol/PreparedStatement.zig` — Prepared statement execution and parameter handling
- `src/sql/mysql/MySQLStatement.zig` — Statement-level logic including duplicate field detection
- `src/sql/mysql/MySQLConnection.zig` — Connection-level result set and statement handling

## Required Behavior

When fixing this issue, ensure the following behavioral requirements are met:

1. **ColumnDefinition41 cleanup**: When column definition structures are discarded, all heap memory they own must be released. This includes string data fields and any union-type fields that may hold allocated memory.

2. **Re-decoding safety**: When column definitions are re-decoded (e.g., on prepared statement re-execution), any previously allocated memory for those structures must be freed before new allocations are made.

3. **Duplicate field handling**: When detecting duplicate column names during result set processing, any existing allocated data in the affected fields must be released before those fields are reassigned.

4. **Initialization safety**: When allocating arrays of column definition structures, the elements must be initialized to a known state before use to prevent reading uninitialized memory or double-free issues.

5. **Parameter cleanup**: When cleaning up prepared statement execution parameters, both individual parameter values and the container/slice holding them must be properly freed.

## Verification

After the fix:
- After 5,000 queries on a 50-column table, RSS should remain stable instead of growing by ~17 MB
- All heap allocations made during query execution must have corresponding deallocations during cleanup
- The code must compile successfully with `zig ast-check` or `zig build`
