# Task: Remove sui-data-ingestion-core dependency from sui-kv-rpc

## Problem Description

The `sui-kv-rpc` crate currently depends on `sui-data-ingestion-core`, but this dependency should be removed and replaced with `sui-storage` instead. The `get_checkpoint` function in `crates/sui-kv-rpc/src/v2/get_checkpoint.rs` uses APIs from `sui_data_ingestion_core` that need to be migrated to equivalent APIs in `sui_storage::object_store::util`.

## Files to Modify

1. `crates/sui-kv-rpc/Cargo.toml` - Update dependencies
2. `crates/sui-kv-rpc/src/v2/get_checkpoint.rs` - Update imports and code
3. `Cargo.lock` - Will be updated automatically by cargo

## Required Changes

### In Cargo.toml:
- Remove: `sui-data-ingestion-core.workspace = true`
- Add: `sui-storage.workspace = true`

### In get_checkpoint.rs:
- Remove the import: `use sui_data_ingestion_core::{CheckpointReader, create_remote_store_client};`
- Add the import: `use sui_storage::object_store::util::{build_object_store, fetch_checkpoint};`
- Replace the old code pattern:
  ```rust
  let client = create_remote_store_client(url, vec![], 60)?;
  let (checkpoint_data, _) =
      CheckpointReader::fetch_from_object_store(&client, sequence_number).await?;
  let checkpoint = sui_types::full_checkpoint_content::Checkpoint::from(
      std::sync::Arc::into_inner(checkpoint_data).unwrap(),
  );
  ```
- With the new simplified pattern:
  ```rust
  let store = build_object_store(&url, vec![]);
  let checkpoint = fetch_checkpoint(&store, sequence_number).await?;
  ```

## Testing Requirements

After making changes:
1. Run `cargo check -p sui-kv-rpc` to verify compilation
2. Run `cargo clippy -p sui-kv-rpc -- -D warnings` to ensure linting passes

## Notes

- Keep the existing license header at the top of the file
- Do not add any `#[allow(...)]` suppressions - fix underlying issues instead
- The new APIs handle the checkpoint conversion internally, so the code is simplified
