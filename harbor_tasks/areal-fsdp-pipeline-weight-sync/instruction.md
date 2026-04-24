# Performance: Pipelined bucket weight sync in FSDP engine

## Problem

In the FSDP engine's weight update method, the broadcast of each bucket is fully
serialized with the preparation of the next bucket — the inference side cannot
overlap bucket *i*'s network transit with the materialization of bucket *i+1*.
On a Qwen2.5-32B model with 8 H20 GPUs, the `update_weights` call takes ~1.13 s,
with broadcast sync accounting for ~0.24 s.

## Expected behavior

The broadcast of bucket *i* must run concurrently with the preparation of
bucket *i+1*. Specifically:

1. Materialize bucket *i*
2. Start bucket *i* broadcast (using an async dispatch that returns a
   handle representing the in-flight operation)
3. While bucket *i* is in flight, materialize bucket *i+1*
4. Wait for bucket *i* only at a safe point — just before the next
   incompatible collective or the final drain when the method returns

The system must keep at most one bucket in flight at any time to bound memory
usage. All pending broadcasts must be drained before any conflicting collective
or before the method returns, including when an exception is raised (error
safety via try/finally).

## Required implementation components

The following components must be present for tests to pass:

1. **A dataclass** named `_PendingWeightUpdateBucket` decorated with `@dataclass`.
   It must have at least three fields (concrete, not forwarded), including
   `handles` (list of async handles) and `fut` (a Future). The class must be
   instantiable and pass a basic smoke test (instantiation with expected field
   names succeeds).

2. **An async broadcast method** on `FSDPEngine` whose name contains both
   "async" and "bucket" or "weight". It must accept a `stream` parameter and
   return a non-None value. The method must contain distributed primitives with
   `async_op=True`.

3. **Deferred-wait pattern** in the main weight-update loop: a local variable
   is assigned the result of the async dispatch method, and that variable is
   read back within the same loop iteration (so the wait for bucket *i* can
   overlap with the work for bucket *i+1*).

4. **Error-safety wrapper**: the main loop must be wrapped in try/finally, and
   the finally block must call a self-wait helper on the pending bucket to
   ensure in-flight broadcasts are drained even when an exception occurs. The
   helper method name must contain `_wait`.

5. **CUDA stream creation** — at least one `torch.cuda.Stream()` instantiation
   must be present in the class, used when broadcasting weights to enable
   communication/computation overlap.

6. **Backward compatibility**: the existing synchronous
   `_update_bucket_weights_from_distributed` wrapper must remain with a real
   (non-stub) body, and `_init_weight_update_from_distributed` must still be
   present with at least three meaningful statements.

## Constraints

- Only `areal/engine/fsdp_engine.py` should be modified.
- Broadcast operations must always specify `src` rank explicitly.
- No wildcard imports, no bare `print()` calls, no module-level process-group
  creation, no `.item()` or `.tolist()` calls in weight-update methods.
- Non-main ranks (rank != 0) must not break — they continue to participate in
  `_get_full_tensor` calls and barriers as before.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
