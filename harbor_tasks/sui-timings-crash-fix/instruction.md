# Fix Crash in Execution Time Estimator

## Problem

The `ExecutionTimeObserver` in `crates/sui-core/src/authority/execution_time_estimator.rs` is crashing with an assertion failure when processing execution time observations.

The crash occurs in `record_local_observations_timing()` when the number of execution timings produced exceeds the number of original PTB (Programmable Transaction Block) commands. This can happen in certain edge cases where the execution produces more timing entries than expected.

## Symptom

The assertion at the start of the function:
```rust
assert!(tx.commands.len() >= timings.len());
```

fails and causes a panic when `timings.len() > tx.commands.len()`.

## Goal

Modify `crates/sui-core/src/authority/execution_time_estimator.rs` to handle the case where execution produces more timings than the original PTB commands, without crashing.

The fix should:
1. Remove the crash-inducing assertion
2. Gracefully handle the case when `timings.len() > tx.commands.len()` by using only the trailing portion of timings that correspond to the original commands
3. Log a warning when this situation occurs (the codebase uses the `tracing` crate for logging with macros like `warn!`, `debug!`)
4. Preserve the early return behavior for when the epoch is ending (the `epoch_store.upgrade()` check)

## Relevant Code

The function `record_local_observations_timing()` around line 312-320 contains the problematic assertion. The function processes per-command execution timings and updates moving averages for congestion control.

## Testing

After your changes:
1. `cargo check -p sui-core` should pass
2. `cargo test -p sui-core --lib execution_time` should pass
3. `cargo xclippy` should pass (per repo conventions in CLAUDE.md)

## Notes

- Read the existing function carefully to understand the control flow
- The fix should use the trailing timings (last N entries where N = tx.commands.len()) when there are more timings than commands
- Per CLAUDE.md: Never use `#[allow(...)]` suppressions - fix underlying issues
- Per CLAUDE.md: Use `warn!` macro from tracing for warnings
