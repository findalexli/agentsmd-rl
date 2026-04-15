# Fix: XLNet relative_positional_encoding performance issue

## Problem

In `src/transformers/models/xlnet/modeling_xlnet.py`, the `XLNetModel.relative_positional_encoding` method has a performance issue. When the model runs on GPU, this method creates internal tensors on CPU by default. The resulting positional embeddings are then moved to the model's device via a `.to()` call in `XLNetModel.forward`, causing unnecessary CPU-to-GPU data transfers on every forward pass.

## Expected Behavior

Tensors should be created directly on the target device so that the redundant device-transfer call in `forward()` is no longer needed. Follow standard PyTorch conventions for device-aware tensor creation functions.

## Files to Investigate

- `src/transformers/models/xlnet/modeling_xlnet.py` — the `XLNetModel` class, specifically the `relative_positional_encoding` and `forward` methods
