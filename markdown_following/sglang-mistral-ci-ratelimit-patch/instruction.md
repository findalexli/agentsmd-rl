# Bug: CI tokenizer loads trigger HuggingFace 429 rate limiting

## Context

SGLang's CI scheduled runs are failing across most jobs due to HuggingFace API 429 (Too Many Requests) errors. The HF API has a rate limit of 3000 requests per 5 minutes, and CI is exhausting this quota even when models are locally cached and `HF_HUB_OFFLINE=1` is set.

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

The `get_tokenizer()` function in `python/sglang/srt/utils/hf_transformers_utils.py` must be updated to avoid triggering HuggingFace API calls during tokenizer initialization in CI environments. The CI environment is detected via the `SGLANG_IS_IN_CI` environment variable (from `sglang.srt.environ`).

The root cause is that `is_base_mistral` in `transformers.tokenization_utils_tokenizers` calls `model_info()` on the HuggingFace API even for cached models. Since CI models are always pre-cached HF-format checkpoints (never actual Mistral native format), the check is unnecessary in CI.

## Requirements

The solution must satisfy all of the following:

1. **Introduce module-level state** to track whether the patching has occurred (a boolean flag)
2. **Version guard**: only patch for the specific `transformers` version that has this issue (v5.3.0); for other versions, log a warning and skip patching
3. **CI-only application**: the patch must only activate when `SGLANG_IS_IN_CI` is set to a truthy value
4. **One-time application**: the patching function must be idempotent (safe to call multiple times without breaking)
5. **Correct ordering**: the patch must be applied before `AutoTokenizer.from_pretrained` is called inside `get_tokenizer()`
6. **Logging**: log at INFO level when patching succeeds; log at WARNING level when version mismatch skips the patch
7. **Non-stub implementation**: the patching logic must include conditionals, imports, and assignments (at least 6 statements)

## Expected Symbols

The test suite expects the following identifiers to be defined in `hf_transformers_utils.py`:

- A module-level patching flag (e.g., `_is_base_mistral_patched`)
- A version constant (e.g., `_TRANSFORMERS_PATCHED_VERSION = "5.3.0"`)
- A patching function (e.g., `_patch_is_base_mistral_in_ci`)
- A `filter()` method on `TokenizerWarningsFilter`

## Relevant Files

- `python/sglang/srt/utils/hf_transformers_utils.py` — `get_tokenizer()` function
- `python/sglang/srt/environ.py` — `envs.SGLANG_IS_IN_CI`
