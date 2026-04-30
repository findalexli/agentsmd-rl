#!/usr/bin/env bash
set -euo pipefail

cd /workspace/auto-round

# Idempotency guard
if grep -qF "description: \"Adapt AutoRound to support a new diffusion model architecture (DiT" ".claude/skills/adapt-new-diffusion-model/SKILL.md" && grep -qF "description: \"Adapt AutoRound to support a new LLM architecture that doesn't wor" ".claude/skills/adapt-new-llm/SKILL.md" && grep -qF "description: \"Add a new model export format to AutoRound (e.g., auto_round, auto" ".claude/skills/add-export-format/SKILL.md" && grep -qF "description: \"Add a new hardware inference backend to AutoRound for deploying qu" ".claude/skills/add-inference-backend/SKILL.md" && grep -qF "description: \"Add a new quantization data type to AutoRound (e.g., INT, FP8, MXF" ".claude/skills/add-quantization-datatype/SKILL.md" && grep -qF "description: \"Add support for a new Vision-Language Model (VLM) to AutoRound, in" ".claude/skills/add-vlm-model/SKILL.md" && grep -qF "- `add-inference-backend`: guides integration of a new hardware inference backen" ".claude/skills/readme.md" && grep -qF "description: \"Review a pull request for the AutoRound repository with a structur" ".claude/skills/review-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/adapt-new-diffusion-model/SKILL.md b/.claude/skills/adapt-new-diffusion-model/SKILL.md
@@ -0,0 +1,318 @@
+---
+name: adapt-new-diffusion-model
+description: "Adapt AutoRound to support a new diffusion model architecture (DiT, UNet, hybrid AR+DiT). Use when a new diffusion model fails quantization, needs custom output configs, requires a custom pipeline function, or is a hybrid architecture with both autoregressive and diffusion components."
+---
+
+# Adapting AutoRound for a New Diffusion Model Architecture
+
+## Overview
+
+AutoRound's DiffusionCompressor works with standard diffusers pipelines
+(e.g., FLUX). This skill covers what code changes are needed when a new
+diffusion model doesn't work out-of-the-box. Common reasons for adaptation:
+
+- Transformer block type not registered in `output_configs`
+- Non-standard pipeline API (not compatible with `pipe(prompts, ...)`)
+- Hybrid architecture with both AR and diffusion components
+- Model not detected as a diffusion model
+
+## Step 0: Diagnose the Problem
+
+```python
+from auto_round import AutoRound
+
+ar = AutoRound(
+    "your-org/your-diffusion-model",
+    scheme="W4A16",
+    iters=2,
+    nsamples=2,
+    num_inference_steps=5,
+)
+ar.quantize_and_save(output_dir="./test_output", format="fake")
+```
+
+| Error / Symptom | Root Cause | Fix Section |
+|-----------------|-----------|-------------|
+| "using LLM mode" instead of Diffusion | Model not detected as diffusion | Step 1 |
+| `assert len(output_config) == len(tmp_output)` | Block output config mismatch | Step 2 |
+| Pipeline call fails | Non-standard inference API | Step 3 |
+| Hybrid model only quantizes DiT | AR component not handled | Step 4 |
+
+## Step 1: Ensure Model Detection
+
+AutoRound detects diffusion models by checking for `model_index.json` in the
+model directory:
+
+```python
+# auto_round/utils/model.py
+def is_diffusion_model(model_or_path):
+    # Checks for model_index.json presence
+```
+
+If your model doesn't have `model_index.json`, either:
+- Create one in the model directory
+- Force diffusion mode via `ExtraConfig`:
+
+```python
+from auto_round.compressors import ExtraConfig
+
+ar = AutoRound(
+    model,
+    extra_config=ExtraConfig(diffusion_config=DiffusionConfig(...)),
+)
+```
+
+### Pipeline Loading
+
+`diffusion_load_model()` uses `AutoPipelineForText2Image.from_pretrained()` and
+extracts `pipe.transformer` as the quantizable model. If your model uses a
+different attribute (e.g., `pipe.unet`), this needs adjustment in
+`auto_round/utils/model.py`.
+
+## Step 2: Register Transformer Block Output Config
+
+This is the **most common** adaptation needed. The `output_configs` dict maps
+transformer block class names to their output tensor names. Without this,
+calibration crashes because AutoRound doesn't know how to collect activations.
+
+### Find your block class name
+
+```python
+import diffusers
+
+pipe = diffusers.AutoPipelineForText2Image.from_pretrained("your-model")
+for name, module in pipe.transformer.named_modules():
+    if hasattr(module, "forward") and "block" in name.lower():
+        print(f"{name}: {type(module).__name__}")
+```
+
+### Register in `output_configs`
+
+Edit `auto_round/compressors/diffusion/compressor.py`:
+
+```python
+output_configs = {
+    "FluxTransformerBlock": ["encoder_hidden_states", "hidden_states"],
+    "FluxSingleTransformerBlock": ["encoder_hidden_states", "hidden_states"],
+    # Add your block type:
+    "YourTransformerBlock": ["hidden_states"],  # output tensor names in order
+}
+```
+
+The list must match the **exact order** of tensors returned by the block's
+`forward()` method.
+
+### How to determine output tensor names
+
+1. Read the block's `forward()` method in diffusers source code
+2. Identify what tensors it returns (usually `hidden_states`, sometimes also
+   `encoder_hidden_states`)
+3. List them in the order they're returned
+
+**Example**: If `forward()` returns `(hidden_states, encoder_hidden_states)`:
+```python
+output_configs["YourBlock"] = ["hidden_states", "encoder_hidden_states"]
+```
+
+**Example**: If `forward()` returns just `hidden_states`:
+```python
+output_configs["YourBlock"] = ["hidden_states"]
+```
+
+## Step 3: Handle Non-Standard Pipeline API
+
+If your model's inference API differs from the standard
+`pipe(prompts, guidance_scale=..., num_inference_steps=...)`, provide a custom
+pipeline function.
+
+### Option A: Pass `pipeline_fn` parameter (no code changes)
+
+```python
+def your_model_pipeline_fn(pipe, prompts, guidance_scale=7.5, num_inference_steps=28, generator=None, **kwargs):
+    """Custom pipeline function for YourModel."""
+    for prompt in (prompts if isinstance(prompts, list) else [prompts]):
+        pipe.generate(
+            prompt=prompt,
+            cfg_scale=guidance_scale,
+            steps=num_inference_steps,
+            generator=generator,
+        )
+
+
+ar = AutoRound(
+    "your-model",
+    pipeline_fn=your_model_pipeline_fn,
+    num_inference_steps=28,
+    guidance_scale=7.5,
+)
+```
+
+### Option B: Attach to pipe object
+
+If using `diffusion_load_model()` directly:
+
+```python
+pipe._autoround_pipeline_fn = your_model_pipeline_fn
+```
+
+### Option C: Subclass DiffusionCompressor
+
+For full control, override `_run_pipeline()`:
+
+```python
+from auto_round.compressors.diffusion.compressor import DiffusionCompressor
+
+
+class YourModelCompressor(DiffusionCompressor):
+    def _run_pipeline(self, prompts):
+        generator = (
+            None
+            if self.generator_seed is None
+            else torch.Generator(device=self.pipe.device).manual_seed(self.generator_seed)
+        )
+        self.pipe.your_custom_generate(
+            prompts,
+            steps=self.num_inference_steps,
+            cfg=self.guidance_scale,
+            generator=generator,
+        )
+```
+
+## Step 4: Add Hybrid AR+DiT Support
+
+For models with both autoregressive and diffusion components (e.g., GLM-Image).
+
+### 4a. Register AR component
+
+Edit `auto_round/compressors/diffusion/hybrid.py`:
+
+```python
+HYBRID_AR_COMPONENTS = [
+    "vision_language_encoder",  # GLM-Image
+    "your_ar_component",  # Your model's AR attribute name
+]
+```
+
+The attribute name must match what exists on the diffusers pipeline object
+(i.e., `pipe.your_ar_component`).
+
+### 4b. Register DiT block output config
+
+Also in `hybrid.py`, add the DiT-specific output config:
+
+```python
+output_configs["YourDiTBlock"] = ["hidden_states", "encoder_hidden_states"]
+```
+
+### 4c. Register AR block handler
+
+In `auto_round/special_model_handler.py`, add a block handler for the AR
+component so AutoRound knows which layers to quantize:
+
+```python
+def _get_your_hybrid_multimodal_block(model, quant_vision=False):
+    block_names = []
+    if quant_vision and hasattr(model, "vision_encoder"):
+        block_names.append([f"vision_encoder.blocks.{i}" for i in range(len(model.vision_encoder.blocks))])
+    block_names.append([f"language_model.layers.{i}" for i in range(len(model.language_model.layers))])
+    return block_names
+
+
+SPECIAL_MULTIMODAL_BLOCK["your_model_type"] = _get_your_hybrid_multimodal_block
+```
+
+### Hybrid quantization flow
+
+The `HybridCompressor` runs two phases:
+1. **Phase 1 (AR)**: Quantizes the AR component using text calibration data
+   (MLLM-style)
+2. **Phase 2 (DiT)**: Quantizes the DiT component using diffusion pipeline
+   calibration
+
+```python
+ar = AutoRound(
+    "your-hybrid-model",
+    dataset="coco2014",  # DiT calibration
+    ar_dataset="NeelNanda/pile-10k",  # AR calibration
+    quant_ar=True,
+    quant_dit=True,
+)
+```
+
+## Step 5: Add Custom Calibration Dataset (Optional)
+
+If your model needs a specific dataset format:
+
+Edit `auto_round/compressors/diffusion/dataset.py`:
+
+```python
+def get_diffusion_dataloader(dataset_name, nsamples, ...):
+    # Add handling for your dataset format
+    if dataset_name == "your_custom_dataset":
+        return _load_your_dataset(dataset_name, nsamples)
+    ...
+```
+
+The default `coco2014` dataset works for most text-to-image models. Custom
+datasets need a TSV file with `id` and `caption` columns.
+
+## Step 6: Test
+
+```python
+def test_your_diffusion_model():
+    ar = AutoRound(
+        "your-org/your-diffusion-model",
+        scheme="W4A16",
+        iters=2,
+        nsamples=4,
+        num_inference_steps=5,
+        guidance_scale=7.5,
+    )
+    compressed_model, layer_config = ar.quantize()
+    assert len(layer_config) > 0, "No layers quantized"
+    ar.save_quantized(output_dir="./test_output", format="fake")
+```
+
+For hybrid models, test both phases:
+```python
+ar = AutoRound(
+    "your-hybrid-model",
+    quant_ar=True,
+    quant_dit=True,
+    iters=2,
+    nsamples=4,
+)
+```
+
+## Checklist
+
+- [ ] `is_diffusion_model()` detects model (or forced via extra_config)
+- [ ] Transformer block class name identified
+- [ ] `output_configs` entry added with correct output tensor names and order
+- [ ] Pipeline runs without errors during calibration
+- [ ] Custom `pipeline_fn` provided if non-standard API
+- [ ] For hybrid: AR component registered in `HYBRID_AR_COMPONENTS`
+- [ ] For hybrid: AR block handler in `SPECIAL_MULTIMODAL_BLOCK`
+- [ ] For hybrid: DiT output config in `hybrid.py`
+- [ ] Quantization produces valid layers (check "Quantized X/Y layers" log)
+- [ ] Export to `fake` format works
+- [ ] README.md + README_CN.md updated
+
+## Key Files
+
+| File | Purpose |
+|------|---------|
+| `auto_round/compressors/diffusion/compressor.py` | `DiffusionCompressor`, `output_configs` dict |
+| `auto_round/compressors/diffusion/hybrid.py` | `HybridCompressor`, `HYBRID_AR_COMPONENTS` |
+| `auto_round/compressors/diffusion/dataset.py` | Calibration dataset loading |
+| `auto_round/utils/model.py` | `is_diffusion_model()`, `diffusion_load_model()` |
+| `auto_round/special_model_handler.py` | AR block handlers for hybrid models |
+| `auto_round/autoround.py` | Model type routing (diffusion vs hybrid vs LLM) |
+
+## Reference: Existing Adaptations
+
+| Model | Type | What Was Adapted |
+|-------|------|-----------------|
+| FLUX.1-dev | Pure DiT | `output_configs` for `FluxTransformerBlock`/`FluxSingleTransformerBlock` |
+| GLM-Image | Hybrid AR+DiT | `HYBRID_AR_COMPONENTS` + `SPECIAL_MULTIMODAL_BLOCK` + DiT `output_configs` |
+| NextStep | Custom pipeline | `pipeline_fn` parameter for non-standard inference API |
diff --git a/.claude/skills/adapt-new-llm/SKILL.md b/.claude/skills/adapt-new-llm/SKILL.md
@@ -0,0 +1,295 @@
+---
+name: adapt-new-llm
+description: "Adapt AutoRound to support a new LLM architecture that doesn't work out-of-the-box. Use when quantization fails for a new model type, block detection doesn't find layers, MoE models need unfusing, custom forward passes are needed, or non-standard linear layer types need handling."
+---
+
+# Adapting AutoRound for a New LLM Architecture
+
+## Overview
+
+Most standard Transformers-based LLMs work with AutoRound out-of-the-box. This
+skill covers what to do when a new model architecture requires code changes. The
+need for adaptation typically arises from:
+
+- Non-standard layer hierarchy (block detection fails)
+- Fused Mixture-of-Experts (MoE) weights
+- Non-standard linear layer types (not `nn.Linear` or `Conv1D`)
+- Complex multi-component architectures (multimodal routing)
+- Shared cache keys or position embeddings
+
+## Step 0: Diagnose the Problem
+
+Try quantizing the model first:
+
+```python
+from auto_round import AutoRound
+
+ar = AutoRound("your-org/your-model", scheme="W4A16", iters=2, nsamples=2)
+ar.quantize_and_save(output_dir="./test_output", format="auto_round")
+```
+
+Common failure modes and their fixes:
+
+| Error / Symptom | Root Cause | Fix Section |
+|-----------------|-----------|-------------|
+| "No quantizable layers found" | Block detection failed | Step 1 |
+| "Quantized 0/N layers" | Layers not `nn.Linear`/`Conv1D` | Step 4 |
+| Shape mismatch in MoE layers | Fused expert weights | Step 2 |
+| Wrong outputs / calibration diverges | Forward pass not exercised correctly | Step 3 |
+| Cache key errors (Gemma3-style) | Shared position embeddings | Step 5 |
+
+## Step 1: Fix Block Detection
+
+AutoRound discovers quantizable blocks via `get_block_names()` which searches
+recursively for `nn.ModuleList` instances. If your model has a non-standard
+layer hierarchy, block detection may fail.
+
+### Check current detection
+
+```python
+from auto_round.utils import get_block_names
+
+model = ...  # loaded model
+print(get_block_names(model))
+```
+
+### Option A: Use `to_quant_block_names` parameter
+
+For simple cases, override block names without code changes:
+
+```python
+ar = AutoRound(
+    model,
+    to_quant_block_names="model.decoder.layers",  # explicit path
+)
+```
+
+### Option B: Register in `SPECIAL_MULTIMODAL_BLOCK`
+
+For multimodal or multi-component models, add a custom block handler in
+`auto_round/special_model_handler.py`:
+
+```python
+def _get_your_model_multimodal_block(model, quant_vision=False):
+    """Get block names for YourModel.
+
+    YourModel structure:
+    - encoder.layers: encoder blocks
+    - decoder.layers: decoder blocks
+    """
+    block_names = []
+
+    if quant_vision and hasattr(model, "encoder"):
+        block_names.append([f"encoder.layers.{i}" for i in range(len(model.encoder.layers))])
+
+    block_names.append([f"decoder.layers.{i}" for i in range(len(model.decoder.layers))])
+
+    return block_names
+
+
+# Register: key must match model.config.model_type
+SPECIAL_MULTIMODAL_BLOCK["your_model_type"] = _get_your_model_multimodal_block
+```
+
+Also add to support lists if applicable:
+
+```python
+# If text-only calibration works for this multimodal model:
+SUPPORT_ONLY_TEXT_MODELS.append("your_model_type")
+
+# If batch_size must be limited:
+mllms_with_limited_bs = (..., "your_model_type")
+```
+
+## Step 2: Handle MoE (Mixture-of-Experts) Models
+
+MoE models often have fused 3D expert weights (shape
+`[num_experts, hidden, intermediate]`) that must be "unfused" into per-expert
+`nn.Linear` layers for quantization.
+
+### Check if auto-handled
+
+Transformers >= 5.0 has a `linear_loop` experts interface that auto-unfuses
+most MoE models. Test first — it may just work.
+
+### Register custom unfusing
+
+If auto-unfusing fails, create a custom module in
+`auto_round/modeling/fused_moe/`:
+
+**1. Create `auto_round/modeling/fused_moe/your_moe.py`:**
+
+```python
+"""Unfuse fused MoE weights for YourModel."""
+
+import torch
+import torch.nn as nn
+from auto_round.modeling.fused_moe.replace_modules import register_replacement
+
+
+@register_replacement("YourMoELayer")
+def replace_your_moe_layer(module, name, model):
+    """Replace FusedMoE with per-expert nn.Linear layers."""
+    experts = nn.ModuleList()
+    for i in range(module.num_experts):
+        linear = nn.Linear(module.hidden_size, module.intermediate_size, bias=False)
+        linear.weight.data = module.weight[i].clone()
+        experts.append(linear)
+    return experts
+```
+
+**2. Register in `BUILTIN_MODULES`:**
+
+Edit `auto_round/modeling/fused_moe/replace_modules.py`:
+
+```python
+BUILTIN_MODULES["your_model_type"] = LazyImport("auto_round.modeling.fused_moe.your_moe")
+```
+
+### Existing MoE implementations
+
+| Model Type | File | Pattern |
+|------------|------|---------|
+| `llama4` | `fused_moe/llama4.py` | Custom replacement for no `use_experts_implementation` |
+| `deepseek_v2` | `fused_moe/deepseek_v2.py` | q_scale calibration for Gaudi |
+| `qwen3_5_moe` | `fused_moe/qwen3_5_moe.py` | Transformers >= 5.0 support |
+| `step3p5` | `fused_moe/step3_5_moe.py` | Splits fused MoELinear |
+| `qwen3_omni_moe` | `fused_moe/qwen3_omni.py` | Thinker + talker MoE |
+
+## Step 3: Add Custom Forward Pass
+
+Some models have non-standard forward passes that don't get calibrated correctly
+with the default `model.forward()`. This is common for multi-component
+architectures.
+
+Edit `_handle_special_model()` in `auto_round/special_model_handler.py`:
+
+```python
+def _your_model_forward(model, **kwargs):
+    """Custom forward that routes through all quantizable components."""
+    # Example: route through both encoder and decoder
+    encoder_output = model.encoder(**kwargs)
+    decoder_output = model.decoder(encoder_output, **kwargs)
+    return decoder_output
+
+
+def _handle_special_model(model):
+    ...
+    if hasattr(model, "config") and model.config.model_type == "your_model_type":
+        from functools import partial
+
+        model.forward = partial(_your_model_forward, model)
+    return model
+```
+
+### When is this needed?
+
+- Model has multiple sub-models (thinker/talker, encoder/decoder)
+- Default forward doesn't exercise all quantizable layers
+- Model needs special input preprocessing during calibration
+
+### Existing examples
+
+| Model | Custom Forward | Purpose |
+|-------|---------------|---------|
+| `deepseek_vl_v2` | `_deepseek_vl2_forward` | Route through language component |
+| `qwen2_5_omni` | `_qwen2_5_omni_forward` | Route through thinker → talker |
+| `qwen3_omni_moe` | `_qwen3_omni_moe_forward` | Handle MoE routing in omni model |
+
+## Step 4: Handle Non-Standard Linear Layers
+
+AutoRound quantizes these layer types by default:
+
+```python
+# auto_round/utils/common.py
+SUPPORTED_LAYER_TYPES = (torch.nn.Linear, transformers.pytorch_utils.Conv1D)
+INNER_SUPPORTED_LAYER_TYPES = ("FP8Linear",)  # matched by class name string
+```
+
+If your model uses a custom linear type (e.g., `QuantizedLinear`, `FP8Linear`),
+it won't be quantized unless registered.
+
+### Option A: String-based matching
+
+`INNER_SUPPORTED_LAYER_TYPES` matches by class name string — useful for
+external classes that can't be imported directly:
+
+```python
+INNER_SUPPORTED_LAYER_TYPES = ("FP8Linear", "YourCustomLinear")
+```
+
+### Option B: Type-based registration
+
+If you can import the class:
+
+```python
+from your_library import YourLinear
+
+SUPPORTED_LAYER_TYPES = SUPPORTED_LAYER_TYPES + (YourLinear,)
+```
+
+## Step 5: Handle Shared Cache Keys
+
+Some models share tensors across blocks during inference (e.g., Gemma3's
+rotary position embeddings). These must be declared so the calibration cache
+doesn't duplicate or corrupt them.
+
+Edit `SPECIAL_SHARED_CACHE_KEYS` in `auto_round/special_model_handler.py`:
+
+```python
+SPECIAL_SHARED_CACHE_KEYS["YourModelForCausalLM"] = ("shared_position_embeddings", "shared_rope")
+```
+
+The key is the **class name** of the model (not `model_type`).
+
+## Step 6: Test
+
+```python
+def test_your_model_quantization():
+    ar = AutoRound(
+        "your-org/your-model",
+        scheme="W4A16",
+        iters=2,
+        nsamples=2,
+        batch_size=2,
+    )
+    compressed_model, layer_config = ar.quantize()
+    # Verify layers were quantized
+    assert len(layer_config) > 0, "No layers were quantized"
+
+    ar.save_quantized(output_dir="./tmp_your_model", format="auto_round")
+
+    # Verify inference works
+    from auto_round.utils import model_infer
+
+    output = model_infer(compressed_model, tokenizer, "Hello world")
+    assert output is not None
+```
+
+## Step 7: Update Documentation
+
+1. Add model to supported list in `README.md`
+2. Update `README_CN.md` with equivalent Chinese content
+3. Add example script if the model has notable differences
+
+## Checklist
+
+- [ ] `get_block_names()` finds all quantizable blocks
+- [ ] MoE layers (if any) are unfused correctly
+- [ ] `calib()` runs without shape errors
+- [ ] All target layers are quantized (check "Quantized X/Y layers" log)
+- [ ] Forward pass exercises all quantizable components
+- [ ] Quantized model produces valid outputs
+- [ ] Export to target format works
+- [ ] README.md + README_CN.md updated
+
+## Key Files
+
+| File | Purpose |
+|------|---------|
+| `auto_round/special_model_handler.py` | Block handlers, custom forwards, shared cache keys |
+| `auto_round/modeling/fused_moe/replace_modules.py` | MoE unfusing registry (`BUILTIN_MODULES`) |
+| `auto_round/utils/common.py` | `SUPPORTED_LAYER_TYPES`, `INNER_SUPPORTED_LAYER_TYPES` |
+| `auto_round/utils/model.py` | `get_block_names()`, `is_mllm_model()`, model loading |
+| `auto_round/compressors/base.py` | Core quantization loop, `calib()`, `_quantize_blocks()` |
+| `auto_round/autoround.py` | `AutoRound` factory — model type routing logic |
diff --git a/.claude/skills/add-export-format/SKILL.md b/.claude/skills/add-export-format/SKILL.md
@@ -0,0 +1,233 @@
+---
+name: add-export-format
+description: "Add a new model export format to AutoRound (e.g., auto_round, auto_gptq, auto_awq, gguf, llm_compressor). Use when implementing a new quantized model serialization format, adding a new packing method, or extending export compatibility for deployment frameworks like vLLM, SGLang, or llama.cpp."
+---
+
+# Adding a New Export Format to AutoRound
+
+## Overview
+
+This skill guides you through adding a new export format for saving quantized
+models. An export format defines how quantized weights, scales, and zero-points
+are packed and serialized for deployment. Each format is registered via the
+`@OutputFormat.register()` decorator in `auto_round/formats.py`.
+
+## Prerequisites
+
+Before starting, determine:
+
+1. **Target deployment framework**: vLLM, llama.cpp, Transformers, SGLang, etc.
+2. **Packing scheme**: How quantized weights are packed (e.g., INT32 packing,
+   safetensors, GGUF binary)
+3. **Supported quantization schemes**: Which bit-widths, data types, and configs
+   are compatible
+4. **Config format**: How quantization metadata is stored (e.g., `quantize_config.json`,
+   GGUF metadata)
+
+## Step 1: Create Export Module Directory
+
+Create a new directory:
+
+```
+auto_round/export/export_to_yourformat/
+├── __init__.py
+└── export.py
+```
+
+## Step 2: Implement the Export Logic
+
+In `export.py`, implement two core functions:
+
+### `pack_layer()`
+
+Packs a single quantized layer's weights, scales, and zero-points:
+
+```python
+def pack_layer(layer_name, model, backend, output_dtype=torch.float16):
+    """Pack a quantized layer for serialization.
+
+    Args:
+        layer_name: Full module path (e.g., "model.layers.0.self_attn.q_proj")
+        model: The quantized model
+        backend: Backend configuration string
+        output_dtype: Output tensor dtype
+
+    Returns:
+        dict: Packed tensors ready for serialization
+    """
+    layer = get_module(model, layer_name)
+    device = layer.weight.device
+
+    # Get quantization parameters from layer
+    bits = layer.bits
+    group_size = layer.group_size
+    scale = layer.scale
+    zp = layer.zp
+    weight = layer.weight
+
+    # Pack weights according to your format
+    packed_weight = _pack_weights(weight, bits, group_size)
+
+    return {
+        f"{layer_name}.qweight": packed_weight,
+        f"{layer_name}.scales": scale,
+        f"{layer_name}.qzeros": zp,
+    }
+```
+
+### `save_quantized_as_yourformat()`
+
+Saves the complete quantized model:
+
+```python
+def save_quantized_as_yourformat(output_dir, model, tokenizer, layer_config, serialization_dict=None, **kwargs):
+    """Save quantized model in your format.
+
+    Args:
+        output_dir: Directory to save to
+        model: The quantized model
+        tokenizer: Model tokenizer
+        layer_config: Per-layer quantization configuration
+        serialization_dict: Pre-packed layer tensors (optional)
+        **kwargs: Additional format-specific arguments
+    """
+    import os
+    from safetensors.torch import save_file
+
+    os.makedirs(output_dir, exist_ok=True)
+
+    # 1. Pack all quantized layers (if not pre-packed)
+    if serialization_dict is None:
+        serialization_dict = {}
+        for layer_name, config in layer_config.items():
+            serialization_dict.update(pack_layer(layer_name, model, ...))
+
+    # 2. Save weights
+    save_file(serialization_dict, os.path.join(output_dir, "model.safetensors"))
+
+    # 3. Save quantization config
+    quant_config = {
+        "quant_method": "yourformat",
+        "bits": ...,
+        "group_size": ...,
+        # format-specific metadata
+    }
+    # Write config to output_dir
+
+    # 4. Save tokenizer
+    tokenizer.save_pretrained(output_dir)
+```
+
+## Step 3: Register the Format
+
+Create the `OutputFormat` subclass in `auto_round/formats.py`:
+
+```python
+@OutputFormat.register("yourformat")
+class YourFormat(OutputFormat):
+    format_name = "yourformat"
+    support_schemes = ["W4A16", "W8A16"]  # List supported scheme names
+
+    def __init__(self, format: str, ar):
+        super().__init__(format, ar)
+
+    @classmethod
+    def check_scheme_args(cls, scheme: QuantizationScheme) -> bool:
+        """Check if a QuantizationScheme is compatible with this format."""
+        return scheme.bits in [4, 8] and scheme.data_type == "int" and scheme.act_bits >= 16
+
+    def pack_layer(self, layer_name, model, output_dtype=torch.float16):
+        from auto_round.export.export_to_yourformat.export import pack_layer
+
+        return pack_layer(layer_name, model, self.get_backend_name(), output_dtype)
+
+    def save_quantized(self, output_dir, model, tokenizer, layer_config, serialization_dict=None, **kwargs):
+        from auto_round.export.export_to_yourformat.export import save_quantized_as_yourformat
+
+        return save_quantized_as_yourformat(
+            output_dir, model, tokenizer, layer_config, serialization_dict=serialization_dict, **kwargs
+        )
+```
+
+## Step 4: Update SUPPORTED_FORMATS
+
+Update the supported-format registry in `auto_round/utils/common.py` so your
+format appears in CLI help and validation.
+
+In this repository, `SUPPORTED_FORMATS` is a `SupportedFormats` object, not a
+plain list. Add your format string to the `_support_format` tuple inside
+`SupportedFormats.__init__()`:
+
+```python
+class SupportedFormats:
+    def __init__(self):
+        self._support_format = (
+            "auto_round",
+            "auto_gptq",
+            # ...
+            "yourformat",  # Add your format here
+        )
+```
+
+`SUPPORTED_FORMATS = SupportedFormats()` is then built from that tuple (plus
+GGUF-derived formats), so contributors should modify the registry definition,
+not treat `SUPPORTED_FORMATS` itself as a mutable list.
+
+## Step 5: Wire Up Backend Info (If Needed)
+
+If your format requires specific inference backends, register them in
+`auto_round/inference/backend.py`:
+
+```python
+BackendInfos["auto_round:yourformat"] = BackendInfo(
+    device=["cuda"],
+    sym=[True, False],
+    packing_format=["yourformat"],
+    bits=[4, 8],
+    group_size=[32, 64, 128],
+    priority=2,
+)
+```
+
+## Step 6: Test
+
+```python
+def test_yourformat_export(tiny_opt_model_path, dataloader):
+    ar = AutoRound(
+        tiny_opt_model_path,
+        bits=4,
+        group_size=128,
+        dataset=dataloader,
+        iters=2,
+        nsamples=2,
+    )
+    compressed_model, _ = ar.quantize()
+    ar.save_quantized(output_dir="./tmp_yourformat", format="yourformat")
+
+    # Verify saved files exist
+    assert os.path.exists("./tmp_yourformat/model.safetensors")
+
+    # Verify model can be loaded back
+    from transformers import AutoModelForCausalLM
+
+    loaded = AutoModelForCausalLM.from_pretrained("./tmp_yourformat")
+```
+
+## Reference: Existing Export Format Implementations
+
+| Directory | Format Name | Key Patterns |
+|-----------|-------------|--------------|
+| `export_to_autoround/` | auto_round | Native format, QuantLinear packing, safetensors |
+| `export_to_autogptq/` | auto_gptq | GPTQ-compatible INT packing |
+| `export_to_awq/` | auto_awq | AWQ-compatible format |
+| `export_to_gguf/` | gguf | Binary GGUF format with super-block quantization, uses `@register_qtype()` |
+| `export_to_llmcompressor/` | llm_compressor | CompressedTensors format for vLLM |
+
+## Key Registration Points
+
+| What | Where | Mechanism |
+|------|-------|-----------|
+| Format class | `auto_round/formats.py` | `@OutputFormat.register("name")` |
+| Support matrix | `OutputFormat.support_schemes` | Class attribute list |
+| Backend info | `auto_round/inference/backend.py` | `BackendInfos["name"]` dict |
+| CLI format registry | `auto_round/utils/common.py` | `SupportedFormats._support_format` tuple |
diff --git a/.claude/skills/add-inference-backend/SKILL.md b/.claude/skills/add-inference-backend/SKILL.md
@@ -0,0 +1,250 @@
+---
+name: add-inference-backend
+description: "Add a new hardware inference backend to AutoRound for deploying quantized models (e.g., CUDA/Marlin, Triton, IPEX/CPU, HPU, ARK). Use when implementing QuantLinear kernels, registering backend capabilities, or enabling quantized model inference on a new hardware platform."
+---
+
+# Adding a New Inference Backend to AutoRound
+
+## Overview
+
+This skill guides you through adding a new inference backend for running
+quantized models on a specific hardware platform. A backend defines how
+quantized weights are unpacked and computed at inference time. AutoRound
+automatically selects the best available backend based on hardware, quantization
+config, and priority.
+
+## Prerequisites
+
+Before starting, determine:
+
+1. **Target hardware**: CPU (Intel/AMD), CUDA GPU, Intel XPU, Habana HPU, etc.
+2. **Supported quantization configs**: Which bit-widths, group sizes, and data
+   types your backend handles
+3. **Kernel implementation**: Triton, CUDA C++, PyTorch native, or external
+   library (e.g., GPTQModel Marlin)
+4. **Packing format**: How quantized weights are stored in memory
+
+## Step 1: Register Backend Info
+
+Edit `auto_round/inference/backend.py` to register your backend's capabilities:
+
+```python
+BackendInfos["auto_round:your_backend"] = BackendInfo(
+    device=["cuda"],  # Supported devices
+    sym=[True, False],  # Symmetric and/or asymmetric
+    packing_format=["auto_round"],  # Compatible packing formats
+    bits=[2, 4, 8],  # Supported bit-widths
+    group_size=[32, 64, 128, -1],  # Supported group sizes (-1 = per-channel)
+    compute_dtype=["float16", "bfloat16"],  # Compute precision
+    data_type=["int"],  # Quantization data types
+    act_bits=[16, 32],  # Activation bit-widths (16 = WxA16)
+    priority=2,  # Higher = preferred (0-5 typical range)
+    checkers=[your_feature_checker],  # Validation functions (optional)
+    alias=["your_backend_short"],  # Alternative names (optional)
+    requirements=["some_package>=1.0"],  # Required packages (optional)
+    systems=["linux"],  # OS restriction (optional)
+)
+```
+
+### BackendInfo Fields Reference
+
+| Field | Type | Description |
+|-------|------|-------------|
+| `device` | `list[str]` | Hardware targets: `"cpu"`, `"cuda"`, `"xpu"`, `"hpu"` |
+| `sym` | `list[bool]` | `True` for symmetric, `False` for asymmetric |
+| `packing_format` | `list[str]` | How weights are packed: `"auto_round"`, `"auto_gptq"`, etc. |
+| `bits` | `list[int]` | Supported weight bit-widths |
+| `group_size` | `list[int]` | Group sizes; `-1` means per-channel |
+| `compute_dtype` | `list[str]` | Compute precision during inference |
+| `data_type` | `list[str]` | Quantization data types: `"int"`, `"nv_fp"`, `"mx_fp"` |
+| `act_bits` | `list[int]` | Activation bits: `[16, 32]` for weight-only, `[8]` for W8A8 |
+| `priority` | `int` | Selection priority (higher wins when multiple backends match) |
+| `checkers` | `list[Callable]` | Functions to validate layer compatibility |
+| `alias` | `list[str]` | Alternative names for CLI/API usage |
+| `requirements` | `list[str]` | pip-installable dependency specifications |
+| `systems` | `list[str]` | OS names: `"linux"`, `"windows"`, `"darwin"` |
+
+### Checker Functions
+
+Use these pre-built checkers or create your own:
+
+```python
+# Require in_features and out_features divisible by 32
+from auto_round.inference.backend import feature_multiply_checker_32
+
+# Require in_features divisible by group_size
+from auto_round.inference.backend import in_feature_checker_group_size
+
+
+# Custom checker
+def your_feature_checker(in_feature, out_feature, config):
+    """Check if layer dimensions are compatible with your backend."""
+    return in_feature % 64 == 0 and out_feature % 64 == 0 and config["group_size"] in [64, 128]
+```
+
+## Step 2: Implement QuantLinear Module
+
+Create `auto_round_extension/your_device/qlinear_your_backend.py`:
+
+```python
+import torch
+import torch.nn as nn
+
+QUANT_TYPE = "your_backend"
+
+
+class QuantLinear(nn.Module):
+    """Quantized linear layer for your backend.
+
+    Stores packed quantized weights and performs dequantize-then-matmul
+    (or fused quantized matmul) at inference time.
+    """
+
+    QUANT_TYPE = QUANT_TYPE
+
+    def __init__(self, bits, group_size, in_features, out_features, bias=True, sym=True, **kwargs):
+        super().__init__()
+        self.bits = bits
+        self.group_size = group_size
+        self.in_features = in_features
+        self.out_features = out_features
+        self.sym = sym
+
+        # Register packed weight buffers
+        # Example: INT4 packed into INT32
+        pack_factor = 32 // bits
+        self.register_buffer(
+            "qweight",
+            torch.zeros(in_features // pack_factor, out_features, dtype=torch.int32),
+        )
+        self.register_buffer(
+            "scales",
+            torch.zeros(
+                (in_features // group_size, out_features),
+                dtype=torch.float16,
+            ),
+        )
+        if not sym:
+            self.register_buffer(
+                "qzeros",
+                torch.zeros(
+                    (in_features // group_size, out_features // pack_factor),
+                    dtype=torch.int32,
+                ),
+            )
+        if bias:
+            self.register_buffer("bias", torch.zeros(out_features, dtype=torch.float16))
+        else:
+            self.bias = None
+
+    def forward(self, x):
+        """Dequantize weights and compute linear transformation."""
+        weight = self._dequantize()
+        out = torch.matmul(x, weight.T)
+        if self.bias is not None:
+            out += self.bias
+        return out
+
+    def _dequantize(self):
+        """Unpack and dequantize weights."""
+        # Implement your dequantization kernel here
+        # Can use Triton, CUDA, or PyTorch operations
+        ...
+
+    @classmethod
+    def pack(cls, linear, scales, zeros, bias=None):
+        """Pack a standard nn.Linear into this quantized format.
+
+        Called during export to convert calibrated weights into packed format.
+        """
+        ...
+```
+
+## Step 3: Wire Up QuantLinear Import Logic
+
+Register your backend in the explicit import logic in
+`auto_round/inference/backend.py`. In this repository, backend loading is not a
+generic directory scan; `dynamic_import_inference_linear()` maps backend keys to
+specific `QuantLinear` implementations.
+
+Add a new backend key in `BackendInfos[...]` if needed, and make sure
+`dynamic_import_inference_linear()` returns your `QuantLinear` class for that
+backend:
+
+```python
+if backend == "auto_round:your_backend":
+    from auto_round_extension.your_device.qlinear_your_backend import QuantLinear
+
+    return QuantLinear
+```
+
+If your backend fits an existing branch pattern, you can also reuse that logic,
+but contributors should update the explicit import mapping rather than rely on
+implicit auto-discovery.
+
+## Step 4: Add Extension `__init__.py`
+
+Create `auto_round_extension/your_device/__init__.py` if the directory is new:
+
+```python
+# Auto-Round extension for YourDevice backend
+```
+
+## Step 5: Test
+
+### Unit test for the QuantLinear
+
+```python
+def test_your_backend_qlinear():
+    from auto_round_extension.your_device.qlinear_your_backend import QuantLinear
+
+    ql = QuantLinear(bits=4, group_size=128, in_features=256, out_features=512)
+    x = torch.randn(1, 256, dtype=torch.float16, device="cuda")
+    out = ql(x)
+    assert out.shape == (1, 512)
+```
+
+### End-to-end test
+
+```python
+def test_your_backend_e2e(tiny_opt_model_path, dataloader):
+    ar = AutoRound(
+        tiny_opt_model_path,
+        bits=4,
+        group_size=128,
+        dataset=dataloader,
+        iters=2,
+        nsamples=2,
+    )
+    compressed_model, _ = ar.quantize()
+    ar.save_quantized(output_dir="./tmp_backend_test", format="auto_round")
+
+    # Load and verify inference with your backend
+    from transformers import AutoModelForCausalLM, AutoTokenizer
+
+    model = AutoModelForCausalLM.from_pretrained("./tmp_backend_test")
+    tokenizer = AutoTokenizer.from_pretrained("./tmp_backend_test")
+    inputs = tokenizer("Hello", return_tensors="pt").to("cuda")
+    outputs = model.generate(**inputs, max_new_tokens=10)
+    assert outputs.shape[1] > inputs["input_ids"].shape[1]
+```
+
+## Reference: Existing Backend Implementations
+
+| Backend Key | Device | Extension Dir | Key Patterns |
+|-------------|--------|---------------|--------------|
+| `auto_gptq:exllamav2` | CUDA | `cuda/` | Marlin kernels via GPTQModel, priority=3 |
+| `auto_round:triton_*` | CUDA | `triton/` | Triton JIT-compiled kernels |
+| `auto_round:torch_*` | CPU/CUDA | `torch/` | Pure PyTorch fallback |
+| `auto_round:ark` | ARK | `ark/` | ARK accelerator kernels |
+| HPU backends | HPU | `hpu/` | Habana Gaudi optimized |
+| IPEX backends | CPU | `ipex/` | Intel Extension for PyTorch |
+
+## Key Registration Points
+
+| What | Where | Mechanism |
+|------|-------|-----------|
+| Backend capabilities | `auto_round/inference/backend.py` | `BackendInfos["name"]` dict |
+| QuantLinear module | `auto_round_extension/<device>/qlinear_*.py` | `QUANT_TYPE` class attr |
+| QuantLinear import wiring | `auto_round/inference/backend.py` | `dynamic_import_inference_linear()` |
+| Feature checkers | `auto_round/inference/backend.py` | `functools.partial` wrappers |
diff --git a/.claude/skills/add-quantization-datatype/SKILL.md b/.claude/skills/add-quantization-datatype/SKILL.md
@@ -0,0 +1,175 @@
+---
+name: add-quantization-datatype
+description: "Add a new quantization data type to AutoRound (e.g., INT, FP8, MXFP, NVFP, GGUF variants). Use when implementing a new weight/activation quantization scheme, registering a new quant function, or extending the data_type registry."
+---
+
+# Adding a New Quantization Data Type to AutoRound
+
+## Overview
+
+This skill guides you through adding a new quantization data type to AutoRound.
+A data type defines how tensors are quantized and dequantized (e.g., INT
+symmetric, FP8 per-block, MXFP4). Each data type is registered via a decorator
+and plugged into the quantization loop automatically.
+
+## Prerequisites
+
+Before starting, determine:
+
+1. **Data type category**: Integer (INT), floating-point (FP8, BF16), mixed-format
+   (MXFP, NVFP), or GGUF variant
+2. **Quantization parameters**: bits, group_size, symmetric/asymmetric, scale format
+3. **Special requirements**: Block-wise scaling, imatrix support, custom rounding
+
+## Step 1: Create the Data Type Module
+
+Create a new file at `auto_round/data_type/your_dtype.py`.
+
+### Function Signature
+
+The quantization function must follow this contract:
+
+```python
+from auto_round.data_type.register import register_dtype
+from auto_round.data_type.utils import reshape_pad_tensor_by_group_size, revert_tensor_by_pad
+
+
+@register_dtype("your_dtype_name")
+def quant_tensor_your_dtype(
+    tensor,
+    bits=4,
+    group_size=128,
+    v=0,
+    min_scale=0,
+    max_scale=0,
+    scale_dtype=torch.float16,
+    q_scale_thresh=0,
+    weight_fp8_max_scale=0,
+    imatrix=None,
+    **kwargs
+):
+    """Quantize a tensor using your data type.
+
+    Args:
+        tensor: The weight tensor to quantize (2D: [out_features, in_features])
+        bits: Number of quantization bits
+        group_size: Number of elements per quantization group
+        v: Learnable perturbation tensor (for SignSGD optimization, same shape as tensor)
+        min_scale: Minimum scale clipping value
+        max_scale: Maximum scale clipping value
+        scale_dtype: Data type for quantization scales
+        q_scale_thresh: Threshold for scale quantization
+        weight_fp8_max_scale: Max scale for FP8 weight quantization
+        imatrix: Importance matrix for weighted quantization (optional)
+        **kwargs: Additional parameters
+
+    Returns:
+        tuple: (qdq_tensor, scale, zp)
+            - qdq_tensor: Quantized-then-dequantized tensor (same shape as input)
+            - scale: Quantization scale tensor
+            - zp: Zero-point tensor (or maxq for symmetric)
+    """
+    # 1. Apply perturbation
+    tensor = tensor + v
+
+    # 2. Reshape by group_size
+    orig_shape = tensor.shape
+    tensor, orig_out_features = reshape_pad_tensor_by_group_size(tensor, group_size)
+
+    # 3. Compute scale and zero-point
+    # ... your quantization logic here ...
+
+    # 4. Quantize and dequantize (Straight-Through Estimator for gradients)
+    from auto_round.data_type.utils import round_ste
+
+    tensor_q = round_ste(tensor / scale) + zp  # or your rounding logic
+    qdq_tensor = (tensor_q - zp) * scale
+
+    # 5. Revert padding
+    qdq_tensor = revert_tensor_by_pad(qdq_tensor, orig_out_features, orig_shape)
+
+    return qdq_tensor, scale, zp
+```
+
+### Key Utilities from `auto_round/data_type/utils.py`
+
+- `reshape_pad_tensor_by_group_size(tensor, group_size)` — Reshape tensor into
+  groups, padding if needed
+- `revert_tensor_by_pad(tensor, orig_out_features, orig_shape)` — Undo padding
+  and restore original shape
+- `round_ste(x)` — Round with Straight-Through Estimator (gradient passthrough)
+- `get_quant_func(data_type, bits)` — Look up registered quant function
+
+## Step 2: Register Multiple Variants (Optional)
+
+If your data type has variants, register them all:
+
+```python
+@register_dtype(["your_dtype", "your_dtype_v2"])
+def quant_tensor_your_dtype(tensor, bits=4, group_size=128, v=0, **kwargs):
+    variant = kwargs.get("data_type", "your_dtype")
+    # Branch logic based on variant
+    ...
+```
+
+## Step 3: Register in `__init__.py`
+
+Add your import to `auto_round/data_type/__init__.py`:
+
+```python
+import auto_round.data_type.your_dtype
+```
+
+This triggers the `@register_dtype` decorator, populating `QUANT_FUNC_WITH_DTYPE`.
+
+## Step 4: Add Scheme Preset (If Needed)
+
+If your data type corresponds to a named scheme (e.g., "W4A16", "MXFP4"), add
+it to `auto_round/schemes.py`:
+
+```python
+YOUR_SCHEME = QuantizationScheme(
+    bits=4,
+    group_size=32,
+    sym=True,
+    data_type="your_dtype",
+)
+PRESET_SCHEMES["YOUR_SCHEME"] = YOUR_SCHEME
+```
+
+## Step 5: Update Export Format Support
+
+If your data type needs specific export handling, update the relevant export
+format's `support_schemes` list in the corresponding `OutputFormat` subclass
+under `auto_round/export/`.
+
+## Step 6: Test
+
+Create tests in the appropriate test directory (e.g., `test/test_cuda/` or
+`test/test_cpu/`):
+
+```python
+def test_your_dtype_quantization(tiny_opt_model_path, dataloader):
+    ar = AutoRound(
+        tiny_opt_model_path,
+        bits=4,
+        group_size=128,
+        data_type="your_dtype",
+        dataset=dataloader,
+        iters=2,
+        nsamples=2,
+    )
+    compressed_model, _ = ar.quantize()
+    # Verify model produces valid outputs
+```
+
+## Reference: Existing Data Type Implementations
+
+| File | Data Types | Key Patterns |
+|------|-----------|--------------|
+| `auto_round/data_type/int.py` | int (sym/asym) | Basic INT quantization with min/max scaling |
+| `auto_round/data_type/fp8.py` | fp8_e4m3fn, fp8_e5m2, fp8_dynamic, fp8_block | Per-tensor/block FP8 with amax-based scaling |
+| `auto_round/data_type/mxfp.py` | mx_fp, mx_fp_rceil | Microscaling with shared exponent |
+| `auto_round/data_type/nvfp.py` | nv_fp, nv_fp4 | NVIDIA FP4 with static group scale |
+| `auto_round/data_type/w4fp8.py` | w4fp8 | Hybrid INT4 weight + FP8 activation |
+| `auto_round/data_type/gguf.py` | GGUF Q2_K through Q8_0 | Super-block quantization with multiple sub-types |
diff --git a/.claude/skills/add-vlm-model/SKILL.md b/.claude/skills/add-vlm-model/SKILL.md
@@ -0,0 +1,257 @@
+---
+name: add-vlm-model
+description: "Add support for a new Vision-Language Model (VLM) to AutoRound, including multimodal block handler, calibration dataset template, and special model handling. Use when integrating a new VLM like LLaVA, Qwen2-VL, GLM-Image, Phi-Vision, or similar multi-modal models for quantization."
+---
+
+# Adding a New Vision-Language Model to AutoRound
+
+## Overview
+
+This skill guides you through adding support for a new Vision-Language Model
+(VLM) to AutoRound. VLMs require special handling because they typically have
+separate vision encoder and language model components, and calibration may need
+multi-modal data.
+
+The integration involves three parts:
+1. **Multimodal Block Handler** — Tell AutoRound how to find quantizable blocks
+2. **Calibration Template** — Define how to build calibration prompts
+3. **Special Model Handler** — Handle model-specific forward pass quirks
+
+## Prerequisites
+
+Before starting, determine:
+
+1. **Model architecture**: What sub-modules exist? (vision encoder, projector,
+   language model, audio tower, etc.)
+2. **Model type**: The `model_type` string from `config.json`
+3. **Block structure**: Where are the transformer layers? (e.g.,
+   `model.layers`, `thinker.model.layers`, `language_model.layers`)
+4. **Text-only support**: Can the model be calibrated with text-only data?
+5. **Batch size limitations**: Does the VLM have restrictions on batch size?
+
+## Step 1: Add Multimodal Block Handler
+
+Edit `auto_round/special_model_handler.py`:
+
+### 1a. Create a block discovery function
+
+```python
+def _get_your_vlm_multimodal_block(model, quant_vision=False):
+    """Get block names for YourVLM model.
+
+    YourVLM structure:
+    - model.vision_encoder.blocks: vision encoder
+    - model.projector.layers: vision-language projector
+    - model.language_model.layers: text decoder
+
+    By default, only the text decoder is quantized. Set quant_vision=True
+    to include vision encoder and projector blocks.
+    """
+    block_names = []
+
+    if quant_vision:
+        if hasattr(model, "model") and hasattr(model.model, "vision_encoder"):
+            if hasattr(model.model.vision_encoder, "blocks"):
+                block_names.append(
+                    [f"model.vision_encoder.blocks.{i}" for i in range(len(model.model.vision_encoder.blocks))]
+                )
+        # Add projector if it has quantizable layers
+        if hasattr(model, "model") and hasattr(model.model, "projector"):
+            if hasattr(model.model.projector, "layers"):
+                block_names.append([f"model.projector.layers.{i}" for i in range(len(model.model.projector.layers))])
+
+    # Language model layers (always quantized)
+    if hasattr(model, "model") and hasattr(model.model, "language_model"):
+        if hasattr(model.model.language_model, "layers"):
+            block_names.append(
+                [f"model.language_model.layers.{i}" for i in range(len(model.model.language_model.layers))]
+            )
+
+    return block_names
+```
+
+### 1b. Register in the `SPECIAL_MULTIMODAL_BLOCK` dict
+
+Find the `SPECIAL_MULTIMODAL_BLOCK` dictionary (in `special_model_handler.py`)
+and add your model:
+
+```python
+SPECIAL_MULTIMODAL_BLOCK["your_vlm"] = _get_your_vlm_multimodal_block
+```
+
+The key must match the `model_type` from the model's `config.json`.
+
+### 1c. Add to support lists
+
+```python
+# If your VLM supports text-only calibration (most do):
+SUPPORT_ONLY_TEXT_MODELS.append("your_vlm")
+
+# If your VLM has batch size limitations:
+mllms_with_limited_bs = (
+    ...,
+    "your_vlm",
+)
+```
+
+## Step 2: Add Calibration Template
+
+### 2a. Create template JSON
+
+Create `auto_round/compressors/mllm/templates/your_vlm.json`:
+
+```json
+{
+    "model_type": "your_vlm",
+    "format_user": "<|user|>\n{content}\n",
+    "format_assistant": "<|assistant|>\n{content}\n",
+    "format_system": "<|system|>\n{content}\n",
+    "format_observation": "",
+    "system": "",
+    "separator": "",
+    "stop_words": ["<|end|>"]
+}
+```
+
+Adjust the template fields to match your model's chat format. Check the model's
+`tokenizer_config.json` or documentation for the correct chat template.
+
+### 2b. Register the template
+
+Edit `auto_round/compressors/mllm/template.py`:
+
+```python
+_register_template(
+    "your_vlm",
+    default_dataset="liuhaotian/llava_conv_58k",  # or appropriate dataset
+    processor=PROCESSORS["default"],  # or a custom processor
+)
+```
+
+### 2c. Add a custom processor (if needed)
+
+If your model requires special image/prompt processing for calibration, create a
+processor in `auto_round/compressors/mllm/template.py`:
+
+```python
+def _your_vlm_processor(raw_data, model_path, seqlen, processor=None, **kwargs):
+    """Process calibration data for YourVLM.
+
+    Args:
+        raw_data: Dataset samples
+        model_path: Path to the model
+        seqlen: Sequence length for calibration
+        processor: The model's processor
+
+    Returns:
+        list: Processed samples ready for calibration
+    """
+    # Build prompts with images and text
+    ...
+```
+
+Register it:
+```python
+PROCESSORS["your_vlm"] = _your_vlm_processor
+```
+
+## Step 3: Handle Special Forward Pass (If Needed)
+
+If your VLM's `forward()` method is non-standard (e.g., requires special
+kwargs, has multiple model components that need separate handling), add a
+custom forward wrapper in `special_model_handler.py`:
+
+```python
+def _your_vlm_forward(model, **kwargs):
+    """Custom forward pass for YourVLM during calibration."""
+    # Handle special input processing
+    # Route inputs to correct sub-models
+    return model.language_model(**kwargs)
+```
+
+Register it in `_handle_special_model()`:
+
+```python
+def _handle_special_model(model):
+    ...
+    if hasattr(model, "config") and model.config.model_type == "your_vlm":
+        from functools import partial
+
+        model.forward = partial(_your_vlm_forward, model)
+    return model
+```
+
+## Step 4: Add Custom Calibration Dataset (Optional)
+
+If your model needs a specialized calibration dataset loader, create one in
+`auto_round/calib_dataset.py` using the `@register_dataset` decorator:
+
+```python
+@register_dataset("your_vlm_dataset")
+class YourVLMDataset:
+    def __init__(self, dataset_name, model_path, seqlen, **kwargs): ...
+
+    def __len__(self):
+        return len(self.data)
+
+    def __iter__(self):
+        for sample in self.data:
+            yield sample
+```
+
+## Step 5: Test
+
+```python
+def test_your_vlm_quantization():
+    model_name = "your-org/your-vlm-small"
+    ar = AutoRound(
+        model_name,
+        bits=4,
+        group_size=128,
+        iters=2,
+        nsamples=2,
+        quant_nontext_module=False,  # text-only quantization
+    )
+    compressed_model, _ = ar.quantize()
+    ar.save_quantized(output_dir="./tmp_your_vlm", format="auto_round")
+```
+
+Test with vision quantization:
+```python
+ar = AutoRound(
+    model_name,
+    bits=4,
+    group_size=128,
+    quant_nontext_module=True,  # also quantize vision encoder
+)
+```
+
+## Step 6: Update Documentation
+
+1. Add your model to the supported VLM list in `README.md`
+2. Update `README_CN.md` with the same changes (Chinese translation required)
+3. Add example quantization script if the model has special usage patterns
+
+## Reference: Existing VLM Implementations
+
+| Model Type | Block Handler | Template | Special Forward |
+|------------|--------------|----------|-----------------|
+| `llava` | `_get_llava_multimodal_block` | llava template | No |
+| `qwen2_vl` | `_get_qwen2_vl_multimodal_block` | qwen2_vl template | No |
+| `qwen2_5_omni` | `_get_qwen2_5_omni_multimodal_block` | qwen2_5_omni template | Yes (`_qwen2_5_omni_forward`) |
+| `qwen3_omni_moe` | `_get_qwen3_omni_moe_multimodal_block` | qwen3_omni_moe template | Yes (`_qwen3_omni_moe_forward`) |
+| `deepseek_vl_v2` | `_get_deepseek_vl2_multimodal_block` | deepseek_vl_v2 template | Yes (`_deepseek_vl2_forward`) |
+| `glm_image` | `_get_glm_image_multimodal_block` | glm_image template | No |
+| `phi3_v` | via generic handler | phi3_v template | No |
+
+## Key Registration Points
+
+| What | Where | Mechanism |
+|------|-------|-----------|
+| Block handler | `special_model_handler.py` | `SPECIAL_MULTIMODAL_BLOCK[model_type]` |
+| Text-only support | `special_model_handler.py` | `SUPPORT_ONLY_TEXT_MODELS` list |
+| Batch limit | `special_model_handler.py` | `mllms_with_limited_bs` tuple |
+| Template | `compressors/mllm/templates/*.json` | `_register_template()` |
+| Processor | `compressors/mllm/template.py` | `PROCESSORS` dict |
+| Custom forward | `special_model_handler.py` | `_handle_special_model()` |
+| Dataset loader | `calib_dataset.py` | `@register_dataset()` |
diff --git a/.claude/skills/readme.md b/.claude/skills/readme.md
@@ -0,0 +1,36 @@
+# Claude Skills for AutoRound
+
+This directory contains Claude Code skills maintained for the `auto-round`
+repository. These skills capture repeatable workflows for common contributor
+tasks such as adding quantization data types, export formats, VLM model support,
+inference backends, and pull request review.
+
+## Directory Structure
+
+Each skill lives in its own directory under `.claude/skills/`. A skill may
+include:
+
+- `SKILL.md`: the main workflow and operating instructions
+- `references/`: focused reference material used by the skill
+
+## Available Skills
+
+- `add-quantization-datatype`: guides integration of a new quantization data
+  type (e.g., INT, FP8, MXFP, NVFP) into the `auto_round/data_type/` registry
+- `add-export-format`: covers addition of a new model export format (e.g.,
+  auto_round, auto_gptq, auto_awq, gguf, llm_compressor)
+- `add-vlm-model`: walks through adding support for a new Vision-Language Model,
+  including template, calibration dataset, and block handler registration
+- `add-inference-backend`: guides integration of a new hardware inference backend
+  (e.g., CUDA, HPU, IPEX, Triton)
+- `review-pr`: provides a structured workflow for reviewing pull requests,
+  including Chinese translation verification
+
+## Maintenance Guidelines
+
+- Keep skill names short and task-oriented.
+- Prefer repository-local paths, commands, and examples.
+- Avoid hardcoding fast-changing support matrices unless the skill is actively
+  maintained alongside those changes.
+- Treat skills as contributor tooling: optimize for clarity, actionability, and
+  low maintenance overhead.
diff --git a/.claude/skills/review-pr/SKILL.md b/.claude/skills/review-pr/SKILL.md
@@ -0,0 +1,133 @@
+---
+name: review-pr
+description: "Review a pull request for the AutoRound repository with a structured checklist covering code quality, test coverage, documentation, Chinese translations, and quantization-specific concerns. Use when reviewing or preparing to submit a PR."
+---
+
+# Pull Request Review Workflow for AutoRound
+
+## Overview
+
+This skill provides a structured workflow for reviewing pull requests in the
+AutoRound repository. It covers code quality, testing, documentation, and
+project-specific requirements like Chinese translation parity.
+
+## Review Checklist
+
+### 1. Code Quality
+
+- [ ] Code follows existing patterns in the codebase (decorator registration,
+      factory patterns, etc.)
+- [ ] No hardcoded paths or credentials
+- [ ] Proper error handling at system boundaries
+- [ ] No unnecessary abstractions or over-engineering
+- [ ] Import organization follows existing conventions
+- [ ] Apache 2.0 license header present on new files:
+  ```python
+  # Copyright (c) 2025 Intel Corporation
+  #
+  # Licensed under the Apache License, Version 2.0 (the "License");
+  # ...
+  ```
+
+### 2. Quantization-Specific Concerns
+
+- [ ] Numerical stability: scale computation avoids division by zero
+- [ ] Gradient flow: uses `round_ste()` or equivalent STE for differentiable
+      rounding
+- [ ] Tensor shapes: group_size reshaping handles padding correctly
+- [ ] dtype consistency: scale_dtype, compute_dtype used properly
+- [ ] Memory efficiency: no unnecessary tensor copies on GPU
+- [ ] Device handling: tensors moved to correct device before operations
+
+### 3. Registration Points
+
+When the PR adds new functionality, verify all registration points are updated:
+
+| Feature | Registration Location |
+|---------|----------------------|
+| Data type | `auto_round/data_type/__init__.py` import + `@register_dtype` |
+| Export format | `auto_round/formats.py` `@OutputFormat.register()` |
+| VLM model | `special_model_handler.py` `SPECIAL_MULTIMODAL_BLOCK` + lists |
+| Backend | `auto_round/inference/backend.py` `BackendInfos` dict |
+| Dataset | `auto_round/calib_dataset.py` `@register_dataset` |
+| Scheme preset | `auto_round/schemes.py` `PRESET_SCHEMES` dict |
+
+### 4. Test Coverage
+
+- [ ] New functionality has corresponding tests
+- [ ] Tests use existing fixtures (`tiny_opt_model_path`, `dataloader`, etc.)
+- [ ] Tests are placed in the correct backend directory (`test_cpu/`, `test_cuda/`, etc.)
+- [ ] Tests use minimal iterations (`iters=2, nsamples=2`) for speed
+- [ ] No flaky assertions (avoid exact float comparisons)
+
+### 5. Documentation
+
+- [ ] README.md updated if user-facing features change
+- [ ] **Chinese translation updated**: Any changes to `*.md` files must have
+      corresponding updates in their `*_CN.md` counterparts:
+  - `README.md` → `README_CN.md`
+  - `docs/step_by_step.md` → `docs/step_by_step_CN.md`
+  - `docs/environments.md` → `docs/environments_CN.md`
+- [ ] Translation maintains equivalent content and structure (not just copied
+      English text)
+- [ ] Docstrings added for new public APIs
+
+### 6. Contributing Requirements
+
+- [ ] Commits are signed off (`git commit -s`) per DCO
+- [ ] No unrelated changes mixed in
+- [ ] PR description clearly explains the motivation and changes
+- [ ] Breaking changes are called out explicitly
+
+## Chinese Translation Verification
+
+This is a **hard requirement** for the AutoRound project. Use this procedure:
+
+1. **Identify modified markdown files**:
+   ```bash
+   git diff --name-only HEAD~1 -- '*.md'
+   ```
+
+2. **Check for corresponding CN files**:
+   For each modified `.md` file, verify a `_CN.md` counterpart exists and is
+   also modified:
+   - `README.md` → `README_CN.md`
+   - `docs/step_by_step.md` → `docs/step_by_step_CN.md`
+   - `docs/environments.md` → `docs/environments_CN.md`
+
+3. **Compare structure**:
+   - Same number of sections/headings
+   - Same tables, code blocks, and links
+   - Equivalent content (not machine-translated gibberish)
+
+4. **Files that do NOT need CN translation** (no `_CN` counterpart exists):
+   - `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
+   - `test/README.md`
+   - `docs/publication_list.md`, `docs/tips_and_tricks.md`, accuracy result docs
+
+## Common Issues to Watch For
+
+### Quantization Bugs
+
+- **Scale overflow**: Large models with small group_size can produce FP16 overflow
+  in scales. Check for `torch.clamp` or `torch.finfo` guards.
+- **Asymmetric zero-point drift**: Zero-points must be integer-rounded for INT
+  quantization.
+- **GGUF super-block alignment**: GGUF formats require specific block sizes
+  (typically 256 elements). Verify padding/alignment logic.
+
+### Export Compatibility
+
+- **Format detection**: Verify `quantize_config.json` or equivalent metadata is
+  saved correctly for the target framework to detect.
+- **Weight name mapping**: Ensure packed weight names match what the inference
+  framework expects.
+- **Mixed-precision layers**: Layers excluded from quantization (e.g., `lm_head`)
+  must be saved in their original format.
+
+### Backend Selection
+
+- **Priority conflicts**: New backends should not override existing backends unless
+  intentional. Check `priority` values.
+- **Feature checker coverage**: Ensure checkers don't silently reject valid layers
+  (test with real model shapes).
PATCH

echo "Gold patch applied."
