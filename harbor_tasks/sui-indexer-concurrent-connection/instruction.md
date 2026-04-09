# Task: Implement ConcurrentConnection for ObjectStoreConnection

## Problem

The `ObjectStoreConnection` in `sui-indexer-alt-object-store` has stub implementations for the `ConcurrentConnection` trait methods. Currently:

- `reader_watermark()` always returns `Ok(None)`
- `pruner_watermark()` always returns `Ok(None)`
- `set_reader_watermark()` fails with "Pruning not supported by this store"
- `set_pruner_watermark()` fails with "Pruning not supported by this store"

These stubs prevent the object store from being used with features that require concurrent access patterns, such as backwards indexing.

Additionally, the `init_watermark()` method needs to properly handle:
1. Creating a new watermark when none exists
2. Reading existing watermarks in the current format
3. Migrating from the legacy watermark format (which had different fields) to the new format

## Requirements

Implement the `ConcurrentConnection` trait methods for `ObjectStoreConnection` so they actually read from and write to the object store:

1. **`reader_watermark`** - Should return the current reader watermark (checkpoint_hi_inclusive and reader_lo) if available
2. **`pruner_watermark`** - Should calculate `wait_for_ms` based on the stored pruner_timestamp_ms and the provided delay, using saturating arithmetic to prevent overflow/underflow
3. **`set_reader_watermark`** - Should update the reader_lo field in the stored watermark
4. **`set_pruner_watermark`** - Should update the pruner_hi field in the stored watermark

For `init_watermark`:
- When creating a new watermark, initialize all required fields including reader_lo and pruner_hi
- When reading an existing watermark, check if it's in the legacy format (missing reader_lo, pruner_hi, or pruner_timestamp_ms fields) and migrate it to the new format
- Return the checkpoint_hi_inclusive and reader_lo values from the stored watermark

## Key Implementation Notes

- Watermarks are stored as JSON files at path `_metadata/watermarks/{pipeline}.json`
- The watermark structure has changed - the new format includes reader_lo, pruner_hi, and pruner_timestamp_ms fields
- The new `checkpoint_hi_inclusive` field is `Option<u64>` (was required `u64` in legacy format)
- You may need to refactor the existing committer watermark methods to share code with the new concurrent connection methods
- Use proper error handling for overflow/underflow scenarios in pruner_watermark calculations

## Target File

`crates/sui-indexer-alt-object-store/src/lib.rs`

## Testing

The crate includes comprehensive unit tests. Run them with:
```bash
cargo test -p sui-indexer-alt-object-store --lib
```

All tests should pass after your implementation.
