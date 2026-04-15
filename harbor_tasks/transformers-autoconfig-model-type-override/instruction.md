# Bug: Cannot override incorrect `model_type` in AutoConfig.from_pretrained

## Problem

Some HuggingFace model checkpoints on the Hub have the wrong `model_type` field in their `config.json`. For example, a checkpoint might declare `model_type: "qwen2_vl"` when it should actually be `"qwen2_5_vl"`. This causes `AutoConfig.from_pretrained` to instantiate the wrong configuration class, leading to downstream errors.

Currently, there is no way for advanced users (e.g., inference frameworks like vLLM) to override the `model_type` read from the config file. Even if you pass `model_type="correct_type"` as a kwarg to `AutoConfig.from_pretrained`, the value from `config.json` always takes precedence because the override is never applied during config dict loading.

## Expected behavior

1. **Override behavior**: If a user passes `model_type` as a kwarg and it differs from what's in the config file, the config dict should be updated to use the caller's value.

2. **Warning on mismatch**: When the override is applied (i.e., kwarg model_type differs from config value), a WARNING must be emitted that includes **both** the original type from the config file **and** the new type from the kwarg. For example, if the config has `old_type` and the kwarg passes `new_type`, the warning must mention `old_type` and `new_type` in the same message.

3. **No warning when matching**: If the kwarg `model_type` matches the value already in the config file, no warning should be emitted — specifically, no message containing "override" (case-insensitive) should appear.

4. **Code quality**: The modified file must:
   - Have at least 800 lines (not stubbed out)
   - Pass `ruff check src/transformers/configuration_utils.py` with zero violations
   - Introduce no more than 30 new lines compared to HEAD

5. **Regression**: Loading a checkpoint without a `model_type` kwarg must continue to work unchanged. When the kwarg matches the config value, the config dict must not be modified and no override warning may appear.

## Reproduction

```python
from transformers import AutoConfig

# Load a checkpoint that has model_type="wrong_type" in its config.json
# Passing model_type="correct_type" should override it, but currently doesn't
config = AutoConfig.from_pretrained("some-checkpoint", model_type="correct_type")
print(config.model_type)  # Still prints "wrong_type"
```