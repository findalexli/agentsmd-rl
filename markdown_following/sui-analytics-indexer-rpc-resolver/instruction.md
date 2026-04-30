# Task: Migrate Analytics Indexer to sui-rpc-resolver

## Problem

The analytics indexer currently uses a custom 2-level package cache (`PackageCache` in `package_store/mod.rs`) for resolving type layouts. This cache has a critical flaw: only the in-memory layer is invalidated for system packages on epoch changes, while the RocksDB layer persists stale data. This leads to stalled pipelines when the display registry rolls out new system packages.

The custom cache implementation is complex, error-prone, and duplicates functionality that now exists in the `sui-rpc-resolver` crate.

## Your Task

Migrate the analytics indexer from the custom `PackageCache` to use `sui-rpc-resolver` with its built-in caching. The migration requires:

1. **Remove the old package cache** - Delete `src/package_store/mod.rs` and remove `pub mod package_store` from `src/lib.rs`

2. **Add a new SystemPackageEviction handler** - Create `src/handlers/system_package_eviction.rs` that:
   - Monitors checkpoint processing for epoch changes
   - Evicts system packages from the cache when epochs change
   - Implements `Processor` and `sequential::Handler` traits from `sui_indexer_alt_framework`

3. **Update all handlers** - Modify the processor structs in `src/handlers/tables/`:
   - Change `df.rs`, `event.rs`, `wrapped_object.rs`: Replace `Arc<PackageCache>` with `Arc<PackageStoreWithLruCache<RpcPackageStore>>`
   - Change `object.rs`: Add an `rpc_client` field and implement `get_original_package_id` method locally
   - Update all resolver usage from `package_cache.resolver_for_epoch(epoch)` to `Resolver::new(package_cache.clone())`

4. **Update the indexer** - Modify `src/indexer.rs` to:
   - Use `RpcPackageStore::new(&rpc_url).with_cache()` instead of `PackageCache::new()`
   - Remove the `work_dir`/`tempfile` logic
   - Register the `SystemPackageEviction` pipeline

5. **Update pipeline** - Modify `src/pipeline.rs` to pass `rpc_url` to `ObjectProcessor::new()`

6. **Update dependencies** - Modify `Cargo.toml` to:
   - Add `sui-rpc-resolver` dependency
   - Remove `lru`, `typed-store`, and `tempfile` dependencies

## Key Files to Modify

- `crates/sui-analytics-indexer/src/handlers/system_package_eviction.rs` (new file)
- `crates/sui-analytics-indexer/src/handlers/mod.rs`
- `crates/sui-analytics-indexer/src/handlers/tables/df.rs`
- `crates/sui-analytics-indexer/src/handlers/tables/event.rs`
- `crates/sui-analytics-indexer/src/handlers/tables/object.rs`
- `crates/sui-analytics-indexer/src/handlers/tables/wrapped_object.rs`
- `crates/sui-analytics-indexer/src/indexer.rs`
- `crates/sui-analytics-indexer/src/lib.rs`
- `crates/sui-analytics-indexer/src/pipeline.rs`
- `crates/sui-analytics-indexer/src/store/mod.rs`
- `crates/sui-analytics-indexer/Cargo.toml`
- `Cargo.lock`

## File to Delete

- `crates/sui-analytics-indexer/src/package_store/mod.rs`

## Expected Outcome

After the migration:
- The crate compiles successfully (`cargo check -p sui-analytics-indexer`)
- All handlers use `PackageStoreWithLruCache<RpcPackageStore>` instead of `PackageCache`
- The `SystemPackageEviction` handler exists and properly evicts system packages on epoch changes
- Old dependencies (`lru`, `typed-store`, `tempfile`) are removed from Cargo.toml
- The `sui-rpc-resolver` dependency is added to Cargo.toml

## Notes

- The migration simplifies the codebase by removing ~230 lines of custom caching code
- The new approach handles system package cache invalidation more reliably
- Some handlers will need to use `Resolver::new()` instead of `resolver_for_epoch()`
- The `ObjectProcessor` needs a local RPC client since it needs to resolve original package IDs

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
