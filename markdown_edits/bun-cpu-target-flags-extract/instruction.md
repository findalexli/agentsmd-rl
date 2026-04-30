# Fix local WebKit builds missing CPU target flags

## Problem

When building Bun with a local WebKit profile (`webkit: "local"`), the WebKit dependency's `optFlags` are initialized as an empty array. This means local WebKit builds (via nested cmake) compile for generic x86-64, while the rest of Bun and prebuilt WebKit binaries target `haswell`/`nehalem`. This causes a performance and instruction-set mismatch.

The root cause is that `webkit.ts` clears all global dep flags when configuring WebKit's cmake (because WebKit's own cmake sets `-O`/`-g`/sanitizer flags that would conflict). But this also drops the `-march`/`-mcpu` CPU target flags, which WebKit's cmake never sets on its own.

## What to fix

In `scripts/build/flags.ts`:
- The CPU target entries (`-mcpu=apple-m1`, `-march=armv8-a+crc`, `-march=haswell`, etc.) are currently embedded directly in `globalFlags`. Extract them into a separate `cpuTargetFlags` array.
- Add a `computeCpuTargetFlags(cfg)` function that evaluates just the CPU target flags (similar to how `computeFlags` works for all flags).
- Spread `cpuTargetFlags` back into `globalFlags` so existing behavior is preserved.

In `scripts/build/deps/webkit.ts`:
- Import the new `computeCpuTargetFlags` function from `flags.ts`.
- Use it to seed the `optFlags` array instead of starting with an empty array, so local WebKit builds inherit the correct CPU target.

After fixing the code, update the relevant documentation in `scripts/build/CLAUDE.md` to reflect the new flag table and function.
