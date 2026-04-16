# Bug: Cannot override incorrect `model_type` in AutoConfig.from_pretrained

## Problem

Some HuggingFace model checkpoints on the Hub have the wrong `model_type` field in their `config.json`. For example, a checkpoint might declare `model_type: "qwen2_vl"` when it should actually be `"qwen2_5_vl"`. This causes `AutoConfig.from_pretrained` to instantiate the wrong configuration class, leading to downstream errors.

Currently, there is no way for advanced users (e.g., inference frameworks like vLLM) to override the `model_type` read from the config file. Even if you pass `model_type="correct_type"` as a kwarg to `AutoConfig.from_pretrained`, the value from `config.json` always takes precedence because the override is never applied during config dict loading.

Internally, `AutoConfig.from_pretrained` delegates config dict loading to `PretrainedConfig._get_config_dict`. The `model_type` kwarg is available in `kwargs` within that method, but is currently ignored when constructing the config dict.

## Expected behavior

1. **Override behavior**: When `PretrainedConfig._get_config_dict` is called with a `model_type` kwarg that differs from the value in the config file, the returned config dict should use the caller's value. For example:
   - Config has `"wrong_type"`, kwarg is `"correct_type"` -> returned dict has `model_type == "correct_type"`
   - Config has `"qwen2_vl"`, kwarg is `"qwen2_5_vl"` -> returned dict has `model_type == "qwen2_5_vl"`
   - Config has `"gpt2"`, kwarg is `"llama"` -> returned dict has `model_type == "llama"`

2. **Warning on mismatch**: When the override is applied (i.e., kwarg `model_type` differs from the config value), a WARNING-level log message must be emitted to the `transformers.configuration_utils` logger that includes **both** the original type from the config file **and** the new type from the kwarg in the same message. For example, if the config has `old_type` and the kwarg passes `new_type`, the warning must mention both `old_type` and `new_type`. This must work for any pair of mismatched types (e.g., `gpt2`/`llama`, `bert`/`roberta`).

3. **No warning when matching**: If the kwarg `model_type` matches the value already in the config file, no warning should be emitted -- specifically, no message containing "override" (case-insensitive) should appear in the logger output.

4. **Regression**: Loading a checkpoint without a `model_type` kwarg must continue to work unchanged -- `PretrainedConfig._get_config_dict` must still return the correct `model_type` and all other config values (e.g., `hidden_size`) from the config file. When the kwarg matches the config value, the config dict must not be modified and no override warning may appear.

## Code quality requirements

The modified file `src/transformers/configuration_utils.py` must satisfy:

- At least 800 lines (must not be stubbed out)
- Pass `ruff check src/transformers/configuration_utils.py` with zero violations
- Introduce no more than 30 new lines compared to HEAD (keep the fix minimal)
- Successfully compile (`py_compile`)
- Import without errors (`from transformers.configuration_utils import PretrainedConfig`)
- `from transformers import *` must still work

## Repository validation

The fix must not break any of the following repository CI check scripts (all run from the repo root):

- `python utils/check_config_docstrings.py`
- `python utils/check_config_attributes.py`
- `python utils/check_inits.py`
- `python utils/check_dummies.py`
- `python utils/check_modeling_structure.py`
- `python utils/check_pipeline_typing.py`
- `python utils/check_doc_toc.py`
- `python utils/check_doctest_list.py`
- `python utils/sort_auto_mappings.py --check_only`

## Reproduction

```python
from transformers import PretrainedConfig

# Create a checkpoint directory with model_type="wrong_type" in config.json
# Then try to override it:
config_dict, kwargs = PretrainedConfig._get_config_dict(
    "path/to/checkpoint", model_type="correct_type"
)
print(config_dict["model_type"])  # Currently prints "wrong_type", should print "correct_type"
```
