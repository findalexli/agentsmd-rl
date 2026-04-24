# Fix: CUDA IPC cache leaks during weight updates

## Problem

During weight updates in the SLIME training framework, GPU memory is leaked through the CUDA IPC cache. Over time, as weights are repeatedly updated across processes, GPU memory usage grows unboundedly, eventually leading to out-of-memory errors.

## Symptom

The `update_weights` method iterates over HuggingFace weight chunks and sends them to colocated engines. When GPU tensors are serialized for inter-process communication via CUDA IPC, cache entries accumulate across chunks and training steps because they are not explicitly released. This causes GPU memory to grow unboundedly.

## Expected Behavior

- The `update_weights` method must release all GPU tensors from each weight chunk so the CUDA caching allocator can reclaim memory blocks. This includes both the per-chunk iteration variable and the result returned from the send operation.
- IPC cache entries must be explicitly released after processing each weight chunk inside the loop, and again after the post-loop synchronization barrier, so that subsequent training steps do not accumulate leaked references.
- The `_send_to_colocated_engine` method must retain its tuple return signature.

## Test Assertions

The test oracle verifies:
- The loop over weight chunks calls `torch.cuda.ipc_collect()` at least twice between the first and second `dist.barrier()` calls (one call per chunk).
- At least one `torch.cuda.ipc_collect()` call occurs after the second `dist.barrier()` (post-loop cleanup).
- Both `long_lived_tensors` and `hf_named_tensors` are released (via `del` or assignment to `None`) inside the weight chunk loop.
- `_send_to_colocated_engine` returns a tuple.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `black (Python formatter)`
