# Remove eslint-disable comments for no-restricted-imports in create-cloudflare

## Problem

The `packages/create-cloudflare` package has several `// eslint-disable-next-line no-restricted-imports` comments suppressing ESLint warnings. The ESLint rule `no-restricted-imports` is configured to flag direct value imports of `expect` from `vitest` in helper/utility files — only test files should import `expect` directly.

Currently bare eslint-disable comments appear in:
- `packages/create-cloudflare/e2e/helpers/framework-helpers.ts`
- `packages/create-cloudflare/e2e/helpers/workers-helpers.ts`
- `packages/create-cloudflare/src/helpers/__tests__/mocks.ts`

Additionally, `packages/create-cloudflare/e2e/helpers/to-exist.ts` requires `expect` to be imported from vitest in order to extend it with custom matchers.

## Symptom

The current code in the helper files directly imports `expect` from `vitest` as a value import. This causes ESLint to emit `no-restricted-imports` warnings. The `// eslint-disable-next-line` comments suppress these warnings without resolving the underlying issue.

## Expected Behavior

### eslint-disable comment cleanup
- Three files (`framework-helpers.ts`, `workers-helpers.ts`, `mocks.ts`) must have all bare `// eslint-disable-next-line no-restricted-imports` comments removed entirely. The restricted import itself must also be removed from these files.
- `to-exist.ts` may keep its eslint-disable comment but must add a justification after `--` explaining why the exception is necessary (e.g., `// eslint-disable-next-line no-restricted-imports -- reason here`).

### vitest expect handling in helpers
The following exported async functions must accept `expect` as a typed parameter (e.g., `expect: ExpectStatic`) rather than importing it directly:

**framework-helpers.ts** (8 functions):
- `runC3ForFrameworkTest`
- `verifyDeployment`
- `verifyDevScript`
- `verifyPreviewScript`
- `verifyTypes`
- `verifyCloudflareVitePluginConfigured`
- `testGitCommitMessage`
- `testDeploymentCommitMessage`

**workers-helpers.ts** (2 functions):
- `runC3ForWorkerTest`
- `verifyLocalDev`

The helper files should use a type-only import for `ExpectStatic` from vitest (not a value import).

### mocks.ts validation
In `packages/create-cloudflare/src/helpers/__tests__/mocks.ts`:
- Replace all `expect.fail()` calls with `throw new Error()` calls
- At least 3 `throw new Error()` calls must be present
- Remove the value import of `expect` from vitest (keep `vi` import only)

### Call site updates
The e2e test files that call the refactored helper functions must pass `expect` as an argument:
- `packages/create-cloudflare/e2e/tests/frameworks/frameworks.test.ts` must pass `expect` to `runC3ForFrameworkTest`, `verifyDeployment`, `verifyDevScript`, `verifyPreviewScript`, `verifyTypes`, and `verifyCloudflareVitePluginConfigured`
- `packages/create-cloudflare/e2e/tests/workers/workers.test.ts` must pass `expect` to `runC3ForWorkerTest` and `verifyLocalDev`

## Verification
After the changes:
- All bare eslint-disable comments in the three helper files are gone
- `to-exist.ts` has a justified eslint-disable comment
- All listed functions accept `expect` as a parameter
- `mocks.ts` uses `throw new Error()` instead of `expect.fail()`
- Call sites pass `expect` to the refactored helper functions
