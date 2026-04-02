"""
Task: slime-cuda-ipc-cache-leak
Repo: THUDM/slime @ 08b201bd576e02fba08dae22e5c9324643e88884
PR:   1731

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path

# AST-only because: update_weights requires torch, ray, torch.distributed, CUDA GPU,
# and a full Megatron/SLIME distributed runtime — cannot be imported or called in test.
REPO = "/workspace/slime"
TARGET = f"{REPO}/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"


def _parse_target():
    """Parse the target file and return the AST tree."""
    src = Path(TARGET).read_text()
    return ast.parse(src), src


def _find_function(tree, name):
    """Find a function/method by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _released_names(node):
    """Return set of variable names released by a del or =None statement."""
    names = set()
    if isinstance(node, ast.Delete):
        for t in node.targets:
            if isinstance(t, ast.Name):
                names.add(t.id)
            elif isinstance(t, ast.Tuple):
                for elt in t.elts:
                    if isinstance(elt, ast.Name):
                        names.add(elt.id)
    elif isinstance(node, ast.Assign):
        if isinstance(node.value, ast.Constant) and node.value.value is None:
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
                elif isinstance(t, ast.Tuple):
                    for elt in t.elts:
                        if isinstance(elt, ast.Name):
                            names.add(elt.id)
    return names


def _is_ipc_collect_call(node):
    """Check if an AST node is a call to torch.cuda.ipc_collect()."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    # torch.cuda.ipc_collect()
    if isinstance(func, ast.Attribute) and func.attr == "ipc_collect":
        if isinstance(func.value, ast.Attribute) and func.value.attr == "cuda":
            if isinstance(func.value.value, ast.Name) and func.value.value.id == "torch":
                return True
        # cuda.ipc_collect() if cuda was imported directly
        if isinstance(func.value, ast.Name) and func.value.id == "cuda":
            return True
    return False


def _is_barrier_call(node):
    """Check if an AST node is a call to dist.barrier()."""
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Attribute) and node.func.attr == "barrier":
        return True
    return False


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    tree, _ = _parse_target()
    assert tree is not None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hf_named_tensors_released_in_loop():
    """Both long_lived_tensors and hf_named_tensors must be released (del or =None)
    inside the weight chunk for-loop in update_weights."""
    tree, _ = _parse_target()
    func = _find_function(tree, "update_weights")
    assert func is not None, "update_weights function not found"

    released_long = False
    released_hf = False

    for node in ast.walk(func):
        if isinstance(node, ast.For):
            for child in ast.walk(node):
                released = _released_names(child)
                if "long_lived_tensors" in released:
                    released_long = True
                if "hf_named_tensors" in released:
                    released_hf = True

    assert released_long, "long_lived_tensors not released in loop (need del or = None)"
    assert released_hf, "hf_named_tensors not released in loop (need del or = None)"


# [pr_diff] fail_to_pass
def test_ipc_collect_in_loop():
    """torch.cuda.ipc_collect() must be called inside the weight chunk for-loop
    to release IPC cache entries after each chunk."""
    tree, _ = _parse_target()
    func = _find_function(tree, "update_weights")
    assert func is not None, "update_weights function not found"

    found_in_loop = False
    for node in ast.walk(func):
        if isinstance(node, ast.For):
            for child in ast.walk(node):
                if isinstance(child, ast.Expr) and _is_ipc_collect_call(child.value):
                    found_in_loop = True
                elif _is_ipc_collect_call(child):
                    found_in_loop = True

    assert found_in_loop, "torch.cuda.ipc_collect() not found inside loop in update_weights"


# [pr_diff] fail_to_pass
def test_ipc_collect_after_barrier():
    """torch.cuda.ipc_collect() must be called after dist.barrier() to clean up
    the last chunk's IPC entries for non-source ranks."""
    tree, _ = _parse_target()
    func = _find_function(tree, "update_weights")
    assert func is not None, "update_weights function not found"

    barrier_lines = []
    collect_lines = []

    for child in ast.walk(func):
        if isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
            if _is_barrier_call(child.value):
                barrier_lines.append(child.lineno)
            if _is_ipc_collect_call(child.value):
                collect_lines.append(child.lineno)

    found = any(cl > bl for bl in barrier_lines for cl in collect_lines)
    assert found, (
        f"No torch.cuda.ipc_collect() found after dist.barrier() in update_weights. "
        f"barrier lines: {barrier_lines}, collect lines: {collect_lines}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """update_weights must have a substantial body (not a stub)."""
    tree, _ = _parse_target()
    func = _find_function(tree, "update_weights")
    assert func is not None, "update_weights function not found"

    body_count = sum(
        1 for s in func.body
        if not (
            isinstance(s, ast.Pass)
            or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
        )
    )
    assert body_count > 5, f"update_weights has only {body_count} statements (need >5)"


# [static] pass_to_pass
def test_send_hf_params_exists():
    """_send_hf_params method must still exist (not deleted or renamed)."""
    tree, _ = _parse_target()
    func = _find_function(tree, "_send_hf_params")
    assert func is not None, "_send_hf_params method not found"


# [repo_tests] pass_to_pass
def test_send_to_colocated_engine_structure():
    """_send_to_colocated_engine must retain its tuple return signature."""
    tree, _ = _parse_target()
    func = _find_function(tree, "_send_to_colocated_engine")
    assert func is not None, "_send_to_colocated_engine not found"

    has_tuple_return = any(
        isinstance(child, ast.Return) and isinstance(child.value, ast.Tuple)
        for child in ast.walk(func)
    )
    assert has_tuple_return, "_send_to_colocated_engine missing tuple return"


# [static] pass_to_pass
def test_ray_and_dist_integration():
    """Core distributed integration (ray.get, dist.barrier) must be intact."""
    _, src = _parse_target()
    assert "ray.get" in src, "ray.get call missing from source"
    assert "dist.barrier" in src, "dist.barrier call missing from source"
