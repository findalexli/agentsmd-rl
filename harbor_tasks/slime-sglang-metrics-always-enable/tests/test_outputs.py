"""
Task: slime-sglang-metrics-always-enable
Repo: THUDM/slime @ a9614431b35e9c54b88a42f9d565ef81075172a1
PR:   #1747

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path

REPO = "/workspace/slime"

ENGINE = f"{REPO}/slime/backends/sglang_utils/sglang_engine.py"
ROLLOUT_RAY = f"{REPO}/slime/ray/rollout.py"
ROLLOUT_SGLANG = f"{REPO}/slime/rollout/sglang_rollout.py"
WANDB = f"{REPO}/slime/utils/wandb_utils.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(path: str) -> tuple[str, ast.Module]:
    src = Path(path).read_text()
    return src, ast.parse(src)


def _find_func(tree: ast.Module, name: str, *, is_async: bool = False):
    """Return the first FunctionDef/AsyncFunctionDef node with the given name."""
    cls = ast.AsyncFunctionDef if is_async else ast.FunctionDef
    for node in ast.walk(tree):
        if isinstance(node, cls) and node.name == name:
            return node
    return None


def _func_source(src: str, node) -> str:
    seg = ast.get_source_segment(src, node)
    if seg is not None:
        return seg
    lines = src.splitlines()
    return "\n".join(lines[node.lineno - 1 : node.end_lineno])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    # AST-only because: all files depend on torch/ray/sglang — cannot import
    """All four modified files must parse without syntax errors."""
    for path in [ENGINE, ROLLOUT_RAY, ROLLOUT_SGLANG, WANDB]:
        source = Path(path).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_enable_metrics_in_server_kwargs():
    # AST-only because: _compute_server_args depends on sglang ServerArgs and ray internals
    """_compute_server_args must set enable_metrics=True in the kwargs dict."""
    src, tree = _parse(ENGINE)
    func = _find_func(tree, "_compute_server_args")
    assert func is not None, "_compute_server_args function not found"

    # Walk through all dict literals in the function to find one with enable_metrics
    for child in ast.walk(func):
        if isinstance(child, ast.Dict):
            keys = [
                k.value if isinstance(k, ast.Constant) else None
                for k in child.keys
            ]
            if "enable_metrics" in keys:
                idx = keys.index("enable_metrics")
                val = child.values[idx]
                assert isinstance(val, ast.Constant) and val.value is True, (
                    f"enable_metrics must be True, got {ast.dump(val)}"
                )
                return
    raise AssertionError("enable_metrics not found in any dict literal in _compute_server_args")


# [pr_diff] fail_to_pass
def test_enable_metrics_in_passthrough_args():
    # AST-only because: _EXTERNAL_ENGINE_SKIP_CHECK_FIELDS is a module-level list in a file with heavy imports
    """enable_metrics must be in the _EXTERNAL_ENGINE_SKIP_CHECK_FIELDS allowlist."""
    src, tree = _parse(ENGINE)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_EXTERNAL_ENGINE_SKIP_CHECK_FIELDS":
                    assert isinstance(node.value, ast.List)
                    elts = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
                    assert "enable_metrics" in elts, (
                        f"enable_metrics not in _EXTERNAL_ENGINE_SKIP_CHECK_FIELDS: {elts}"
                    )
                    return
    raise AssertionError("_EXTERNAL_ENGINE_SKIP_CHECK_FIELDS not found at module level")


# [pr_diff] fail_to_pass
def test_metrics_router_not_gated_on_flag():
    # AST-only because: _get_metrics_router_addr is a method on a ray-based class
    """_get_metrics_router_addr must not early-return when sglang_enable_metrics is unset."""
    src, tree = _parse(ROLLOUT_RAY)
    func = _find_func(tree, "_get_metrics_router_addr")
    assert func is not None, "_get_metrics_router_addr not found"
    body = _func_source(src, func)
    assert "sglang_enable_metrics" not in body, (
        "_get_metrics_router_addr still checks sglang_enable_metrics"
    )


# [pr_diff] fail_to_pass
def test_wandb_forwarding_not_gated_on_flag():
    # AST-only because: init_wandb_secondary depends on wandb SDK
    """init_wandb_secondary must forward metrics when router_addr is set, without checking sglang_enable_metrics."""
    src, tree = _parse(WANDB)
    func = _find_func(tree, "init_wandb_secondary")
    assert func is not None, "init_wandb_secondary not found"
    body = _func_source(src, func)
    assert "sglang_enable_metrics" not in body, (
        "init_wandb_secondary still checks sglang_enable_metrics"
    )
    assert "router_addr" in body, (
        "init_wandb_secondary must still check router_addr"
    )


# [pr_diff] fail_to_pass
def test_prefill_load_balance_method():
    # AST-only because: _compute_server_args depends on sglang ServerArgs
    """Prefill workers must use follow_bootstrap_room, not round_robin."""
    src, tree = _parse(ENGINE)
    func = _find_func(tree, "_compute_server_args")
    assert func is not None, "_compute_server_args function not found"
    body = _func_source(src, func)
    # The fix changes round_robin -> follow_bootstrap_room for prefill
    assert "follow_bootstrap_room" in body, (
        "Prefill load_balance_method should be follow_bootstrap_room"
    )
    # The load_balance_method assignment in the prefill branch must use follow_bootstrap_room
    # Check that the specific assignment doesn't use round_robin (avoid matching
    # unrelated keys like "prefill_round_robin_balance" in other branches)
    for node in ast.walk(func):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Subscript):
                    key = None
                    if isinstance(target.slice, ast.Constant):
                        key = target.slice.value
                    if key == "load_balance_method":
                        val = node.value
                        if isinstance(val, ast.Constant):
                            assert val.value != "round_robin", (
                                "load_balance_method is still round_robin"
                            )
                            assert val.value == "follow_bootstrap_room", (
                                f"load_balance_method should be follow_bootstrap_room, got {val.value}"
                            )
                            return
    raise AssertionError("load_balance_method assignment not found in _compute_server_args")


# [pr_diff] fail_to_pass
def test_dp_rank_context_removed():
    # AST-only because: SGLangRolloutState depends on torch/numpy/sglang
    """dp_rank_context method must be removed from GenerateState."""
    src, tree = _parse(ROLLOUT_SGLANG)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "GenerateState":
            methods = [
                n.name
                for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            assert "dp_rank_context" not in methods, (
                f"dp_rank_context should be removed, still found in: {methods}"
            )
            # Also verify the dp bookkeeping attrs are gone from __init__
            init = next(
                (n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"),
                None,
            )
            if init is not None:
                init_src = _func_source(src, init)
                assert "dp_counts" not in init_src, "dp_counts should be removed from __init__"
                assert "dp_rank" not in init_src, "dp_rank should be removed from __init__"
            return
    raise AssertionError("GenerateState class not found")


# [pr_diff] fail_to_pass
def test_generate_and_rm_no_dp_rank_context():
    # AST-only because: generate_and_rm is async, depends on sglang/ray
    """generate_and_rm must not use dp_rank_context."""
    src, tree = _parse(ROLLOUT_SGLANG)
    func = _find_func(tree, "generate_and_rm", is_async=True)
    assert func is not None, "generate_and_rm not found"
    body = _func_source(src, func)
    assert "dp_rank_context" not in body, (
        "generate_and_rm still references dp_rank_context"
    )


# [pr_diff] fail_to_pass
def test_contextmanager_import_removed():
    """contextmanager import should be removed since dp_rank_context (its only user) is gone."""
    source = Path(ROLLOUT_SGLANG).read_text()
    assert "from contextlib import contextmanager" not in source, (
        "contextmanager import still present but dp_rank_context was the only user"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) -- regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_key_functions_exist():
    # AST-only because: all files have heavy deps that prevent import
    """All key functions and classes must still be present after changes."""
    # sglang_engine.py
    _, tree = _parse(ENGINE)
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "_compute_server_args" in funcs, "Missing _compute_server_args"

    # rollout.py
    _, tree = _parse(ROLLOUT_RAY)
    methods = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "_get_metrics_router_addr" in methods, "Missing _get_metrics_router_addr"

    # sglang_rollout.py
    _, tree = _parse(ROLLOUT_SGLANG)
    classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    assert "GenerateState" in classes, "Missing GenerateState class"
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "generate_and_rm" in funcs, "Missing generate_and_rm"
    assert "reset" in funcs, "Missing reset method"

    # wandb_utils.py
    _, tree = _parse(WANDB)
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "init_wandb_secondary" in funcs, "Missing init_wandb_secondary"


# [static] pass_to_pass
def test_files_not_truncated():
    """Changed files must not be truncated stubs."""
    min_lines = {
        ENGINE: 200,
        ROLLOUT_RAY: 100,
        ROLLOUT_SGLANG: 100,
        WANDB: 50,
    }
    for path, expected_min in min_lines.items():
        lines = len(Path(path).read_text().splitlines())
        assert lines >= expected_min, (
            f"{Path(path).name} looks truncated: {lines} lines (expected >= {expected_min})"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from .claude/skills/
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- .claude/skills/add-tests-and-ci/SKILL.md:25 @ a9614431
def test_changes_contained():
    """Fix touches at most 5 files (keep test scope small and behavior-focused)."""
    import subprocess

    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    changed = [f for f in r.stdout.strip().splitlines() if f]
    assert len(changed) <= 5, f"Too many files changed ({len(changed)}): {changed}"


# [agent_config] pass_to_pass -- .claude/skills/add-rollout-function/SKILL.md:44-46 @ a9614431
def test_rollout_train_eval_branches():
    # AST-only because: sglang_rollout.py depends on torch/numpy/sglang
    """Rollout must preserve both train and eval branches (RolloutFnTrainOutput / RolloutFnEvalOutput)."""
    src = Path(ROLLOUT_SGLANG).read_text()
    assert "RolloutFnTrainOutput" in src, (
        "RolloutFnTrainOutput missing — both train and eval branches must be preserved"
    )
    assert "RolloutFnEvalOutput" in src, (
        "RolloutFnEvalOutput missing — both train and eval branches must be preserved"
    )
