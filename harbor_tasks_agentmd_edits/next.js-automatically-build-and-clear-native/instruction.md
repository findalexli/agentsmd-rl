# Automate native SWC build in pnpm build pipeline

## Problem

Developers frequently forget to run `pnpm swc-build-native` after pulling Rust changes in the `crates/` or `turbopack/` directories, leading to confusing runtime errors from stale native binaries. Conversely, rebuilding native binaries when nothing changed wastes significant time. The current workflow requires developers to manually decide which build command to run based on what they changed.

## Expected Behavior

`pnpm build` should automatically handle native SWC binary rebuilding. A new script in `packages/next-swc/` should:
- Skip native builds entirely in CI (CI uses prebuilt npm packages)
- Detect whether Rust source files changed since the last version bump
- Rebuild native binaries only when Rust changes are detected
- Clear stale `.node` binaries when no Rust changes exist (so prebuilt npm packages are used instead)

The script should be wired into the turborepo pipeline as the `build` task for `@next/swc`, with appropriate Rust-specific inputs and cache configuration.

Additionally, the `scripts/build-native.ts` type generation should be improved to use prettier via stdin instead of writing files before formatting.

After implementing the code changes, update the project's agent instructions to reflect the simplified build workflow — developers no longer need separate commands for Rust-only or mixed edits.

## Files to Look At

- `packages/next-swc/` — where the new build automation script should live
- `packages/next-swc/package.json` — needs a `build` script entry
- `packages/next-swc/turbo.json` — turborepo task configuration for `@next/swc`
- `scripts/build-native.ts` — type generation and prettier formatting
- `AGENTS.md` — developer rebuild instructions that reference `swc-build-native`
