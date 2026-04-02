"""
Task: slime-remote-kwargs-deepgemm-precompile
Repo: THUDM/slime @ 243d0883b90e407ee56a6a51d2d8d80fe5cae47e
PR:   1765

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path

REPO = "/workspace/slime"
DIST_FILE = f"{REPO}/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py"
ROLLOUT_FILE = f"{REPO}/slime/ray/rollout.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files must parse without syntax errors."""
    # AST-only because: syntax validation is inherently an AST operation
    for fpath in [DIST_FILE, ROLLOUT_FILE]:
        src = Path(fpath).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_keyword_args_in_remote_call():
    """init_weights_update_group.remote() calls in connect_rollout_engines_from_distributed
    must use keyword arguments for all core params, not positional."""
    # AST-only because: Ray remote calls require a running Ray cluster with NCCL/GPU
    src = Path(DIST_FILE).read_text()
    tree = ast.parse(src)

    # Find the target function
    target_func = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "connect_rollout_engines_from_distributed":
                target_func = node
                break
    assert target_func is not None, "connect_rollout_engines_from_distributed not found"

    # Find all init_weights_update_group.remote() calls within this function
    calls_found = 0
    calls_ok = 0
    required_kwargs = {"master_address", "master_port", "rank_offset", "world_size", "group_name"}

    for node in ast.walk(target_func):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "remote"):
            continue
        inner = func.value
        if not (isinstance(inner, ast.Attribute) and inner.attr == "init_weights_update_group"):
            continue

        calls_found += 1
        kw_names = {kw.arg for kw in node.keywords if kw.arg is not None}
        if required_kwargs.issubset(kw_names) and len(node.args) == 0:
            calls_ok += 1

    assert calls_found > 0, "No init_weights_update_group.remote() calls found"
    assert calls_found == calls_ok, (
        f"{calls_found - calls_ok}/{calls_found} calls still use positional args"
    )


# [pr_diff] fail_to_pass
def test_precompile_default_true():
    """SGLANG_JIT_DEEPGEMM_PRECOMPILE must default to 'true' in start_engines."""
    # AST-only because: start_engines is a Ray actor method requiring GPU cluster
    src = Path(ROLLOUT_FILE).read_text()
    tree = ast.parse(src)

    start_engines = _find_method(tree, "start_engines")
    assert start_engines is not None, "start_engines method not found"

    value = _find_env_var_default(start_engines, "SGLANG_JIT_DEEPGEMM_PRECOMPILE")
    assert value is not None, "SGLANG_JIT_DEEPGEMM_PRECOMPILE not found in start_engines"
    assert str(value).lower() == "true", (
        f"SGLANG_JIT_DEEPGEMM_PRECOMPILE defaults to '{value}', expected 'true'"
    )


# [pr_diff] fail_to_pass
def test_fast_warmup_present():
    """SGLANG_JIT_DEEPGEMM_FAST_WARMUP must be present with default 'true'
    in start_engines."""
    # AST-only because: start_engines is a Ray actor method requiring GPU cluster
    src = Path(ROLLOUT_FILE).read_text()
    tree = ast.parse(src)

    start_engines = _find_method(tree, "start_engines")
    assert start_engines is not None, "start_engines method not found"

    value = _find_env_var_default(start_engines, "SGLANG_JIT_DEEPGEMM_FAST_WARMUP")
    assert value is not None, "SGLANG_JIT_DEEPGEMM_FAST_WARMUP not found in start_engines"
    assert str(value).lower() == "true", (
        f"SGLANG_JIT_DEEPGEMM_FAST_WARMUP defaults to '{value}', expected 'true'"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_env_vars_preserved():
    """Existing env vars in start_engines must still be present."""
    # AST-only because: start_engines is a Ray actor method requiring GPU cluster
    src = Path(ROLLOUT_FILE).read_text()
    tree = ast.parse(src)

    start_engines = _find_method(tree, "start_engines")
    assert start_engines is not None, "start_engines method not found"

    required = {
        "SGL_DISABLE_TP_MEMORY_INBALANCE_CHECK",
        "SGLANG_DISABLE_TP_MEMORY_INBALANCE_CHECK",
        "SGLANG_MEMORY_SAVER_CUDA_GRAPH",
        "SGLANG_BATCH_INVARIANT_OPS_ENABLE_MM_FALLBACK_VARIANT",
    }
    found = set()
    for node in ast.walk(start_engines):
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if key is not None and isinstance(key, ast.Constant) and isinstance(key.value, str):
                    found.add(key.value)

    missing = required - found
    assert not missing, f"Missing env vars: {missing}"


# [pr_diff] pass_to_pass
def test_connect_function_preserved():
    """connect_rollout_engines_from_distributed must exist with non-trivial body."""
    # AST-only because: function requires Ray/NCCL distributed backend to execute
    src = Path(DIST_FILE).read_text()
    tree = ast.parse(src)

    func = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "connect_rollout_engines_from_distributed":
                func = node
                break

    assert func is not None, "connect_rollout_engines_from_distributed not found"
    stmts = [n for n in ast.walk(func) if isinstance(n, ast.stmt)]
    assert len(stmts) > 5, f"Function body too small ({len(stmts)} stmts) — likely a stub"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified files must not be truncated or replaced with stubs."""
    import os

    dist_size = os.path.getsize(DIST_FILE)
    rollout_size = os.path.getsize(ROLLOUT_FILE)
    # Originals are ~12KB and ~28KB; reject anything below 60%
    assert dist_size > 7000, f"dist file too small ({dist_size} bytes) — likely truncated"
    assert rollout_size > 16000, f"rollout file too small ({rollout_size} bytes) — likely truncated"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_method(tree: ast.AST, name: str):
    """Find a function/method by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name:
                return node
    return None


def _find_env_var_default(func_node: ast.AST, var_name: str):
    """Find the default value for an env var key in a dict literal within a function."""
    for node in ast.walk(func_node):
        if not isinstance(node, ast.Dict):
            continue
        for key, val in zip(node.keys, node.values):
            if key is None:
                continue
            if isinstance(key, ast.Constant) and key.value == var_name:
                if isinstance(val, ast.Constant):
                    return val.value
    return None
