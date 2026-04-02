# Flaky Test: Windows Compile Metadata Invalid Version

## Bug

The test `invalid version format should error gracefully` in `test/bundler/compile-windows-metadata.test.ts` is flaky on CI. It times out intermittently, especially on slower machines under load.

## Root Cause

The test runs 5 sequential `bun build --compile` invocations inside a single test case using a `for` loop. Each invocation spawns a subprocess that takes a non-trivial amount of time. Since the parent `describe` block uses `.concurrent`, individual test cases get their own timeout budget — but because all 5 invocations share one test case's timeout, the cumulative time often exceeds the 90-second test timeout on slower CI machines.

## What to Fix

Restructure the test so that each invalid version string gets its own test case. The parent `describe` block already uses `.concurrent`, so splitting them into individual test cases means they will run in parallel, each with its own timeout budget.

The invalid versions being tested are:
- `"not.a.version"`
- `"1.2.3.4.5"`
- `"1.-2.3.4"`
- `"65536.0.0.0"` (exceeds 65535 limit)
- `""` (empty string)

## Files

- `test/bundler/compile-windows-metadata.test.ts` — the test file containing the flaky test

## Constraints

- All 5 invalid version formats must still be tested
- The test assertions (non-zero exit code) must remain the same
- Do not change any other tests in the file
