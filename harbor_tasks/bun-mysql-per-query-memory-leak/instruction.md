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

## Where to Look

Focus on the `deinit()` functions and any code path that reassigns heap-allocated fields. The `ColumnDefinition41` struct has several `Data` fields and a `name_or_index` field (a `ColumnIdentifier`) — all of which hold heap-allocated copies. The `PreparedStatement.Execute` struct manages a dynamically allocated parameter array.

Check whether all heap allocations are properly freed:
1. In cleanup/teardown paths (`deinit`)
2. Before reassignment (when a field is overwritten with a new value, the old value must be freed first)
3. When ownership is transferred or a sentinel value replaces owned data
