# Fix: XLNet relative_positional_encoding computes on CPU every forward pass

## Problem

The `XLNetModel.relative_positional_encoding` method creates all `torch.arange` tensors on CPU by default, regardless of where the model is running. On every forward pass, these tensors are created on CPU and then moved to the model's device via `.to(output_h.device)` at the call site. This causes unnecessary CPU-to-GPU data transfers on every forward pass, degrading performance.

## Root Cause

In `src/transformers/models/xlnet/modeling_xlnet.py`, the `relative_positional_encoding` method creates four `torch.arange` tensors (`freq_seq`, `fwd_pos_seq`, `bwd_pos_seq`) without specifying a `device` parameter. By default, `torch.arange` creates tensors on CPU. The caller in `XLNetModel.forward` then moves the resulting `pos_emb` to the correct device with `.to(output_h.device)`, causing a redundant transfer every forward pass.

## Expected Fix

Add a `device` parameter to `relative_positional_encoding` and pass it to all `torch.arange` calls so tensors are created directly on the correct device. Update the call site in `forward` to pass the device and remove the now-unnecessary `.to()` call.

## Files to Investigate

- `src/transformers/models/xlnet/modeling_xlnet.py` -- the `relative_positional_encoding` method and its call site in `forward`
