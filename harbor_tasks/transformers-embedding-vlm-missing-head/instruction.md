# Embedding VLMs report spurious missing weight warnings

## Problem

The embedding/retrieval VLM models (`ColPaliForRetrieval`, `ColQwen2ForRetrieval`, `ColModernVBertForRetrieval`) incorrectly report `missing_weights - lm_head not found` errors when loading pretrained weights. These models are used purely for retrieval (producing embeddings), not text generation -- they have no language model head and should never require one.

## Expected behavior

- These retrieval models should load without any missing-weight warnings about `lm_head`
- `ColPaliForRetrieval.base_model_prefix`, `ColQwen2ForRetrieval.base_model_prefix`, and `ColModernVBertForRetrieval.base_model_prefix` must all be set to `"vlm"`
- The conversion mapping in `src/transformers/conversion_mapping.py` must include an entry for `colqwen2`
- The conversion mapping must NOT include an entry for `colpali`

## Files to investigate

- `src/transformers/models/colpali/modeling_colpali.py` -- `ColPaliForRetrieval`
- `src/transformers/models/colqwen2/modeling_colqwen2.py` -- `ColQwen2ForRetrieval`
- `src/transformers/models/colqwen2/modular_colqwen2.py` -- the modular source for ColQwen2
- `src/transformers/models/colmodernvbert/modeling_colmodernvbert.py` -- `ColModernVBertForRetrieval`
- `src/transformers/conversion_mapping.py` -- `_build_checkpoint_conversion_mapping()` for weight renaming rules

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
