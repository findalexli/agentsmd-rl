"""
Task: slime-glm4v-moe-bridge-layer-spec
Repo: THUDM/slime @ e4d22dc929169fcc2cdf538d1798d9a5473f4d1d
PR:   1738

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: megatron-core is not installable on CPU, so all tests use AST parsing
to inspect the source code rather than importing it directly.
"""

import ast
from pathlib import Path

FILE = Path("/workspace/slime/slime_plugins/megatron_bridge/glm4v_moe.py")


def _parse():
    src = FILE.read_text()
    return src, ast.parse(src)


def _find_method(tree, method_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            return node
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """glm4v_moe.py must parse without syntax errors."""
    src = FILE.read_text()
    ast.parse(src)  # raises SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_moe_layer_freq_is_list():
    """moe_layer_freq must evaluate to a list, not a string expression."""
    src, tree = _parse()
    provider_bridge = _find_method(tree, "provider_bridge")
    assert provider_bridge is not None, "provider_bridge method not found"

    # Find assignment to a variable containing 'moe_layer_freq'
    for child in ast.walk(provider_bridge):
        if isinstance(child, ast.Assign):
            for target in child.targets:
                if isinstance(target, ast.Name) and "moe_layer_freq" in target.id:
                    rhs_src = ast.get_source_segment(src, child.value)
                    assert rhs_src, "Could not extract moe_layer_freq RHS source"
                    ns = {"first_k_dense": 1, "num_layers": 46}
                    result = eval(rhs_src, {"__builtins__": __builtins__}, ns)
                    assert not isinstance(result, str), (
                        f"moe_layer_freq evaluates to string: {result!r}"
                    )
                    assert isinstance(result, (list, tuple)), (
                        f"moe_layer_freq is unexpected type: {type(result).__name__}"
                    )
                    return

    # Fallback: check the keyword arg directly
    for child in ast.walk(provider_bridge):
        if isinstance(child, ast.keyword) and child.arg == "moe_layer_freq":
            val = child.value
            assert not isinstance(val, (ast.JoinedStr, ast.Constant)), (
                "moe_layer_freq passed as string literal or f-string"
            )
            if isinstance(val, (ast.List, ast.Tuple, ast.ListComp)):
                return
            if isinstance(val, ast.Name):
                # Variable reference — already checked above, accept it
                return

    raise AssertionError("Could not find moe_layer_freq computation")


# [pr_diff] fail_to_pass
def test_moe_layer_freq_values_correct():
    """moe_layer_freq list has correct dense/MoE pattern for varied configs."""
    src, tree = _parse()
    provider_bridge = _find_method(tree, "provider_bridge")
    assert provider_bridge is not None

    rhs_src = None
    for child in ast.walk(provider_bridge):
        if isinstance(child, ast.Assign):
            for target in child.targets:
                if isinstance(target, ast.Name) and "moe_layer_freq" in target.id:
                    rhs_src = ast.get_source_segment(src, child.value)
                    break
            if rhs_src:
                break

    assert rhs_src, "Could not extract moe_layer_freq expression"

    # Test with multiple (first_k_dense, num_layers) configurations
    configs = [(1, 46), (2, 10), (0, 5), (3, 3)]
    for dk, nl in configs:
        ns = {
            "first_k_dense": dk,
            "num_layers": nl,
            "num_hidden_layers": nl,
            "first_k_dense_replace": dk,
        }
        result = eval(rhs_src, {"__builtins__": __builtins__}, ns)
        assert isinstance(result, (list, tuple)), f"Not a list for dk={dk}, nl={nl}"
        assert len(result) == nl, f"Length {len(result)} != {nl} for dk={dk}, nl={nl}"
        for i in range(dk):
            assert result[i] == 0, f"Layer {i} should be dense (0), got {result[i]}"
        for i in range(dk, nl):
            assert result[i] == 1, f"Layer {i} should be MoE (1), got {result[i]}"


# [pr_diff] fail_to_pass
def test_provide_uses_decoder_block_spec():
    """provide() must call get_gpt_decoder_block_spec, not the old function."""
    _, tree = _parse()
    provide = _find_method(tree, "provide")
    assert provide is not None, "provide() method not found"

    calls = set()
    for child in ast.walk(provide):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                calls.add(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                calls.add(child.func.attr)

    assert "get_gpt_layer_with_transformer_engine_spec" not in calls, (
        "Still using old get_gpt_layer_with_transformer_engine_spec"
    )
    assert "get_gpt_decoder_block_spec" in calls, (
        "get_gpt_decoder_block_spec not called in provide()"
    )


# [pr_diff] fail_to_pass
def test_provide_passes_config_to_spec():
    """get_gpt_decoder_block_spec must receive a config argument."""
    _, tree = _parse()
    provide = _find_method(tree, "provide")
    assert provide is not None

    for child in ast.walk(provide):
        if isinstance(child, ast.Call):
            name = None
            if isinstance(child.func, ast.Name):
                name = child.func.id
            elif isinstance(child.func, ast.Attribute):
                name = child.func.attr
            if name == "get_gpt_decoder_block_spec":
                kw_names = {kw.arg for kw in child.keywords}
                has_config_kw = "config" in kw_names
                has_positional = len(child.args) >= 1
                assert has_config_kw or has_positional, (
                    "get_gpt_decoder_block_spec called without config"
                )
                return

    raise AssertionError("get_gpt_decoder_block_spec call not found in provide()")


# [pr_diff] fail_to_pass
def test_imports_decoder_block_spec():
    """Must import get_gpt_decoder_block_spec, not the old function."""
    _, tree = _parse()

    imported_names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names[alias.asname or alias.name] = alias.name

    for real_name in imported_names.values():
        assert real_name != "get_gpt_layer_with_transformer_engine_spec", (
            "Still imports get_gpt_layer_with_transformer_engine_spec"
        )

    found = any(
        v == "get_gpt_decoder_block_spec" for v in imported_names.values()
    )
    assert found, "get_gpt_decoder_block_spec not imported"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_key_classes_exist():
    """Core classes must still be defined."""
    _, tree = _parse()
    classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    required = {"Glm4vMoeVLModel", "Glm4vMoeVLModelProvider", "Glm4vMoeBridge"}
    missing = required - classes
    assert not missing, f"Missing classes: {missing}"


# [repo_tests] pass_to_pass
def test_key_methods_not_stubbed():
    """Core methods must have real logic, not stubs."""
    _, tree = _parse()

    required_methods = {
        "Glm4vMoeVLModelProvider": ["provide"],
        "Glm4vMoeBridge": ["provider_bridge"],
        "Glm4vMoeVLModel": ["__init__", "forward"],
    }
    for cls_name, methods in required_methods.items():
        cls_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == cls_name:
                cls_node = node
                break
        assert cls_node is not None, f"Class {cls_name} not found"

        found = {}
        for item in ast.walk(cls_node):
            if isinstance(item, ast.FunctionDef) and item.name in methods:
                stmts = sum(
                    1 for s in ast.walk(item)
                    if isinstance(s, (ast.Assign, ast.Return, ast.If, ast.For,
                                      ast.Call, ast.AugAssign, ast.AnnAssign))
                )
                found[item.name] = stmts

        for m in methods:
            assert m in found, f"{cls_name}.{m} not found"
            assert found[m] >= 3, (
                f"{cls_name}.{m} has only {found[m]} statements (likely stub)"
            )


# [static] pass_to_pass
def test_file_not_stub():
    """File must not be stubbed out — needs substantial content."""
    lines = [
        l for l in FILE.read_text().splitlines()
        if l.strip() and not l.strip().startswith("#")
    ]
    assert len(lines) >= 150, (
        f"File too short ({len(lines)} non-empty non-comment lines), likely stubbed"
    )
