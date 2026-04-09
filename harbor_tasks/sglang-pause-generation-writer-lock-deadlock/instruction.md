# Fix writer lock deadlock in update_weights_from_ipc during pause_generation

## Problem

The `update_weights_from_ipc` function in the tokenizer manager has a deadlock bug that occurs when the scheduler is in `pause_generation` mode.

When the scheduler is paused, existing readers are blocked waiting on `is_pause_cond`. If `update_weights_from_ipc` tries to acquire the `writer_lock` in this state, it will deadlock because:
1. The writer lock cannot be acquired while readers hold the lock
2. The readers are stuck waiting for the scheduler to resume (on `is_pause_cond`)
3. The scheduler won't resume until the weight update completes

This creates a circular dependency that hangs the weight update operation.

## Expected Behavior

When the scheduler is paused, `update_weights_from_ipc` should skip acquiring the writer lock (using `nullcontext()` instead) because:
- No concurrent inference can race when the scheduler is paused
- Readers are already blocked on `is_pause_cond`
- The writer lock acquisition would deadlock

## Files to Look At

- `python/sglang/srt/managers/tokenizer_communicator_mixin.py` — Contains `update_weights_from_ipc` function that needs fixing

Look at how similar functions like `update_weights_from_distributed` handle this same scenario. They check `is_pause` before acquiring the lock and use `nullcontext()` when paused.
