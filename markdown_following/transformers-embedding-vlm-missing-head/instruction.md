# Embedding VLMs report spurious missing weight warnings

## Problem

The embedding/retrieval VLM models (`ColPaliForRetrieval`, `ColQwen2ForRetrieval`, `ColModernVBertForRetrieval`) incorrectly report `missing_weights - lm_head not found` errors when loading pretrained weights. These models are used purely for retrieval (producing embeddings), not text generation -- they have no language model head and should never require one.

Currently, these models import `AutoModelForImageTextToText` to load their VLM component, and their forward methods access the VLM through `self.vlm.model()` and `self.vlm.model.visual()` indirections. These patterns assume a causal LM head exists, which triggers the spurious weight warnings.

## Expected behavior

- These retrieval models should load without any missing-weight warnings about `lm_head`
- `ColPaliForRetrieval.base_model_prefix`, `ColQwen2ForRetrieval.base_model_prefix`, and `ColModernVBertForRetrieval.base_model_prefix` must all be set to `"vlm"`
- The forward methods should call `self.vlm()` directly rather than going through `.model` indirections
- The conversion mapping in `src/transformers/conversion_mapping.py` must include an entry for `colqwen2`
- The conversion mapping must NOT include an entry for `colpali`

## Key modules

The retrieval models are defined in the `src/transformers/models/` directory:
- `colpali/` — contains `ColPaliForRetrieval`
- `colqwen2/` — contains `ColQwen2ForRetrieval` and its `modular_colqwen2.py` source
- `colmodernvbert/` — contains `ColModernVBertForRetrieval`

The `colqwen2` model uses the modular model generation system; its `modular_colqwen2.py` file is the authoritative source that generates the standalone `modeling_colqwen2.py`. Any changes must be made to the modular file, not just the generated modeling file.

The checkpoint conversion mapping is defined in `_build_checkpoint_conversion_mapping()`.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
