# Embedding VLMs report spurious missing weight warnings

## Problem

The embedding/retrieval VLM models (`ColPaliForRetrieval`, `ColQwen2ForRetrieval`, `ColModernVBertForRetrieval`) incorrectly report `missing_weights - lm_head not found` errors when loading pretrained weights. These models are used purely for retrieval (producing embeddings), not text generation -- they have no language model head and should never require one.

The root cause is that these models wrap their underlying VLM using `AutoModelForImageTextToText`, which creates a full causal-LM model including an `lm_head`. Since the retrieval models only use the backbone for embedding extraction, they should use the base model class instead, which doesn't include the head.

Additionally, the `base_model_prefix` is not set on these retrieval classes, which means the framework doesn't know where to find the nested base model for weight loading purposes. This causes weight-name mismatches during checkpoint conversion.

## Files to investigate

- `src/transformers/models/colpali/modeling_colpali.py` -- `ColPaliForRetrieval.__init__` and `forward`
- `src/transformers/models/colqwen2/modeling_colqwen2.py` -- `ColQwen2ForRetrieval.__init__` and `forward`
- `src/transformers/models/colqwen2/modular_colqwen2.py` -- the modular source for ColQwen2
- `src/transformers/models/colmodernvbert/modeling_colmodernvbert.py` -- `ColModernVBertForRetrieval`
- `src/transformers/conversion_mapping.py` -- `_build_checkpoint_conversion_mapping()` for weight renaming rules

## Expected behavior

- These retrieval models should load without any missing-weight warnings about `lm_head`
- The underlying VLM should be instantiated as a base model (without a head), not as a causal-LM model
- Forward calls should go directly through the base model, not through a `.model` sub-attribute
- Weight conversion mappings should be correct for the actual model architecture
- Redundant methods that simply delegate to the wrapped VLM can be removed if the base class already provides them
