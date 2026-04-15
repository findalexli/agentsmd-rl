# Bug: Qwen3.5 dense model precision regression with tensor parallelism

## Context

The `docker/patch/latest/sglang.patch` file contains patches applied to sglang during the Docker build. Among these patches are modifications to `python/sglang/srt/models/qwen3_5.py`, which adds support for the Qwen3.5 architecture.

## Problem

When running Qwen3.5 **dense** (non-MoE) models with `TP_SIZE > 1`, the model produces incorrect numerical results due to a bug in how allreduce communication is handled in the forward pass of `Qwen3_5LinearDecoderLayer` and `Qwen3_5AttentionDecoderLayer`.

The issue is that dense MLP layers and MoE layers have different communication requirements during the MLP forward pass. Currently, both layer types unconditionally call the MLP and then immediately run `postprocess_layer`, without checking whether the MLP is dense (which requires special allreduce fusion handling) or MoE (which uses a different path).

## Expected Behavior

After the fix, both `Qwen3_5LinearDecoderLayer` and `Qwen3_5AttentionDecoderLayer` should:

1. Correctly distinguish between dense MLP layers and MoE layers during the forward pass
2. For dense MLP layers: use allreduce fusion with the next layer when tensor parallelism is enabled
3. For MoE layers: maintain the existing calling convention
4. Produce correct numerical results when using tensor parallelism with dense Qwen3.5 models

## Files to modify

- `docker/patch/latest/sglang.patch` — the patch hunks targeting `python/sglang/srt/models/qwen3_5.py`

## Required changes

Both `Qwen3_5LinearDecoderLayer` and `Qwen3_5AttentionDecoderLayer` must be fixed:

- In the `__init__` method, pass the appropriate parameters to enable allreduce fusion in the LayerCommunicator
- In the `forward` method:
  - Check the layer communicator to determine whether allreduce fusion with the next layer should be used
  - Branch based on whether the MLP is a MoE block or dense
  - For dense MLPs, call the MLP with the fusion flag instead of the batch parameter
  - When fusion is active, mark the hidden states tensor appropriately and skip the regular postprocessing
  - When fusion is not active, proceed with the normal postprocess_layer call
