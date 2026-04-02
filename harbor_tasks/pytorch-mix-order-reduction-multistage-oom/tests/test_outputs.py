"""
Task: pytorch-mix-order-reduction-multistage-oom
Repo: pytorch/pytorch @ 5d919bfe0f2ba7c7aabdb75ef6a20512f163e662
PR:   176495

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import textwrap
import types
from pathlib import Path

REPO = "/workspace/pytorch"

CONFIG_PY = f"{REPO}/torch/_inductor/config.py"
CODEGEN_TRITON = f"{REPO}/torch/_inductor/codegen/triton.py"
HEURISTICS_PY = f"{REPO}/torch/_inductor/runtime/triton_heuristics.py"

ATTR = "mix_order_reduction_allow_multi_stages"
ENV_VAR = "TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES"


def _find_config_attr_value(env_overrides=None):
    """Find and eval the ATTR assignment inside the triton class.

    Returns the evaluated bool, or None if the attribute doesn't exist.
    AST-only because: importing torch._inductor.config requires full torch installation.
    """
    source = Path(CONFIG_PY).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == "triton"):
            continue
        for stmt in ast.walk(node):
            # Handle both annotated (x: bool = ...) and plain (x = ...) assignments
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                target_name, value_node = stmt.target.id, stmt.value
            elif isinstance(stmt, ast.Assign) and stmt.targets and isinstance(stmt.targets[0], ast.Name):
                target_name, value_node = stmt.targets[0].id, stmt.value
            else:
                continue
            if target_name != ATTR or value_node is None:
                continue
            expr_src = ast.get_source_segment(source, value_node)
            if not expr_src:
                continue
            env = os.environ.copy()
            env.pop(ENV_VAR, None)
            if env_overrides:
                env.update(env_overrides)
            fake_os = types.ModuleType("os")
            fake_os.environ = env
            ns = {"os": fake_os, "__builtins__": __builtins__}
            return eval(expr_src, ns)
    return None


def _exec_heuristics_branch(allow_multi_stages, rnumel_hint, num_iters=8):
    """Find the if-block in persistent_reduction whose CONDITION tests ATTR and execute it.

    Returns MAX_NUM_STAGES, or None if the branch is not found.
    AST-only because: importing torch._inductor.runtime.triton_heuristics requires triton GPU toolkit.

    Uses child.test to identify the right if-block (not body content), so an outer if that happens
    to contain both keywords in its body is not confused with the target if.
    """
    source = Path(HEURISTICS_PY).read_text()
    tree = ast.parse(source)
    for func_node in ast.walk(tree):
        if not (isinstance(func_node, ast.FunctionDef) and func_node.name == "persistent_reduction"):
            continue
        for child in ast.walk(func_node):
            if not isinstance(child, ast.If):
                continue
            # Match on the CONDITION of the if, not its body, to avoid outer if-blocks
            test_src = ast.get_source_segment(source, child.test)
            if not (test_src and ATTR in test_src):
                continue
            # Use full source lines (not get_source_segment which slices the first line
            # at col_offset, leaving body lines misindented relative to it), then dedent.
            block_lines = source.splitlines()[child.lineno - 1 : child.end_lineno]
            if_src = textwrap.dedent("\n".join(block_lines))
            ns = {
                "inductor_meta": {ATTR: allow_multi_stages},
                "rnumel_hint": rnumel_hint,
                "num_iters": num_iters,
                "__builtins__": __builtins__,
            }
            exec(if_src, ns)
            return ns.get("MAX_NUM_STAGES")
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [CONFIG_PY, CODEGEN_TRITON, HEURISTICS_PY]:
        source = Path(path).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_config_default_false():
    """New config attribute mix_order_reduction_allow_multi_stages defaults to False."""
    val = _find_config_attr_value()
    assert val is not None, f"Attribute {ATTR!r} not found in triton class in config.py"
    assert val is False, f"Config should default to False (env var unset), got {val!r}"


# [pr_diff] fail_to_pass
def test_config_env_var_enables():
    """Setting TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES=1 enables multi-stages."""
    val_on = _find_config_attr_value({ENV_VAR: "1"})
    assert val_on is True, f"Config should be True when env var='1', got {val_on!r}"

    val_off = _find_config_attr_value({ENV_VAR: "0"})
    assert val_off is False, f"Config should be False when env var='0', got {val_off!r}"

    val_unset = _find_config_attr_value()
    assert val_unset is False, f"Config should default to False when env var unset, got {val_unset!r}"


# [pr_diff] fail_to_pass
def test_heuristics_single_stage_when_disabled():
    """persistent_reduction sets MAX_NUM_STAGES=1 when multi-stages disabled, regardless of rnumel."""
    for rnumel_hint in [512, 4096, 8192, 10000, 65536]:
        max_stages = _exec_heuristics_branch(False, rnumel_hint)
        assert max_stages is not None, f"MAX_NUM_STAGES branch not found in persistent_reduction"
        assert max_stages == 1, (
            f"MAX_NUM_STAGES should be 1 when disabled (rnumel={rnumel_hint}), got {max_stages}"
        )


# [pr_diff] fail_to_pass
def test_heuristics_single_stage_small_rnumel():
    """persistent_reduction sets MAX_NUM_STAGES=1 even with small rnumel when disabled."""
    for rnumel_hint in [128, 512, 1024]:
        max_stages = _exec_heuristics_branch(False, rnumel_hint)
        assert max_stages is not None, "MAX_NUM_STAGES branch not found in persistent_reduction"
        assert max_stages == 1, (
            f"MAX_NUM_STAGES should be 1 when disabled (small rnumel={rnumel_hint}), got {max_stages}"
        )


# [pr_diff] fail_to_pass
def test_heuristics_multi_stage_when_enabled():
    """persistent_reduction allows up to 3 stages for small rnumel (<=8192) when enabled."""
    for rnumel_hint in [1024, 4096, 8192]:
        max_stages = _exec_heuristics_branch(True, rnumel_hint, num_iters=16)
        assert max_stages is not None, "MAX_NUM_STAGES branch not found"
        assert max_stages == 3, (
            f"MAX_NUM_STAGES should be 3 for rnumel={rnumel_hint} when enabled, got {max_stages}"
        )


# [pr_diff] fail_to_pass
def test_heuristics_large_rnumel_caps_at_two():
    """When enabled with large rnumel (>8192), MAX_NUM_STAGES caps at 2."""
    for rnumel_hint in [8193, 16384, 65536]:
        max_stages = _exec_heuristics_branch(True, rnumel_hint, num_iters=16)
        assert max_stages is not None, "MAX_NUM_STAGES branch not found"
        assert max_stages == 2, (
            f"MAX_NUM_STAGES should be 2 for rnumel={rnumel_hint} when enabled, got {max_stages}"
        )


# [pr_diff] fail_to_pass
def test_codegen_propagates_config_key():
    """inductor_meta_common includes mix_order_reduction_allow_multi_stages as a dict key."""
    # AST-only because: importing torch._inductor.codegen.triton requires full torch + triton
    source = Path(CODEGEN_TRITON).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "inductor_meta_common":
            for child in ast.walk(node):
                if isinstance(child, ast.Constant) and child.value == ATTR:
                    return  # found
            raise AssertionError(
                f"inductor_meta_common does not include {ATTR!r} as a string key"
            )
    raise AssertionError("inductor_meta_common function not found in codegen/triton.py")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_configs_intact():
    """Existing mix_order_reduction config attributes are still present in the triton class."""
    # AST-only because: importing torch._inductor.config requires full torch installation
    source = Path(CONFIG_PY).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == "triton"):
            continue
        attr_names = set()
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                attr_names.add(stmt.target.id)
            elif isinstance(stmt, ast.Assign):
                for t in stmt.targets:
                    if isinstance(t, ast.Name):
                        attr_names.add(t.id)
        for attr in [
            "mix_order_reduction",
            "mix_order_reduction_autotune_split_size",
            "mix_order_reduction_non_strict_mode",
        ]:
            assert attr in attr_names, f"Existing config attribute {attr!r} is missing from triton class"
        return
    raise AssertionError("triton class not found in config.py")


# [static] pass_to_pass
def test_config_not_hardcoded_false():
    """Config reads env var — env var change actually toggles the value (not a hardcoded stub)."""
    val_off = _find_config_attr_value()
    val_on = _find_config_attr_value({ENV_VAR: "1"})
    assert val_off != val_on, (
        f"Config should toggle with {ENV_VAR}, but got off={val_off!r} on={val_on!r}"
    )
