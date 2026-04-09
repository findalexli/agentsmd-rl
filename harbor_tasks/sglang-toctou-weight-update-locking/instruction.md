# Fix TOCTOU race in pause-aware weight update locking

## Problem

The `update_weights_from_distributed`, `update_weights_from_tensor`, and `update_weights_from_ipc` functions in the tokenizer manager have a time-of-check to time-of-use (TOCTOU) race condition in their locking pattern.

Currently:
1. The code reads `is_pause` while holding the `is_pause_cond` lock
2. Then it releases the lock
3. Then it decides whether to use `writer_lock` or `nullcontext()` based on the (now stale) value

Between steps 1 and 3, `resume_generation` could change `is_pause` to `False`, causing a weight update to run without the writer lock while inference resumes. This is a race condition window.

## Expected Behavior

When the engine is paused, the weight update should run **inside** the `is_pause_cond` scope. This prevents `resume_generation` from racing with the update - it cannot proceed until the update completes.

When not paused, the update should use the `writer_lock` outside the `is_pause_cond` scope.

The fix also removes the now-unused `nullcontext` import from `contextlib`.

## Files to Look At

- `python/sglang/srt/managers/tokenizer_communicator_mixin.py` — Contains the three functions with the race condition:
  - `update_weights_from_distributed`
  - `update_weights_from_tensor`
  - `update_weights_from_ipc`

Look for the pattern where `is_pause` is read under `is_pause_cond` lock, then a decision is made after releasing the lock. The fix moves the update operations inside the lock scope when paused.
