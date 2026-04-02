# Bug: CPU thread binding disrupted by downstream `torch.set_num_threads` calls

## Context

vLLM's CPU backend supports thread affinity binding via `VLLM_CPU_OMP_THREADS_BIND` (or automatic NUMA-aware binding). In `vllm/v1/worker/cpu_worker.py`, the `CPUWorker.init_device()` method calls `torch.ops._C.init_cpu_threads_env()` to bind OpenMP threads to specific CPU cores for optimal performance.

## Problem

After thread binding is established, other parts of the codebase (or downstream libraries) may call `torch.set_num_threads()`. This disrupts the carefully configured thread binding, leading to performance degradation on multi-socket CPU systems. The thread affinity set up during `init_device()` gets overridden, and threads may migrate across NUMA nodes.

## Expected Behavior

Once CPU thread binding has been configured in `init_device()`, subsequent calls to `torch.set_num_threads()` should not be allowed to disrupt the binding. The system should protect the thread configuration and inform developers via logging if something attempts to change it.

## Relevant Files

- `vllm/v1/worker/cpu_worker.py` — `CPUWorker.init_device()` method, specifically the section after `init_cpu_threads_env` is called
