# Fix HFRunner.forward() Hanging When Subprocess Dies

## Bug Description

In `python/sglang/test/runners.py`, the `HFRunner.forward()` method calls `self.out_queue.get()` without a timeout. This is a blocking call with no limit on how long it will wait. If the subprocess (`self.model_proc`) crashes during initialization or at any point before producing output, this call hangs forever — there is no mechanism to detect that the subprocess is dead and no way to break out of the blocking get.

This causes tests to time out silently instead of failing fast with a clear error message. For example, when a HuggingFace model tokenizer load hits a 429 rate limit during `HFRunner.start_model_process`, the subprocess crashes before entering its processing loop. Since it never puts a result into `out_queue`, the parent blocks indefinitely on `out_queue.get()` until the CI step timeout kills the entire job. This can waste 18+ minutes of CI time with zero diagnostic output.

The problematic behavior occurs whenever the subprocess dies for any reason: a normal exit with a nonzero exit code (e.g., 1, 42, 137), or when the process is killed by a signal (which produces negative exit codes like -9 for SIGKILL, -11 for SIGSEGV, -15 for SIGTERM). In all these cases, `forward()` hangs rather than reporting the failure.

## Location

File: `python/sglang/test/runners.py`, in the `HFRunner` class, `forward()` method.

## Expected Behavior

- If the subprocess is healthy and produces output, `forward()` returns the result from the queue as before.
- If the subprocess dies before producing output, `forward()` must raise a `RuntimeError` whose message includes the subprocess exit code, rather than hanging indefinitely.
- The error must be raised promptly (within seconds), not after minutes of waiting.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format` and `ruff check`
- `black` (Python formatter)
- `typos` (spell-check via `codespell`)
- `isort` (import sorting)
- `pyflakes` (undefined name detection)
