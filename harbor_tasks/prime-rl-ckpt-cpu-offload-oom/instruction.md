# Fix OOM when resuming from checkpoint with CPU optimizer offloading

## Problem

When resuming training from a distributed checkpoint with `CPUOffloadOptimizer` enabled, the process runs out of GPU memory (OOM) on the first training step after loading.

The issue is in `AppState.load_state_dict()` in `src/prime_rl/trainer/ckpt.py`. After `set_state_dict()` loads optimizer states onto GPU and `_move_states("cpu")` moves them back to CPU, the loaded `state_dict` dictionary still holds references to the now-stale GPU optimizer tensors. The CUDA caching allocator retains this memory, causing a massive spike in reserved (but unallocated) GPU memory — up to ~11 GB of wasted VRAM on a small model.

## Expected Behavior

After `load_state_dict` completes with CPU-offloaded optimizers, stale GPU tensor references should be released and GPU memory should be reclaimed. The reserved-minus-allocated memory gap should be near zero, not gigabytes.

## Files to Look At

- `src/prime_rl/trainer/ckpt.py` — Contains `AppState.load_state_dict()` where the checkpoint is loaded and optimizer states are moved to CPU. The cleanup of stale GPU references is missing.
