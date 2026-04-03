# Automate native SWC build in `pnpm build` pipeline

## Problem

Developers frequently forget to run `pnpm swc-build-native` after pulling Rust changes in `crates/` or `turbopack/`, leading to confusing runtime errors from stale native binaries. Conversely, rebuilding native binaries when nothing has changed wastes significant time.

The `@next/swc` package (`packages/next-swc/`) currently has no `build` task in Turborepo's pipeline, so `pnpm build` skips it entirely. There's no automated way to detect whether Rust files changed and conditionally rebuild.

## Expected Behavior

Running `pnpm build` should automatically detect whether Rust source files have changed since the last version bump and:
1. **Rebuild native binaries** if Rust files changed (committed, staged, or unstaged)
2. **Clear stale `.node` binaries** if no Rust changes are detected (so prebuilt npm packages are used)
3. **Skip entirely in CI** (CI uses prebuilt `@next/swc-*` npm packages)

The script should be integrated into the Turborepo pipeline as the `build` task for `@next/swc`, with appropriate Rust-specific inputs for cache invalidation.

Additionally, the `scripts/build-native.ts` file should be updated so that the `writeTypes()` function uses prettier via stdin (not `--write`) and skips the file write when content hasn't changed.

After making these code changes, update the project's agent instruction file (`AGENTS.md`) to reflect that developers no longer need separate commands for Rust rebuilds — `pnpm build` now handles everything automatically.

## Files to Look At

- `packages/next-swc/` — the SWC native bindings package that needs a `build` task
- `packages/next-swc/package.json` — needs a `build` script entry
- `packages/next-swc/turbo.json` — Turborepo task configuration for this package
- `scripts/build-native.ts` — the existing build script for native bindings (writeTypes needs refactoring)
- `AGENTS.md` — agent instructions that document the rebuild workflow
