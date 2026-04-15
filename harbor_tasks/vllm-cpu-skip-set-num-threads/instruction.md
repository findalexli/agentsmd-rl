# Bug: CPU thread binding disrupted by downstream `torch.set_num_threads` calls

## Context

vLLM's CPU backend supports thread affinity binding via `VLLM_CPU_OMP_THREADS_BIND` (or automatic NUMA-aware binding). In `vllm/v1/worker/cpu_worker.py`, the `CPUWorker.init_device()` method calls `torch.ops._C.init_cpu_threads_env()` to bind OpenMP threads to specific CPU cores for optimal performance.

## Problem

After thread binding is established in `init_device()`, other parts of the codebase (or downstream libraries) may call `torch.set_num_threads()`. This disrupts the carefully configured thread binding, leading to performance degradation on multi-socket CPU systems. The thread affinity set up during `init_device()` gets overridden, and threads may migrate across NUMA nodes.

## Expected Behavior

Once CPU thread binding has been configured in `init_device()`, subsequent calls to `torch.set_num_threads()` must not change the thread count. Additionally, the system must emit a log warning (at WARNING level or higher) when `torch.set_num_threads` is called after thread binding, so that developers are informed when something attempts to change the thread configuration. The warning message must mention `set_num_threads` or the word `skip`.

## Implementation Requirements

- The file `vllm/v1/worker/cpu_worker.py` must continue to define the `CPUWorker` class with its `init_device` method.
- The method `init_device` must still call `init_worker_distributed_environment` and `set_random_seed`.
- The Python syntax must be valid (no syntax errors).
- The code must pass the repository's pre-commit checks:
  - ruff lint (no violations)
  - typos (no typos)
  - SPDX license header (valid format)
  - mypy type checking (must pass with `--ignore-missing-imports --follow-imports=silent`)
