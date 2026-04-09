# Remove eslint-disable comments for no-restricted-imports in create-cloudflare

## Problem

The `packages/create-cloudflare` package has several `// eslint-disable-next-line no-restricted-imports` comments suppressing ESLint warnings. These comments were added as a workaround but should be properly resolved. The ESLint rule `no-restricted-imports` is configured to flag direct imports of `expect` from `vitest` in helper/utility files — the intent is that only test files should import `expect` directly.

Currently these comments appear in:
- Two e2e helper files (`framework-helpers.ts`, `workers-helpers.ts`) that import and use `expect` from vitest
- A mock utility file (`mocks.ts`) that imports and uses `expect.fail()` from vitest
- A vitest matcher extension file (`to-exist.ts`) that imports `expect` to extend it with custom matchers

## Expected Behavior

- All *removable* `// eslint-disable-next-line no-restricted-imports` comments should be eliminated by refactoring the code so the restricted import is no longer needed
- Where the comment genuinely cannot be removed (because the restricted import is required by design), add a justification after `--` explaining why the exception is necessary
- All call sites in the e2e test files must be updated to match any function signature changes

## Files to Look At

- `packages/create-cloudflare/e2e/helpers/framework-helpers.ts` — E2E test helpers with restricted vitest import
- `packages/create-cloudflare/e2e/helpers/workers-helpers.ts` — Worker test helpers with restricted vitest import
- `packages/create-cloudflare/e2e/helpers/to-exist.ts` — Custom vitest matcher extension
- `packages/create-cloudflare/src/helpers/__tests__/mocks.ts` — Mock utilities using `expect.fail()`
- `packages/create-cloudflare/e2e/tests/frameworks/frameworks.test.ts` — Framework e2e tests (call sites)
- `packages/create-cloudflare/e2e/tests/workers/workers.test.ts` — Worker e2e tests (call sites)
