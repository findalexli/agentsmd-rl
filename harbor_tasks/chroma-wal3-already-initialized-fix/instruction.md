# Fix wal3 Manifest Manager Error Handling Bug

## Problem

The wal3 (write-ahead log) replicated manifest manager has a bug in its error handling that causes `open_or_initialize` callers to retry indefinitely when racing to initialize a log that another process has already initialized.

## Symptom

When multiple processes race to initialize the same replicated log:
1. The first process successfully initializes the log in Spanner
2. The second process gets a `AlreadyExists` error from Spanner
3. The manifest manager incorrectly maps this to an error variant that signals "retry" rather than "already done"
4. The caller sees the retry signal and retries indefinitely
5. This results in an infinite retry loop instead of recognizing the log is already initialized

## What You Need to Do

1. **Find the error handling code** in the manifest manager that processes Spanner's `AlreadyExists` error code
2. **Fix the error mapping** so that when Spanner returns `AlreadyExists` (meaning the log was already initialized by another process), the manifest manager returns an error variant that correctly signals "already initialized" rather than "retry needed"
3. **Update the test** in `rust/wal3/tests/repl_02_initialized_init_again.rs` to verify the specific error variant that indicates "already initialized" — not just that an error occurred
4. **Create a new test** at `rust/wal3/tests/repl_06_parallel_open_or_initialize.rs` that exercises concurrent `open_or_initialize` calls to verify the race condition is handled correctly

## Files to Modify

- `rust/wal3/src/interfaces/repl/manifest_manager.rs` — fix the error return
- `rust/wal3/tests/repl_02_initialized_init_again.rs` — tighten test assertions
- `rust/wal3/tests/repl_06_parallel_open_or_initialize.rs` — add concurrent race test

## Detailed Requirements

### manifest_manager.rs

The file has an error handling block that checks `status.code() == Code::AlreadyExists`. Currently this block returns the wrong error variant. Change it to return the correct variant that indicates the log was already initialized (not a retryable contention error).

### repl_02 test

The existing test `test_k8s_mcmr_integration_repl_02_initialized_init_again` in `rust/wal3/tests/repl_02_initialized_init_again.rs` currently uses `result.is_err()` to check that the second initialization fails. Update this assertion to verify the **specific error variant** that means "already initialized".

Specifically, the test must use the expression:
```rust
matches!(result, Err(Error::AlreadyInitialized))
```

You will need to import the `Error` type from the `wal3` crate in the test file. The test must NOT use `result.is_err()` after this change.

### repl_06 test

Create a new test in `rust/wal3/tests/repl_06_parallel_open_or_initialize.rs` with:

- The async test function named `test_k8s_mcmr_integration_repl_06_parallel_open_or_initialize`
- A call to `open_or_initialize` from multiple concurrent tasks (32 tasks)
- The variable `num_writers = 32` (exactly this expression, with spaces as shown)

The test should verify that when multiple concurrent `open_or_initialize` calls race to initialize the same log, all calls complete successfully (the winner initializes, and the others receive an "already initialized" response that is handled as success, not retry).
