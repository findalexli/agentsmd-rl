# Bug: Debugger breakpoints land at wrong line numbers for large files when using BUN_INSPECT

## Summary

When using an IDE debug terminal (e.g., VSCode) that sets the `BUN_INSPECT` environment variable to enable the debugger, breakpoints in TypeScript files larger than 50KB resolve to incorrect line numbers. For example, a breakpoint set at line 1979 may land at line 1494 instead.

## Background

Bun has a **runtime transpiler cache** (`RuntimeTranspilerCache`) with a 50KB minimum file size threshold. When a cache hit occurs, the printer step is skipped entirely and the cached transpiled output is used directly. However, the cached output does **not** contain the inline `//# sourceMappingURL=data:...` comment that the debugger frontend needs to correctly map breakpoint positions back to source lines.

The `--inspect`, `--inspect-wait`, and `--inspect-brk` CLI flags already handle this correctly — they disable the transpiler cache so the printer always runs and generates the inline source map. However, when the debugger is activated via the `BUN_INSPECT` environment variable (the mechanism IDEs use), the cache is **not** disabled.

## Relevant Code

- **`src/bun.js/VirtualMachine.zig`** — the `configureDebugger()` function is called whenever the inspector is being set up. This is where debugger-related transpiler settings are applied (e.g., disabling minification).

- **`src/cli/Arguments.zig`** — the CLI argument parser where `--inspect*` flags are processed. Currently, each `--inspect` variant individually disables the transpiler cache here.

## Expected Behavior

When the debugger is active (regardless of whether it was activated via CLI flag or `BUN_INSPECT` environment variable), the runtime transpiler cache should be disabled so that inline source maps are always generated.

## Reproduction

1. Create a TypeScript file larger than 50KB
2. Set `BUN_INSPECT` environment variable and `BUN_RUNTIME_TRANSPILER_CACHE_PATH` to a temp directory
3. Run the file with bun
4. Observe that the cache directory contains cached files — this should not happen when the inspector is active
