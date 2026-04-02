"""
Task: vllm-transformers-v5-config-fixes
Repo: vllm-project/vllm @ 28048bd6b09cb164a934a8c134b7d7a7f4733b4f
PR:   #38247

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib.util
import sys
import types
from pathlib import Path

REPO = "/workspace/vllm"

# Stub parent packages so individual config modules can be loaded without full vllm install
for name in ["vllm", "vllm.transformers_utils", "vllm.transformers_utils.configs"]:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)


def _load_config_module(mod_name: str, filename: str):
    """Load a vllm config module by file path."""
    path = f"{REPO}/vllm/transformers_utils/configs/{filename}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """All modified Python files must parse without syntax errors."""
    import ast

    files = [
        f"{REPO}/vllm/transformers_utils/config.py",
        f"{REPO}/vllm/transformers_utils/configs/colmodernvbert.py",
        f"{REPO}/vllm/transformers_utils/configs/deepseek_vl2.py",
        f"{REPO}/vllm/transformers_utils/configs/flex_olmo.py",
        f"{REPO}/vllm/transformers_utils/configs/isaac.py",
        f"{REPO}/vllm/transformers_utils/configs/qwen3_next.py",
        f"{REPO}/vllm/transformers_utils/configs/step3p5.py",
    ]
    for f in files:
        source = Path(f).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_step3p5_layer_types_cropping():
    """Step3p5Config must crop layer_types to num_hidden_layers length."""
    from transformers import PretrainedConfig

    mod = _load_config_module("step3p5", "step3p5.py")
    Step3p5Config = mod.Step3p5Config

    # Longer than num_hidden_layers — must be cropped
    c1 = Step3p5Config(
        num_hidden_layers=4,
        layer_types=["full", "full", "sparse", "full", "extra1", "extra2"],
    )
    assert isinstance(c1, PretrainedConfig)
    assert len(c1.layer_types) == 4, f"Expected 4, got {len(c1.layer_types)}"

    # Different num_hidden_layers to prevent hardcoded length
    c2 = Step3p5Config(num_hidden_layers=2, layer_types=["a", "b", "c", "d"])
    assert len(c2.layer_types) == 2, f"Expected 2, got {len(c2.layer_types)}"

    # Exact length — should be preserved unchanged
    c3 = Step3p5Config(num_hidden_layers=3, layer_types=["x", "y", "z"])
    assert len(c3.layer_types) == 3, f"Expected 3, got {len(c3.layer_types)}"


# [pr_diff] fail_to_pass
def test_config_classes_instantiate():
    """ColModernVBert, FlexOlmo, Isaac, Qwen3Next configs instantiate as valid PretrainedConfig."""
    from transformers import PretrainedConfig

    configs = [
        ("colmodernvbert.py", "ColModernVBertConfig", {}),
        ("flex_olmo.py", "FlexOlmoConfig", {}),
        ("isaac.py", "IsaacConfig", {}),
        ("qwen3_next.py", "Qwen3NextConfig", {}),
    ]

    for filename, cls_name, kwargs in configs:
        mod = _load_config_module(cls_name, filename)
        cls = getattr(mod, cls_name)
        config = cls(**kwargs)

        assert isinstance(config, PretrainedConfig), f"{cls_name} is not a PretrainedConfig"
        assert isinstance(config.to_dict(), dict), f"{cls_name}.to_dict() failed"
        assert getattr(config, "model_type", None), f"{cls_name}.model_type not set"


# [pr_diff] fail_to_pass
def test_deepseek_vlv2_nested_configs():
    """DeepseekVLV2Config must pop nested config dicts from kwargs, not just get them."""
    from transformers import PretrainedConfig

    mod = _load_config_module("deepseek_vl2", "deepseek_vl2.py")

    # Instantiate with nested config dicts — triggers the bug on base commit
    config = mod.DeepseekVLV2Config(
        vision_config={"image_size": 384},
        projector_config={},
        language_config={"vocab_size": 32000, "hidden_size": 4096},
    )
    assert isinstance(config, PretrainedConfig)

    # Nested configs must be objects, not plain dicts
    assert not isinstance(config.vision_config, dict), "vision_config still a dict"
    assert hasattr(config, "text_config"), "text_config not set"
    assert not isinstance(config.text_config, dict), "text_config is a dict"
    assert isinstance(config.text_config, PretrainedConfig), "text_config not a PretrainedConfig"

    # Must serialize without crashing
    assert isinstance(config.to_dict(), dict)

    # Verify with different values to resist hardcoding
    config2 = mod.DeepseekVLV2Config(
        vision_config={"image_size": 512},
        projector_config={},
        language_config={"vocab_size": 64000, "hidden_size": 2048},
    )
    if hasattr(config2.vision_config, "image_size"):
        assert config2.vision_config.image_size == 512


# [pr_diff] fail_to_pass
def test_autoconfig_registration():
    """config.py must register non-speculative custom configs via AutoConfig.register.

    AST check justified: HFConfigParser.parse() requires HF Hub network access,
    so behavioral invocation is not feasible in this environment.
    """
    import ast

    source = Path(f"{REPO}/vllm/transformers_utils/config.py").read_text()
    tree = ast.parse(source)

    # AutoConfig.register() call must exist
    has_register = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "register"
                and isinstance(func.value, ast.Name)
                and func.value.id == "AutoConfig"
            ):
                has_register = True
                break
    assert has_register, "AutoConfig.register() call not found in config.py"

    # A collection distinguishing speculative decoding configs must exist
    has_spec_set = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Set, ast.List, ast.Tuple)):
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and elt.value in ("eagle", "speculators"):
                    has_spec_set = True
                    break
        if has_spec_set:
            break

    if not has_spec_set:
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and "specul" in target.id.lower():
                        has_spec_set = True
                        break
            if has_spec_set:
                break

    assert has_spec_set, "No speculative decoding config set found"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_modules_importable():
    """All config modules must import without errors."""
    modules = [
        ("colmodernvbert", "colmodernvbert.py"),
        ("deepseek_vl2", "deepseek_vl2.py"),
        ("flex_olmo", "flex_olmo.py"),
        ("isaac", "isaac.py"),
        ("qwen3_next", "qwen3_next.py"),
        ("step3p5", "step3p5.py"),
    ]
    for name, filename in modules:
        _load_config_module(name, filename)


# [static] pass_to_pass
def test_not_stub():
    """Modified files must have meaningful content (not stubs)."""
    import os

    files = [
        f"{REPO}/vllm/transformers_utils/config.py",
        f"{REPO}/vllm/transformers_utils/configs/colmodernvbert.py",
        f"{REPO}/vllm/transformers_utils/configs/deepseek_vl2.py",
        f"{REPO}/vllm/transformers_utils/configs/flex_olmo.py",
        f"{REPO}/vllm/transformers_utils/configs/isaac.py",
        f"{REPO}/vllm/transformers_utils/configs/qwen3_next.py",
        f"{REPO}/vllm/transformers_utils/configs/step3p5.py",
    ]
    for f in files:
        p = Path(f)
        assert p.exists(), f"{f} does not exist"
        lines = len(p.read_text().splitlines())
        assert lines >= 20, f"{f} has only {lines} lines (stub?)"
        size = os.path.getsize(f)
        assert size >= 500, f"{f} is only {size} bytes (stub?)"

    config_lines = len(
        Path(f"{REPO}/vllm/transformers_utils/config.py").read_text().splitlines()
    )
    assert config_lines >= 100, f"config.py has only {config_lines} lines"
