# Standard Schema Table Validation for data-table

## Problem

The `data-table` package's `createTable()` results are not [Standard Schema](https://standardschema.dev/)-compatible. Tables cannot be passed directly to `parse()` or `parseSafe()` from `@remix-run/data-schema`, forcing users to manually validate data before writes rather than using the same schema infrastructure they use elsewhere.

Additionally, the `data-table` package defines and exports its own `DataSchema` type instead of using the canonical `Schema` type from the owning `data-schema` package, which goes against the monorepo's architectural guidelines for cross-package boundaries.

## Expected Behavior

After the fix:

1. **Standard Schema compatibility**: Table objects returned by `createTable()` must implement the [Standard Schema](https://standardschema.dev/) protocol. Tables must expose a `~standard` property containing a `validate(value: unknown)` function that returns:
   - `{ value: T }` for valid input
   - `{ issues: ReadonlyArray<{ message: string, path?: string[] }> }` for invalid input

2. **Validation behavior**: The `validate` function must enforce these rules:
   - Partial objects are accepted — only provided columns need to be valid, and their parsed values are returned
   - Empty objects `{}` are valid (no columns required)
   - Unknown columns are rejected — each unknown column produces an issue where `message` includes "Unknown column" and `path` is an array containing the column name (e.g., `["extra"]` for a column named `extra`)
   - Invalid column values are rejected — issues have `path` as an array pointing to the column (e.g., `["id"]`)
   - Non-object values (`null`, arrays) are rejected — the function returns `{ issues: [...] }` rather than `{ value: ... }`
   - All unknown columns should be reported (not just the first one)

3. **parseSafe interop**: `parseSafe` imported from `@remix-run/data-schema` must work directly on table objects, returning `{ success: true, value }` for valid input and `{ success: false, issues }` for invalid input

4. **Existing exports preserved**: The `tableMetadataKey` export must continue to work — accessing `table[tableMetadataKey]` must still return metadata with `name`, `primaryKey`, etc. Column references on the table (e.g., `table.id`) must also remain functional.

5. **Type consistency**: The `data-table` package should use the `Schema` type from `data-schema` rather than defining its own `DataSchema` type.

6. **Write-path consistency**: Database write helpers (`create`, `update`, etc.) must use the same validation semantics as the Standard Schema `validate` function described above.

## Documentation Updates

Update the following documentation:

- `AGENTS.md`: Document the cross-package boundary rule about avoiding re-exports. The file should mention avoiding "re-export" (or "reexport") and reference either "cross-package" boundaries or importing from the "owning package".
- `packages/data-table/README.md`: Add a "Data Validation" section documenting Standard Schema compatibility and that partial objects are allowed.
