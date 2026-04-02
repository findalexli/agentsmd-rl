# Fix: Tensor size mismatch after pause_generation

## Problem

In `pause_generation`, after calling `filter_batch` on `last_batch`, `merge_batch` is called unconditionally. When the extend `last_batch` has all requests finished, `filter_batch` sets `last_batch.reqs = []` but returns early without updating tensors (seq_lens, req_pool_indices, output_ids, etc. still have M=1 element). The unconditional `merge_batch` then `torch.cat`s the stale M-element tensors into `running_batch`, yielding `seq_lens.shape[0] = N+1` while `len(reqs) = N`.

This breaks the invariant `len(reqs) == seq_lens.shape[0]`. The extra slot corrupts KV-cache allocations and surfaces as:
```
RuntimeError: The size of tensor a (652) must match the size of tensor b (651)
```

## Root Cause

In `python/sglang/srt/managers/scheduler.py`, the `pause_generation` method calls `self.running_batch.merge_batch(self.last_batch)` unconditionally after `filter_batch`. The same pattern in `get_next_batch_to_run` already has an `is_empty()` guard that prevents this.

## Expected Behavior

After `filter_batch` completes, any merge into `running_batch` should only happen when `last_batch` still contains live requests. An analogous guard already exists in `get_next_batch_to_run` — the same defensive pattern should be applied in `pause_generation`.

## File to Modify

- `python/sglang/srt/managers/scheduler.py` -- the `pause_generation` method
