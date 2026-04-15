# Fix: CUDA IPC cache leaks during weight updates

## Problem

During weight updates in the SLIME training framework, GPU memory is leaked through the CUDA IPC cache. Over time, as weights are repeatedly updated across processes, GPU memory usage grows unboundedly, eventually leading to out-of-memory errors.

## Root Cause

In `slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py`, the `update_weights` method iterates over HuggingFace weight chunks and sends them to colocated engines via `_send_hf_params`. When `ForkingPickler` serializes GPU tensors for inter-process communication, it calls `storage._share_cuda_()`, which creates permanent entries in the CUDA IPC cache that hold strong references to GPU memory. These entries are only released when `torch.cuda.ipc_collect()` detects the consumer has closed its IPC handle.

The current code fails to release IPC cache entries for some GPU tensors, and never calls `torch.cuda.ipc_collect()`, so IPC cache entries accumulate across chunks and training steps.

## Expected Behavior

- The `update_weights` method must release all GPU tensors from each weight chunk so the CUDA caching allocator can reclaim the memory blocks.
- IPC cache entries must be explicitly released via `torch.cuda.ipc_collect()` so that subsequent training steps do not accumulate leaked references.

## Files to Investigate

- `slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py` -- the `update_weights` method loop and cleanup logic