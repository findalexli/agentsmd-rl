# Automate native SWC build in pnpm build pipeline

## Problem

Developers frequently forget to run `pnpm swc-build-native` after pulling Rust changes in the `crates/` or `turbopack/` directories, leading to confusing runtime errors from stale native binaries. Conversely, rebuilding native binaries when nothing changed wastes significant time. The current workflow requires developers to manually decide which build command to run based on what they changed.

## Expected Behavior

`pnpm build` should automatically handle native SWC binary rebuilding. The build automation for `@next/swc` lives in a script named `maybe-build-native.mjs` inside `packages/next-swc/` and must:

- Exit successfully (return code 0) with no arguments (outside CI)
- When the `CI` environment variable is set, exit 0 and print the exact string `Skipping swc-build-native in CI` — no other output
- Detect whether any `.rs` files in `crates/` or `turbopack/` directories changed since the last version bump
- Define a function named `hasRustChanges` that accepts a commit hash and returns whether Rust source files changed
- Define a function named `getVersionBumpCommit` that returns the git commit hash of the last version bump (found by searching git log for `"version":` in `packages/next/package.json`)
- Rebuild native binaries only when Rust changes are detected
- Clear stale `.node` binaries when no Rust changes exist (so prebuilt npm packages are used instead)

The script must include `*.rs` or `**/*.rs` glob patterns when checking for Rust file changes.

The script should be wired into the turborepo pipeline:
- `packages/next-swc/package.json` must have a `build` script that invokes `node maybe-build-native.mjs`
- `packages/next-swc/turbo.json` must define a `build` task under the `tasks` key with:
  - `inputs` array containing at least the `crates` directory and files matching `Cargo*`
  - `env` array containing `CI`

Additionally, `scripts/build-native.ts` must use prettier via stdin (`--stdin-filepath`) instead of writing files before formatting. The script must not use `--write` with prettier (neither single-quoted `'--write'` nor double-quoted `"--write"`).

After implementing the code changes, update the `AGENTS.md` rebuild instructions:
- Remove the line `**Edited Turbopack (Rust)?** → pnpm swc-build-native`
- Remove the line `**Edited both?** → pnpm turbo build build-native`
- Add a line containing the words `Turbopack`, `Rust`, and `pnpm build` on the same line to indicate that for Turbopack/Rust edits, `pnpm build` is sufficient

## Files to Look At

- `packages/next-swc/` — where the build automation script (`maybe-build-native.mjs`) should live
- `packages/next-swc/package.json` — needs a `build` script entry invoking `node maybe-build-native.mjs`
- `packages/next-swc/turbo.json` — turborepo task configuration for `@next/swc` with Rust-relevant build task
- `scripts/build-native.ts` — type generation and prettier formatting; must use `--stdin-filepath` not `--write`
- `AGENTS.md` — developer rebuild instructions that reference `swc-build-native`