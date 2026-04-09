# Remove eslint-disable comments for no-restricted-imports in create-cloudflare

## Problem

The `packages/create-cloudflare` package has several `// eslint-disable-next-line no-restricted-imports` comments that suppress warnings about importing `expect` directly from `vitest`. These comments exist in e2e test helpers and a mock utility file. The ESLint rule `no-restricted-imports` is configured to prevent direct imports of `expect` from vitest in helper/utility files (as opposed to test files where vitest provides `expect` via the test context).

Most of these eslint-disable comments can be eliminated by refactoring the code so that the restricted import is no longer needed. In one case (`to-exist.ts`), the import is genuinely required and the comment should remain but with a justification explaining why.

## Expected Behavior

- All *removable* `// eslint-disable-next-line no-restricted-imports` comments should be eliminated from the create-cloudflare package
- Where the comment cannot be removed (because the import is genuinely needed), add a justification after `--` explaining why
- Helper functions that previously imported `expect` directly should be refactored to receive it from their callers instead
- The mock utility file (`mocks.ts`) should not depend on `expect` from vitest at all — find an alternative for `expect.fail()`

## Files to Look At

- `packages/create-cloudflare/e2e/helpers/framework-helpers.ts` — E2E framework test helpers that import `expect` from vitest
- `packages/create-cloudflare/e2e/helpers/workers-helpers.ts` — E2E worker test helpers that import `expect` from vitest
- `packages/create-cloudflare/e2e/helpers/to-exist.ts` — Custom vitest matcher that needs the `expect` import to extend it
- `packages/create-cloudflare/src/helpers/__tests__/mocks.ts` — Mock utilities that use `expect.fail()` for validation
- `packages/create-cloudflare/e2e/tests/frameworks/frameworks.test.ts` — Framework test file that calls the helper functions
- `packages/create-cloudflare/e2e/tests/workers/workers.test.ts` — Worker test file that calls the helper functions
