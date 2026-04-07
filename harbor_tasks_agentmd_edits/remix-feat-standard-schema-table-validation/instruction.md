# Standard Schema Table Validation for data-table

## Problem

The `data-table` package's `createTable()` results are not [Standard Schema](https://standardschema.dev/)-compatible. This means tables cannot be passed directly to `parse()` or `parseSafe()` from `remix/data-schema`, forcing users to manually validate data before writes rather than using the same schema infrastructure they already use elsewhere.

Additionally, the `data-table` package was re-exporting the `DataSchema` type from its own package instead of having consumers import directly from the owning `data-schema` package, which goes against the monorepo's architectural guidelines.

## Expected Behavior

After the fix:
1. Tables should be Standard Schema-compatible so they work with `parseSafe()` from `remix/data-schema`
2. Table validation should accept partial objects, reject unknown columns, and parse provided values through each column's schema
3. The `DataSchema` type should be removed from data-table's exports — consumers should import `Schema` directly from `data-schema`
4. Write-path validation in the database helper should route through the shared table validator for consistency

## Files to Look At

- `packages/data-table/src/lib/table.ts` — Table creation, metadata, and the new Standard Schema `~standard` property
- `packages/data-table/src/lib/database.ts` — Database helper that uses table validation for write operations
- `packages/data-table/src/index.ts` — Public API exports
- `AGENTS.md` — Monorepo architecture rules (update to document the cross-package boundary guideline)
- `packages/data-table/README.md` — Package documentation (update to document the new validation behavior)

## Notes

After implementing the code changes, update the relevant documentation:
- The project's `AGENTS.md` should document the cross-package boundary rule about avoiding re-exports
- The `data-table` README should document the data validation behavior and Standard Schema compatibility
