# Memory Leak in MySQL Adapter — Per-Query Allocation Growth

## Problem

The `bun:sql` MySQL adapter leaks native (Zig) memory on every query execution. The JavaScript heap remains stable, but RSS grows monotonically until the process is killed by the OOM killer on Linux. This happens with any query pattern — simple SELECTs, parameterized queries, wide tables — and is proportional to the number of columns and query executions.

## Symptoms

- RSS grows ~3.5 KB per column per query execution (e.g., a 50-column table leaks ~175 KB per query)
- After 5,000 queries on a 50-column table, RSS grows by ~17 MB
- `Bun.gc(true)` does not reclaim the leaked memory (it's native, not JS heap)
- The leak occurs with prepared statement re-execution (same query run multiple times)

## Relevant Files

The MySQL protocol implementation lives in:

- `src/sql/mysql/protocol/ColumnDefinition41.zig` — Column definition decoding and cleanup
- `src/sql/mysql/protocol/PreparedStatement.zig` — Prepared statement execution and parameter handling
- `src/sql/mysql/MySQLStatement.zig` — Statement-level logic including duplicate field detection
- `src/sql/mysql/MySQLConnection.zig` — Connection-level result set and statement handling

## Required Behavior

The fix should prevent RSS growth during repeated query execution. To achieve this:

1. **ColumnDefinition41.zig**: The `ColumnDefinition41` struct contains several `Data` fields (`catalog`, `schema`, `table`, `org_table`, `name`, `org_name`) and a `name_or_index` field (of type `ColumnIdentifier`). All owned heap memory must be freed when `deinit()` is called. Additionally, when `decodeInternal()` assigns a new value to `name_or_index`, any previously owned memory must be freed first.

2. **PreparedStatement.zig**: The `Execute` struct has a `deinit()` method and a `params` field (a slice). The `params` slice array itself must be freed (not just the individual items within it).

3. **MySQLStatement.zig**: In `checkForDuplicateFields()`, when a column's `name_or_index` field is overwritten, any previously owned memory must be freed before the assignment.

4. **MySQLConnection.zig**: `ColumnDefinition41` arrays allocated with `bun.default_allocator.alloc()` must be properly initialized before use to prevent undefined behavior with partially-initialized structures.

## Verification

After 5,000 queries on a 50-column table, RSS should remain stable instead of growing by ~17 MB. All heap allocations should have corresponding deallocation during cleanup.
