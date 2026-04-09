# Support Opening .trace Files via .link Indirection

## Problem

The Playwright trace CLI currently only supports opening `.zip` trace files. When a user tries to open a raw `.trace` file directly, the system attempts to extract it as a zip archive, which fails.

Additionally, there are several related issues:

1. **`traceLoader.load()` signature is inflexible**: The method requires both `backend` and `unzipProgress` parameters. The `unzipProgress` callback should be optional for cases where progress tracking isn't needed.

2. **No filtering by trace file**: The `traceLoader.load()` method loads all `.trace` files in a directory. It should support an optional `traceFile` parameter to load only a specific trace file.

3. **CLI error handling is incomplete**: The `cliProgram()` call in `program.ts` doesn't catch errors, causing unhandled promise rejections instead of proper error messages.

4. **Missing error handling in tracing**: The `tracingStop` tool doesn't check if tracing was actually started before trying to access the `traceLegend` property.

## Expected Behavior

1. When `openTrace()` is called with a `.trace` file (not `.zip`), it should create a `.link` file in the trace directory containing the path to the original trace file, rather than trying to extract it.

2. `loadTrace()` should check for a `.link` file and if present, read the actual trace path from it, then use that path for loading.

3. `traceLoader.load()` should accept an optional `traceFile` parameter (second parameter) and an optional `unzipProgress` callback (third parameter).

4. CLI commands should catch errors and exit gracefully with proper error messages.

5. Tracing stop should validate that tracing was started before accessing trace data.

## Files to Look At

- `packages/playwright-core/src/tools/trace/traceUtils.ts` — Contains `openTrace()` and `loadTrace()` functions that handle trace file operations
- `packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts` — Contains `TraceLoader` class with the `load()` method
- `packages/playwright-core/src/cli/program.ts` — CLI entry point that needs error handling
- `packages/playwright-core/src/tools/backend/tracing.ts` — Tracing tool that needs validation
- `packages/trace-viewer/src/sw/main.ts` — Service worker that calls `traceLoader.load()`
- `tests/config/utils.ts` — Test utilities that also use `traceLoader.load()`
