# MariaDB Adapter Precision Loss

## Problem

The MariaDB adapter in `packages/adapter-mariadb/src/mariadb.ts` loses precision when handling large decimal values. When performing operations on `Decimal` fields with large values (e.g., `5000000000000000000000000000`), the values become corrupted during database operations.

## Symptoms

- Large decimal values are incorrectly stored/retrieved from MariaDB
- Precision is lost even when using `Decimal` type with explicit precision (`@db.Decimal(30, 0)`)
- The issue affects both reads and writes of large decimal values

## Technical Details

The `performIO` method in the `MariaDbQueryable` class handles query execution. Transaction operations use a different code path that is unaffected.

The MariaDB driver supports two protocols for query execution: a text-based protocol and a binary protocol. The current implementation uses one of these protocols, which causes precision loss for large decimal values when exchanging data with the database.

## Relevant Files

- `packages/adapter-mariadb/src/mariadb.ts` - Main adapter implementation
  - The `MariaDbQueryable` class handles query execution via the `performIO` method
  - The `MariaDbTransaction` class handles transaction operations

## Constraints

- Follow the coding conventions in `AGENTS.md` (no unnecessary inline comments)
- The adapter must continue to work with the existing test suite
- `pnpm eslint src/ --max-warnings=0` must pass in the adapter package
- The error-mapping tests in `src/errors.test.ts` must pass