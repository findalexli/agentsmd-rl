"""Behavioral checks for auto-round-add-claude-skills-for-autoround (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auto-round")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adapt-new-diffusion-model/SKILL.md')
    assert 'description: "Adapt AutoRound to support a new diffusion model architecture (DiT, UNet, hybrid AR+DiT). Use when a new diffusion model fails quantization, needs custom output configs, requires a custo' in text, "expected to find: " + 'description: "Adapt AutoRound to support a new diffusion model architecture (DiT, UNet, hybrid AR+DiT). Use when a new diffusion model fails quantization, needs custom output configs, requires a custo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adapt-new-diffusion-model/SKILL.md')
    assert 'def your_model_pipeline_fn(pipe, prompts, guidance_scale=7.5, num_inference_steps=28, generator=None, **kwargs):' in text, "expected to find: " + 'def your_model_pipeline_fn(pipe, prompts, guidance_scale=7.5, num_inference_steps=28, generator=None, **kwargs):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adapt-new-diffusion-model/SKILL.md')
    assert '| GLM-Image | Hybrid AR+DiT | `HYBRID_AR_COMPONENTS` + `SPECIAL_MULTIMODAL_BLOCK` + DiT `output_configs` |' in text, "expected to find: " + '| GLM-Image | Hybrid AR+DiT | `HYBRID_AR_COMPONENTS` + `SPECIAL_MULTIMODAL_BLOCK` + DiT `output_configs` |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adapt-new-llm/SKILL.md')
    assert 'description: "Adapt AutoRound to support a new LLM architecture that doesn\'t work out-of-the-box. Use when quantization fails for a new model type, block detection doesn\'t find layers, MoE models need' in text, "expected to find: " + 'description: "Adapt AutoRound to support a new LLM architecture that doesn\'t work out-of-the-box. Use when quantization fails for a new model type, block detection doesn\'t find layers, MoE models need'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adapt-new-llm/SKILL.md')
    assert '| `auto_round/modeling/fused_moe/replace_modules.py` | MoE unfusing registry (`BUILTIN_MODULES`) |' in text, "expected to find: " + '| `auto_round/modeling/fused_moe/replace_modules.py` | MoE unfusing registry (`BUILTIN_MODULES`) |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adapt-new-llm/SKILL.md')
    assert 'SPECIAL_SHARED_CACHE_KEYS["YourModelForCausalLM"] = ("shared_position_embeddings", "shared_rope")' in text, "expected to find: " + 'SPECIAL_SHARED_CACHE_KEYS["YourModelForCausalLM"] = ("shared_position_embeddings", "shared_rope")'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-export-format/SKILL.md')
    assert 'description: "Add a new model export format to AutoRound (e.g., auto_round, auto_gptq, auto_awq, gguf, llm_compressor). Use when implementing a new quantized model serialization format, adding a new p' in text, "expected to find: " + 'description: "Add a new model export format to AutoRound (e.g., auto_round, auto_gptq, auto_awq, gguf, llm_compressor). Use when implementing a new quantized model serialization format, adding a new p'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-export-format/SKILL.md')
    assert 'def save_quantized_as_yourformat(output_dir, model, tokenizer, layer_config, serialization_dict=None, **kwargs):' in text, "expected to find: " + 'def save_quantized_as_yourformat(output_dir, model, tokenizer, layer_config, serialization_dict=None, **kwargs):'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-export-format/SKILL.md')
    assert '| `export_to_gguf/` | gguf | Binary GGUF format with super-block quantization, uses `@register_qtype()` |' in text, "expected to find: " + '| `export_to_gguf/` | gguf | Binary GGUF format with super-block quantization, uses `@register_qtype()` |'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-inference-backend/SKILL.md')
    assert 'description: "Add a new hardware inference backend to AutoRound for deploying quantized models (e.g., CUDA/Marlin, Triton, IPEX/CPU, HPU, ARK). Use when implementing QuantLinear kernels, registering b' in text, "expected to find: " + 'description: "Add a new hardware inference backend to AutoRound for deploying quantized models (e.g., CUDA/Marlin, Triton, IPEX/CPU, HPU, ARK). Use when implementing QuantLinear kernels, registering b'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-inference-backend/SKILL.md')
    assert '| QuantLinear import wiring | `auto_round/inference/backend.py` | `dynamic_import_inference_linear()` |' in text, "expected to find: " + '| QuantLinear import wiring | `auto_round/inference/backend.py` | `dynamic_import_inference_linear()` |'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-inference-backend/SKILL.md')
    assert '| `packing_format` | `list[str]` | How weights are packed: `"auto_round"`, `"auto_gptq"`, etc. |' in text, "expected to find: " + '| `packing_format` | `list[str]` | How weights are packed: `"auto_round"`, `"auto_gptq"`, etc. |'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-quantization-datatype/SKILL.md')
    assert 'description: "Add a new quantization data type to AutoRound (e.g., INT, FP8, MXFP, NVFP, GGUF variants). Use when implementing a new weight/activation quantization scheme, registering a new quant func' in text, "expected to find: " + 'description: "Add a new quantization data type to AutoRound (e.g., INT, FP8, MXFP, NVFP, GGUF variants). Use when implementing a new weight/activation quantization scheme, registering a new quant func'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-quantization-datatype/SKILL.md')
    assert '| `auto_round/data_type/fp8.py` | fp8_e4m3fn, fp8_e5m2, fp8_dynamic, fp8_block | Per-tensor/block FP8 with amax-based scaling |' in text, "expected to find: " + '| `auto_round/data_type/fp8.py` | fp8_e4m3fn, fp8_e5m2, fp8_dynamic, fp8_block | Per-tensor/block FP8 with amax-based scaling |'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-quantization-datatype/SKILL.md')
    assert '| `auto_round/data_type/gguf.py` | GGUF Q2_K through Q8_0 | Super-block quantization with multiple sub-types |' in text, "expected to find: " + '| `auto_round/data_type/gguf.py` | GGUF Q2_K through Q8_0 | Super-block quantization with multiple sub-types |'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-vlm-model/SKILL.md')
    assert 'description: "Add support for a new Vision-Language Model (VLM) to AutoRound, including multimodal block handler, calibration dataset template, and special model handling. Use when integrating a new V' in text, "expected to find: " + 'description: "Add support for a new Vision-Language Model (VLM) to AutoRound, including multimodal block handler, calibration dataset template, and special model handling. Use when integrating a new V'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-vlm-model/SKILL.md')
    assert '| `qwen3_omni_moe` | `_get_qwen3_omni_moe_multimodal_block` | qwen3_omni_moe template | Yes (`_qwen3_omni_moe_forward`) |' in text, "expected to find: " + '| `qwen3_omni_moe` | `_get_qwen3_omni_moe_multimodal_block` | qwen3_omni_moe template | Yes (`_qwen3_omni_moe_forward`) |'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-vlm-model/SKILL.md')
    assert '| `deepseek_vl_v2` | `_get_deepseek_vl2_multimodal_block` | deepseek_vl_v2 template | Yes (`_deepseek_vl2_forward`) |' in text, "expected to find: " + '| `deepseek_vl_v2` | `_get_deepseek_vl2_multimodal_block` | deepseek_vl_v2 template | Yes (`_deepseek_vl2_forward`) |'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/readme.md')
    assert '- `add-inference-backend`: guides integration of a new hardware inference backend' in text, "expected to find: " + '- `add-inference-backend`: guides integration of a new hardware inference backend'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/readme.md')
    assert 'tasks such as adding quantization data types, export formats, VLM model support,' in text, "expected to find: " + 'tasks such as adding quantization data types, export formats, VLM model support,'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/readme.md')
    assert '- `add-vlm-model`: walks through adding support for a new Vision-Language Model,' in text, "expected to find: " + '- `add-vlm-model`: walks through adding support for a new Vision-Language Model,'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert 'description: "Review a pull request for the AutoRound repository with a structured checklist covering code quality, test coverage, documentation, Chinese translations, and quantization-specific concer' in text, "expected to find: " + 'description: "Review a pull request for the AutoRound repository with a structured checklist covering code quality, test coverage, documentation, Chinese translations, and quantization-specific concer'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert '- [ ] Tests are placed in the correct backend directory (`test_cpu/`, `test_cuda/`, etc.)' in text, "expected to find: " + '- [ ] Tests are placed in the correct backend directory (`test_cpu/`, `test_cuda/`, etc.)'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert '- **Priority conflicts**: New backends should not override existing backends unless' in text, "expected to find: " + '- **Priority conflicts**: New backends should not override existing backends unless'[:80]

