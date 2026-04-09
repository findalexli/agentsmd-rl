# Fix LoRA GT generation backend selection

## Problem

In GT (ground truth) generation mode for diffusion CI, LoRA test cases were being forced to use `--backend diffusers`, but this is inconsistent with normal CI inference where LoRA cases use the native SGLang backend. This caused GT outputs for LoRA cases to be generated under a different execution path than the one used in normal CI, leading to inconsistent results.

Additionally, in GT mode, the pre-generation `set_lora` step for dynamic LoRA loading was being skipped entirely. This meant that dynamic LoRA cases in GT mode would fail to load their LoRA adapters before generation.

## Expected Behavior

1. In GT generation mode, **non-LoRA cases** should still be forced to `--backend diffusers` for consistent ground truth generation
2. In GT generation mode, **LoRA cases** should NOT be forced to `--backend diffusers` - they should use the normal SGLang backend path so adapter state matches CI
3. Dynamic LoRA loading (`set_lora` step) should run in GT mode before generation for cases that have `run_lora_dynamic_load_check=True`

## Files to Look At

- `python/sglang/multimodal_gen/test/server/test_server_common.py` — This file contains the `diffusion_server` pytest fixture that sets up the server args, and the `test_diffusion_generation` test method. Look for:
  - The `SGLANG_GEN_GT` environment variable check that forces `--backend diffusers`
  - The `run_lora_dynamic_load_check` logic that was skipping GT mode
