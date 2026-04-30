# Fix dynamic import deferral and memory safety issues in Bun

## Problem Summary

Bun's module loading has four distinct issues that need to be addressed:

1. Dynamic `import()` expressions for unknown `node:` prefixed modules (like `node:sqlite`) are resolved at load time instead of being deferred to runtime
2. The logger accesses arena-allocated memory that may be reset before error processing completes
3. The S3 credentials file uses incompatible string utility functions that don't follow project conventions
4. The project's `src/CLAUDE.md` file has formatting inconsistencies including a misaligned "Instead of / Use" table

## Required Changes

### Issue 1: Dynamic import resolution timing

When a CommonJS file containing `import("node:sqlite")` is `require()`d, the operation fails immediately at load time rather than deferring to runtime. This prevents `try/catch` blocks from gracefully handling missing modules.

The linker code that handles runtime deferral of module resolution must be extended to cover dynamic `import()` expressions in addition to CommonJS require operations. The resolution of unknown `node:` prefixed modules should be deferred to runtime, allowing errors to be caught at execution time with code `ERR_UNKNOWN_BUILTIN_MODULE`.

### Issue 2: Logger memory lifetime

When errors are logged with arena-allocated sources, the error handler may access memory that has already been released back to the arena. The line text used in error messages must remain valid for the duration of error processing.

In `src/logger.zig`, the error reporting functions should ensure any referenced source text is stable for the lifetime of the error handler, specifically by duplicating line text so it outlives the arena-allocated source.

### Issue 3: String utilities in credentials

The S3 credentials module at `src/s3/credentials.zig` uses `std.mem` functions for string operations where project conventions documented in CLAUDE.md require `bun.strings` APIs instead. Specifically, string search operations like `std.mem.indexOfAny` should use the `strings.indexOfAny` equivalent from `bun.strings`. The file should import `const strings = bun.strings` to access these APIs.

### Issue 4: CLAUDE.md formatting

The `src/CLAUDE.md` file's "Instead of / Use" table has inconsistent column alignment. Fix the table formatting to have properly aligned columns. The header separator row should use markdown table syntax with dashes separated by pipes, and each separator column should be wide enough to align with its content.

Section headers in the file need blank lines after them:
- "Key functions (all take `bun.FileDescriptor`, not `std.posix.fd_t`):"
- "Key methods:"
- "For pooled path buffers (avoids 64KB stack allocations on Windows):"

## Regression Test

Create a test file at `test/regression/issue/25707.test.ts` that verifies the dynamic import deferral behavior. The test should import from `"harness"` and `"bun:test"`, and use `Bun.spawn()` with `bunExe()`, `bunEnv`, and `tempDir()` to create temporary CJS files and run them as subprocesses. The test should verify the exact behaviors below via these test cases:

1. **"require() of CJS file containing dynamic import of non-existent node: module does not fail at load time"** — `require()` of a CJS file containing `import("node:sqlite")` inside a try/catch does not fail at load time, and the subprocess exits with code 0
2. **"require() of CJS file with bare dynamic import of non-existent node: module does not fail at load time"** — `require()` of a CJS file that has a bare `import("node:sqlite")` (no try/catch wrapper) does not fail at load time
3. **"dynamic import of non-existent node: module in CJS rejects at runtime with correct error"** — When the dynamic import actually executes at runtime and the module doesn't exist, it rejects with `ERR_UNKNOWN_BUILTIN_MODULE`

## Expected Behavior

After these fixes:
- `require()` of a CJS file containing `import("node:sqlite")` should NOT fail at load time
- The dynamic import should be deferred to runtime, allowing try/catch to handle missing modules gracefully
- When the dynamic import executes and the module doesn't exist, it should reject with `ERR_UNKNOWN_BUILTIN_MODULE`
- Logger errors involving arena-allocated sources should not cause use-after-poison
- The credentials file should use `const strings = bun.strings` and `strings.indexOfAny` instead of `std.mem.indexOfAny`
- The CLAUDE.md table should have properly aligned columns with consistent formatting
- Section headers in CLAUDE.md should have blank lines after them for readability
