# Add NUMA CPU Affinity Binding to Platform Abstraction

## Problem

On multi-socket NUMA machines (e.g., 8-GPU nodes with 2 NUMA nodes), training processes may be scheduled on CPU cores that are physically far from their assigned GPU. This causes cross-NUMA memory access penalties, increasing latency for CPU-GPU data transfers and reducing training throughput.

The platform abstraction layer (`areal/infra/platforms/platform.py` and its subclasses) currently provides device management methods like `set_device()`, but has no mechanism to bind a process to CPU cores local to its assigned GPU.

## Expected Behavior

- The `Platform` base class should expose a method for setting NUMA CPU affinity, with a safe no-op default so non-CUDA platforms are unaffected.
- The CUDA platform subclass (`areal/infra/platforms/cuda.py`) should implement this using NVML to detect the GPU's NUMA topology and bind the process to the appropriate CPU cores.
- The implementation should be fully defensive: gracefully handle the case where `pynvml` is not installed, and catch any NVML call failures without crashing.
- All training engines (`FSDPEngine`, `MegatronEngine`, `ArchonEngine`) should call this method during initialization, right after `set_device()`.

## Files of Interest

- `areal/infra/platforms/platform.py` — `Platform` base class
- `areal/infra/platforms/cuda.py` — `CudaPlatform` subclass
- `areal/engine/fsdp_engine.py` — `_create_device_model()` method
- `areal/engine/megatron_engine.py` — `initialize()` method
- `areal/experimental/engine/archon_engine.py` — `_create_device_model()` method

## Hints

- Look at how `set_device()` is defined in the base class and overridden/used — follow the same pattern.
- The CUDA implementation should use `pynvml` (the `nvidia-ml-py` package) for NVML access.
- Use `os.sched_getaffinity(0)` to verify the affinity was set and log the number of bound CPU cores.
- Ensure NVML is properly initialized and shut down (use a `finally` block).
