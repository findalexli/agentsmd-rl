# Hisparse Minor Fix

## Problem

The HiSparse memory management system in SGLang has three bugs:

### 1. Inefficient CUDA memory transfer width

The `transfer_item_warp` device function in `python/sglang/jit_kernel/csrc/hisparse.cuh` transfers data using individual 64-bit memory operations. However, the data it handles is 128-bit aligned, making this approach inefficient.

The correct implementation uses 128-bit bulk PTX transfers:
- Load instruction: `ld.global.nc.v2.b64` (loads a pair of 64-bit values as one 128-bit operation)
- Store instruction: `st.global.cg.v2.b64` (stores a pair of 64-bit values as one 128-bit operation)

The transfer operates on 16-byte chunks, where the number of chunk pairs is `item_size_bytes / 16`. For data sizes not evenly divisible by 16 bytes, a tail handler is needed — it uses `ld.global.nc.b64` to transfer the remaining 8-byte portion.

### 2. Request retraction in wrong code path

The `hisparse_coordinator.retract_req()` call currently lives in `scheduler.py` alongside batch-update logic. However, request retraction is semantically part of request release, which is handled in `schedule_batch.py`. Since `hisparse_coordinator` can be `None`, any retraction call must guard against this with an `is not None` check.

### 3. batch_is_full flag never clears

In `scheduler.py`, after a `hisparse_coordinator` is assigned to a running batch, the `batch_is_full` flag stays stuck at its previous value. This prevents the scheduler from scheduling additional prefills even when capacity is available.

## Files

- `python/sglang/jit_kernel/csrc/hisparse.cuh`
- `python/sglang/srt/managers/schedule_batch.py`
- `python/sglang/srt/managers/scheduler.py`
