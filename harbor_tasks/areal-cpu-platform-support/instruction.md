# CPU-only platform support is broken

## Problem

When running AReaL on a CPU-only system (macOS or Linux without a GPU), several components crash because the `CpuPlatform` class does not implement the full platform interface expected by the training engines and scheduler.

Specifically:

1. **Missing memory management methods**: Code that queries device memory (e.g., `memory_allocated()`, `memory_reserved()`, `mem_get_info()`, `empty_cache()`) hits `AttributeError` on CPU platforms because `CpuPlatform` doesn't define these methods and the `Platform.__getattr__` fallback to `torch.cpu` fails since those are CUDA-specific APIs.

2. **Wrong device type in engines**: The `_create_device_model()` method in the FSDP and Archon engines unconditionally creates a CUDA-indexed device via `torch.device(int(LOCAL_RANK))`, which produces `device(type='cuda', index=0)` even on CPU-only systems.

3. **Invalid environment variable key**: The local scheduler sets `env[current_platform.device_control_env_var]` unconditionally, but on `CpuPlatform` this evaluates to `env[""]` since the CPU platform has no device visibility control variable.

## Expected Behavior

- All platform memory query methods should work on CPU without errors (returning zero/no-op values)
- Engine device selection should detect CPU platforms and use `torch.device("cpu")`
- The scheduler should skip setting the device visibility environment variable when the platform doesn't define one

## Files to Look At

- `areal/infra/platforms/cpu.py` — CpuPlatform class, missing memory management stubs
- `areal/engine/fsdp_engine.py` — `_create_device_model()` around line 779
- `areal/experimental/engine/archon_engine.py` — `_create_device_model()` around line 940
- `areal/infra/scheduler/local.py` — `create_workers()` around line 633, device env var assignment
