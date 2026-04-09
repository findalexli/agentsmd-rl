# Fix Panic in Execution Time Estimator

There's a bug in the execution time estimator that causes a panic (assertion failure) when the number of execution timings exceeds the number of PTB (Programmable Transaction Block) commands.

## Problem

In `crates/sui-core/src/authority/execution_time_estimator.rs`, the `process_execution_time_observation` function has an assertion that can fail:

```rust
assert!(tx.commands.len() >= timings.len());
```

This assumption doesn't hold when transactions involve shared objects and coin reservations - the execution can produce more timings than the original PTB commands.

## Your Task

Fix this issue by:
1. Removing the panic-inducing assertion
2. Adding defensive logic to handle the case where `timings.len() > tx.commands.len()`
3. When there are excess timings, slice to use only the trailing timings (the last `tx.commands.len()` entries)
4. Adding appropriate warning logs when this edge case occurs

The fix should preserve the existing epoch store check (the early return when epoch is ending) and maintain compatibility with the existing function signature.

## Hints

- Look for the `process_execution_time_observation` function in `execution_time_estimator.rs`
- The defensive approach should use the last N timings where N = number of commands
- Consider what logging would be helpful for debugging this edge case in production
- Ensure the code compiles with `cargo check -p sui-core`
