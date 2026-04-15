# Bug: Process hangs on fatal error in async orchestrator

## Summary

When a fatal error occurs inside an async function decorated with `clean_exit` (e.g., `ValueError: dataset is not set`), the process gets stuck in a `RUNNING` state and never terminates. This creates orphan runs that are never cleaned up.

## Location

- **File**: `src/prime_rl/utils/utils.py`
- **Function**: `clean_exit` decorator (both the `async_wrapper` and `sync_wrapper` inner functions)

## Reproduction

The `clean_exit` decorator wraps orchestrator/trainer entry points to ensure `torch.distributed` process groups and `wandb` runs are properly cleaned up on exit. When an exception occurs:

1. The `except` block logs the error and calls `wandb.finish(exit_code=1)`
2. The exception is re-raised
3. In an async context, the re-raised exception does **not** terminate the process — the event loop swallows it and the process hangs indefinitely

The `finally` block (which tears down the distributed process group) still needs to execute, so the solution must preserve that behavior while ensuring the process actually terminates.

## Expected behavior

When a fatal exception occurs in a `clean_exit`-decorated function:
- The error should be logged
- `wandb.finish(exit_code=1)` should be called
- The distributed process group should be destroyed (via the `finally` block)
- The process must call `sys.exit(1)` to raise `SystemExit(1)`, ensuring:
  - The `finally` block executes before process termination
  - The process exits with code 1 (not 0)
  - The process does not hang in async contexts
