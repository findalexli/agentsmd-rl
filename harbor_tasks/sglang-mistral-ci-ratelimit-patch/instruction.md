# Bug: CI tokenizer loads trigger HuggingFace 429 rate limiting

## Context

SGLang's CI scheduled runs are failing across most jobs due to HuggingFace API 429 (Too Many Requests) errors. The HF API has a rate limit of 3000 requests per 5 minutes, and CI is exhausting this quota.

## Root Cause

The `transformers` library (v5.3.0) calls `model_info()` on the HuggingFace API inside `_patch_mistral_regex` → `is_base_mistral` for **every tokenizer load**, even when models are locally cached and `HF_HUB_OFFLINE=1` is set. With N concurrent CI jobs each loading multiple tokenizers, this quickly exhausts the rate limit.

The traceback looks like:
```
AutoTokenizer.from_pretrained
  → XLMRobertaTokenizer.__init__
    → _patch_mistral_regex
      → is_base_mistral(model_id)
        → model_info(model_id)  # HF API call
          → 429 Too Many Requests
```

## What Needs to Happen

The `get_tokenizer()` function in `python/sglang/srt/utils/hf_transformers_utils.py` needs to prevent this unnecessary HF API call when running in CI (detected via the `SGLANG_IS_IN_CI` environment variable from `sglang.srt.environ`).

The `is_base_mistral` function in `transformers.tokenization_utils_tokenizers` only controls regex pattern selection in tokenizer init — CI models are all pre-cached HF-format checkpoints and are never actual Mistral native format, so it's safe to short-circuit this check in CI.

The fix should:
- Only apply in CI (`SGLANG_IS_IN_CI` env var)
- Only apply for the known problematic transformers version (to avoid masking changes in future versions)
- Be applied once, before the first `AutoTokenizer.from_pretrained` call
- Log appropriately (info when patching, warning when version changes)

## Relevant Files

- `python/sglang/srt/utils/hf_transformers_utils.py` — `get_tokenizer()` function
- `python/sglang/srt/environ.py` — `envs.SGLANG_IS_IN_CI`
