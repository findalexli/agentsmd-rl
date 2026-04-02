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

## Additional Context

When auto-detecting target modules, consider that `get_layer_id()` returns `None` for modules outside the standard `model.layers.N.xxx` hierarchy (e.g., `lm_head`). The module wrapping loop in `init_lora_modules()` currently does not handle this case, which would cause an `IndexError` if such modules are included in the target set.

The auto-detection should only return modules that the LoRA system is known to support (e.g., `qkv_proj`, `o_proj`, `gate_up_proj`, `down_proj`, `lm_head`, `embed_tokens`).
