# Automate native SWC build in pnpm build pipeline

## Problem

Developers frequently forget to run `pnpm swc-build-native` after pulling Rust changes in the `crates/` or `turbopack/` directories, leading to confusing runtime errors from stale native binaries. Conversely, rebuilding native binaries when nothing changed wastes significant time. The current workflow requires developers to manually decide which build command to run based on what they changed.

## Expected Behavior

`pnpm build` should automatically handle native SWC binary rebuilding. The build automation for `@next/swc` lives in a script named `maybe-build-native.mjs` inside `packages/next-swc/` and must:

- Exit successfully (return code 0) with no arguments (outside CI)
- When the `CI` environment variable is set, exit 0 and print the exact string `Skipping swc-build-native in CI` — no other output
- Detect whether any `.rs` files in `crates/` or `turbopack/` directories changed since the last version bump
- Rebuild native binaries only when Rust changes are detected
- Clear stale `.node` binaries when no Rust changes exist (so prebuilt npm packages are used instead)

The script should be wired into the turborepo pipeline:
- `packages/next-swc/package.json` must have a `build` script that invokes `maybe-build-native`
- `packages/next-swc/turbo.json` must define a `build` task under the `tasks` key with:
  - `inputs` array containing at least the `crates` directory and files matching `Cargo*`
  - `env` array containing `CI`

Additionally, the `scripts/build-native.ts` type generation should be improved to use prettier via stdin (`--stdin-filepath`) instead of writing files before formatting. The script must not use `--write` with prettier.

After implementing the code changes, update the `AGENTS.md` rebuild instructions:
- Remove the separate commands `pnpm swc-build-native` (standalone) and `pnpm turbo build build-native`
- Add a line indicating that for Turbopack/Rust edits, `pnpm build` is sufficient

## Files to Look At

- `packages/next-swc/` — where the build automation script (`maybe-build-native.mjs`) should live
- `packages/next-swc/package.json` — needs a `build` script entry invoking `maybe-build-native`
- `packages/next-swc/turbo.json` — turborepo task configuration for `@next/swc` with Rust-relevant build task
- `scripts/build-native.ts` — type generation and prettier formatting
- `AGENTS.md` — developer rebuild instructions that reference `swc-build-native`
