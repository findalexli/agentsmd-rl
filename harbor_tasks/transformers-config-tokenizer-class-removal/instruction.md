# Bug: `tokenizer_class` attribute on `PreTrainedConfig` causes compatibility issues

## Summary

The `PreTrainedConfig` base class in `src/transformers/configuration_utils.py` declares a `tokenizer_class` class-level attribute. This attribute was never meant to be part of the config's public API — it was a leftover from an older design where configs carried a reference to their associated tokenizer class. Now that configs support arbitrary `**kwargs`, this explicit field is redundant and causes problems.

## Symptoms

1. When downstream frameworks (e.g., vLLM) instantiate configs for custom models via `AutoConfig.from_pretrained(...)`, the `tokenizer_class` attribute appears in the serialized config dict even though no tokenizer class was explicitly set. This pollutes the config namespace and can interfere with custom model loading pipelines.

2. The import of `PreTrainedTokenizerBase` in `configuration_utils.py` is only needed for the type annotation of this attribute. Removing the attribute would also remove this unnecessary import dependency, making config-only imports lighter.

3. The `MT5Config` and `UMT5Config` model configs in `src/transformers/models/mt5/configuration_mt5.py` and `src/transformers/models/umt5/configuration_umt5.py` both override this attribute with a hardcoded default of `"T5Tokenizer"`. This hardcoded value leaks into serialized configs and is not appropriate for a config object.

## Affected Files

- `src/transformers/configuration_utils.py` — the base `PreTrainedConfig` class
- `src/transformers/models/mt5/configuration_mt5.py` — `MT5Config`
- `src/transformers/models/umt5/configuration_umt5.py` — `UMT5Config`
- `tests/utils/test_configuration_utils.py` — test that tracks known common kwargs

## Expected Behavior

- `PreTrainedConfig()` should not have `tokenizer_class` as a declared class attribute
- `MT5Config()` and `UMT5Config()` should not serialize a default `tokenizer_class` value
- The `configuration_utils` module should not need to import tokenizer base classes
- Users can still pass `tokenizer_class` as a kwarg if needed (handled by `**kwargs`)
