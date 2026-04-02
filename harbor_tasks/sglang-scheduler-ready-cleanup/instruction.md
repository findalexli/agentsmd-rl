# Scheduler readiness check is slow to detect failures

## Problem

In `python/sglang/srt/entrypoints/engine.py`, the `_wait_for_scheduler_ready` function has two issues:

1. **Delayed failure detection**: When a scheduler process sends a non-ready status (indicating initialization failure), the error is not raised until *all* ranks have been polled. This means if rank 0 fails initialization and reports a non-ready status, the system still waits for all remaining ranks before raising the error. The status check should happen immediately after receiving data from each rank.

2. **Duplicated error message**: The error message for a dead scheduler process is copy-pasted in multiple places within the function. When a scheduler dies (e.g., killed by OOM), the same multi-line RuntimeError string appears in both the `EOFError` handler and the process liveness check. This should be extracted into a helper function to avoid duplication.

## Where to look

- `python/sglang/srt/entrypoints/engine.py` — the `_wait_for_scheduler_ready` function (around line 1227)

## Expected behavior

- If any rank reports a non-ready status, fail immediately rather than waiting for all ranks
- The dead-scheduler error message should be defined once and reused
- The poll-timeout dead-process check should not be nested inside an `else` clause — it should run whenever the poll times out regardless of code path
