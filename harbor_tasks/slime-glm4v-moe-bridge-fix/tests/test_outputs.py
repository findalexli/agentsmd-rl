"""
Task: slime-glm4v-moe-bridge-fix
Repo: slime @ e4d22dc929169fcc2cdf538d1798d9a5473f4d1d
PR:   1738

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/slime"
TARGET = f"{REPO}/slime_plugins/megatron_bridge/glm4v_moe.py"


def _find_moe_freq_expr():
    """Extract the moe_layer_freq value expression source from provider_bridge.

    Walks the AST of the target file to find the keyword argument
    ``moe_layer_freq=...`` in the provider constructor call inside
    ``provider_bridge``.  If the value is a variable reference, resolves it
    to the assignment RHS.  Returns the source text of the expression.
    """
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "provider_bridge":
            for inner in ast.walk(node):
                if not isinstance(inner, ast.Call):
                    continue
                for kw in inner.keywords:
                    if kw.arg != "moe_layer_freq":
                        continue
                    if isinstance(kw.value, ast.Name):
                        var_name = kw.value.id
                        for stmt in ast.walk(node):
                            if isinstance(stmt, ast.Assign):
                                for t in stmt.targets:
                                    if isinstance(t, ast.Name) and t.id == var_name:
                                        return ast.get_source_segment(src, stmt.value)
                    return ast.get_source_segment(src, kw.value)
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without syntax errors."""
    r = subprocess.run(
        ["python3", "-c", f"import py_compile; py_compile.compile(r'{TARGET}', doraise=True)"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_decoder_block_spec_import():
    """get_gpt_decoder_block_spec must be imported instead of the legacy function."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.name)
    assert "get_gpt_decoder_block_spec" in imported_names, (
        "Missing import of get_gpt_decoder_block_spec from "
        "megatron.core.models.gpt.gpt_layer_specs"
    )
    assert "get_gpt_layer_with_transformer_engine_spec" not in imported_names, (
        "Legacy get_gpt_layer_with_transformer_engine_spec must be removed"
    )


# [pr_diff] fail_to_pass
def test_moe_layer_freq_is_list():
    """moe_layer_freq must be constructed as a list, not a string expression."""
    expr_src = _find_moe_freq_expr()
    assert expr_src is not None, "Could not find moe_layer_freq value in provider_bridge"
    # Evaluate with typical GLM-4V config (1 dense + 39 MoE layers)
    result = eval(expr_src, {"__builtins__": {}}, {"first_k_dense": 1, "num_layers": 40})
    assert isinstance(result, list), (
        f"moe_layer_freq should be a list, got {type(result).__name__}: {result!r}"
    )
    assert len(result) == 40, f"Expected 40 entries, got {len(result)}"
    assert result[0] == 0, f"First layer should be dense (0), got {result[0]}"
    assert all(v == 1 for v in result[1:]), "All non-dense layers should be MoE (1)"


# [pr_diff] fail_to_pass
def test_moe_layer_freq_varied_configs():
    """moe_layer_freq list must be correct for various first_k_dense / num_layers combos."""
    expr_src = _find_moe_freq_expr()
    assert expr_src is not None, "Could not find moe_layer_freq value in provider_bridge"
    configs = [
        (1, 40),   # typical: 1 dense + 39 MoE
        (2, 32),   # 2 dense + 30 MoE
        (0, 16),   # all MoE
        (5, 60),   # 5 dense + 55 MoE
    ]
    for first_k_dense, num_layers in configs:
        result = eval(
            expr_src, {"__builtins__": {}},
            {"first_k_dense": first_k_dense, "num_layers": num_layers},
        )
        expected = [0] * first_k_dense + [1] * (num_layers - first_k_dense)
        assert result == expected, (
            f"Wrong freq for (first_k_dense={first_k_dense}, num_layers={num_layers}): "
            f"got {result!r}, expected {expected!r}"
        )


# [pr_diff] fail_to_pass
def test_provide_uses_decoder_block_spec():
    """provide() must call get_gpt_decoder_block_spec with config= keyword."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "provide":
            for inner in ast.walk(node):
                if not isinstance(inner, ast.Call):
                    continue
                func = inner.func
                name = None
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name and "get_gpt" in name:
                    assert name == "get_gpt_decoder_block_spec", (
                        f"provide() calls {name} instead of get_gpt_decoder_block_spec"
                    )
                    kw_names = [kw.arg for kw in inner.keywords]
                    assert "config" in kw_names, (
                        f"get_gpt_decoder_block_spec must receive config= keyword, "
                        f"got keywords: {kw_names}"
                    )
                    return
    assert False, "No get_gpt_* spec function call found in provide() method"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """provider_bridge and provide methods must have real logic, not stubs."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    for method_name in ("provider_bridge", "provide"):
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                body_stmts = [
                    s for s in node.body
                    if not isinstance(s, (ast.Pass, ast.Expr))
                ]
                assert len(body_stmts) >= 3, (
                    f"{method_name} appears to be a stub "
                    f"(only {len(body_stmts)} non-trivial statements)"
                )
                found = True
                break
        assert found, f"Method {method_name} not found in {TARGET}"
