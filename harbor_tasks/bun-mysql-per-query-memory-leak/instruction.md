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

The fix should prevent RSS growth during repeated query execution.

**ColumnDefinition41.zig**: The `ColumnDefinition41` struct holds multiple owned string fields (`catalog`, `schema`, `table`, `org_table`, `name`, `org_name`) and a `name_or_index` field of type `ColumnIdentifier`. When the struct is reused or discarded, all owned heap memory must be explicitly released. Additionally, when `name_or_index` is reassigned during decoding, any previously held memory is leaked.

**PreparedStatement.zig**: The `Execute` struct holds a params slice. Its cleanup method iterates over and releases each param element, but the slice allocation itself is never freed.

**MySQLStatement.zig**: In `checkForDuplicateFields()`, when a duplicate column is detected, the `name_or_index` field is overwritten with `.duplicate` without releasing the memory previously held by that field.

**MySQLConnection.zig**: `ColumnDefinition41` arrays are allocated but the array elements are not initialized to a defined state before use.

## Verification

After 5,000 queries on a 50-column table, RSS should remain stable instead of growing by ~17 MB. All heap allocations must have corresponding deallocation during cleanup.