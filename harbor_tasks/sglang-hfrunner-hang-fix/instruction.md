# Fix HFRunner.forward() Hanging When Subprocess Dies

## Bug Description

In `python/sglang/test/runners.py`, the `HFRunner.forward()` method calls `self.out_queue.get()` which blocks indefinitely. If the subprocess (`self.model_proc`) crashes during initialization or at any point before producing output, this call hangs forever. This causes tests to time out silently instead of failing fast with a clear error message.

## Location

File: `python/sglang/test/runners.py`, in the `HFRunner` class, `forward()` method.

## What to Fix

Modify the `forward()` method so that instead of blocking indefinitely on `self.out_queue.get()`, it periodically checks whether the subprocess (`self.model_proc`) is still alive. If the subprocess has died and the output queue is empty, raise a descriptive `RuntimeError` indicating the subprocess exit code.

## Expected Behavior

- If the subprocess is healthy, `forward()` returns the result from the queue as before.
- If the subprocess dies before producing output, `forward()` raises a `RuntimeError` with a message that includes the subprocess exit code, rather than hanging indefinitely.
