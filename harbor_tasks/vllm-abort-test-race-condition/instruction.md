# Flaky Race Condition in test_abort_during_final_step

## Bug Description

The test `test_abort_during_final_step` in `tests/v1/engine/test_abort_final_step.py` is flaky when `async_scheduling=False`. It intermittently fails with:

```
AssertionError: Expected at least 1 captured finish status, got 0.
File content: ['INIT:WORKER', 'INIT:SCHEDULER']
```

## Root Cause

In synchronous scheduling mode, after `execute_model` is unblocked, the engine core must complete the full step pipeline (forward pass, sampling, GPU-to-CPU copy, abort/output processing) before writing the finish status to the status file.

The test currently uses a fixed short sleep before reading the status file and asserting on its contents. Under CI load this is insufficient — the engine hasn't finished writing by the time the assertion runs.

The `async_scheduling=True` variant is not affected because the abort is processed at the start of the next busy-loop iteration, before the sampling future resolves, removing sampling from the critical path for the status file write.

## What Needs to Change

The test's wait strategy in `tests/v1/engine/test_abort_final_step.py` needs to be made robust against timing variability. The fixed sleep should be replaced with an approach that actively waits for the expected status to appear, with a reasonable timeout to avoid hanging indefinitely.

## Relevant Code

- `tests/v1/engine/test_abort_final_step.py` — the `test_abort_during_final_step` async test function, specifically the section after `await gen_task` where the status file is read and asserted on.
