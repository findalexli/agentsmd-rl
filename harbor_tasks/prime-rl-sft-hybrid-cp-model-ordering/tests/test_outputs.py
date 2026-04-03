"""
Task: prime-rl-sft-hybrid-cp-model-ordering
Repo: PrimeIntellect-ai/prime-rl @ b7afd84024531074830143d88bf0f60f506e1588
PR:   2097

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path

FILE = Path("/workspace/src/prime_rl/trainer/sft/train.py")


def _parse_train_func():
    """Parse train.py and return (source, AST node for train())."""
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "train":
            return source, node
    raise AssertionError("train() function not found in train.py")


def _find_calls(node, name):
    """Find all Call nodes in an AST subtree matching a function name."""
    results = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func_name = getattr(child.func, "id", None) or getattr(child.func, "attr", None)
            if func_name == name:
                results.append(child)
    return results


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """train.py must be valid Python."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    source = FILE.read_text()
    compile(source, str(FILE), "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_model_assigned_before_hybrid_cp():
    """model must be assigned (via setup_model) before setup_hybrid_cp(model, ...) is called.

    The base-commit bug: setup_hybrid_cp(model, ...) runs on ~line 108 but
    model = setup_model(...) doesn't happen until ~line 125.
    The fix moves setup_hybrid_cp after the model assignment.
    """
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()

    # Find lines where 'model' is assigned (model = ... or model, ... = ...)
    model_assign_lines = []
    for node in ast.walk(train_node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "model":
                    model_assign_lines.append(node.lineno)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name) and elt.id == "model":
                            model_assign_lines.append(node.lineno)

    assert model_assign_lines, "No assignment to 'model' found in train()"

    # Find setup_hybrid_cp call
    hybrid_cp_calls = _find_calls(train_node, "setup_hybrid_cp")
    assert hybrid_cp_calls, "setup_hybrid_cp() call not found in train()"

    hybrid_line = hybrid_cp_calls[0].lineno

    # At least one model assignment must come BEFORE setup_hybrid_cp
    assert any(ml < hybrid_line for ml in model_assign_lines), (
        f"model is not assigned before setup_hybrid_cp (line {hybrid_line}). "
        f"Model assignments at lines: {model_assign_lines}"
    )


# [pr_diff] fail_to_pass
def test_hybrid_cp_after_model_init():
    """setup_hybrid_cp() must be called AFTER setup_model() in train().

    AST ordering check: the line number of setup_hybrid_cp must be greater
    than the line number of setup_model. Tests multiple orderings to ensure
    the fix isn't fragile.
    """
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()

    setup_model_calls = _find_calls(train_node, "setup_model")
    setup_hybrid_cp_calls = _find_calls(train_node, "setup_hybrid_cp")

    assert setup_model_calls, "setup_model() call not found in train()"
    assert setup_hybrid_cp_calls, "setup_hybrid_cp() call not found in train()"

    sm_line = setup_model_calls[0].lineno
    shcp_line = setup_hybrid_cp_calls[0].lineno

    assert shcp_line > sm_line, (
        f"setup_hybrid_cp (line {shcp_line}) must come after "
        f"setup_model (line {sm_line}) in train()"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_setup_hybrid_cp_retained():
    """setup_hybrid_cp call must still exist — not deleted to dodge NameError."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()
    calls = _find_calls(train_node, "setup_hybrid_cp")
    assert calls, "setup_hybrid_cp() call was removed from train()"


# [pr_diff] pass_to_pass
def test_substitute_ring_attn_present():
    """substitute_ring_attn must still be called (regression guard)."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "substitute_ring_attn":
                return
    raise AssertionError("substitute_ring_attn() call was removed")


# [pr_diff] pass_to_pass
def test_setup_model_present():
    """setup_model must still be called."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()
    calls = _find_calls(train_node, "setup_model")
    assert calls, "setup_model() call was removed from train()"


# [static] pass_to_pass
def test_train_not_stub():
    """train() must have >= 20 top-level statements (reject total rewrites)."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()
    assert len(train_node.body) >= 20, (
        f"train() has only {len(train_node.body)} statements — likely a stub"
    )


# [pr_diff] pass_to_pass
def test_setup_ckpt_managers_retained():
    """setup_ckpt_managers must still be called (reject gutted rewrites)."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "setup_ckpt_managers":
                return
    raise AssertionError("setup_ckpt_managers() call was removed")


# [pr_diff] pass_to_pass
def test_hybrid_cp_guarded_by_cp_enabled():
    """setup_hybrid_cp must be inside a cp_enabled conditional (not called unconditionally)."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    _, train_node = _parse_train_func()

    # Walk the train function to find setup_hybrid_cp calls
    # and verify each is inside an If node that tests cp_enabled
    for node in ast.walk(train_node):
        if isinstance(node, ast.If):
            # Check if this If tests cp_enabled (attribute or name)
            test_src = ast.dump(node.test)
            if "cp_enabled" in test_src:
                # Check if setup_hybrid_cp is called inside this If body
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        name = getattr(child.func, "id", None) or getattr(child.func, "attr", None)
                        if name == "setup_hybrid_cp":
                            return
    raise AssertionError(
        "setup_hybrid_cp() is not guarded by a cp_enabled check — "
        "it must only run when context parallelism is enabled"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ b7afd84024531074830143d88bf0f60f506e1588
def test_no_try_except_around_hybrid_cp():
    """setup_hybrid_cp must not be wrapped in try/except (AGENTS.md: avoid unnecessary try/except)."""
    # AST-only because: train.py requires torch/distributed/CUDA — cannot import
    source = FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    name = getattr(child.func, "id", None) or getattr(child.func, "attr", None)
                    if name == "setup_hybrid_cp":
                        raise AssertionError(
                            "setup_hybrid_cp is inside a try/except block — "
                            "AGENTS.md says avoid unnecessary try/except"
                        )
