# Move Turbopack native build out of `pnpm build`

## Problem

Running `pnpm build` in the Next.js monorepo currently triggers both the JavaScript package builds and the Turbopack native (Rust) binary compilation via `maybe-build-native.mjs` in `packages/next-swc/`. This means developers who already have a custom-compiled Turbopack binary (e.g., with specific profiling flags) cannot rebuild just the JS parts without also recompiling the native code, which is slow and overwrites their custom binary.

## Expected Behavior

- `pnpm build` should only build JS code — it should not trigger native Turbopack compilation.
- A separate command (e.g., `pnpm build-all`) should exist for building everything, including the native auto-build.
- The `packages/next-swc` turbo configuration needs updating so its auto-build task is no longer named `build` (which turbo picks up automatically).

After making the code changes, update the project's agent instructions (`AGENTS.md`) to reflect the new build command split. All references to `pnpm build` that mean "build everything including Rust" should be updated to use the new command, and `pnpm build` should be documented as JS-only.

## Files to Look At

- `package.json` — root monorepo scripts
- `packages/next-swc/package.json` — next-swc build scripts
- `packages/next-swc/turbo.json` — turbo task definitions for next-swc
- `AGENTS.md` — agent development instructions referencing build commands
