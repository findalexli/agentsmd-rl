# Fix: Multi-node allreduce fusion hangs with flashinfer trtllm backend

## Problem

The flashinfer allreduce in vLLM hangs when running in multi-node configurations. The trtllm backend does not support multi-node allreduce, but the default backend is hardcoded to `"trtllm"` regardless of the cluster topology.

Additionally, the quant workspace creator always attempts to create a trtllm workspace even in multi-node setups, which also fails.

## Expected Behavior

1. **Default backend resolution**: `VLLM_FLASHINFER_ALLREDUCE_BACKEND` must default to `"auto"` (not `"trtllm"`). The actual backend must be resolved at runtime based on the number of nodes. Use `get_node_count()` from `vllm.distributed.parallel_state` to determine the cluster size.

2. **Multi-node backend selection**: When the backend is `"auto"` and `get_node_count() > 1`, the resolved backend must be `"mnnvl"` (a backend that supports multi-node allreduce). When `get_node_count() == 1`, the resolved backend must be `"trtllm"`.

3. **Explicit passthrough**: When the user explicitly sets `VLLM_FLASHINFER_ALLREDUCE_BACKEND` to a non-auto value (e.g., `"trtllm"` or `"mnnvl"`), the resolver must return that exact value without attempting auto-selection.

4. **Multi-node trtllm error**: When `get_node_count() > 1` and the resolved backend is `"trtllm"`, a `ValueError` must be raised. The error message must contain the word `"multi"` or `"trtllm"` (e.g., `"Flashinfer allreduce is not supported for multi-node allreduce with 'trtllm' backend. Please use 'mnnvl' backend instead."`).

5. **Quant workspace for multi-node**: `get_fi_ar_quant_workspace` must return `None` (not create a workspace) when `get_node_count() > 1`. For single-node (`get_node_count() == 1`), it must create and return the workspace.

## Files to Look At

- `vllm/distributed/device_communicators/flashinfer_all_reduce.py` — allreduce workspace creation and backend selection
- `vllm/envs.py` — environment variable defaults including `VLLM_FLASHINFER_ALLREDUCE_BACKEND`

## Implementation Notes

- Use `get_node_count` from `vllm.distributed.parallel_state` to query the number of nodes at runtime
- Create a function named `_resolve_fi_ar_backend` that implements the backend resolution logic and returns the resolved backend string
- The quant workspace function must check node count before attempting workspace creation