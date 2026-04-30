# Add host memory metrics to available_memory

## Problem

The `available_memory()` function in `slime/utils/memory_utils.py` reports GPU memory usage (total, free, used, allocated, reserved) but provides no visibility into host (CPU/RAM) memory. When debugging out-of-memory issues during training, operators need to see both GPU and host memory in the same diagnostic output to distinguish between GPU OOM and host OOM.

## Expected Behavior

`available_memory()` should return host memory metrics alongside the existing GPU metrics. The returned dictionary should include:

**Host memory keys** (in GB):
- `host_total_GB` — total host memory
- `host_available_GB` — available host memory
- `host_used_GB` — used host memory
- `host_free_GB` — free host memory

**GPU keys** (already present, must be preserved):
- `gpu`
- `total_GB`
- `free_GB`
- `used_GB`
- `allocated_GB`
- `reserved_GB`

Values must be numeric (int or float) in the GB range (not raw bytes).

## Files to Look At

- `slime/utils/memory_utils.py` — memory utility functions including `available_memory()` and the `_byte_to_gb` helper

## Code Style Requirements

This project enforces consistent code style via pre-commit hooks:

- **ruff** for linting
- **isort** for import sorting (with `--profile=black`)
- **black** for code formatting

All code changes must pass these checks. New imports (if any) should be placed following the existing import ordering conventions used in the file.
