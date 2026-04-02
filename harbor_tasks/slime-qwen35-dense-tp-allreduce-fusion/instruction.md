# Bug: Qwen3.5 dense model precision regression with tensor parallelism

## Context

The `docker/patch/latest/sglang.patch` file contains patches applied to sglang during the Docker build. Among these patches are modifications to `python/sglang/srt/models/qwen3_5.py`, which adds support for the Qwen3.5 architecture.

## Problem

When running Qwen3.5 **dense** (non-MoE) models with `TP_SIZE > 1`, the model produces incorrect results due to a precision bug in the forward pass of both `Qwen3_5LinearDecoderLayer` and `Qwen3_5AttentionDecoderLayer`.

The issue is in how the MLP output and allreduce communication are handled in the `forward` methods of these two decoder layer classes. Currently, both classes unconditionally call `self.mlp(hidden_states, forward_batch, use_reduce_scatter)` and then immediately run `self.layer_communicator.postprocess_layer(...)`. This calling convention is correct for MoE layers (`Qwen2MoeSparseMoeBlock`) but wrong for dense MLP layers.

Dense MLP layers need to:
1. Check whether allreduce fusion with the next layer should be used (via `self.layer_communicator.should_fuse_mlp_allreduce_with_next_layer`)
2. Call the MLP with the fusion flag instead of `forward_batch`
3. Conditionally skip `postprocess_layer` when fusion is active (setting `_sglang_needs_allreduce_fusion` on the tensor instead)

Additionally, the `allow_allreduce_fusion=True` parameter is missing from the `LayerCommunicator` initialization in both decoder classes' `__init__` methods.

## Files to modify

- `docker/patch/latest/sglang.patch` — the patch hunks targeting `python/sglang/srt/models/qwen3_5.py`

## Expected behavior

After the fix, both `Qwen3_5LinearDecoderLayer` and `Qwen3_5AttentionDecoderLayer` should:
- Pass `allow_allreduce_fusion=True` to the layer communicator in `__init__`
- In `forward`, branch on whether the MLP is a MoE block (`isinstance(self.mlp, Qwen2MoeSparseMoeBlock)`) — if so, use the existing calling convention; if dense, use the allreduce fusion path
- Produce correct numerical results when using tensor parallelism with dense Qwen3.5 models
