# Remove Driver Type Re-exports from Data-Table Adapters

## Problem

The `data-table-mysql`, `data-table-postgres`, and `data-table-sqlite` adapter packages each define and publicly export their own "driver-shaped" types (`MysqlDatabasePool`, `MysqlDatabaseConnection`, `PostgresDatabasePool`, `PostgresDatabaseClient`, `SqliteDatabaseConnection`, etc.). These types duplicate the shapes already provided by the underlying driver packages (`mysql2/promise`, `pg`, `better-sqlite3`), adding an unnecessary API layer that consumers must navigate.

This also violates the repo's cross-package boundary convention: consumers should import types from the owning package directly rather than through re-exports.

## Expected Behavior

Each adapter should:

1. **Remove the public driver-type re-exports** from its `src/index.ts` entry point. Only the adapter-owned types (like `MysqlDatabaseAdapterOptions`) and the adapter class/factory should be exported.
2. **Use the concrete driver types directly** inside the adapter implementation (e.g., import `Pool` and `PoolConnection` from `mysql2/promise` rather than defining custom `MysqlDatabasePool` and `MysqlDatabaseConnection` interfaces).
3. **Add proper type guards** where needed — for example, the MySQL adapter needs to distinguish pool connections from plain connections to safely call `release()`.

After making the code changes, update the relevant package READMEs to reflect the new public API surface. Users who previously imported driver-shaped types from the adapter packages need to know where to get those types now.

## Files to Look At

- `packages/data-table-mysql/src/index.ts` — public API entry point
- `packages/data-table-mysql/src/lib/adapter.ts` — adapter implementation with driver types
- `packages/data-table-postgres/src/index.ts` — public API entry point
- `packages/data-table-postgres/src/lib/adapter.ts` — adapter implementation with driver types
- `packages/data-table-sqlite/src/index.ts` — public API entry point
- `packages/data-table-sqlite/src/lib/adapter.ts` — adapter implementation with driver types
- `packages/data-table-mysql/README.md` — package documentation
- `packages/data-table-postgres/README.md` — package documentation
- `packages/data-table-sqlite/README.md` — package documentation
