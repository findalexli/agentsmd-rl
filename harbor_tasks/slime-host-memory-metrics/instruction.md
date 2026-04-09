# Add host memory metrics to available_memory

## Problem

The `available_memory()` function in `slime/utils/memory_utils.py` reports GPU memory usage (total, free, used, allocated, reserved) but provides no visibility into host (CPU/RAM) memory. When debugging out-of-memory issues during training, operators need to see both GPU and host memory in the same diagnostic output to distinguish between GPU OOM and host OOM.

## Expected Behavior

`available_memory()` should return host memory metrics alongside the existing GPU metrics. The returned dictionary should include total, available, used, and free host memory — reported in GB, consistent with the existing GPU metrics format.

## Files to Look At

- `slime/utils/memory_utils.py` — memory utility functions including `available_memory()` and the `_byte_to_gb` helper
