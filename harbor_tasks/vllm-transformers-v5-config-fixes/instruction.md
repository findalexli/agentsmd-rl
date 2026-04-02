# Transformers v5 Config Compatibility Bugs

After upgrading to transformers v5, several vendored model configuration classes in `vllm/transformers_utils/configs/` crash during instantiation with validation errors. The transformers library recently added strict validation to `PretrainedConfig.__init__()`, and our custom config subclasses are not compatible with this change.

## Symptoms

1. **Config init crashes**: `ColModernVBertConfig`, `FlexOlmoConfig`, `IsaacConfig`, and `Qwen3NextConfig` all raise validation errors when instantiated. The parent class's `__init__` now performs validation, but these subclasses haven't finished setting up their attributes by the time validation runs.

2. **Step3p5Config fails on some checkpoints**: Certain model checkpoints provide a `layer_types` list with more entries than `num_hidden_layers`, triggering a length validation mismatch during config loading.

3. **DeepseekVLV2Config nested config errors**: The DeepSeek VL v2 config fails because nested sub-configuration dictionaries (vision, projector, language) aren't properly separated from the kwargs before the parent constructor processes them, leading to type validation errors. Additionally, the `kv_lora_rank` field from `DeepseekV2Config` needs special handling under v5's stricter type system.

4. **Custom configs not found via AutoConfig**: The `HFConfigParser.parse()` method in `vllm/transformers_utils/config.py` loads all custom config types directly from the internal registry, bypassing `AutoConfig`. This means other vllm subsystems (tokenizer loading, etc.) that use `AutoConfig.from_pretrained()` can't find these config classes. Only a small subset of configs (speculative decoding) actually need direct loading.

## Files to investigate

- `vllm/transformers_utils/config.py` — `HFConfigParser.parse()` method
- `vllm/transformers_utils/configs/colmodernvbert.py` — `ColModernVBertConfig.__init__()`
- `vllm/transformers_utils/configs/deepseek_vl2.py` — `DeepseekVLV2Config.__init__()`
- `vllm/transformers_utils/configs/flex_olmo.py` — `FlexOlmoConfig.__init__()`
- `vllm/transformers_utils/configs/isaac.py` — `IsaacConfig.__init__()`
- `vllm/transformers_utils/configs/qwen3_next.py` — `Qwen3NextConfig.__init__()`
- `vllm/transformers_utils/configs/step3p5.py` — `Step3p5Config.__init__()`
