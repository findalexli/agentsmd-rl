# Performance: Serialized bucket weight sync in FSDP engine

## Problem

In `areal/engine/fsdp_engine.py`, the `_update_weights_from_distributed` method
broadcasts model parameters to inference workers in chunks (buckets). Currently,
the entire pipeline for each bucket is fully serialized:

1. Materialize full tensors for bucket *i*
2. Notify the inference side about bucket *i*
3. Broadcast bucket *i* (all ranks)
4. **Wait** for bucket *i* to finish
5. Only then start materializing bucket *i+1*

This means the communication latency of nearly every bucket is fully exposed on the
critical path. On a Qwen2.5-32B model with 8 H20 GPUs, the `update_weights` call
takes ~1.13 s, with broadcast sync accounting for ~0.24 s.

## Expected behavior

The bucket broadcast for bucket *i* should overlap with the preparation (tensor
materialization) of bucket *i+1*. The scheduling should look like:

1. Materialize bucket *i*
2. Start bucket *i* broadcast **asynchronously**
3. While bucket *i* is in flight, materialize bucket *i+1*
4. Wait for bucket *i* only before the next incompatible collective or the final flush

At most one bucket should be in flight at any time to keep memory bounded. The
change must preserve ordering guarantees — all pending broadcasts must be drained
before any conflicting collective or before the method returns (even on error).

## Relevant code

- `FSDPEngine._update_weights_from_distributed` (~line 1130) — the main loop
- `FSDPEngine._update_bucket_weights_from_distributed` (~line 1035) — per-bucket sync logic
- The method uses `dist.broadcast(..., async_op=True)` for individual tensors within
  a bucket, but then immediately waits on all handles before returning. The outer
  loop never overlaps consecutive buckets.

## Constraints

- Only `areal/engine/fsdp_engine.py` should be modified.
- The optimization should use a CUDA stream for broadcast overlap on rank 0 when
  CUDA is available, falling back to synchronous behavior otherwise.
- Non-main ranks (rank != 0) only participate in `_get_full_tensor` calls and
  barriers — they must not break.
- The `_update_bucket_weights_from_distributed` synchronous API must be preserved
  for use by any remaining callers.
