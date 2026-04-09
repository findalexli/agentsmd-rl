# Add IR PGO build support

## Problem

The Bun build system currently does not support Profile-Guided Optimization (PGO). Developers cannot use `--pgo-generate` or `--pgo-use` flags when building Bun, which limits optimization opportunities for release builds.

## Expected Behavior

Add two new CLI flags to the build system:
- `--pgo-generate=<dir>` — produce an instrumented build that writes `.profraw` files at runtime
- `--pgo-use=<file.profdata>` — produce an optimized build using merged profile data

These flags should:
1. Be recognized by the CLI argument parser in `scripts/build.ts`
2. Be stored in the Config interface with proper TypeScript types (`string | undefined`)
3. Be mutually exclusive — if both are provided, throw a `BuildError`
4. Appear in the formatted config output (e.g., "pgo-gen" or "pgo-use" in the features list)
5. Forward the appropriate compiler and linker flags for PGO
6. Forward PGO flags to WebKit when building locally

## Files to Look At

- `scripts/build.ts` — CLI argument parsing (around line 314)
- `scripts/build/config.ts` — Config interface, resolveConfig function, formatConfig function
- `scripts/build/flags.ts` — globalFlags and linkerFlags arrays
- `scripts/build/deps/webkit.ts` — WebKit dependency configuration (CMAKE flags)

## Notes

- The flags should only apply on Unix platforms (the PR checks `c.unix`)
- Use `-fprofile-generate=<dir>` for instrumentation and `-fprofile-use=<file>` for optimization
- When using PGO, also pass warning suppression flags: `-Wno-profile-instr-out-of-date`, `-Wno-profile-instr-unprofiled`, `-Wno-backend-plugin`
- The existing `lto` flag pattern is a good reference for implementation
