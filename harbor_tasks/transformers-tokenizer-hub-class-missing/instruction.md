# Missing model types in tokenizer Hub compatibility override list

## Bug description

The file `src/transformers/models/auto/tokenization_auto.py` maintains a set called `MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS` that lists model types whose Hub-hosted `tokenizer_config.json` files specify an incorrect or outdated `tokenizer_class` value. When a model type is missing from this set, `AutoTokenizer.from_pretrained()` tries to load the tokenizer class listed on the Hub, which may not exist or may be wrong, causing loading failures.

Several model types are known to have incorrect Hub tokenizer classes but are not listed in this set. Specifically, models from the DeepSeek V2 and V3 families, as well as ModernBERT-based models, fail to load correctly via `AutoTokenizer` because they aren't in the override list.

For example, trying to load a tokenizer for a DeepSeek-R1 or DeepSeek-Coder-V2 model, or a ModernBERT fine-tune, can fail because the Hub config points to a tokenizer class that doesn't match what the library expects.

## Expected behavior

All model types with known incorrect Hub tokenizer classes should be registered in the override set so that `AutoTokenizer` falls back to `TokenizersBackend` for these models.

## Relevant files

- `src/transformers/models/auto/tokenization_auto.py` — the `MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS` set and the loop that adds overrides to `TOKENIZER_MAPPING_NAMES`
