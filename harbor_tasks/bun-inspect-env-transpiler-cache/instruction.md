# Bug: Debugger breakpoints land at wrong line numbers for large files when using BUN_INSPECT

## Summary

When using an IDE debug terminal (e.g., VSCode) that sets the `BUN_INSPECT` environment variable to enable the debugger, breakpoints in TypeScript files larger than 50KB resolve to incorrect line numbers. For example, a breakpoint set at line 1979 may land at line 1494 instead.

## Background

Bun has a **runtime transpiler cache** (`RuntimeTranspilerCache`) with a 50KB minimum file size threshold. When a cache hit occurs, the printer step is skipped entirely and the cached transpiled output is used directly. However, the cached output does **not** contain the inline `//# sourceMappingURL=data:...` comment that the debugger frontend needs to correctly map breakpoint positions back to source lines.

The `--inspect`, `--inspect-wait`, and `--inspect-brk` CLI flags already handle this correctly — they disable the transpiler cache so the printer always runs and generates the inline source map. However, when the debugger is activated via the `BUN_INSPECT` environment variable (the mechanism IDEs use), the cache is **not** disabled.

## Files Involved

- **`src/bun.js/VirtualMachine.zig`** — contains debugger configuration logic including `configureDebugger` and `isInspectorEnabled()` functions

- **`src/cli/Arguments.zig`** — the CLI argument parser where `--inspect`, `--inspect-wait`, and `--inspect-brk` flags are processed

## Required Behavior

When the debugger is active (regardless of whether it was activated via CLI flag or `BUN_INSPECT` environment variable), the runtime transpiler cache must be disabled so that inline source maps are always generated.

Specifically:

1. The fix must disable `RuntimeTranspilerCache` by setting `is_disabled = true` on it (or calling a `disable()` method if one exists).

2. The cache disable must apply universally for all debugger modes (including when `BUN_INSPECT` is used), not just for specific CLI flag modes.

3. The fix should check for the debugger being enabled via `isInspectorEnabled()` or equivalent inspector state check.

4. When the debugger is active, the following transpiler settings must be configured:
   - `minify_identifiers` — must be disabled
   - `minify_syntax` — must be disabled
   - `minify_whitespace` — must be disabled
   - `debugger` — must be set to `true`

5. The `--inspect`, `--inspect-wait`, and `--inspect-brk` CLI flags in `src/cli/Arguments.zig` must continue to be handled.

## Reproduction

1. Create a TypeScript file larger than 50KB
2. Set `BUN_INSPECT` environment variable and `BUN_RUNTIME_TRANSPILER_CACHE_PATH` to a temp directory
3. Run the file with bun
4. Observe that the cache directory contains cached files — this demonstrates the bug (cached files should not be created when the inspector is active)
