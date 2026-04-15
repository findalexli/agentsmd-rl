# Support Opening Raw .trace Files and Improve Trace Loader Flexibility

## Problem

The Playwright trace handling has several issues:

1. **Opening raw .trace files fails**: When `openTrace()` (in `packages/playwright-core/src/tools/trace/traceUtils.ts`) receives a `.trace` file instead of a `.zip` archive, it attempts to extract it as a zip, which fails. The function needs to distinguish between `.zip` archives and raw `.trace` files, handling each appropriately. The companion `loadTrace()` function also needs updating to work with the new flow.

2. **`TraceLoader.load()` requires `unzipProgress` callback**: The `load()` method in `packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts` currently requires an `unzipProgress` callback parameter. This makes it inconvenient when progress tracking isn't needed — callers still have to pass a no-op function. The `unzipProgress` parameter should be optional.

3. **No trace file filtering**: `TraceLoader.load()` loads all `.trace` files found in a directory. It should accept an optional `traceFile` parameter to load only a specific trace file.

4. **CLI unhandled promise rejection**: In `packages/playwright-core/src/cli/program.ts`, the `cliProgram()` call does not catch errors, causing unhandled promise rejections instead of clean error messages and exit.

5. **Unsafe `traceLegend` access**: In `packages/playwright-core/src/tools/backend/tracing.ts`, the `tracingStop` tool accesses the `traceLegend` property without first verifying that tracing was actually started, which can cause errors.

## Expected Behavior

1. `openTrace()` should distinguish between `.zip` and raw `.trace` files, handling each appropriately without attempting zip extraction on non-zip files. The companion `loadTrace()` function should resolve the correct trace directory and trace file in both cases.

2. `TraceLoader.load()` should make `unzipProgress` an optional parameter so callers can omit it when progress tracking is not needed.

3. `TraceLoader.load()` should accept an optional `traceFile` parameter to filter which trace to load from the directory.

4. The CLI should catch errors from `cliProgram()` and exit gracefully with proper error messages.

5. `tracingStop` should validate that tracing was started before accessing `traceLegend`.

## Related Files

- `packages/playwright-core/src/tools/trace/traceUtils.ts` — `openTrace()` and `loadTrace()` functions
- `packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts` — `TraceLoader` class with `load()` method
- `packages/playwright-core/src/cli/program.ts` — CLI entry point
- `packages/playwright-core/src/tools/backend/tracing.ts` — Tracing tool
- `packages/trace-viewer/src/sw/main.ts` — Service worker that calls `traceLoader.load()`
- `tests/config/utils.ts` — Test utilities that also use `traceLoader.load()`
