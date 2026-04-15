# Flaky Test: Windows Compile Metadata Invalid Version

## Bug

The test `invalid version format should error gracefully` in `test/bundler/compile-windows-metadata.test.ts` is flaky on CI. It times out intermittently, especially on slower machines under load.

## Root Cause

The test runs 5 sequential `bun build --compile` invocations inside a single test case using a `for` loop. Each invocation spawns a subprocess that takes a non-trivial amount of time. Because all 5 invocations share one test case's timeout budget, the cumulative time often exceeds the 90-second test timeout on slower CI machines.

## What to Fix

The fix must eliminate the sequential for-loop pattern and restructure the invalid version tests so they no longer share a single timeout budget.

Specifically, the restructured test must:
- Use `test.each()` with an array of objects, where each object has a `version` property containing the invalid version string
- Include `$version` in the test name string for proper test reporting
- Remove the `invalidVersions` array variable entirely

The 5 invalid version strings that must be tested are:
- `"not.a.version"`
- `"1.2.3.4.5"`
- `"1.-2.3.4"`
- `"65536.0.0.0"` (exceeds 65535 limit)
- `""` (empty string)

## Files

- `test/bundler/compile-windows-metadata.test.ts` — the test file containing the flaky test

## Constraints

- All 5 invalid version formats must still be tested
- The test assertions (non-zero exit code via `expect(exitCode).not.toBe(0)`) must remain the same
- Do not change any other tests in the file
- The test bodies must still use `await using proc = Bun.spawn(...)` with `await proc.exited`
- The file must still use `bunExe()`, `bunEnv`, and `tempDir` from the test harness
- The `describe.concurrent` pattern must be preserved
