# Bug: Models with `sliding_window=0` break model loading

## Summary

Some HuggingFace model checkpoints (e.g., certain Qwen1.5 variants) set `sliding_window` to `0` in their configuration to indicate that sliding window attention is **disabled**. However, vLLM does not handle this convention — it only recognizes `None` as meaning "no sliding window."

When `sliding_window=0` is present in the HF config, vLLM treats it as an active sliding window with a window size of 0. This causes `max_model_len` to be capped to 0 during model configuration, which breaks model loading entirely.

## Relevant Code

The issue is in `vllm/config/model.py`, in the `ModelConfig` class. The `__post_init__` method calls `get_and_verify_max_len()` which uses the raw `sliding_window` value from the HF config. The `get_sliding_window()` method (which reads `hf_text_config.sliding_window`) returns `0` instead of `None`, and downstream logic incorrectly caps the model length.

The fix should handle the `sliding_window=0` case before `get_and_verify_max_len()` is called, converting it to the vLLM convention of `None` for disabled sliding window.

## Reproduction

Any model config with `"sliding_window": 0` in the HuggingFace config will trigger this — the model will fail to load or behave incorrectly because `max_model_len` gets capped to 0.
