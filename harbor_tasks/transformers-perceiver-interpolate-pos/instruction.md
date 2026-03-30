The `interpolate_pos_encoding` method in `PerceiverTrainablePositionEncoding` (in `src/transformers/models/perceiver/modeling_perceiver.py`) has a bug that makes positional encoding interpolation a no-op when called with a different resolution than training.

The method computes `new_height` and `new_width` from the existing position embeddings (the source grid dimensions), then passes those same values as the `size` argument to `nn.functional.interpolate`. This means it interpolates from `(new_height, new_width)` to `(new_height, new_width)` -- effectively doing nothing.

The correct behavior (matching the pattern used in other vision models like ViT, DeiT, etc.) is to pass the target dimensions `(height, width)` to `nn.functional.interpolate` so that the position embeddings are actually resized to match the input resolution.

This causes `PerceiverForImageClassificationLearned` to produce incorrect results when given images at a different resolution from what the model was trained on with `interpolate_pos_encoding=True`.

## File to Modify

- `src/transformers/models/perceiver/modeling_perceiver.py`
