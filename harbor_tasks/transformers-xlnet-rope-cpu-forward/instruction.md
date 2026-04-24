# Fix: XLNet relative_positional_encoding performance issue

## Problem

In `src/transformers/models/xlnet/modeling_xlnet.py`, the `XLNetModel.relative_positional_encoding` method has a performance issue. When the model runs on GPU, this method creates internal tensors on CPU by default. The resulting positional embeddings are then moved to the model's device via a `.to()` call in `XLNetModel.forward`, causing unnecessary CPU-to-GPU data transfers on every forward pass.

## Expected Behavior

Modify `relative_positional_encoding` and `forward` in `XLNetModel` to satisfy all of the following:

1. `relative_positional_encoding` must accept a parameter named `device` that defaults to `None`
2. All `torch.arange` calls within `relative_positional_encoding` must use the keyword argument `device=device` so tensors are created directly on the target device
3. `forward()` must pass `device=output_h.device` when calling `relative_positional_encoding`
4. The redundant device-transfer line `pos_emb = pos_emb.to(...)` in `forward()` must be removed

These changes ensure positional embedding tensors are created directly on the target device, eliminating the unnecessary CPU-to-GPU transfer.

## Files to Investigate

- `src/transformers/models/xlnet/modeling_xlnet.py` — the `XLNetModel` class, specifically the `relative_positional_encoding` and `forward` methods

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
