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

- `reader_watermark` should return `Some(ReaderWatermark)` when a valid watermark exists in the object store at `_metadata/watermarks/{pipeline}.json`, filtering results where `reader_lo <= checkpoint_hi_inclusive` (the reader's low watermark must not exceed the committed checkpoint). If `checkpoint_hi_inclusive < reader_lo`, return `None`.
- `pruner_watermark` should compute and return `Some(PrunerWatermark)` with proper `wait_for_ms` calculation using saturating arithmetic (`pruner_ready_ms = pruner_timestamp_ms + delay_ms`, `wait_for_ms = pruner_ready_ms.saturating_sub(now_ms)`). Return an error if the result overflows `i64`.
- `set_reader_watermark` should update the `reader_lo` field in the stored watermark using conditional put with version/e_tag handling, and return `Ok(true)`
- `set_pruner_watermark` should update the `pruner_hi` and `pruner_timestamp_ms` fields using conditional put with version/e_tag handling, and return `Ok(true)`
- `init_watermark` should:
  - Create a new watermark file at `_metadata/watermarks/{pipeline}.json` if one doesn't exist, using `reader_lo = checkpoint_hi_inclusive + 1` when a checkpoint is provided, or `reader_lo = 0` when no checkpoint is provided
  - Handle the `AlreadyExists` case by reading the existing watermark and returning its values
  - Support migration from a legacy watermark format (missing `reader_lo`, `pruner_hi`, `pruner_timestamp_ms` fields) - when these fields are missing, initialize them to appropriate default values and write the migrated watermark back to the store

## Key Implementation Details

The watermark format stored in the object store needs these 7 fields:
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

Use conditional put operations (with version/e_tag) for `set_reader_watermark` and `set_pruner_watermark` to handle concurrent updates safely.

## Testing

The crate includes comprehensive unit tests. You must implement the following tests (they don't exist yet and need to be written):

1. **`test_reader_watermark_roundtrip`** - Verify that `set_reader_watermark` followed by `reader_watermark` returns the updated value with proper filtering

2. **`test_pruner_watermark_wait_for_ms`** - Verify that `pruner_watermark` correctly computes `wait_for_ms` based on the delay and current time

3. **`test_pruner_watermark_saturates_when_ready`** - Verify that when the pruner is ready (current time >= pruner_timestamp_ms + delay), `wait_for_ms` saturates to 0 instead of underflowing

4. **`test_set_pruner_watermark`** - Verify that `set_pruner_watermark` updates the watermark and returns `Ok(true)`

5. **`test_init_watermark_fresh_with_checkpoint`** - Verify that `init_watermark` creates a new watermark with `reader_lo = checkpoint + 1` when no watermark exists and a checkpoint is provided

6. **`test_init_watermark_migrates_legacy_format`** - Verify that `init_watermark` properly migrates legacy watermarks that are missing the `reader_lo`, `pruner_hi`, or `pruner_timestamp_ms` fields, writing the migrated data back to the store

Run `cargo test -p sui-indexer-alt-object-store` to check your implementation.

## References

- Look at the existing `committer_watermark` and `set_committer_watermark` implementations for patterns on how to interact with the object store
- The `object_store` crate provides the underlying storage interface
- Check the `sui_indexer_alt_framework_store_traits` crate for trait definitions
