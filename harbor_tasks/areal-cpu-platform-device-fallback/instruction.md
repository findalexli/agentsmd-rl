# CPU-Only Platform Support Is Broken

## Bug Description

AReaL's platform abstraction (`areal/infra/platforms/`) is supposed to let the framework
run on CPU-only systems (macOS, CI boxes without GPUs). In practice, several code paths
crash or misbehave when the active platform is `CpuPlatform`.

### Problem 1 — Missing memory introspection methods on `CpuPlatform`

The `Platform` base class delegates unknown attribute lookups to `torch.<device_type>`.
For GPU platforms this works fine (`torch.cuda.memory_allocated()`, etc.), but
`torch.cpu` does not expose `memory_allocated`, `memory_reserved`, `mem_get_info`, or
`empty_cache`. Any code path that calls these on `CpuPlatform` raises `AttributeError`.

Look at `areal/infra/platforms/cpu.py` — the class is missing explicit implementations
for these memory-related methods.

### Problem 2 — Device creation assumes CUDA ordinal

In the FSDP and Archon engines' `_create_device_model` method, the device is created as
`torch.device(int(LOCAL_RANK))`. When `LOCAL_RANK=0`, `torch.device(0)` creates a CUDA
device — which crashes on a CPU-only system. The method needs to respect the current
platform's device type.

Affected files:
- `areal/engine/fsdp_engine.py` — `_create_device_model`
- `areal/experimental/engine/archon_engine.py` — `_create_device_model`

### Problem 3 — Scheduler sets an empty environment variable key

`CpuPlatform.device_control_env_var` is an empty string (`""`). In the local scheduler's
`create_workers` method (`areal/infra/scheduler/local.py`), the code unconditionally sets
`env[current_platform.device_control_env_var]`, which inserts a key of `""` into the
environment dictionary. This should be guarded so it only runs when the env var name is
non-empty.

## Expected Behavior

All three issues should be fixed so that the framework can launch and run on a CPU-only
system without errors.
