The `interpolate_pos_encoding` method in `PerceiverTrainablePositionEncoding` (in `src/transformers/models/perceiver/modeling_perceiver.py`) has a bug that makes positional encoding interpolation a no-op when called with a different resolution than training.

When `PerceiverTrainablePositionEncoding` is trained at one image resolution and then asked to produce positional encodings for a different resolution (via `interpolate_pos_encoding`), the method returns embeddings with the same shape as the source grid — the interpolation does nothing. This causes `PerceiverForImageClassificationLearned` to produce incorrect results on images whose resolution differs from the training resolution.

Expected behavior: positional encodings should be resized to match the target resolution, similar to how ViT, DeiT, and other vision models handle this. The output tensor's first dimension should equal `height * width`, not the original `index_dims[0] * index_dims[1]`.

## File to Modify

- `src/transformers/models/perceiver/modeling_perceiver.py`

## Verification

The fix can be verified by checking that calling `interpolate_pos_encoding` with different `height`/`width` than the training `index_dims` produces output tensors whose first dimension equals `height * width`, not the original `index_dims[0] * index_dims[1]`. For example, interpolating from a 4×4 source grid (16 positions) to an 8×8 target should yield 64 positions.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
