# Task: Implement ConcurrentConnection Trait for ObjectStoreConnection

## Problem Description

The `ObjectStoreConnection` in the sui-indexer-alt-object-store crate has stub implementations for the `ConcurrentConnection` trait methods. These stubs either return `Ok(None)` or error with "Pruning not supported by this store". Additionally, the `init_watermark` method ignores its checkpoint parameter and delegates to an incomplete implementation.

## What Needs to Be Fixed

The following trait methods are not working correctly:

1. **`reader_watermark()`** - Currently returns `Ok(None)` instead of actual watermark data with checkpoint and reader position information

2. **`pruner_watermark()`** - Currently returns `Ok(None)` instead of actual watermark data with a computed wait time based on how long until pruning can proceed

3. **`set_reader_watermark()`** - Currently returns an error instead of updating the reader position in the watermark

4. **`set_pruner_watermark()`** - Currently returns an error instead of updating the pruner position in the watermark

5. **`init_watermark()`** - Currently ignores the `checkpoint_hi_inclusive` parameter instead of using it to properly initialize watermark positions

## Watermark Data

The watermark stores information about how far indexer processing has progressed. The key fields are:
- `checkpoint_hi_inclusive` - The highest checkpoint that has been committed
- `reader_lo` - The lowest checkpoint available for reading (must be <= checkpoint for visibility)
- `pruner_hi` - The highest checkpoint that has been pruned
- `pruner_timestamp_ms` - Timestamp of last pruning operation

The existing watermark format needs to be extended with new fields to track reader and pruner positions. The system must handle backwards compatibility with watermarks that don't yet have these new fields.

## Implementation Notes

- Watermarks are stored as JSON files at path `_metadata/watermarks/{pipeline}.json`
- Reads must filter out watermarks where the checkpoint is less than `reader_lo` (visibility check)
- Writes must use proper concurrency control (e_tag/version) to prevent lost updates
- Wait time calculations must use `u128` for intermediate arithmetic to avoid overflow, then convert to `i64` using saturating subtraction

## Verification

Run the unit tests:
```bash
cargo test -p sui-indexer-alt-object-store --lib
```

The implementation must make the following test cases pass. Each test exercises a specific behavior that must work correctly:

### Reader Watermark Tests
- **`test_reader_watermark_roundtrip`** — Reading then writing the reader watermark returns the written value (read/write roundtrip)
- **`test_set_pruner_watermark`** — Setting the pruner watermark updates the stored value

### Pruner Watermark Tests
- **`test_pruner_watermark_wait_for_ms`** — Computing wait time for pruning uses correct u128 intermediate arithmetic to avoid overflow

### Init Watermark Tests
- **`test_init_watermark_fresh_with_checkpoint`** — Initializing watermark with a checkpoint value properly sets `checkpoint_hi_inclusive`
- **`test_init_watermark_migrates_legacy_format`** — Watermarks stored in the old format (without reader_lo/pruner_hi fields) are migrated correctly on first read
- **`test_init_watermark_returns_existing_on_conflict`** — When a watermark already exists (AlreadyExists error), the existing value is returned rather than an error

## File to Modify

- `crates/sui-indexer-alt-object-store/src/lib.rs` - Main implementation file

## Notes

- Use `std::time::{SystemTime, UNIX_EPOCH}` for timestamp calculations
- Use `u128` for intermediate calculations to avoid overflow, then `saturating_sub` and `i64::try_from`
- The `InMemory` object store from `object_store::memory::InMemory` is useful for testing
- Review the trait definitions in `sui_indexer_alt_framework_store_traits` to understand the expected types

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)`
