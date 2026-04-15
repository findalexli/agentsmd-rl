# Bug: LoRA adapters with `target_modules="all-linear"` fail to load

## Summary

When loading a LoRA adapter whose PEFT config uses `target_modules="all-linear"` (or `"all"`), SGLang raises a `ValueError` telling the user to manually specify `--lora-target-modules` on the CLI. This is inconvenient — HuggingFace adapters commonly use this shorthand, and other serving frameworks resolve it automatically.

The server should auto-detect the LoRA-compatible linear modules by inspecting the base model, rather than requiring users to enumerate them manually.

## Reproduction

1. Start the server with a LoRA adapter that has `target_modules: "all-linear"` in its PEFT config (many public HuggingFace adapters use this).
2. Observe the error:
   ```
   ValueError: LoRA adapter '<name>' uses target_modules='all-linear' which cannot
   be resolved automatically. Please explicitly specify --lora-target-modules during
   server startup.
   ```

## Relevant Files

- `python/sglang/srt/lora/lora_manager.py` — the `init_lora_shapes()` method handles target module resolution; the `init_lora_modules()` method wraps base model modules with LoRA layers
- `python/sglang/srt/lora/utils.py` — utility functions for normalizing target module names

## Required Behavior

### Auto-detection function

A function named `auto_detect_lora_target_modules` must be available in `python/sglang/srt/lora/utils.py`. It takes a PyTorch model and returns a `set` of normalized LoRA target module name strings, derived by inspecting the model's submodule hierarchy. The detection rules are:

- Submodules that are instances of `LinearBase` (from `sglang.srt.layers.linear`): the leaf name of the module is included **only if** it is a recognized LoRA-compatible name. Recognized names include `qkv_proj`, `o_proj`, `gate_up_proj`, and `down_proj`. Modules with unrecognized names (e.g., `weird_custom_proj`) must be excluded.
- Submodules that are instances of `ParallelLMHead` (from `sglang.srt.layers.vocab_parallel_embedding`) are detected as `"lm_head"`.
- Submodules that are instances of `FusedMoE` (from `sglang.srt.layers.moe.fused_moe_triton.layer`) produce both `"gate_up_proj"` and `"down_proj"`.
- `nn.Embedding` modules are **not** linear layers and must not be included in detection results.

For a dense transformer model with `qkv_proj`, `o_proj`, `gate_up_proj`, `down_proj` (all `LinearBase`), `lm_head` (`ParallelLMHead`), and an `nn.Embedding` for embeddings, auto-detection should return `{"qkv_proj", "o_proj", "gate_up_proj", "down_proj", "lm_head"}` — excluding the embedding.

### Normalization behavior of `get_normalized_target_modules`

The existing `get_normalized_target_modules` function must be updated to:

- **Reject invalid string inputs**: When called with a string value other than `"all"` or `"all-linear"` (e.g., `"linear"`, `"custom-target"`, `"some-invalid-shorthand"`), it must raise a `ValueError` whose message mentions both `"all"` and `"all-linear"`.
- **Preserve existing behavior for valid inputs**:
  - `"all-linear"` and `"all"` → returns `{"all"}`
  - List inputs are normalized: `"q_proj"` and `"v_proj"` merge into `"qkv_proj"`, `"gate_proj"` normalizes to `"gate_up_proj"`, `"down_proj"` stays as `"down_proj"`. For example, `["q_proj", "v_proj", "gate_proj", "down_proj"]` returns `{"qkv_proj", "gate_up_proj", "down_proj"}`.

### Changes to `lora_manager.py`

- **`init_lora_shapes()`**: Must no longer raise a `ValueError` containing the text `"cannot be resolved automatically"`. When an adapter uses `target_modules="all-linear"` or `"all"` and no CLI override is provided, the method should resolve the modules by calling `auto_detect_lora_target_modules` on the base model.
- **Import**: `get_normalized_target_modules` must be imported from `sglang.srt.lora.utils` in `lora_manager.py`.
- **`init_lora_modules()`**: `get_layer_id()` returns `None` for modules outside the standard `model.layers.N.xxx` hierarchy (e.g., `lm_head`). The code must guard against this — modules with a `None` layer ID must be handled gracefully to prevent an `IndexError`.
