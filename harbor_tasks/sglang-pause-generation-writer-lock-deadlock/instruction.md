# Fix writer lock deadlock during pause_generation

## Symptom

When `pause_generation` is active, the `update_weights_from_ipc` function in `python/sglang/srt/managers/tokenizer_communicator_mixin.py` deadlocks. The function acquires `model_update_lock.writer_lock` unconditionally. When the scheduler is paused, existing readers are blocked on `is_pause_cond` waiting for the scheduler to resume, and the scheduler cannot resume until the weight update completes — creating a circular wait.

## Task

Fix the deadlock in `update_weights_from_ipc` so it no longer hangs when the scheduler is paused. After the fix, calling this function during an active `pause_generation` should complete successfully rather than deadlocking.

Tests verify the modified `update_weights_from_ipc` function source (via `ast.unparse`) contains all of these patterns:

- `async with self.is_pause_cond:`
- `is_paused = self.is_pause`
- `lock_context =`
- `nullcontext()`
- `async with lock_context:`

Tests also verify consistency with the `update_weights_from_distributed` function in the same file, which already handles the paused state correctly — the same patterns must appear in both functions.

The modified file must remain syntactically valid and pass `ruff` (F401, F821), `black`, `isort`, `codespell`, and `pre-commit` checks.
