# Bug: `process_vision_info` crashes for non-Qwen vision-language models

## Summary

The `slime/utils/processing_utils.py` module's `process_vision_info` function unconditionally imports from `qwen_vl_utils`, which means it crashes with an `ImportError` for any vision-language model that isn't in the Qwen family (e.g., GLM-4V variants). The function needs a generic fallback that can extract images from chat message dicts without relying on Qwen-specific utilities.

When implemented, `process_vision_info(messages, processor)` must:
- Return a dictionary with exactly two keys: `'images'` and `'videos'`
- Accept a `processor` parameter as its second argument
- Extract PIL Image objects from base64-encoded strings (e.g., `"iVBORw0KGgo..."`)
- Extract PIL Image objects from data URIs (e.g., `"data:image/png;base64,iVBORw0KGgo..."`)
- Pass through PIL Image objects that are already provided directly
- Return `'images': None` or `'images': []` when messages contain no image content
- Handle both list-style content (with `type`/`image` fields) and plain string content

## Related issues

Several other parts of the multimodal pipeline also lack robustness for non-Qwen VL models:

1. **`slime/utils/processing_utils.py` — `load_processor`**: When `AutoProcessor.from_pretrained` fails (which happens for GLM-4V models on older transformers versions), the function just returns `None` instead of trying alternative processor construction paths.

2. **`slime/backends/megatron_utils/actor.py` — `_get_rollout_data`**: The multimodal training input transfer loop assumes every value in the multimodal dict is a `torch.Tensor`, but after serialization/deserialization through Ray, some values may arrive as numpy arrays. The code must detect numpy arrays (via `isinstance(..., np.ndarray)` checks) and convert them to torch tensors before calling `.to()` methods.

3. **`slime/rollout/sglang_rollout.py` — `generate`**: For the first turn of a multimodal conversation, the function sends pre-tokenized `input_ids` to sglang. But for models where the processor expands image tokens, the `input_ids` length mismatches the `image_data` count. Additionally, the code must safely access the `'images'` key in `multimodal_inputs` using `.get("images")` or an `in` check rather than direct key access, to avoid `KeyError` when the key is absent.

4. **`slime_plugins/megatron_bridge/glm4v_moe.py`**: With context parallelism (CP > 1), the vision encoder produces embeddings for ALL image tokens across the full sequence, but each CP rank only holds a zigzag chunk. The image embeddings need to be sliced to match the local chunk's image token positions. Additionally, the vision encoder should be frozen during RL training (no gradients, eval mode), and the vision output extraction needs updating.

## Code Style Requirements

- Python code must pass `ruff` linting checks (rules E, F, B, and UP as configured in the repo's `pyproject.toml`)
- Imports must be sorted correctly according to `isort` (black-compatible profile, as configured in `pyproject.toml`)

## Files to investigate

- `slime/utils/processing_utils.py` — `process_vision_info`, `load_processor`
- `slime/backends/megatron_utils/actor.py` — `_get_rollout_data` method
- `slime/rollout/sglang_rollout.py` — `generate` function
- `slime_plugins/megatron_bridge/glm4v_moe.py` — `forward` method, vision encoder setup
