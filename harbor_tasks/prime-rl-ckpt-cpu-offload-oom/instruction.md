# Fix OOM when resuming from checkpoint with CPU optimizer offloading

## Problem

When resuming training from a distributed checkpoint with `CPUOffloadOptimizer` enabled, the process runs out of GPU memory (OOM) on the first training step after loading.

The checkpoint loading code in `src/prime_rl/trainer/ckpt.py` loads optimizer states onto GPU, then moves them back to CPU for CPU-offloaded optimizers. After this, the `state_dict` dictionary retains references to stale GPU tensors. These stale references prevent the CUDA caching allocator from releasing memory — reserved GPU memory stays high (gigabytes) even though the tensors are no longer needed.

## Expected Behavior

After checkpoint loading completes with CPU-offloaded optimizers, the reserved-minus-allocated memory gap should be near zero, not gigabytes. The code must explicitly release stale GPU tensor references and return memory to the CUDA allocator.

## Relevant Code Location

- File: `src/prime_rl/trainer/ckpt.py`
- Class: `AppState`
- Method: `load_state_dict`

The `load_state_dict` method in the `AppState` class handles checkpoint state restoration for training.

## What the Tests Check

The test suite verifies that `load_state_dict` in `AppState` (in `src/prime_rl/trainer/ckpt.py`):
1. Imports the `gc` module
2. Calls `gc.collect()` and `torch.cuda.empty_cache()` to reclaim GPU memory
3. Gates this cleanup on the presence of `CPUOffloadOptimizer` in the optimizers list
4. Calls `state_dict.clear()` as part of the cleanup
5. Contains at least 5 substantive statements (not a stub)