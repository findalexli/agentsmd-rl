# Bug: Hot-reload sourcemap tests hang due to lost stderr data

## Summary

Three tests in `test/cli/hot/hot.test.ts` intermittently hang and time out:
- "should work with sourcemap generation"
- "should work with sourcemap loading"
- "should work with sourcemap loading with large files"

All three tests verify exactly 50 reload cycles (asserting `toBe(50)` or `toEqual(50)`).

## Root Cause

All three tests share the same error-handling loop pattern for driving a hot-reload cycle. They read stderr chunks, split by newline, and iterate over lines looking for error messages. When a duplicate/stale error is detected (from the previous reload cycle), the code sets `str = ""` inside the inner loop before doing `continue outer` to jump back to reading the next stderr chunk. This discards any remaining unprocessed lines from the current chunk that haven't been iterated yet. The lost lines may contain the expected error output, causing the test to wait forever for data that was already consumed and thrown away.

Additionally, two of the three tests spawn a bundler subprocess with `--watch` and use `stdout: "inherit"` and/or `stderr: "inherit"`. When the test runner's pipe buffer fills up, the bundler blocks on writes, creating backpressure that can stall the entire test.

A third issue: the bundler-based tests don't detect early bundler exits. If the bundler process terminates unexpectedly, the test continues waiting on stderr from the runner process indefinitely instead of failing fast.

## Symptoms to Fix

1. **Data loss when skipping duplicate errors**: When a duplicate error is detected and the code continues to the next outer iteration, the remaining unprocessed lines from the current split must be preserved (e.g., by saving the trailing partial line with `pop()`, `at(-1)`, or similar array operations) rather than discarded via `str = ""`.

2. **Pipe backpressure in bundler subprocesses**: Bundler subprocesses (those spawned with `--watch`) must not use `stdout: "inherit"` or `stderr: "inherit"` as this causes pipe buffer backpressure.

3. **No early-exit detection**: Bundler-based tests must implement early-exit detection (e.g., via `Promise.race`, monitoring `bundler.exited`, or `AbortController`) so they fail fast if the bundler dies unexpectedly.

## Constraints

- The fix must change at least 10 non-comment lines (the file is ~350+ lines).
- The modified code must pass:
  - Prettier@3.6.2 formatting check
  - oxlint with 0 errors
  - TypeScript typecheck in `test/` directory
- The three sourcemap tests must continue to exist and verify 50 reload cycles each.
