# Task: Remove sui-data-ingestion-core dependency from sui-kv-rpc

## Problem Description

The `sui-kv-rpc` crate currently depends on `sui-data-ingestion-core` which should be removed and replaced with `sui-storage`. The `get_checkpoint` function in the KV RPC crate needs to continue fetching checkpoint data, but using `sui-storage` APIs instead of the deprecated `sui_data_ingestion_core` utilities.

## Files to Modify

1. `crates/sui-kv-rpc/Cargo.toml` - Update dependencies
2. `crates/sui-kv-rpc/src/v2/get_checkpoint.rs` - Update code to use new APIs
3. `Cargo.lock` - Will be updated automatically by cargo

## Dependencies

In `crates/sui-kv-rpc/Cargo.toml`, replace the `sui-data-ingestion-core` dependency with `sui-storage`.

## Code Requirements

The `get_checkpoint` function must continue to work correctly. The object store utilities for checkpoint operations are available in `sui_storage::object_store::util` and the code must compile successfully.

After making changes:
1. Run `cargo check -p sui-kv-rpc` to verify compilation
2. Run `cargo clippy -p sui-kv-rpc -- -D warnings` to ensure linting passes

## Notes

- Keep the existing license header at the top of the file
- Do not add any `#[allow(...)]` suppressions - fix underlying issues instead

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)`
