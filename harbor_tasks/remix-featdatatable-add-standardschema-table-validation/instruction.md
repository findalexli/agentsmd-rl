# Make data-table tables Standard Schema-compatible

## Problem

The `createTable()` function in `packages/data-table/src/lib/table.ts` returns table objects that cannot be used directly with `parse()`/`parseSafe()` from `remix/data-schema`. If you try to pass a table to `parseSafe()`, it fails because the table object does not implement the [Standard Schema](https://standardschema.dev/) interface.

Additionally, write validation logic in `database.ts` (`create`, `update`, etc.) has its own inline validation that duplicates the per-column parsing logic. This inline validation should be refactored into a shared validator function named `validatePartialRow` that both the write path and the Standard Schema `validate` method can use. The `validatePartialRow` function should accept a table and a partial row object, and return a result where validation failures are indicated by the presence of an `issues` key in the result.

The `data-table` package also re-exports the `DataSchema` type from `data-schema`, which violates the principle that consumers should import types from the package that owns them.

## Expected Behavior

1. Table objects returned by `createTable()` should be Standard Schema-compatible — they should have a `~standard` property with `version`, `vendor`, and a `validate` function
2. The validation semantics should match write-path behavior: partial objects accepted, unknown columns rejected, provided column values parsed through their column schemas
3. Export a function named `validatePartialRow` from `table.ts` that accepts a table and a partial row object. Valid inputs should produce a result without an `issues` key; invalid inputs (e.g., unknown columns) should produce a result with an `issues` key.
4. Write validation in `database.ts` should import and use `validatePartialRow` from `./table.ts` instead of reimplementing validation inline
5. The `DataSchema` type should no longer be re-exported from `data-table`'s public API — use `Schema` from `data-schema` directly internally
6. The `timestampSchema()` helper should import and use `createSchema` from `@remix-run/data-schema` instead of manually constructing the `~standard` object

After making the code changes, update the relevant documentation:

- `AGENTS.md`: add a guideline about cross-package boundaries, advising against re-exporting types from other packages and instead importing them directly from the owning package
- `packages/data-table/README.md`: document Standard Schema compatibility, explain that `parseSafe`/`parse` can be used with table objects, note that partial objects are accepted, and that unknown columns are rejected

## Files to Look At

- `packages/data-table/src/lib/table.ts` — table creation and type definitions
- `packages/data-table/src/lib/database.ts` — write-path validation (create/update helpers)
- `packages/data-table/src/index.ts` — public API exports
- `AGENTS.md` — project-wide agent instructions
- `packages/data-table/README.md` — package documentation
