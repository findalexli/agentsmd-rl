# Bug: Mistral Small 4 fails to start due to config/weight format mismatch

## Problem

When launching models in the Mistral family (e.g. `Mistral-Small-4-119B-2603`), the server crashes with an `AttributeError` because attention weight tensors (e.g. `w_kc`) are `None`.

## Root Cause

Mistral models may ship with both `params.json` (native Mistral format) and `config.json` (HuggingFace format) in the same model repository. This creates a mismatch:

1. **Config loading**: Some Mistral models are routed through a native config loader that reads `params.json` and expects native weight names like `layers.X.attention.wkv_b.weight`.

2. **Weight loading**: The format detection logic currently returns `False` (HuggingFace format) whenever **both** `params.json` and `config.json` are present. This causes weights to load with HF-style names (e.g. `language_model.model.layers.X.self_attn.kv_b_proj.weight`) instead of native-style names.

3. **Result**: The weight remapping fails to match, attention projection weights are never loaded, and the server crashes with an `AttributeError`.

## Expected Behavior

The format detection should correctly identify which models use Mistral native format, even when both config files are present:

- **Should return True (Mistral native format) for**: `Mistral-Small-4-119B-2603`, `Mistral-Large-3-2503`, `Leanstral-22B-v0.1`, `Mistral-Small-4-Base` — these models are routed through the native config loader and require native weight format.

- **Should return False (HuggingFace format) for**: `Mistral-7B-Instruct-v0.3`, `Codestral-Mamba-22B-v0.1`, `Pixtral-12B-2409`, `Mistral-Small-3-24B`, `Mistral-Nemo-Instruct-2407` — these models should default to HF format even when `params.json` is present.

- **Should return True when only `params.json` is present** (no `config.json`), regardless of model name.

- **Should return False when neither file is present**, or when only `config.json` is present without `params.json`.

## Validation

After fixing the bug:
- `Mistral-Small-4-119B-2603`, `Mistral-Large-3-2503`, `Leanstral-22B-v0.1`, `Mistral-Small-4-Base` — with both `params.json` and `config.json` present → format detection returns `True`
- `Mistral-7B-Instruct-v0.3`, `Codestral-Mamba-22B-v0.1`, `Pixtral-12B-2409`, `Mistral-Small-3-24B`, `Mistral-Nemo-Instruct-2407` — with both `params.json` and `config.json` present → format detection returns `False`
- Any model with only `params.json` (no `config.json`) → format detection returns `True`
- Any model with neither file or only `config.json` → format detection returns `False`