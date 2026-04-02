"""
Task: vllm-rocm-aiter-state-leak
Repo: vllm-project/vllm @ 0aac2048bf3a7e60eaddf1ebcb4165ed777eb8ff
PR:   20255

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: All three target files require ROCm GPU + torch to import/execute,
so tests use AST analysis to verify structural correctness.
# AST-only because: all three files import torch/ROCm/vllm GPU backends that
# cannot be imported without GPU hardware and ROCm drivers.
"""

import ast
from pathlib import Path

REPO = "/workspace/vllm"


def _parse(relpath: str) -> ast.Module:
    return ast.parse(Path(f"{REPO}/{relpath}").read_text())


def _names_in_expr(node: ast.AST) -> set[str]:
    """Collect all Name.id values in an expression subtree."""
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _find_func(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _call_attrs_in(node: ast.AST) -> set[str]:
    """Collect all method names from Call nodes (func.attr)."""
    attrs = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            attrs.add(child.func.attr)
    return attrs


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All three modified files must parse without errors."""
    for f in [
        "tests/kernels/moe/test_shared_fused_moe_routed_transform.py",
        "tests/kernels/moe/test_routing_simulator.py",
        "vllm/distributed/parallel_state.py",
    ]:
        ast.parse(Path(f"{REPO}/{f}").read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rocm_env_setup_not_gated_on_use_rocm_aiter():
    """The if-block that sets AITER env vars must NOT be gated on use_rocm_aiter.

    Bug: env vars only set when use_rocm_aiter=True, so False case has stale state.
    Fix: any restructuring where ROCm env setup runs regardless of use_rocm_aiter value.
    """
    tree = _parse("tests/kernels/moe/test_shared_fused_moe_routed_transform.py")
    func = _find_func(tree, "test_routed_input_transform_inside_vs_outside")
    assert func is not None, "test function not found"

    # Find If nodes whose body contains a setenv call
    for child in ast.walk(func):
        if not isinstance(child, ast.If):
            continue
        has_setenv = any(
            isinstance(sub, ast.Call)
            and isinstance(sub.func, ast.Attribute)
            and sub.func.attr == "setenv"
            for sub in ast.walk(child)
        )
        if has_setenv:
            cond_names = _names_in_expr(child.test)
            assert "use_rocm_aiter" not in cond_names, (
                "env-var setup is still gated on use_rocm_aiter"
            )
            return  # found the if-block, condition is clean

    # If no if-block with setenv, check if setenv is at function top level (also valid)
    for child in ast.iter_child_nodes(func):
        if (
            isinstance(child, ast.Expr)
            and isinstance(child.value, ast.Call)
            and isinstance(child.value.func, ast.Attribute)
            and child.value.func.attr == "setenv"
        ):
            return  # setenv at top level, no gate at all

    raise AssertionError("No setenv call found in test function")


# [pr_diff] fail_to_pass
def test_cleanup_calls_refresh_env_variables():
    """cleanup_dist_env_and_memory must call refresh_env_variables().

    Bug: cleanup doesn't reset AITER cached state, causing cross-test leaks.
    Verify an actual Call node exists, not just a string/comment.
    """
    tree = _parse("vllm/distributed/parallel_state.py")
    func = _find_func(tree, "cleanup_dist_env_and_memory")
    assert func is not None, "cleanup_dist_env_and_memory not found"

    call_attrs = _call_attrs_in(func)
    assert "refresh_env_variables" in call_attrs, (
        "cleanup_dist_env_and_memory does not call refresh_env_variables()"
    )


# [pr_diff] fail_to_pass
def test_routing_simulator_no_direct_dict_mutation():
    """test_routing_strategy_integration must not directly mutate environment_variables dict.

    Bug: direct dict assignment isn't reverted by monkeypatch teardown.
    Accept any fix that removes the direct Subscript assignment.
    """
    tree = _parse("tests/kernels/moe/test_routing_simulator.py")
    func = _find_func(tree, "test_routing_strategy_integration")
    assert func is not None, "test_routing_strategy_integration not found"

    for child in ast.walk(func):
        if isinstance(child, ast.Assign):
            for target in child.targets:
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Attribute)
                    and target.value.attr == "environment_variables"
                ):
                    raise AssertionError(
                        "Direct dict mutation of environment_variables still present"
                    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_cleanup_retains_existing_calls():
    """cleanup_dist_env_and_memory must still call disable_envs_cache() and gc.unfreeze()."""
    tree = _parse("vllm/distributed/parallel_state.py")
    func = _find_func(tree, "cleanup_dist_env_and_memory")
    assert func is not None

    call_attrs = _call_attrs_in(func)
    assert "disable_envs_cache" in call_attrs, "Missing call to disable_envs_cache()"
    assert "unfreeze" in call_attrs, "Missing call to gc.unfreeze()"


# [pr_diff] pass_to_pass
def test_aiter_env_var_names_present():
    """Test file still references both VLLM_ROCM_USE_AITER and VLLM_ROCM_USE_AITER_MOE."""
    tree = _parse("tests/kernels/moe/test_shared_fused_moe_routed_transform.py")

    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in ("VLLM_ROCM_USE_AITER", "VLLM_ROCM_USE_AITER_MOE"):
                found.add(node.value)

    assert "VLLM_ROCM_USE_AITER" in found, "Missing VLLM_ROCM_USE_AITER string"
    assert "VLLM_ROCM_USE_AITER_MOE" in found, "Missing VLLM_ROCM_USE_AITER_MOE string"


# ---------------------------------------------------------------------------
# Anti-stub (static) — verify meaningful implementation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cleanup_not_stub():
    """cleanup_dist_env_and_memory has meaningful code (not emptied out)."""
    tree = _parse("vllm/distributed/parallel_state.py")
    func = _find_func(tree, "cleanup_dist_env_and_memory")
    assert func is not None

    stmt_types = (ast.Assign, ast.Call, ast.If, ast.Import, ast.ImportFrom, ast.Return, ast.Expr)
    stmts = sum(1 for child in ast.walk(func) if isinstance(child, stmt_types))
    # Base version has ~10 statements; fix adds ~3-5 more
    assert stmts >= 8, f"cleanup body too small ({stmts} statements), likely a stub"
