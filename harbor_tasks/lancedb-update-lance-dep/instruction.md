# Task: Update Lance Dependency to v3.1.0-beta.2

## Problem

The lancedb repository currently depends on the Lance Rust workspace at version `v3.0.0-beta.5`. This needs to be updated to version `v3.1.0-beta.2` to incorporate the latest improvements and bug fixes from the upstream Lance project.

## Files to Modify

You need to update the Lance dependency version in the following files:

1. **Cargo.toml** - Update all `lance-*` workspace dependencies from `3.0.0-beta.5` to `3.1.0-beta.2`
2. **java/pom.xml** - Update `lance-core.version` property from `3.0.0-beta.5` to `3.1.0-beta.2`
3. **Cargo.lock** - Update to reflect the new dependency versions (this is typically auto-generated via `cargo update`)

## Requirements

- All Lance-related dependencies in `Cargo.toml` must use version `3.1.0-beta.2` with tag `v3.1.0-beta.2`
- The `lance-core.version` in `java/pom.xml` must be updated to `3.1.0-beta.2`
- After updating, `cargo check` should pass without errors
- After updating, `cargo clippy -- -D warnings` should pass without warnings

## Notes

- The Lance dependencies use git references to `https://github.com/lance-format/lance.git`
- There are 14 Lance-related workspace dependencies in Cargo.toml:
  - `lance`, `lance-core`, `lance-datagen`, `lance-file`, `lance-io`, `lance-index`
  - `lance-linalg`, `lance-namespace`, `lance-namespace-impls`, `lance-table`
  - `lance-testing`, `lance-datafusion`, `lance-encoding`, `lance-arrow`
- The new version may have removed some dependencies (like the `lance-geo` crate and related geo-spatial dependencies), so the Cargo.lock will likely shrink

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)`
