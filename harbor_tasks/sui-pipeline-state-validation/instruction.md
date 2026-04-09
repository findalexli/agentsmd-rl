# Fix Pipeline State Validation

The `WatermarkPart` struct in `crates/sui-indexer-alt-framework/src/pipeline/mod.rs` tracks the number of rows from a watermark that have been processed. It has two methods that modify state:

1. `add()` - combines rows from another WatermarkPart
2. `take()` - extracts a portion of rows from this part

Currently, these methods use `debug_assert!()` and `debug_assert_eq!()` to check for invalid state transitions. The problem is that `debug_assert!` macros are **ignored in release builds**, meaning invalid state can silently occur in production without being detected.

The following invariant checks need to be enforced in all builds (not just debug builds):

1. **In `add()`**: The checkpoint values must match between the two parts (currently `debug_assert_eq!`)
2. **In `add()`**: After adding rows, `batch_rows` must never exceed `total_rows` (not currently checked)
3. **In `take()`**: Cannot take more rows than are available (currently `debug_assert!`)

Your task is to modify the `WatermarkPart` implementation so that these conditions cause a panic in **all** builds (release and debug), not just debug builds.

## What to look for

- The `WatermarkPart` struct has fields: `batch_rows: usize` and `total_rows: usize`
- The `add()` method currently uses `debug_assert_eq!` to check checkpoint equality
- The `take()` method currently uses `debug_assert!` to check row availability

## Expected behavior

- Invalid state transitions should panic immediately with a descriptive message
- The code should compile without warnings or errors
- All existing tests should continue to pass

## Files to modify

- `crates/sui-indexer-alt-framework/src/pipeline/mod.rs` - Modify the `add()` and `take()` methods on `WatermarkPart`
