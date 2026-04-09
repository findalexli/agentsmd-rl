# CLI warning for Rosetta 2 on Apple Silicon

## Problem

When a user runs Next.js CLI commands (e.g., `next dev`, `next build`) on an Apple Silicon Mac using a Node.js binary compiled for x86_64 (e.g., downloaded the x64 macOS installer instead of the ARM64 one), Node.js runs under Rosetta 2 translation. This can cause degraded performance, but the user gets no indication that this is happening.

## Expected Behavior

The Next.js CLI should detect when it is running under Rosetta 2 translation on Apple Silicon and print a warning to inform the user about the potential performance impact.

## Files to Look At

- `packages/next/src/bin/next.ts` — the CLI entry point where platform detection should be added, inside the `NextRootCommand` class's `createCommand` hook
