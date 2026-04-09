# Task: Fix Pipeline Watermark Assertions

## Problem

The `WatermarkPart` struct in the indexer pipeline has invariant checks that use `debug_assert!` macros. These checks are meant to catch unrecoverable states where:

1. Two watermark parts being combined are from different checkpoints
2. The batch row count exceeds the total row count
3. Attempting to take more rows than available

However, `debug_assert!` is removed in release builds, meaning these invariant violations go undetected in production. This could allow corrupted data to propagate silently through the pipeline.

## Location

The relevant code is in `crates/sui-indexer-alt-framework/src/pipeline/mod.rs`, specifically in the `WatermarkPart` struct's `add()` and `take()` methods.

## Requirements

Change the assertion macros so that these invariant violations cause panics in all build configurations (debug AND release), not just debug builds. The specific invariants that must be enforced are:

1. When adding two `WatermarkPart` values, they must be from the same checkpoint
2. After adding, the batch row count must not exceed the total row count
3. When taking rows from a `WatermarkPart`, you cannot take more rows than are available in the batch

## Notes

- Review the existing `WatermarkPart` implementation and its current assertion usage
- Ensure appropriate error messages are preserved when changing the assertion macros
- The fix should be minimal and focused on the assertion macro changes only
