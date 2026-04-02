# Incomplete model registry and incorrect type annotation

## Bug 1: Missing models in tokenizer compatibility set

The file `src/transformers/models/auto/tokenization_auto.py` maintains a set called `MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS` that lists model types whose Hub-hosted tokenizer class name doesn't match the expected local class. When a model type is missing from this set, `AutoTokenizer` can fail to load the correct tokenizer for that model.

Several model types that have known incorrect Hub tokenizer classes are missing from this set. Models affected include types from the h2ovl, internvl, minicpm, minimax, molmo, nemotron, nvfp4, openvla, phi3 vision, phimoe, chatlm, and kimi families.

Additionally, the entries in the set are not consistently sorted alphabetically, which makes it harder to maintain and audit.

## Bug 2: Wrong type annotation in Llama4 config

The `Llama4TextConfig` class in `src/transformers/models/llama4/configuration_llama4.py` has an incorrect type annotation for its `layer_types` attribute. This attribute stores string values describing layer types (such as layer kind descriptors), but the current annotation declares them as integers. This causes type-checking tools to flag legitimate usage as errors and could confuse downstream tooling that relies on type hints for validation or serialization.

## Expected behavior

1. All model types with known incorrect Hub tokenizer classes should be listed in `MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS`, sorted alphabetically.
2. The `layer_types` attribute should have a type annotation consistent with its actual string values.
