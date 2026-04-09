# Task: Add Retry Logic for Intrinsic Cursor Updates

## Problem

The `update_intrinsic_cursor` operation in the log service can fail due to transient race conditions that manifest as `StorageError::Precondition` errors. Currently, these failures are not retried, causing unnecessary operation failures when a simple retry would resolve the issue.

## Context

The code is in a Rust log service that manages distributed log cursors. The relevant function is in `rust/log-service/src/lib.rs` and currently calls `update_intrinsic_cursor` directly without any retry logic.

## What You Need to Do

1. Add the `backon` crate as a dependency to `rust/log-service/Cargo.toml` (use workspace = true)
2. Import the necessary types from `backon` in `rust/log-service/src/lib.rs`
3. Wrap the `update_intrinsic_cursor` call with exponential backoff retry logic:
   - Retry up to 3 times
   - Use 20ms minimum delay
   - Use 200ms maximum delay
   - Only retry on `StorageError::Precondition` errors (not all errors)
4. Ensure the code compiles successfully

## Key Requirements

- Use `ExponentialBuilder` from the `backon` crate
- The retry should use a closure that captures the necessary variables
- The retry condition must check that the error is a `StorageError::Precondition`
- Use `async move` properly within the retry closure
- Maintain the same error handling behavior (convert `wal3::Error` to `Status`)

## Files to Modify

- `rust/log-service/Cargo.toml` - add backon dependency
- `rust/log-service/src/lib.rs` - add retry logic around `update_intrinsic_cursor` call
- `Cargo.lock` - will be auto-updated by cargo

## Verification

After your changes:
1. `cargo check -p chroma-log-service` should pass
2. The code should follow the retry pattern using backon's `Retryable` trait
