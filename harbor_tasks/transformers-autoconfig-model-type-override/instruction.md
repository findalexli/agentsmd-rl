# Bug: Cannot override incorrect `model_type` in AutoConfig.from_pretrained

## Problem

Some HuggingFace model checkpoints on the Hub have the wrong `model_type` field in their `config.json`. For example, a checkpoint might declare `model_type: "qwen2_vl"` when it should actually be `"qwen2_5_vl"`. This causes `AutoConfig.from_pretrained` to instantiate the wrong configuration class, leading to downstream errors.

Currently, there is no way for advanced users (e.g., inference frameworks like vLLM) to override the `model_type` read from the config file. Even if you pass `model_type="correct_type"` as a kwarg to `AutoConfig.from_pretrained`, the value from `config.json` always takes precedence because the override is never applied during config dict loading.

## Where to look

The relevant code is in `src/transformers/configuration_utils.py`, specifically the `_get_config_dict` classmethod of `PretrainedConfig`. This method loads the JSON config from disk/Hub, populates the `config_dict`, and returns it along with remaining kwargs.

After the config dict is loaded and the timm fallback is handled, the method returns `config_dict, kwargs` without checking whether the caller wanted to override `model_type`.

## Expected behavior

If a user passes `model_type` as a kwarg and it differs from what's in the config file, the config dict should be updated to use the caller's value. A warning should be emitted to let the user know they are overriding the checkpoint's declared model type, since this could lead to unexpected behavior if used incorrectly.

## Reproduction

```python
from transformers import AutoConfig

# Load a checkpoint that has model_type="wrong_type" in its config.json
# Passing model_type="correct_type" should override it, but currently doesn't
config = AutoConfig.from_pretrained("some-checkpoint", model_type="correct_type")
print(config.model_type)  # Still prints "wrong_type"
```
