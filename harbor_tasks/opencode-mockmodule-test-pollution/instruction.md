# Flaky TUI Thread & Config Tests Due to Mock Leakage

## Problem

Two test files in `packages/opencode/test/` are causing flaky failures in CI:

### 1. `packages/opencode/test/cli/tui/thread.test.ts`

This test uses `mock.module()` from Bun's test runner to mock several dependencies (`@/config/tui`, `@/util/rpc`, `@/cli/ui`, etc.). However, when the test suite finishes and other test files run afterward (particularly the plugin-loader tests), those later suites see the mocked modules instead of the real implementations.

The root cause is that Bun's `mock.module()` caches module overrides globally, and `mock.restore()` does **not** reset module-level mocks — only function-level spies. This is a known Bun limitation (see oven-sh/bun#7823).

The result: plugin-loader tests that depend on the real `TuiConfig.waitForDependencies` receive the mocked version (which returns `{}`) and fail intermittently depending on test execution order.

### 2. `packages/opencode/test/config/config.test.ts`

The "dedupes concurrent config dependency installs" and "serializes config dependency installs across dirs" tests mock `BunProc.run` to count how many times the install runner is invoked. However, the mock intercepts **all** `BunProc.run` calls — including unrelated background operations that may happen to call `BunProc.run` during the test. This causes the call counters and peak-concurrency tracking to be inflated by unrelated invocations, making assertions flaky.

## Expected Outcome

- The TUI thread tests should not leak mock state to other test suites
- The config dependency install tests should only count `BunProc.run` calls that are relevant to the directories under test
- All existing test assertions must still pass
