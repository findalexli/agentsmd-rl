# Bug: Mistral Small 4 fails to start due to config/weight format mismatch

## Problem

When launching `mistralai/Mistral-Small-4-119B-2603`, the server crashes with an `AttributeError` because attention weight tensors (e.g. `w_kc`) are `None`.

## Root Cause

Mistral Small 4 ships with **both** `params.json` (native Mistral format) and `config.json` (HuggingFace format) in its model repository. This creates a mismatch between how the config is loaded and how the weights are loaded:

1. **Config loading**: The model name matches patterns in `hf_transformers_utils.py` that trigger the native Mistral config loader (which reads `params.json` and expects native weight names like `layers.X.attention.wkv_b.weight`).

2. **Weight loading**: The format detection function in `python/sglang/srt/server_args.py` (`_is_mistral_native_format`) sees both `params.json` and `config.json` and returns `False` — defaulting to HuggingFace format. This means weights load with HF-style names (e.g. `language_model.model.layers.X.self_attn.kv_b_proj.weight`).

3. **Result**: The weight remapping regex cannot match the HF names against the native-format expectations, so all weights are skipped as "Unrecognized" — attention projection weights are never loaded, and the server crashes.

## Where to Look

- `python/sglang/srt/server_args.py` — the `_is_mistral_native_format()` method. This is where the format detection logic lives. Currently it returns `False` whenever both `params.json` and `config.json` exist, with no exceptions.

- `python/sglang/srt/hf_transformers_utils.py` — contains name-based checks that route certain models (like Mistral Large 3 and similar architectures) through a native config loader. The format detection in `server_args.py` needs to be aware of which models get routed through this path.

## Expected Behavior

Models that are routed through the native Mistral config loader should also use native weight format, even when both `params.json` and `config.json` are present. The format detection logic should recognize these models and return `True` so that `load_format` is set to `"mistral"`.
