# Make data-table tables Standard Schema-compatible

## Problem

The `createTable()` function in `packages/data-table/src/lib/table.ts` returns table objects that cannot be used directly with `parse()`/`parseSafe()` from `remix/data-schema`. If you try to pass a table to `parseSafe()`, it fails because the table object does not implement the [Standard Schema](https://standardschema.dev/) interface.

Additionally, write validation logic in `database.ts` (`create`, `update`, etc.) has its own inline validation that duplicates the per-column parsing logic. This inline validation should be refactored into a shared validator that both the write path and the Standard Schema `validate` method can use.

The `data-table` package also re-exports the `DataSchema` type from `data-schema`, which violates the principle that consumers should import types from the package that owns them.

## Expected Behavior

1. Table objects returned by `createTable()` should be Standard Schema-compatible — they should have a `~standard` property with `version`, `vendor`, and a `validate` function
2. The validation semantics should match write-path behavior: partial objects accepted, unknown columns rejected, provided column values parsed through their column schemas
3. Write validation in `database.ts` should use the shared validator from `table.ts` instead of reimplementing it inline
4. The `DataSchema` type should no longer be re-exported from `data-table` — use `Schema` from `data-schema` directly internally
5. The `timestampSchema()` helper should use `createSchema` from `data-schema` instead of manually constructing the `~standard` object

After making the code changes, update the relevant documentation to reflect these changes:
- The project's `AGENTS.md` should be updated to capture the architectural guideline about not re-exporting types across package boundaries
- The `packages/data-table/README.md` should document the new validation behavior and Standard Schema compatibility

## Files to Look At

- `packages/data-table/src/lib/table.ts` — table creation and type definitions
- `packages/data-table/src/lib/database.ts` — write-path validation (create/update helpers)
- `packages/data-table/src/index.ts` — public API exports
- `AGENTS.md` — project-wide agent instructions
- `packages/data-table/README.md` — package documentation
