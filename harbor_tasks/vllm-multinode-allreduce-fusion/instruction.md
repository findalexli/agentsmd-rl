# Fix: Multi-node allreduce fusion hangs with flashinfer trtllm backend

## Problem

The flashinfer trtllm allreduce backend does not work for multi-node setups. Running allreduce fusion results in a hang in multi-node configurations because the trtllm backend does not support multi-node allreduce.

The default backend was hardcoded to `trtllm`, which works for single-node but hangs on multi-node.

## Root Cause

In `vllm/distributed/device_communicators/flashinfer_all_reduce.py`, the `VLLM_FLASHINFER_ALLREDUCE_BACKEND` environment variable defaults to `"trtllm"` and `get_fi_ar_workspace` uses it directly without checking the node count. The `trtllm` backend only supports single-node allreduce.

Additionally, `get_fi_ar_quant_workspace` always creates a trtllm workspace, which also fails in multi-node.

## Expected Behavior

1. Change the default backend from `"trtllm"` to `"auto"` in `vllm/envs.py`
2. Add a `_resolve_fi_ar_backend()` helper that auto-selects `mnnvl` for multi-node and `trtllm` for single-node
3. Raise `ValueError` if user explicitly requests `trtllm` in multi-node
4. Return `None` from `get_fi_ar_quant_workspace` for multi-node (quant fusion not supported)

## Files to Modify

- `vllm/distributed/device_communicators/flashinfer_all_reduce.py` -- add backend resolution
- `vllm/envs.py` -- change default from "trtllm" to "auto"
