# Task: Implement ConcurrentConnection for ObjectStoreConnection

## Problem Description

The `ObjectStoreConnection` in `sui-indexer-alt-object-store` has stub implementations for the `ConcurrentConnection` trait methods and an incomplete `init_watermark` method. These need to be properly implemented to support backwards indexing functionality.

## Current Behavior

The following methods in `crates/sui-indexer-alt-object-store/src/lib.rs` are not fully implemented:

1. **`ConcurrentConnection::reader_watermark`** - Currently returns `Ok(None)`, indicating no reader watermark is available
2. **`ConcurrentConnection::pruner_watermark`** - Currently returns `Ok(None)`, indicating no pruner watermark is available  
3. **`ConcurrentConnection::set_reader_watermark`** - Currently calls `bail!("Pruning not supported by this store")`
4. **`ConcurrentConnection::set_pruner_watermark`** - Currently calls `bail!("Pruning not supported by this store")`
5. **`Connection::init_watermark`** - Currently delegates to `reader_watermark` which returns None, instead of implementing proper watermark initialization

## Expected Behavior

These methods should properly interact with the object store to read and write watermark data:

- `reader_watermark` should return `Some(ReaderWatermark)` when a valid watermark exists in the object store
- `pruner_watermark` should compute and return `Some(PrunerWatermark)` with proper `wait_for_ms` calculation
- `set_reader_watermark` should update the `reader_lo` field in the stored watermark and return `Ok(true)`
- `set_pruner_watermark` should update the `pruner_hi` and `pruner_timestamp_ms` fields and return `Ok(true)`
- `init_watermark` should:
  - Create a new watermark file if one doesn't exist
  - Handle the `AlreadyExists` case by reading and potentially migrating existing watermarks
  - Support migration from a legacy watermark format (missing `reader_lo`, `pruner_hi`, `pruner_timestamp_ms` fields)

## Key Implementation Details

The watermark format stored in the object store needs these fields:
- `epoch_hi_inclusive: u64`
- `checkpoint_hi_inclusive: Option<u64>`
- `tx_hi: u64`
- `timestamp_ms_hi_inclusive: u64`
- `reader_lo: u64`
- `pruner_hi: u64`
- `pruner_timestamp_ms: u64`

Watermark files are stored at path: `_metadata/watermarks/{pipeline}.json`

For pruner watermark calculation, use saturating arithmetic to handle edge cases:
- `pruner_ready_ms = pruner_timestamp_ms + delay_ms`
- `wait_for_ms = pruner_ready_ms.saturating_sub(now_ms)`
- Return error if the result overflows `i64`

## Testing

The crate includes comprehensive unit tests that verify the expected behavior. Run `cargo test -p sui-indexer-alt-object-store` to check your implementation.

Key test scenarios to make pass:
- `test_reader_watermark_roundtrip` - setting and reading reader watermark
- `test_pruner_watermark_wait_for_ms` - computing pruner wait time
- `test_pruner_watermark_saturates_when_ready` - saturating subtraction behavior
- `test_init_watermark_migrates_legacy_format` - legacy format migration

## References

- Look at the existing `committer_watermark` and `set_committer_watermark` implementations for patterns on how to interact with the object store
- The `object_store` crate provides the underlying storage interface
- Check the `sui_indexer_alt_framework_store_traits` crate for trait definitions
