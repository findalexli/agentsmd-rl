# Support Opening Raw .trace Files and Improve Trace Loader Flexibility

## Problem

The Playwright trace handling has several issues that prevent proper functionality:

1. **Opening raw .trace files fails**: When the trace viewer receives a `.trace` file directly, it attempts to extract it as a zip archive, which fails. Users need to be able to open `.trace` files directly without manual conversion.

2. **TraceLoader.load() requires unzipProgress callback**: The `load()` method requires a callback parameter for tracking unzip progress. Callers that don't need progress tracking must still provide a no-op function, which is inconvenient.

3. **No trace file filtering**: `TraceLoader.load()` loads all `.trace` files found in a directory. Users may want to load only a specific trace file by name.

4. **CLI unhandled promise rejection**: When the CLI entry point encounters an error, the error results in an unhandled promise rejection rather than a clean error message and proper process exit.

5. **Unsafe traceLegend access**: The tracing stop functionality crashes if tracing was never started, because it accesses a `traceLegend` property without first checking whether tracing is active.

## Expected Behavior

1. When opening a trace file that ends with `.trace` (not `.zip`), the system should create a `.link` file in the trace directory containing the path to the trace file. When loading, if a `.link` file exists, the system should read it to locate the actual trace file.

2. `TraceLoader.load()` should work without requiring an unzip progress callback — the parameter should be optional.

3. `TraceLoader.load()` should accept an optional parameter to filter which trace file to load, rather than loading all trace files in a directory.

4. The CLI should handle errors from the main program gracefully, logging the error and exiting the process cleanly.

5. When stopping tracing, if tracing was never started, the system should throw an error with a message indicating that tracing is not active.

## Files Likely Involved

Trace handling functionality is typically found in:
- Trace utility modules (handling `openTrace` and `loadTrace` operations)
- Isomorphic trace loader modules (containing `TraceLoader` class)
- CLI entry points
- Backend tracing modules

Look for files related to trace handling, CLI program initialization, and tracing backend operations.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
