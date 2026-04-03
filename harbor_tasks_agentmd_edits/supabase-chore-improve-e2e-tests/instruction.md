# Improve E2E clipboard assertions and remove brittle timeouts

## Problem

The Studio E2E tests (`e2e/studio/features/`) use a brittle pattern for clipboard assertions: they call `navigator.clipboard.readText()` directly and rely on `waitForTimeout(500)` to wait for the clipboard to be populated. This makes tests:

- **Flaky** — the 500ms timeout may not be enough on slow CI runners
- **Slow** — the fixed timeout always waits the full duration even when the clipboard is ready sooner

The affected spec files include `database.spec.ts`, `sql-editor.spec.ts`, `storage.spec.ts`, and `table-editor.spec.ts`. Each has multiple instances of this pattern.

Additionally, `e2e/studio/utils/storage-helpers.ts` has a `waitForTimeout(15_000)` in `uploadFile` that waits a fixed 15 seconds for file uploads instead of using proper Playwright assertions.

## Expected Behavior

1. **Create a reusable clipboard assertion utility** in `e2e/studio/utils/` that uses Playwright's built-in retry mechanism (e.g., `expect().toPass()`) instead of hard-coded timeouts. The utility should support both exact matching and substring containment.

2. **Migrate all spec files** to use the new utility instead of directly calling `navigator.clipboard.readText()` with `waitForTimeout`.

3. **Fix the upload helper** in `storage-helpers.ts` to use Playwright assertions instead of a 15-second timeout.

4. After making the code changes, **update the project's testing rules** (`.cursor/rules/testing/e2e-studio/RULE.md`) to document the new clipboard assertion utility and remove the outdated guidance that showed clipboard timeouts as an acceptable pattern.

## Files to Look At

- `e2e/studio/features/database.spec.ts` — clipboard read with timeout in table copy tests
- `e2e/studio/features/sql-editor.spec.ts` — clipboard read with timeout in export tests
- `e2e/studio/features/storage.spec.ts` — clipboard read with timeout in URL copy tests
- `e2e/studio/features/table-editor.spec.ts` — clipboard read with timeout in copy name/schema tests
- `e2e/studio/utils/storage-helpers.ts` — 15-second upload timeout
- `.cursor/rules/testing/e2e-studio/RULE.md` — testing best practices documentation
