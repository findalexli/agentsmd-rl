# AutoTokenizer fails to load tokenizers for deepseek_v2, deepseek_v3, and modernbert

## Bug description

When calling `AutoTokenizer.from_pretrained()` for models of type `deepseek_v2`, `deepseek_v3`, or `modernbert`, tokenizer loading fails or produces incorrect results. The Hub-hosted `tokenizer_config.json` files for these models specify an incorrect or outdated `tokenizer_class` value, but the library does not recognize these model types as needing special fallback handling.

Other model families with the same issue (incorrect Hub tokenizer classes) already load correctly — for example: `arctic`, `chameleon`, `deepseek_vl`, `deepseek_vl_v2`, `fuyu`, `jamba`, `llava`, `phi3`. Investigate how those model types are handled and apply the same approach for the three missing ones.

## Expected behavior

After fixing the issue:

1. `deepseek_v2`, `deepseek_v3`, and `modernbert` should be recognized as having incorrect Hub tokenizer classes, the same way as the existing model types listed above.
2. All three model types must be resolvable in `TOKENIZER_MAPPING_NAMES` (from `transformers.models.auto.tokenization_auto`). That is, `TOKENIZER_MAPPING_NAMES.get("deepseek_v2")`, `TOKENIZER_MAPPING_NAMES.get("deepseek_v3")`, and `TOKENIZER_MAPPING_NAMES.get("modernbert")` must each return a non-`None` value.
3. Existing entries must not be removed — the model types listed above must remain recognized, and core mappings (`bert`, `gpt2`, `roberta`, `t5`) must remain in `TOKENIZER_MAPPING_NAMES`.
4. Auto mappings must remain sorted (the repository enforces this via `utils/sort_auto_mappings.py --check_only`).
5. Code must pass `ruff` formatting and linting checks, and repository consistency checks (`check_copies`, `check_dummies`, `check_inits`, `check_config_attributes`, `check_config_docstrings`, `check_pipeline_typing`, `check_doc_toc`) must continue to pass.
6. Do not modify any `# Copied from` blocks.
