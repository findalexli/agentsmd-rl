# Upgrade imara-diff dependency to 0.2.0

The `ruff` codebase uses the `imara-diff` crate (currently pinned to 0.1.x) for computing line-level diffs in the formatter's development tooling. Version 0.2.0 of `imara-diff` has been released with several breaking API changes:

- The module structure has changed — some previously public modules are now private, so import paths need updating.
- The top-level diff computation function has been replaced with a struct-based API.
- The way you access diff statistics (additions/removals counts) has changed — instead of using a separate sink, the new API provides methods directly on the result type.

## Affected code

The file `crates/ruff_dev/src/format_dev.rs` uses `imara-diff` in the `Statistics::from_versions` method (around line 120). This method computes a histogram diff between two strings and extracts insertion/removal counts to calculate a similarity index.

## What needs to happen

1. Update the `imara-diff` version requirement in the workspace `Cargo.toml` to `0.2.0`.
2. Migrate all `imara-diff` usage in `crates/ruff_dev/src/format_dev.rs` to the new 0.2.0 API — fix imports and update the diff computation call site.
3. Ensure the code compiles and the `Statistics` logic remains correct.

Consult the `imara-diff` 0.2.0 API to determine the correct types, methods, and import paths.
