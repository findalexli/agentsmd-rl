"""
Task: sglang-qwen35-pp-cache-moe-fix
Repo: sgl-project/sglang @ c06ca1526cb6008a8dacb4fdb06567e648134664
PR:   21448

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import textwrap
from pathlib import Path

REPO = "/workspace/sglang"


def _extract_get_layer_id():
    """Extract get_layer_id from common.py via AST+exec to avoid torch import."""
    # AST-only because: common.py imports torch at top level
    src = Path(f"{REPO}/python/sglang/srt/layers/utils/common.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_layer_id":
            func_src = ast.get_source_segment(src, node)
            assert func_src is not None, "Could not extract get_layer_id source"
            ns = {"__builtins__": __builtins__, "re": re}
            exec(func_src, ns)
            return ns["get_layer_id"]
    raise AssertionError("get_layer_id not found in common.py")


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    files = [
        "python/sglang/srt/mem_cache/memory_pool.py",
        "python/sglang/srt/model_executor/model_runner_kv_cache_mixin.py",
        "python/sglang/srt/models/qwen3_5.py",
        "python/sglang/srt/models/qwen3_vl.py",
        "python/sglang/srt/disaggregation/decode.py",
    ]
    for f in files:
        src = Path(f"{REPO}/{f}").read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — behavioral tests for get_layer_id
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_get_layer_id():
    """get_layer_id must exist and correctly extract layer IDs from weight names."""
    get_layer_id = _extract_get_layer_id()

    # Standard layer weights — diverse layer numbers
    assert get_layer_id("model.layers.0.mlp.gate_proj.weight") == 0
    assert get_layer_id("model.layers.21.mlp.experts.w2_weight") == 21
    assert get_layer_id("model.layers.99.qkv_proj.weight") == 99
    assert get_layer_id("model.layers.127.self_attn.o_proj.weight") == 127
    assert get_layer_id("model.layers.5.feed_forward.weight") == 5

    # Non-layer weights must return None
    assert get_layer_id("model.embed_tokens.weight") is None
    assert get_layer_id("model.norm.weight") is None
    assert get_layer_id("lm_head.weight") is None
    assert get_layer_id("visual.patch_embed.weight") is None


# [pr_diff] pass_to_pass
def test_pp_weight_filtering():
    """PP filtering using get_layer_id correctly skips out-of-range layers."""
    get_layer_id = _extract_get_layer_id()

    # Build realistic weight names for a 40-layer model with MoE experts
    weight_names = []
    for layer in range(40):
        weight_names.append(f"model.layers.{layer}.mlp.gate_proj.weight")
        weight_names.append(f"model.layers.{layer}.mlp.experts.w2_weight")
        weight_names.append(f"model.layers.{layer}.qkv_proj.weight")
    weight_names.extend(["model.embed_tokens.weight", "model.norm.weight", "lm_head.weight"])

    # Test multiple PP ranges
    for start, end in [(0, 10), (10, 30), (20, 40), (0, 40)]:
        loaded, skipped = [], []
        for name in weight_names:
            layer_id = get_layer_id(name)
            if layer_id is not None and (layer_id < start or layer_id >= end):
                skipped.append(name)
                continue
            loaded.append(name)

        expected_layer_weights = (end - start) * 3
        non_layer = 3  # embed, norm, lm_head
        assert len(loaded) == expected_layer_weights + non_layer, (
            f"Range [{start},{end}): expected {expected_layer_weights + non_layer} loaded, got {len(loaded)}"
        )

    # The original crash scenario: layer 21 expert weight must be loaded in [20,40)
    loaded_2040 = []
    for name in weight_names:
        lid = get_layer_id(name)
        if lid is not None and (lid < 20 or lid >= 40):
            continue
        loaded_2040.append(name)
    assert "model.layers.21.mlp.experts.w2_weight" in loaded_2040
    assert "model.layers.0.mlp.experts.w2_weight" not in loaded_2040


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural tests (AST required: GPU-dependent classes)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_decode_pp_parameters():
    """HybridMambaDecodeReqToTokenPool.__init__ must accept mamba_layer_ids and start_layer."""
    # AST-only because: decode.py classes require GPU/torch runtime to instantiate
    src = Path(f"{REPO}/python/sglang/srt/disaggregation/decode.py").read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "HybridMambaDecodeReqToTokenPool":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    param_names = [arg.arg for arg in item.args.args]
                    assert "mamba_layer_ids" in param_names, (
                        f"__init__ must accept mamba_layer_ids, got: {param_names}"
                    )
                    assert "start_layer" in param_names, (
                        f"__init__ must accept start_layer, got: {param_names}"
                    )
                    # Verify start_layer is not hardcoded to 0
                    init_src = ast.get_source_segment(src, item) or ""
                    assert "# TODO: Support PP" not in init_src, (
                        "Still has TODO: Support PP comment"
                    )
                    found = True
                    break
            break

    assert found, "HybridMambaDecodeReqToTokenPool.__init__ not found"


# [pr_diff] fail_to_pass
def test_qwen3_vl_pp_properties():
    """Qwen3_5VLForConditionalGeneration must have start_layer/end_layer properties that delegate."""
    src = Path(f"{REPO}/python/sglang/srt/models/qwen3_vl.py").read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "Qwen3" in node.name and "Conditional" in node.name:
            props = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in ("start_layer", "end_layer"):
                    is_prop = any(
                        (isinstance(d, ast.Name) and d.id == "property")
                        or (isinstance(d, ast.Attribute) and d.attr == "property")
                        for d in item.decorator_list
                    )
                    assert is_prop, f"{item.name} must be a @property"
                    # Extract function WITHOUT decorator (lineno points to def, not @property)
                    lines = src.splitlines(keepends=True)
                    func_src = textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
                    props[item.name] = func_src

            assert "start_layer" in props, "Must have start_layer property"
            assert "end_layer" in props, "Must have end_layer property"

            # Execute extracted functions against mock objects
            class MockModel:
                start_layer = 15
                end_layer = 30

            class MockModelNoEnd:
                class config:
                    num_hidden_layers = 48

            class ObjWithModel:
                model = MockModel()

            class ObjWithFallback:
                model = MockModelNoEnd()

            class ObjEmpty:
                pass

            ns = {"__builtins__": __builtins__}
            exec(props["start_layer"], ns)
            exec(props["end_layer"], ns)

            # Test delegation to inner model
            assert ns["start_layer"](ObjWithModel()) == 15
            assert ns["end_layer"](ObjWithModel()) == 30

            # Test fallback when end_layer is missing but config exists
            assert ns["end_layer"](ObjWithFallback()) == 48

            # Test fallback when model is missing
            assert ns["start_layer"](ObjEmpty()) == 0

            found = True
            break

    assert found, "Qwen3VLForConditionalGeneration not found"


# [pr_diff] fail_to_pass
def test_qwen3_5_load_weights_pp_filtering():
    """load_weights/load_fused_expert_weights in qwen3_5.py must use get_layer_id for PP skip."""
    # AST-only because: model classes require GPU/torch to instantiate
    src = Path(f"{REPO}/python/sglang/srt/models/qwen3_5.py").read_text()
    tree = ast.parse(src)

    methods_with_filtering = 0
    total_load_methods = 0
    target_classes = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "Qwen3_5" in node.name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in (
                    "load_weights", "load_fused_expert_weights"
                ):
                    total_load_methods += 1
                    has_get_layer_id = False
                    has_continue = False
                    for child in ast.walk(item):
                        if isinstance(child, ast.Call):
                            func = child.func
                            if (isinstance(func, ast.Name) and func.id == "get_layer_id") or (
                                isinstance(func, ast.Attribute) and func.attr == "get_layer_id"
                            ):
                                has_get_layer_id = True
                        if isinstance(child, ast.Continue):
                            has_continue = True
                    if has_get_layer_id and has_continue:
                        methods_with_filtering += 1
                        target_classes.add(node.name)

    assert total_load_methods >= 4, f"Expected >=4 load methods, found {total_load_methods}"
    assert methods_with_filtering >= 4, (
        f"Expected >=4 methods with PP filtering, only {methods_with_filtering} have it"
    )
    assert len(target_classes) >= 2, f"Expected >=2 classes with filtering, got {target_classes}"


# [pr_diff] fail_to_pass
def test_memory_pool_pp_support():
    """memory_pool.py must not hardcode start_layer=0 and MambaPool must accept mamba_layer_ids."""
    # AST-only because: pool classes require torch/CUDA to instantiate
    src = Path(f"{REPO}/python/sglang/srt/mem_cache/memory_pool.py").read_text()
    tree = ast.parse(src)

    # Check 1: no hardcoded self.start_layer = 0 in relevant classes
    hardcoded_count = 0
    parametric_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in (
            "HybridReqToTokenPool", "HybridLinearKVPool",
        ):
            for item in ast.walk(node):
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and target.attr == "start_layer"
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                        ):
                            if isinstance(item.value, ast.Constant) and item.value.value == 0:
                                hardcoded_count += 1
                            else:
                                parametric_count += 1

    assert hardcoded_count == 0, f"Found {hardcoded_count} hardcoded self.start_layer = 0"
    assert parametric_count >= 2, f"Expected >=2 parametric start_layer, got {parametric_count}"
    assert "TODO: Support PP" not in src, "Still has TODO: Support PP comments"

    # Check 2: MambaPool.__init__ accepts a layer IDs parameter
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "MambaPool":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    param_names = [arg.arg for arg in item.args.args] + [arg.arg for arg in item.args.kwonlyargs]
                    has_layer_param = any("layer" in p and "id" in p for p in param_names)
                    assert has_layer_param, f"MambaPool.__init__ must accept layer IDs param, got: {param_names}"
                    init_src = ast.get_source_segment(src, item) or ""
                    assert "len(cache_params.layers)" not in init_src, (
                        "num_mamba_layers must NOT use len(cache_params.layers)"
                    )
                    break
            break


# [agent_config] pass_to_pass — .claude/skills/write-sglang-test/SKILL.md:12 @ c06ca1526cb6008a8dacb4fdb06567e648134664
def test_unit_test_uses_custom_test_case():
    """test_mamba_unittest.py must use CustomTestCase, not raw unittest.TestCase."""
    src = Path(f"{REPO}/test/registered/unit/mem_cache/test_mamba_unittest.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                is_raw_testcase = (
                    isinstance(base, ast.Attribute)
                    and isinstance(base.value, ast.Name)
                    and base.value.id == "unittest"
                    and base.attr == "TestCase"
                )
                assert not is_raw_testcase, (
                    f"Class {node.name} must use CustomTestCase, not unittest.TestCase directly"
                )
