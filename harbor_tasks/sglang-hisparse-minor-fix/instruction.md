# Hisparse Minor Fix

## Problem

The HiSparse memory management system in SGLang has three related issues:

1. **CUDA kernel alignment bug**: The `transfer_item_warp` function in `hisparse.cuh` uses 64-bit transfers for data that is 128-bit aligned. This can cause memory alignment issues and inefficient memory access patterns.

2. **Incorrect retraction location**: When requests are retracted from a batch, `hisparse_coordinator.retract_req()` is called in `scheduler.py`'s `update_running_batch` method instead of in `schedule_batch.py`'s `release_req` method. This causes incorrect cleanup timing.

3. **Missing batch state reset**: After assigning `hisparse_coordinator` to a running batch, the `batch_is_full` flag is not reset to `False`, preventing the scheduler from scheduling more prefills.

## Expected Behavior

1. `transfer_item_warp` should use 128-bit (16-byte) bulk transfers via paired 64-bit loads/stores with proper tail handling for sizes not divisible by 16.

2. `hisparse_coordinator.retract_req(req)` should be called inside `release_req()` in `schedule_batch.py` when releasing a request, with a None check.

3. After `self.running_batch.hisparse_coordinator = self.hisparse_coordinator` in `scheduler.py`, `batch_is_full` should be reset to `False` so the scheduler can continue scheduling prefills.

4. The `retract_req` call should be removed from `scheduler.py`'s `update_running_batch` method.

## Files to Look At

- `python/sglang/jit_kernel/csrc/hisparse.cuh` — The `transfer_item_warp` CUDA device function
- `python/sglang/srt/managers/schedule_batch.py` — The `release_req` method
- `python/sglang/srt/managers/scheduler.py` — The `get_next_batch_to_run` and `update_running_batch` methods

## Notes

- The fix involves both CUDA kernel code and Python scheduler logic
- Pay attention to the alignment requirements in the CUDA transfer function
- The scheduler changes are about proper cleanup and state management
