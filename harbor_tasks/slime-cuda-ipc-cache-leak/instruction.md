# Fix: CUDA IPC cache leaks during weight updates

## Problem

During weight updates in the SLIME training framework, GPU memory is leaked through the CUDA IPC cache. Over time, as weights are repeatedly updated across processes, GPU memory usage grows unboundedly, eventually leading to out-of-memory errors.

## Root Cause

In `update_weight_from_tensor.py`, the `update_weights` method iterates over HuggingFace weight chunks and sends them to colocated engines via `_send_hf_params`. When `ForkingPickler` serializes GPU tensors for inter-process communication, it calls `storage._share_cuda_()`, which creates permanent entries in the CUDA IPC cache that hold strong references to GPU memory. These entries are only released when `torch.cuda.ipc_collect()` detects the consumer has closed its IPC handle.

The current code has two issues:
1. `hf_named_tensors` is not deleted alongside `long_lived_tensors`, so the chunk's GPU tensors remain referenced and cannot be freed
2. `torch.cuda.ipc_collect()` is never called, so IPC cache entries accumulate across chunks and training steps

## Expected Behavior

- After each chunk's `ray.get()` completes, both `long_lived_tensors` and `hf_named_tensors` should be deleted
- `torch.cuda.ipc_collect()` should be called after each chunk to release IPC cache entries
- `torch.cuda.ipc_collect()` should also be called after the post-loop `dist.barrier()` to clean up the last chunk's IPC entries for non-source ranks

## Files to Investigate

- `slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py` -- the `update_weights` method loop and cleanup logic
