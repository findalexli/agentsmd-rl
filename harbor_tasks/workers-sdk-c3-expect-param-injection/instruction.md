# Remove eslint-disable comments for no-restricted-imports in create-cloudflare

## Problem

The `packages/create-cloudflare` package has ESLint warnings suppressed by `// eslint-disable-next-line no-restricted-imports` comments. The `no-restricted-imports` rule is configured to prevent direct value imports of `expect` from `vitest` in helper/utility files — only test files should import `expect` directly.

Currently, bare eslint-disable comments appear in:
- `packages/create-cloudflare/e2e/helpers/framework-helpers.ts`
- `packages/create-cloudflare/e2e/helpers/workers-helpers.ts`
- `packages/create-cloudflare/src/helpers/__tests__/mocks.ts`

Additionally, `packages/create-cloudflare/e2e/helpers/to-exist.ts` imports `expect` from vitest.

## Symptom

The helper files (`framework-helpers.ts`, `workers-helpers.ts`) import `expect` from `vitest` as a value import, which triggers ESLint `no-restricted-imports` warnings. The eslint-disable comments suppress these warnings without resolving the underlying architectural issue — helpers should receive their dependencies from test files rather than importing them directly.

The `mocks.ts` file imports `expect` from vitest and uses `expect.fail()` for validation checks, which also triggers the ESLint rule.

## Expected Behavior

### eslint-disable comment cleanup

**`framework-helpers.ts`, `workers-helpers.ts`, and `mocks.ts`:**
- Must have all bare `// eslint-disable-next-line no-restricted-imports` comments removed
- Must not import `expect` from vitest as a value import

**`to-exist.ts`:**
- May retain its eslint-disable comment, but it must include a justification (`-- reason`) explaining why the exception is necessary

### Helper function signatures

The following exported async functions in `framework-helpers.ts` and `workers-helpers.ts` currently rely on an imported `expect` function. They must be refactored to receive `expect` (of type `ExpectStatic` from vitest) as a parameter instead:

**`framework-helpers.ts` (8 functions):**
- `runC3ForFrameworkTest`
- `verifyDeployment`
- `verifyDevScript`
- `verifyPreviewScript`
- `verifyTypes`
- `verifyCloudflareVitePluginConfigured`
- `testGitCommitMessage`
- `testDeploymentCommitMessage`

**`workers-helpers.ts` (2 functions):**
- `runC3ForWorkerTest`
- `verifyLocalDev`

### mocks.ts validation behavior

In `packages/create-cloudflare/src/helpers/__tests__/mocks.ts`:
- Must not use `expect.fail()` for validation failures (this requires importing `expect`)
- Must have at least 3 validation checks that throw errors when assertions fail
- Must not import `expect` from vitest (only `vi` should be imported)

### Test file call sites

The e2e test files must pass `expect` to the refactored helper functions:

**`packages/create-cloudflare/e2e/tests/frameworks/frameworks.test.ts`:**
- Must pass `expect` to: `runC3ForFrameworkTest`, `verifyDeployment`, `verifyDevScript`

**`packages/create-cloudflare/e2e/tests/workers/workers.test.ts`:**
- Must pass `expect` to: `runC3ForWorkerTest`

## Verification

After the changes:
- ESLint type-checking rules for consistent-type-imports are satisfied in the helper files
- All bare eslint-disable comments for `no-restricted-imports` are removed from the three specified files
- `to-exist.ts` has a justified eslint-disable comment
- Helper functions receive `expect` as a parameter rather than importing it
- `mocks.ts` no longer imports `expect` and uses standard error throwing for validation failures
- E2E test files pass `expect` to helper function calls
- TypeScript compilation passes for the create-cloudflare package
- Unit tests pass for the create-cloudflare package
- Linting and formatting checks pass
- The package builds successfully
