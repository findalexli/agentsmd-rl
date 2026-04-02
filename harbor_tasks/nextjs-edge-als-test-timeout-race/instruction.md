# Edge AsyncLocalStorage test timeout and race condition

The e2e test at `test/e2e/edge-async-local-storage/index.test.ts` is flaky in deploy mode. The test creates a new Next.js instance inside each `it.each` test body using `createNext`. In deploy mode, the deployment step can exceed the 60-second per-test timeout, causing the test to time out before the instance is assigned to the local variable.

When this happens:
1. The `afterEach` cleanup hook tries to call `.destroy()` on an unassigned variable, throwing a `TypeError`.
2. The module-level instance reference is left pointing at the stale, half-initialized deploy instance.
3. The next test case detects the leftover instance and fails with `"createNext called without destroying previous instance"`.

Additionally, the test defines API route source code as inline template strings in the test file, rather than using fixture files.

## Your task

Fix the test so that:
- Instance creation happens once with a longer setup timeout (not per-test with the short test timeout)
- Both API route variants are served from real fixture files in the test directory
- The race condition between instance creation and cleanup is eliminated

## Relevant files

- `test/e2e/edge-async-local-storage/index.test.ts` — the flaky test
- The test uses `createNext` from `e2e-utils` and `fetchViaHTTP` from `next-test-utils`

## Hints

- The Next.js test framework provides helpers that handle instance lifecycle in `beforeAll`/`afterAll` with a longer setup timeout — look at how other e2e tests in the repo set up their instances
- Fixture files should live alongside the test in the `pages/api/` directory
