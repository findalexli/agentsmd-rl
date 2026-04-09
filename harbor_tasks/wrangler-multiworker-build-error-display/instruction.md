# Build errors from auxiliary workers are invisible in multi-worker mode

## Problem

When running `wrangler dev` with multiple `-c` config flags (multi-worker mode), build errors from auxiliary/secondary workers are only logged at debug level. If an auxiliary worker has a build error (e.g., a syntax error or missing module), Wrangler silently hangs — no error message is shown to the user.

This happens because `BundlerController` errors reach `DevEnv.handleErrorEvent()` but there is no branch to handle them. They fall through to the catch-all `else` which re-emits them as unknowable errors on the EventEmitter, never displaying them to the user.

Additionally, `BundlerController` calls `logger.error()` before each `emitErrorEvent()` call, which causes double-logging when the error handler also logs — and in this case the DevEnv handler doesn't even log them properly, so the `logger.error()` calls are the only visibility, but they only appear at debug level for auxiliary workers.

## Expected Behavior

Build errors from **all** workers (primary and auxiliary) should be clearly displayed:

- esbuild `BuildFailure` errors should be formatted nicely with source locations, notes, and suggestions (the same output format the primary worker already gets)
- Non-esbuild bundler errors should log the error message at error level
- Errors should be logged exactly once (not double-logged by both BundlerController and DevEnv)

## Files to Look At

- `packages/wrangler/src/api/startDevWorker/DevEnv.ts` — Central error handler (`handleErrorEvent`) that dispatches errors from all controllers. Needs a new branch for BundlerController errors.
- `packages/wrangler/src/api/startDevWorker/BundlerController.ts` — Emits error events at multiple call sites. Has redundant `logger.error()` calls before each `emitErrorEvent()`.
- `packages/wrangler/src/deployment-bundle/build-failures.ts` — Contains `isBuildFailure()` and `isBuildFailureFromCause()` type guards for detecting esbuild errors.
- `packages/wrangler/src/logger.ts` — Contains `logBuildFailure()` for nicely formatting esbuild errors.
