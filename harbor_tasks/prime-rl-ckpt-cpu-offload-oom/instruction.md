# Fix OOM when resuming from checkpoint with CPU optimizer offloading

## Problem

When resuming training from a distributed checkpoint with `CPUOffloadOptimizer` enabled, the process runs out of GPU memory (OOM) on the first training step after loading.

The root cause involves how checkpoint loading interacts with CPU-offloaded optimizers. During the load sequence in the checkpoint handling code:
1. Optimizer states are first loaded onto GPU
2. The states are then moved back to CPU for CPU-offloaded optimizers
3. The loaded `state_dict` dictionary retains references to stale GPU tensors

These stale references prevent the CUDA caching allocator from releasing memory, causing reserved GPU memory to remain high (measured in gigabytes) even though the tensors are no longer logically needed.

## Expected Behavior

After checkpoint loading completes with CPU-offloaded optimizers:
- The `gc` module must be imported in the checkpoint handling code
- `gc.collect()` must be called to explicitly release stale GPU tensor references and break circular references
- `torch.cuda.empty_cache()` must be called to return GPU memory to the CUDA allocator
- This cleanup must only occur when `CPUOffloadOptimizer` is present in the optimizers list, to avoid unnecessary overhead when CPU offloading is not used

The reserved-minus-allocated memory gap after loading should be near zero, not gigabytes.

## Implementation Requirements

The fix must:
1. Import the `gc` module
2. Track whether any optimizer is a `CPUOffloadOptimizer` during the state restoration loop
3. Call `state_dict.clear()`, `gc.collect()`, and `torch.cuda.empty_cache()` inside a conditional block that only executes when `CPUOffloadOptimizer` was detected
