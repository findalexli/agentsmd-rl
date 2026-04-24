# Fix dynamic import deferral and memory safety issues in Bun

## Problem Summary

Bun's module loading has three distinct issues that need to be addressed:

1. Dynamic `import()` expressions for unknown `node:` prefixed modules (like `node:sqlite`) are resolved at load time instead of being deferred to runtime
2. The logger accesses arena-allocated memory that may be reset before error processing completes
3. The S3 credentials file uses incompatible string utility functions

## Required Changes

### Issue 1: Dynamic import resolution timing

When a CommonJS file containing `import("node:sqlite")` is `require()`d, the operation fails immediately at load time rather than deferring to runtime. This prevents `try/catch` blocks from gracefully handling missing modules.

The linker code that handles runtime deferral of module resolution must be extended to cover dynamic `import()` expressions in addition to CommonJS require operations. The resolution of unknown `node:` prefixed modules should be deferred to runtime, allowing errors to be caught at execution time with code `ERR_UNKNOWN_BUILTIN_MODULE`.

### Issue 2: Logger memory lifetime

When errors are logged with arena-allocated sources, the error handler may access memory that has already been released back to the arena. The line text used in error messages must remain valid for the duration of error processing.

In `src/logger.zig`, the error reporting functions should ensure any referenced source text is stable for the lifetime of the error handler.

### Issue 3: String utilities in credentials

The `src/s3/credentials.zig` file uses string utilities from the standard library where project conventions prefer internal alternatives. Review the string manipulation functions used in the file and ensure they follow the conventions documented in CLAUDE.md for the `bun.strings` API.

### Issue 4: CLAUDE.md formatting

The `src/CLAUDE.md` file's "Instead of / Use" table has inconsistent column alignment. Fix the table formatting to have properly aligned columns. The header separator row should use markdown table syntax with dashes separated by pipes.

Section headers in the file need blank lines after them:
- "Key functions (all take `bun.FileDescriptor`, not `std.posix.fd_t`):"
- "Key methods:"
- "For pooled path buffers (avoids 64KB stack allocations on Windows):"

## Regression Test

Create a test file at `test/regression/issue/25707.test.ts` that verifies the dynamic import deferral behavior. The test should use Bun's test harness with `bunExe()`, `bunEnv`, and `tempDir()` to create temporary CJS files, and should verify:
1. `require()` of a CJS file containing `import("node:sqlite")` does not fail at load time
2. The test output should include verification that loading succeeds
3. When the dynamic import executes and the module doesn't exist, it should reject with `ERR_UNKNOWN_BUILTIN_MODULE`

## Expected Behavior

After these fixes:
- `require()` of a CJS file containing `import("node:sqlite")` should NOT fail at load time
- The dynamic import should be deferred to runtime, allowing try/catch to handle missing modules gracefully
- When the dynamic import executes and the module doesn't exist, it should reject with `ERR_UNKNOWN_BUILTIN_MODULE`
- Logger errors involving arena-allocated sources should not cause use-after-poison
- The credentials file should use `bun.strings` APIs instead of `std.mem` equivalents
- The CLAUDE.md table should have properly aligned columns with consistent formatting