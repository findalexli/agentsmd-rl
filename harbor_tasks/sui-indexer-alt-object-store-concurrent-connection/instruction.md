# Task: Implement ConcurrentConnection Trait for ObjectStoreConnection

## Problem Description

The `ObjectStoreConnection` in `crates/sui-indexer-alt-object-store/src/lib.rs` currently has stub implementations for the `ConcurrentConnection` trait methods. These stubs either return `Ok(None)` or bail with "Pruning not supported by this store". Additionally, the `init_watermark` method ignores its `checkpoint_hi_inclusive` parameter and delegates to an incomplete implementation.

You need to implement proper functionality for:

1. **`ConcurrentConnection::reader_watermark()`** - Should return the current reader watermark (checkpoint_hi_inclusive and reader_lo values)

2. **`ConcurrentConnection::pruner_watermark()`** - Should return the pruner watermark with proper `wait_for_ms` calculation based on `pruner_timestamp_ms + delay - now`

3. **`ConcurrentConnection::set_reader_watermark()`** - Should update the reader_lo field in the watermark

4. **`ConcurrentConnection::set_pruner_watermark()`** - Should update the pruner_hi field in the watermark

5. **`Connection::init_watermark()`** - Should properly use the `checkpoint_hi_inclusive` parameter to create/initialize watermarks

## Key Requirements

### Watermark Format Migration
The existing watermark format stores `checkpoint_hi_inclusive` as a required `u64`. The new format makes it `Option<u64>` and adds three new fields:
- `reader_lo: u64` - The lowest checkpoint available for reading
- `pruner_hi: u64` - The highest checkpoint that has been pruned
- `pruner_timestamp_ms: u64` - Timestamp when pruning last ran

Your implementation must:
1. Handle both the old format (for backwards compatibility) using `#[serde(default)]`
2. Migrate old format watermarks to the new format when encountered
3. Use `reader_lo <= checkpoint_hi_inclusive` as a visibility check for read operations

### Helper Functions
You'll need to implement:
- `watermark_path(pipeline: &str) -> ObjectPath` - Returns path like `_metadata/watermarks/{pipeline}.json`
- `get_watermark_for_read()` - For reading watermarks with visibility check (reader_lo <= checkpoint)
- `get_watermark_for_write()` - For reading watermarks with e_tag/version for conditional writes
- `set_watermark()` - For writing watermarks with proper concurrency control

### Concurrency Control
All watermark writes must use proper concurrency control via the object store's `PutMode::Update` with e_tag and version to prevent lost updates.

## Testing

The crate has comprehensive unit tests. Run them with:
```bash
cargo test -p sui-indexer-alt-object-store --lib
```

Key test cases to verify your implementation:
- `test_reader_watermark_roundtrip` - Tests reading and setting reader watermarks
- `test_pruner_watermark_wait_for_ms` - Tests pruner watermark wait time calculation
- `test_init_watermark_migrates_legacy_format` - Tests migration from old format
- `test_init_watermark_returns_existing_on_conflict` - Tests idempotent initialization

## Files to Modify

- `crates/sui-indexer-alt-object-store/src/lib.rs` - Main implementation file

## Notes

- Use `std::time::{SystemTime, UNIX_EPOCH}` for timestamp calculations
- Use `u128` for intermediate calculations to avoid overflow, then `saturating_sub` and `i64::try_from`
- The `InMemory` object store from `object_store::memory::InMemory` is useful for testing
- Review the trait definitions in `sui_indexer_alt_framework_store_traits` to understand the expected types
