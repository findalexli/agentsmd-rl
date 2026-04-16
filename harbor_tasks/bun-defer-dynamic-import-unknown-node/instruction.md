# Fix dynamic import deferral and memory safety issues in Bun

## Problem Summary

Bun's module loading has three distinct issues that need to be addressed:

1. Dynamic `import()` expressions for unknown `node:` prefixed modules (like `node:sqlite`) are resolved at load time instead of being deferred to runtime
2. The logger accesses arena-allocated memory that may be reset before error processing completes
3. The S3 credentials file uses incompatible string utility functions

## Required Changes

### Issue 1: Dynamic import resolution timing

When a CommonJS file containing `import("node:sqlite")` is `require()`d, the operation fails immediately at load time rather than deferring to runtime. This prevents `try/catch` blocks from gracefully handling missing modules.

The linker code that handles runtime deferral of module resolution must be extended to cover dynamic `import()` expressions in addition to `.require` and `.require_resolve` imports. The resolution of unknown `node:` prefixed modules should be deferred to runtime, allowing errors to be caught at execution time with code `ERR_UNKNOWN_BUILTIN_MODULE`.

### Issue 2: Logger memory lifetime

When `addResolveError` is called with arena-allocated sources, accessing `Location.line_text` after the arena is reset causes a use-after-poison bug. The line text must be copied to ensure the error logging can access it after the source memory is released.

In `src/logger.zig`, the `addResolveError` function should ensure the Location data outlives the source's backing memory.

### Issue 3: String utilities in credentials

The `src/s3/credentials.zig` file uses `std.mem` string utilities where `bun.strings` equivalents should be used per project conventions documented in CLAUDE.md.

The `containsNewlineOrCR` function should use the appropriate `bun.strings` API for checking newlines.

### Issue 4: CLAUDE.md formatting

The `src/CLAUDE.md` file's "Instead of / Use" table needs consistent column alignment. The header separator should use `| ------------------------------------------------------------ | ------------------------------------ |` format, and rows should have properly aligned columns with `bun.sys.File`, `bun.strings`, `bun.FileDescriptor`, etc. replacing their `std.*` equivalents.

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