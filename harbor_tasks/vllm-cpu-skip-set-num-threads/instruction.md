# Bug: CPU thread binding disrupted by downstream `torch.set_num_threads` calls

## Context

vLLM's CPU backend supports thread affinity binding via `VLLM_CPU_OMP_THREADS_BIND` (or automatic NUMA-aware binding). After thread binding is established, calling `torch.set_num_threads()` disrupts the carefully configured thread affinity, leading to performance degradation on multi-socket CPU systems.

## Problem

Once CPU thread binding has been configured, subsequent calls to `torch.set_num_threads()` override the thread affinity setup, causing threads to migrate across NUMA nodes. The current implementation does not protect against this disruption.

## Expected Behavior

After thread binding is established, subsequent calls to `torch.set_num_threads()` must not change the actual thread count. When code attempts to call `set_num_threads` after binding, the system must:

1. Prevent the thread count from changing (noop behavior)
2. Emit a log warning at WARNING level or higher mentioning `set_num_threads` or `skip`

## Implementation Requirements

- Implement the fix using monkey-patching via assignment (`torch.set_num_threads = ...`)
- Define a replacement function (nested within the method that establishes thread binding) that logs the warning and ignores the call
- The replacement function must use the logger named `vllm.v1.worker.cpu_worker`
- The `CPUWorker` class with its `init_device` method must continue to exist
- The method must continue to call `init_worker_distributed_environment` and `set_random_seed`
- The Python syntax must be valid (no syntax errors)
- The code must pass the repository's pre-commit checks:
  - ruff lint (no violations)
  - typos (no typos)
  - SPDX license header (valid format)
  - mypy type checking (must pass with `--ignore-missing-imports --follow-imports=silent`)

## Testing

When correctly implemented, calling `torch.set_num_threads(n)` after thread binding is established will:
- Leave `torch.get_num_threads()` unchanged at its baseline value
- Log a warning message mentioning `set_num_threads` or `skip`
