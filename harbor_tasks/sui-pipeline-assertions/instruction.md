# Fix Pipeline Watermark Assertions

## Problem

The `WatermarkPart` struct in the indexer pipeline uses `debug_assert!` and `debug_assert_eq!` for critical consistency checks. In release builds, these are compiled out, meaning the pipeline can enter an unrecoverable state (with corrupted watermark tracking) without any indication of failure.

Additionally, the `add()` method is missing a bounds check to ensure that `batch_rows` never exceeds `total_rows`, which would indicate a serious accounting error.

## Affected Code

File: `crates/sui-indexer-alt-framework/src/pipeline/mod.rs`

Look at the `WatermarkPart` struct and its `add()` and `take()` methods. These methods have debug-only assertions that should be promoted to always-on assertions, and the `add()` method needs an additional invariant check.

## Requirements

1. Change the checkpoint equality check in `add()` from a debug assertion to a regular assertion
2. Add a bounds check in `add()` to verify that `batch_rows` never exceeds `total_rows` after adding rows
3. Change the row availability check in `take()` from a debug assertion to a regular assertion

The error messages should clearly indicate what invariant was violated for easier debugging in production.

## Verification

After your changes:
- The crate should compile without errors (`cargo check -p sui-indexer-alt-framework`)
- Existing tests should pass (`cargo test -p sui-indexer-alt-framework --lib pipeline`)
