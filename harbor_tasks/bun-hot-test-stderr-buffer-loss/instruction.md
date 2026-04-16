# Bug: Hot-reload sourcemap tests hang due to lost stderr data

## Summary

Three tests intermittently hang and time out:
- "should work with sourcemap generation"
- "should work with sourcemap loading"
- "should work with sourcemap loading with large files"

All three tests verify exactly 50 reload cycles (asserting `toBe(50)` or `toEqual(50)`).

## Target

**File:** `test/cli/hot/hot.test.ts` in the `oven-sh/bun` repository @ commit `af24e281ebacd6ac77c0f14b4206599cf4ae1c9f`

## Symptoms

1. **Stale error lines corrupt state**: When processing stderr chunks split by newline, duplicate/stale errors from previous reload cycles can cause the test to lose track of which lines have been processed, leading to the test waiting for output that will never arrive.

2. **Pipe buffer issues with bundler subprocesses**: Bundler subprocesses spawned with `--watch` may cause the test runner to hang, possibly related to how stdout/stderr is configured for those processes.

3. **No early-exit detection for bundler**: If a bundler process terminates unexpectedly, the test continues waiting indefinitely instead of failing fast.

4. **Performance issue with large strings**: Large repetitive strings constructed using certain patterns may be slow in debug JavaScriptCore builds. The test conventions (see `test/CLAUDE.md`) require a specific approach for constructing such strings efficiently.

## What must be fixed

The three sourcemap tests must pass reliably without hanging. Specifically:

1. The stderr processing must correctly handle all lines from each chunk — no lines from a chunk may be silently discarded when processing errors.

2. Bundler subprocesses (those spawned with `--watch`) must be configured such that they do not cause the test runner to hang.

3. Bundler-based tests must be able to detect when the bundler process exits early.

4. Large repetitive strings (100+ repetitions) must be constructed using an approach that performs well in debug JavaScriptCore builds.

## Verification requirements

After fixing, the code must still satisfy:
- All three sourcemap test names and their `toBe(50)` / `toEqual(50)` assertions must remain
- At least 10 non-comment lines must be modified in the target file
- The file must pass Prettier@3.6.2 formatting check
- The file must pass oxlint with 0 errors
- The file must pass TypeScript typecheck in the `test/` directory