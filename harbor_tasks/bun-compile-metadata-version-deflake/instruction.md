# Flaky Test: Windows Compile Metadata Invalid Version

## Bug

A test in `test/bundler/compile-windows-metadata.test.ts` is flaky on CI. It times out intermittently, especially on slower machines under load.

The test runs 5 sequential `bun build --compile` invocations inside a single test case. Each invocation spawns a subprocess that takes a non-trivial amount of time. Because all 5 share one test case's timeout budget, the cumulative time often exceeds the test timeout on slower CI machines.

## What to Fix

The sequential loop that bundles multiple invalid version checks into a single test case must be replaced. Each invalid version string should be tested as its own independent test case with its own timeout budget. The loop and its backing array variable must be removed entirely.

Each test case should receive its version string as a parameter named `version`, and the version string must appear in each test case's name for proper reporting.

The 5 invalid version strings that must each be tested:
- `"not.a.version"`
- `"1.2.3.4.5"`
- `"1.-2.3.4"`
- `"65536.0.0.0"` (exceeds 65535 limit)
- `""` (empty string)

## Constraints

- All 5 invalid version formats must still be tested
- Non-zero exit code assertions must remain (e.g., `expect(exitCode).not.toBe(0)`)
- Do not change any other tests in the file
- The test bodies must still use `await using proc = Bun.spawn(...)` with `await proc.exited`
- The file must still use `bunExe()`, `bunEnv`, and `tempDir` from the test harness
- The `describe.concurrent` pattern must be preserved

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
