# Make data-table tables Standard Schema-compatible

## Problem

The `createTable()` function in `packages/data-table/src/lib/table.ts` produces table objects that cannot be passed to `parseSafe()` from `remix/data-schema` — it fails with an error indicating the table object lacks the interface that `parseSafe()` expects. Additionally, the write validation in `database.ts` (the `create`, `update`, and similar helpers) contains inline validation logic that duplicates the per-column parsing already available through the table's column schemas. This duplication means the two validation paths can disagree: one accepts a partial object while the other rejects it.

## Symptom Description

**Standard Schema incompatibility**: When a table created with `createTable()` is passed to `parseSafe()`, it fails. The error indicates the table object does not conform to the Standard Schema interface. The same table can be used to define columns, but the table object itself cannot be parsed or validated by Standard Schema tools.

**Validation inconsistency**: Write-path helpers (create, update, etc.) validate inputs using inline logic. If you call the Standard Schema `validate` method on the same table, it may produce different results for equivalent inputs — for example, the write path may accept a partial object while the schema validator rejects it.

**DataSchema re-export**: The `data-table` package re-exports the `DataSchema` type from `data-schema` in its public API. Consumers should import types from the package that owns them, not from a re-exporting intermediary.

## Expected Behavior

1. Table objects returned by `createTable()` should work with `parseSafe()` / `parse()` from `remix/data-schema`. This means the table object must implement the Standard Schema interface (see https://standardschema.dev/ for the spec). In practice, this requires a `~standard` property containing at least a `version` field (integer) and a `validate` function.

2. The validation semantics must be consistent between the write path and the Standard Schema `validate` method: partial objects (omitting non-required columns) should be accepted by both; unknown columns (columns not defined in the table's schema) should be rejected by both; provided values should be parsed through the column schemas in both paths. The shared validation between these two paths should be available through a `validatePartialRow` function exported from `table.ts`.

3. The `timestampSchema()` helper in `table.ts` should use `createSchema` from `@remix-run/data-schema` rather than manually constructing the Standard Schema object structure by hand. This keeps the helper aligned with how other column schemas are built.

4. `DataSchema` must not appear in the public exports of `packages/data-table/src/index.ts`. Types from `data-schema` should be imported directly from `data-schema` inside the `data-table` package, not re-exported through `data-table`'s public API.

5. After making code changes, update the following documentation:
   - **AGENTS.md**: Add a guideline about cross-package boundaries. The rule should state that re-exporting types from other packages should be avoided, and that types should be imported directly from the owning package.
   - **packages/data-table/README.md**: Document Standard Schema compatibility. Explain that `parseSafe` / `parse` from `remix/data-schema` can be used with table objects. Explain that partial objects are accepted (non-required columns may be omitted) and that unknown columns are rejected.

## Code Style Requirements

This project uses ESLint for linting and Prettier for formatting. Run `pnpm lint` to check for lint errors and `pnpm format:check` to verify formatting before submitting any changes.

## File Locations

- `packages/data-table/src/lib/table.ts` — contains `createTable()` and `timestampSchema()`
- `packages/data-table/src/lib/database.ts` — contains write-path helpers (create, update, etc.)
- `packages/data-table/src/index.ts` — public API surface
- `AGENTS.md` — project-wide agent guidelines
- `packages/data-table/README.md` — package documentation