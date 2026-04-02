# LW-DETR and RT-DETR loss functions crash under float16 autocast

## Bug Description

When using `LwDetrImageLoss` (in `src/transformers/loss/loss_lw_detr.py`) or `RTDetrLoss` (in `src/transformers/loss/loss_rt_detr.py`) with automatic mixed precision (AMP) on a CUDA device with float16, the loss computation crashes with a dtype mismatch error.

The issue occurs in the `loss_labels` method of `LwDetrImageLoss` and the `loss_labels_vfl` method of `RTDetrLoss`. Certain operations (specifically `torch.pow`) are promoted to float32 by CUDA autocast, but the results are then assigned back into tensors that remain in the original lower-precision dtype. This causes a runtime error due to the dtype mismatch.

## Reproduction

Using `LwDetrImageLoss.loss_labels()` with float16 logits under `torch.autocast('cuda', dtype=torch.float16)` triggers the crash. Similarly for `RTDetrLoss.loss_labels_vfl()`.

The relevant functions:
- `LwDetrImageLoss.loss_labels` in `src/transformers/loss/loss_lw_detr.py` — the `neg_weights` computation and the quality-score computation use `pow`/`**` which get promoted to float32 under autocast, then assigned into float16 tensors
- `RTDetrLoss.loss_labels_vfl` in `src/transformers/loss/loss_rt_detr.py` — the `weight` computation uses `pow` which similarly gets promoted

## Expected Behavior

The loss functions should work correctly under float16 automatic mixed precision without crashing. Intermediate computations that get promoted to higher precision by autocast should be cast back to the original dtype before being combined with tensors of the original dtype.

## Additional Context

See [torch.amp documentation](https://docs.pytorch.org/docs/stable/amp.html#cuda-ops-that-can-autocast-to-float32) for the list of ops that autocast promotes to float32, including `torch.pow`.

There is also a related deprecation warning in `loss_lw_detr.py` where a list is used for advanced indexing instead of a tuple.
