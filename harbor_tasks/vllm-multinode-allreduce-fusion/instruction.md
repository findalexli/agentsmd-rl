# Fix: Multi-node allreduce fusion hangs with flashinfer trtllm backend

## Problem

The flashinfer allreduce in vLLM hangs when running in multi-node configurations. The trtllm backend does not support multi-node allreduce, but the default backend is hardcoded to `"trtllm"` regardless of the cluster topology.

Additionally, `get_fi_ar_quant_workspace` always attempts to create a trtllm workspace even in multi-node setups, which also fails.

## Expected Behavior

- The default backend should be `"auto"` and resolved at runtime based on the number of nodes
- Multi-node setups (>1 node) should use a backend that supports multi-node allreduce
- Single-node setups should continue using `trtllm`
- If a user explicitly requests `trtllm` in a multi-node setup, a clear error should be raised
- Quant workspace creation should be skipped for multi-node (not supported by trtllm)

## Files to Look At

- `vllm/distributed/device_communicators/flashinfer_all_reduce.py` — allreduce workspace creation and backend selection
- `vllm/envs.py` — environment variable defaults including `VLLM_FLASHINFER_ALLREDUCE_BACKEND`
