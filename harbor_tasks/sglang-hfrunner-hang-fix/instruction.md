# Fix HFRunner.forward() Hanging When Subprocess Dies

## Bug Description

In `python/sglang/test/runners.py`, the `HFRunner.forward()` method calls `self.out_queue.get()` which blocks indefinitely. If the subprocess (`self.model_proc`) crashes during initialization or at any point before producing output, this call hangs forever. This causes tests to time out silently instead of failing fast with a clear error message.

## Location

File: `python/sglang/test/runners.py`, in the `HFRunner` class, `forward()` method.

## Expected Behavior

- If the subprocess is healthy and produces output, `forward()` returns the result from the queue as before.
- If the subprocess dies before producing output, `forward()` must raise a `RuntimeError` whose message includes the subprocess exit code, rather than hanging indefinitely.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `black (Python formatter)`
- `typos (spell-check)`
