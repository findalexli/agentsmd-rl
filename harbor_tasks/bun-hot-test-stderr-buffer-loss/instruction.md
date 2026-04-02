# Bug: Hot-reload sourcemap tests hang due to lost stderr data

## Summary

Three tests in `test/cli/hot/hot.test.ts` intermittently hang and time out:
- "should work with sourcemap generation"
- "should work with sourcemap loading"
- "should work with sourcemap loading with large files"

## Root Cause

All three tests share the same error-handling loop pattern for driving a hot-reload cycle. They read stderr chunks, split by newline, and iterate over lines looking for error messages. When a duplicate/stale error is detected (from the previous reload cycle), the code uses `continue outer` to jump back to reading the next stderr chunk. However, **before** doing so, `str` is set to `""` inside the inner loop — this discards any remaining unprocessed lines from the current chunk that haven't been iterated yet. The lost lines may contain the expected error output, causing the test to wait forever for data that was already consumed and thrown away.

Additionally, two of the three tests spawn a bundler subprocess with `stdout: "inherit"` and/or `stderr: "inherit"`. When the test runner's pipe buffer fills up, the bundler blocks on writes, creating backpressure that can stall the entire test.

A third, subtler issue: the bundler-based tests don't detect early bundler exits. If the bundler process terminates unexpectedly, the test continues waiting on stderr from the runner process indefinitely instead of failing fast.

## Relevant Files

- `test/cli/hot/hot.test.ts` — the three affected tests all use an `outer: for await` loop with the same data-loss pattern.

## What Needs to Change

1. Fix the data-loss pattern: when a duplicate error is encountered, remaining unprocessed lines from the current split must be preserved (re-buffered) rather than discarded.
2. Fix pipe backpressure: bundler subprocesses should not inherit stdout/stderr pipes.
3. Add early-exit detection: race the bundler's exit promise against the reload driver so the test fails fast if the bundler dies.
4. The three tests share nearly identical loop logic — consider extracting a shared helper to avoid repeating the fix three times.
