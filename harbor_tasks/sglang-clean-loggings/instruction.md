# Clean up noisy log output and FastAPI deprecation warning

## Problem

When running SGLang services, several logging and API issues create noise:

1. A `FastAPIDeprecationWarning` is emitted at import time from `sglang.srt.utils.json_response` because it imports and subclasses `ORJSONResponse`, which FastAPI has deprecated in favor of direct `Response` with Pydantic serialization.

2. Verbose log output from `flash_attn.cute.cache_utils` floods the console, adding noise without useful information during multimodal generation runs.

3. Two model encoders (`mistral_3.py` and `qwen2_5vl.py`) pass a misspelled keyword argument (`input_embeds` instead of `inputs_embeds`) when constructing causal mask arguments. This may cause `create_causal_mask` to receive an unexpected keyword or miss a required argument.

## Expected Behavior

- No `FastAPIDeprecationWarning` when importing the JSON response utilities
- `flash_attn.cute.cache_utils` logger output is suppressed alongside other noisy loggers
- Model encoders pass the correct keyword argument name to mask creation functions

## Files to Look At

- `python/sglang/srt/utils/json_response.py` — JSON response helpers; uses deprecated FastAPI base class
- `python/sglang/multimodal_gen/runtime/utils/logging_utils.py` — central logger suppression list
- `python/sglang/multimodal_gen/runtime/models/encoders/mistral_3.py` — Mistral 3 encoder with kwarg typo
- `python/sglang/multimodal_gen/runtime/models/encoders/qwen2_5vl.py` — Qwen 2.5VL encoder with same kwarg typo
