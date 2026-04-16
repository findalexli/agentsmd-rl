# Support Opening Raw .trace Files and Improve Trace Loader Flexibility

## Problem

The Playwright trace handling has several issues:

1. **Opening raw .trace files fails**: When the trace opening functionality receives a `.trace` file instead of a `.zip` archive, it attempts to extract it as a zip, which fails. The system needs to distinguish between `.zip` archives and raw `.trace` files, handling each appropriately. For raw `.trace` files, the system should create a `.link` file containing the path to the trace file, which can then be read by the trace loading functionality to locate the actual trace.

2. **TraceLoader.load() requires `unzipProgress` callback**: The `load()` method currently requires an `unzipProgress` callback parameter. This makes it inconvenient when progress tracking isn't needed — callers still have to pass a no-op function. The `unzipProgress` parameter should be optional (using TypeScript optional parameter syntax `unzipProgress?`).

3. **No trace file filtering**: `TraceLoader.load()` loads all `.trace` files found in a directory. It should accept an optional `traceFile` parameter (using TypeScript optional parameter syntax `traceFile?`) to load only a specific trace file.

4. **CLI unhandled promise rejection**: The CLI entry point does not catch errors from the main program call, causing unhandled promise rejections instead of clean error messages and exit. The fix should add error handling using `.catch(logErrorAndExit)` where `logErrorAndExit` is an error handler function that logs errors and exits the process.

5. **Unsafe traceLegend access**: The tracing stop functionality accesses the `traceLegend` property without first verifying that tracing was actually started. The fix should add validation that checks `if (!traceLegend)` and throws an error with message "Tracing is not started" before accessing the property.

## Expected Behavior

1. When opening a trace file that ends with `.trace` (not `.zip`), the system should:
   - Create a `.link` file in the trace directory containing the full path to the trace file
   - When loading, if a `.link` file exists, read it to get the actual trace file path and use `path.dirname()` to get the trace directory and `path.basename()` to get the trace file name

2. `TraceLoader.load()` should have the signature: `load(backend: TraceLoaderBackend, traceFile?: string, unzipProgress?: UnzipProgress)` making both `traceFile` and `unzipProgress` optional parameters.

3. The CLI should catch errors from the main program call with `.catch(logErrorAndExit)` where `logErrorAndExit` handles error logging and process exit.

4. The tracing stop functionality should validate that `traceLegend` exists before accessing it, throwing "Tracing is not started" if tracing was not started.

## Files Likely Involved

Trace handling functionality is typically found in:
- Trace utility modules (handling `openTrace` and `loadTrace` operations)
- Isomorphic trace loader modules (containing `TraceLoader` class)
- CLI entry points
- Backend tracing modules

Look for files related to trace handling, CLI program initialization, and tracing backend operations.
