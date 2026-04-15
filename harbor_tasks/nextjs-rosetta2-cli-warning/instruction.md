# CLI warning for Rosetta 2 on Apple Silicon

## Problem

When a user runs Next.js CLI commands (e.g., `next dev`, `next build`) on an Apple Silicon Mac using a Node.js binary compiled for x86_64 (e.g., downloaded the x64 macOS installer instead of the ARM64 one), Node.js runs under Rosetta 2 translation. This can cause degraded performance, but the user gets no indication that this is happening.

## Expected Behavior

The Next.js CLI should detect when it is running under Rosetta 2 translation on Apple Silicon and print a warning to inform the user about the potential performance impact. The detection must use all three checks:

1. `process.platform` equals `'darwin'`
2. `process.arch` equals `'x64'`
3. At least one CPU model string (from `os.cpus()`) contains the substring `'Apple'`

The warning message must use the `warn()` function already present in the CLI entry point, and must mention both "Apple Silicon" and "performance" (e.g., `"You are running Next.js on an Apple Silicon Mac with Rosetta 2 translation, which may cause degraded performance."`).

The `os` module must be imported using `import os from 'os'` (ESM import syntax).

## Files to Look At

- `packages/next/src/bin/next.ts` — the CLI entry point where platform detection should be added. The `warn` function is imported from `../build/output/log`.

## Behavior to Avoid

- The warning must NOT fire when `process.arch` is `'arm64'` (native ARM, no translation needed)
- The warning must NOT fire on Linux or Windows, regardless of CPU model
- The warning must NOT fire when running under ARM64 on Apple Silicon (native, no Rosetta)
