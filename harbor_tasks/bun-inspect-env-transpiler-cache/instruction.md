# Bug: Debugger breakpoints land at wrong line numbers when using BUN_INSPECT

## Summary

When using the `BUN_INSPECT` environment variable to activate the debugger (the mechanism IDEs use), breakpoints in TypeScript files larger than 50KB resolve to incorrect line numbers. For example, a breakpoint set at line 1979 may land at line 1494 instead.

## Background

Bun has a **runtime transpiler cache** (`RuntimeTranspilerCache`) with a 50KB minimum file size threshold. When a cache hit occurs, the printer step is skipped entirely and the cached transpiled output is used directly. However, the cached output does **not** contain the inline `//# sourceMappingURL:data:...` comment that the debugger frontend needs to correctly map breakpoint positions back to source lines.

The `--inspect`, `--inspect-wait`, and `--inspect-brk` CLI flags correctly disable the transpiler cache so the printer always runs and generates the inline source map. However, when the debugger is activated via the `BUN_INSPECT` environment variable, the cache is **not** disabled — this is the bug.

## Files Involved

- **`src/bun.js/VirtualMachine.zig`** — contains the `configureDebugger` function that configures debugger settings
- **`src/cli/Arguments.zig`** — the CLI argument parser where `--inspect`, `--inspect-wait`, and `--inspect-brk` flags are processed

## Required Behavior

When the debugger is active (regardless of whether it was activated via CLI flag or `BUN_INSPECT` environment variable), the runtime transpiler cache must be disabled so that inline source maps are always generated.

Specifically:
1. The cache disable must apply to **all** debugger activation paths, not just CLI flag modes
2. The existing `--inspect`, `--inspect-wait`, and `--inspect-brk` CLI flags must continue to be handled
3. The existing debugger settings (`minify_identifiers = false`, `minify_syntax = false`, `minify_whitespace = false`, `debugger = true`) must be preserved

## Symptom Description

When running with `BUN_INSPECT` set, the cache directory (`BUN_RUNTIME_TRANSPILER_CACHE_PATH`) contains cached files even though the debugger is active. Cached transpiled output lacks inline source maps, causing the debugger frontend to resolve breakpoints to incorrect source lines. The cache should **not** be populated when the inspector is active.

## Reproduction

1. Create a TypeScript file larger than 50KB
2. Set `BUN_INSPECT` environment variable and `BUN_RUNTIME_TRANSPILER_CACHE_PATH` to a temp directory
3. Run the file with bun
4. Observe that the cache directory contains cached files — this demonstrates the bug (cached files should not be created when the inspector is active)