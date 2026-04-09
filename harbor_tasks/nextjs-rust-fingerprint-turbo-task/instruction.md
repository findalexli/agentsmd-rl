# Deduplicate Rust input globs in turbo config and add sccache passthrough

## Problem

The `packages/next-swc/turbo.jsonc` file has a maintenance problem: every Rust-related turbo task (`build-native`, `build-native-release`, `build-wasm`, `rust-check-clippy`, `test-cargo-unit`, etc.) repeats the same long list of Rust source input globs (`../../.cargo/**`, `../../crates/**`, `../../turbopack/crates/**`, `../../Cargo.toml`, `../../Cargo.lock`, `../../rust-toolchain.toml`, etc.). This duplication makes the config fragile — adding a new Rust source directory or changing exclusion patterns requires updating every single task definition.

Additionally, the root `turbo.json` does not pass through `SCCACHE_*` and `RUSTC_WRAPPER` environment variables, which means `sccache` cannot be used with turbo-managed Rust builds. The `CI` environment variable is also missing from `globalEnv`.

## Expected Behavior

1. There should be a single task that fingerprints all Rust inputs into a stamp file. All other Rust build/check tasks should depend on this fingerprint task and use the stamp file as their only Rust-related input, instead of repeating the full glob list.

2. A script should exist that writes the turbo-computed hash to a stamp file when running under turbo (when `TURBO_HASH` is set), and gracefully skips when not running under turbo.

3. The root `turbo.json` should pass through sccache-related environment variables (`RUSTC_WRAPPER`, `SCCACHE_*`) and include `CI` in `globalEnv`.

## Files to Look At

- `packages/next-swc/turbo.jsonc` — turbo task definitions for Rust builds and checks
- `packages/next-swc/package.json` — npm scripts for the next-swc package
- `turbo.json` — root turbo configuration (global env settings)
- `scripts/` — directory for build and maintenance scripts
