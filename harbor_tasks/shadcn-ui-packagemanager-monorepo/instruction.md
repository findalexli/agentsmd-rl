# Fix packageManager Field Handling for Monorepos

The shadcn CLI's template adaptation code has a bug in how it handles the `packageManager` field in `package.json` when scaffolding projects.

## The Problem

The current implementation unconditionally deletes the `packageManager` field from `package.json` during scaffolding. This breaks **monorepo templates** that use Turbo, which requires this field to be present with the correct package manager and version.

The expected behavior is:
- **Monorepo templates** (templates that use Turbo): The `packageManager` field should be present and set to the detected package manager version
- **Regular (non-monorepo) templates**: The `packageManager` field should not be present

## Verification

The scaffold tests (`packages/shadcn/src/utils/scaffold.test.ts`) verify:
- Monorepo with bun sets `packageManager` to the detected bun version (e.g., `bun@1.2.0`)
- Monorepo with npm sets `packageManager` to the detected npm version
- Monorepo with yarn sets `packageManager` to the detected yarn version
- Falls back to wildcard (`*`) if version detection fails
- Non-monorepo projects do not have `packageManager` field

## Implementation Requirements

The file `packages/shadcn/src/templates/create-template.ts` must be updated to pass the scaffold tests. Specifically:

1. The implementation must detect what package manager is in use (npm, yarn, pnpm, or bun)

2. For monorepo templates, the `packageManager` field must be set in the format `<manager>@<version>` (e.g., `bun@1.2.0`)

3. If version detection fails for a monorepo, the field should fallback to `<manager>@*` format

4. For non-monorepo templates, the `packageManager` field must be deleted

5. Any comment referencing the old behavior (stripping/removing packageManager) should be updated to reflect the new behavior

The scaffold tests validate that the implementation produces the correct results for all package managers and template types.