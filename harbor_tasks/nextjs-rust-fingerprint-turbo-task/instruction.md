# Deduplicate Rust input globs in turbo config and add sccache passthrough

## Problem

The `packages/next-swc/turbo.jsonc` file has a maintenance problem: every Rust-related turbo task repeats the same long list of Rust source input globs (`../../.cargo/**`, `../../crates/**`, `../../turbopack/crates/**`, `../../Cargo.toml`, `../../Cargo.lock`, `../../rust-toolchain.toml`, etc.). This duplication makes the config fragile — adding a new Rust source directory or changing exclusion patterns requires updating every single task definition.

Additionally, the root `turbo.json` does not pass through `SCCACHE_*` and `RUSTC_WRAPPER` environment variables, which means `sccache` cannot be used with turbo-managed Rust builds. The `CI` environment variable is also missing from `globalEnv`.

## Expected Behavior

1. There should be a single turbo task named `rust-fingerprint` that fingerprints all Rust inputs into a stamp file located at `../../target/.rust-fingerprint`. All other Rust build/check tasks must:
   - Add `rust-fingerprint` to their `dependsOn` list
   - Replace their repeated Rust glob inputs with only the stamp file path `../../target/.rust-fingerprint`
   - Remove the old duplicated Rust input globs from their `inputs` arrays

2. A script `scripts/rust-fingerprint.js` must exist that:
   - Reads the `TURBO_HASH` environment variable
   - When `TURBO_HASH` is set: writes its value to `target/.rust-fingerprint` (resolved from the script directory) and exits 0
   - When `TURBO_HASH` is not set: prints a message containing the word "skipping" (case-insensitive) and exits 0

3. The root `turbo.json` must:
   - Include `CI` in the `globalEnv` array
   - Include both `RUSTC_WRAPPER` and `SCCACHE_*` in the `globalPassThroughEnv` array

4. The `packages/next-swc/turbo.jsonc` must define a `rust-fingerprint` task with:
   - `inputs` globs that cover all Rust sources: at minimum `../../.cargo/**`, `../../crates/**`, `../../turbopack/crates/**`, `../../**/Cargo.toml` (or `../../Cargo.toml`), `../../Cargo.lock`, `../../rust-toolchain.toml`
   - `outputs`: an array containing `../../target/.rust-fingerprint`
   - `cache`: `false`

5. The `packages/next-swc/package.json` must define an npm script entry `"rust-fingerprint": "node ../../scripts/rust-fingerprint.js"` in its `scripts` object.

6. All scripts in the `scripts/` directory must have valid Node.js syntax (pass `node --check`):
   - `scripts/check-manifests.js`
   - `scripts/check-is-release.js`
   - `scripts/check-unused-turbo-tasks.mjs`
   - `scripts/pull-turbo-cache.js`
   - `scripts/turbo-cache.mjs`
   - `scripts/rust-fingerprint.js`
   - `scripts/build-native.ts`
   - `scripts/validate-externals-doc.js`
   - `scripts/git-configure.mjs`
   - `scripts/install-native.mjs`
   - `run-tests.js` (at repo root)
   - `run-evals.js` (at repo root)

7. The following config files must pass Prettier formatting checks:
   - `package.json`
   - `turbo.json`
   - `packages/next-swc/turbo.jsonc`
   - `packages/next-swc/package.json`

8. `turbo.json` must be valid JSON (parseable by `python3 -m json.tool`).

9. `packages/next-swc/turbo.jsonc` must be valid JSONC (parseable after stripping `//` comments and trailing commas before `}` or `]`).

10. Both `package.json` files must be valid JSON and include required scripts:
    - Root `package.json`: must have `build` and `lint` scripts
    - `packages/next-swc/package.json`: must have `build-native` and `rust-check-fmt` scripts

## Files to Look At

- `packages/next-swc/turbo.jsonc` — turbo task definitions for Rust builds and checks
- `packages/next-swc/package.json` — npm scripts for the next-swc package
- `turbo.json` — root turbo configuration (global env settings)
- `scripts/` — directory for build and maintenance scripts

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
