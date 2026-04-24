# Fix OOM when resuming from checkpoint with CPU optimizer offloading

## Problem

When resuming training from a distributed checkpoint with `CPUOffloadOptimizer` enabled, the process runs out of GPU memory (OOM) on the first training step after loading.

The checkpoint loading code in `src/prime_rl/trainer/ckpt.py` loads optimizer states onto GPU, then moves them back to CPU for CPU-offloaded optimizers. After this, the `state_dict` dictionary retains references to stale GPU tensors. These stale references prevent the CUDA caching allocator from releasing memory — reserved GPU memory stays high (gigabytes) even though the tensors are no longer needed.

## Expected Behavior

After checkpoint loading completes with CPU-offloaded optimizers, the reserved-minus-allocated memory gap should be near zero, not gigabytes. The code must explicitly release stale GPU tensor references and return memory to the CUDA allocator.

## Relevant Code Location

The code that handles checkpoint state restoration for training. It manages optimizer state loading and uses a `state_dict` dictionary to track checkpoint data. The bug is in the code path that processes CPU-offloaded optimizers — look for where `state_dict` is used after optimizer states are moved back to CPU.

## What the Tests Check

The test suite verifies that after checkpoint loading completes:
1. The module imports `gc` to break circular reference chains
2. GPU memory is reclaimed via `gc.collect()` and `torch.cuda.empty_cache()`
3. This cleanup runs only when needed, not on every call
4. Stale references in the `state_dict` container are explicitly cleared
5. The method contains real implementation logic (not a stub returning `None`)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
