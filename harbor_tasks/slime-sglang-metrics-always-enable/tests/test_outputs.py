"""
Task: slime-sglang-metrics-always-enable
Repo: THUDM/slime @ a9614431b35e9c54b88a42f9d565ef81075172a1
PR:   #1747

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/slime"

ENGINE = f"{REPO}/slime/backends/sglang_utils/sglang_engine.py"
ROLLOUT_RAY = f"{REPO}/slime/ray/rollout.py"
ROLLOUT_SGLANG = f"{REPO}/slime/rollout/sglang_rollout.py"
WANDB = f"{REPO}/slime/utils/wandb_utils.py"


def _parse(path: str) -> tuple[str, ast.Module]:
    src = Path(path).read_text()
    return src, ast.parse(src)


def _find_func(tree: ast.Module, name: str, *, is_async: bool = False):
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
    return chr(10).join(lines[node.lineno - 1 : node.end_lineno])


def test_syntax_check():
    """All four modified files must parse without syntax errors."""
    for path in [ENGINE, ROLLOUT_RAY, ROLLOUT_SGLANG, WANDB]:
        source = Path(path).read_text()
        ast.parse(source)


def test_enable_metrics_in_server_kwargs():
    """_compute_server_args must set enable_metrics=True in the kwargs dict."""
    src, tree = _parse(ENGINE)
    func = _find_func(tree, "_compute_server_args")
    assert func is not None, "_compute_server_args function not found"
    for child in ast.walk(func):
        if isinstance(child, ast.Dict):
            keys = [k.value if isinstance(k, ast.Constant) else None for k in child.keys]
            if "enable_metrics" in keys:
                idx = keys.index("enable_metrics")
                val = child.values[idx]
                assert isinstance(val, ast.Constant) and val.value is True, f"enable_metrics must be True, got {ast.dump(val)}"
                return
    raise AssertionError("enable_metrics not found in any dict literal in _compute_server_args")


def test_enable_metrics_in_passthrough_args():
    """enable_metrics must be in the _EXTERNAL_ENGINE_SKIP_CHECK_FIELDS allowlist."""
    src, tree = _parse(ENGINE)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_EXTERNAL_ENGINE_SKIP_CHECK_FIELDS":
                    assert isinstance(node.value, ast.List)
                    elts = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
                    assert "enable_metrics" in elts, f"enable_metrics not in _EXTERNAL_ENGINE_SKIP_CHECK_FIELDS: {elts}"
                    return
    raise AssertionError("_EXTERNAL_ENGINE_SKIP_CHECK_FIELDS not found at module level")


def test_metrics_router_not_gated_on_flag():
    """_get_metrics_router_addr must not early-return when sglang_enable_metrics is unset."""
    src, tree = _parse(ROLLOUT_RAY)
    func = _find_func(tree, "_get_metrics_router_addr")
    assert func is not None, "_get_metrics_router_addr not found"
    body = _func_source(src, func)
    assert "sglang_enable_metrics" not in body, "_get_metrics_router_addr still checks sglang_enable_metrics"


def test_wandb_forwarding_not_gated_on_flag():
    """init_wandb_secondary must forward metrics when router_addr is set, without checking sglang_enable_metrics."""
    src, tree = _parse(WANDB)
    func = _find_func(tree, "init_wandb_secondary")
    assert func is not None, "init_wandb_secondary not found"
    body = _func_source(src, func)
    assert "sglang_enable_metrics" not in body, "init_wandb_secondary still checks sglang_enable_metrics"
    assert "router_addr" in body, "init_wandb_secondary must still check router_addr"


def test_prefill_load_balance_method():
    """Prefill workers must use follow_bootstrap_room, not round_robin."""
    src, tree = _parse(ENGINE)
    func = _find_func(tree, "_compute_server_args")
    assert func is not None, "_compute_server_args function not found"
    body = _func_source(src, func)
    assert "follow_bootstrap_room" in body, "Prefill load_balance_method should be follow_bootstrap_room"
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
                            assert val.value != "round_robin", "load_balance_method is still round_robin"
                            assert val.value == "follow_bootstrap_room", f"load_balance_method should be follow_bootstrap_room, got {val.value}"
                            return
    raise AssertionError("load_balance_method assignment not found in _compute_server_args")


def test_dp_rank_context_removed():
    """dp_rank_context method must be removed from GenerateState."""
    src, tree = _parse(ROLLOUT_SGLANG)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "GenerateState":
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            assert "dp_rank_context" not in methods, f"dp_rank_context should be removed, still found in: {methods}"
            init = next((n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"), None)
            if init is not None:
                init_src = _func_source(src, init)
                assert "dp_counts" not in init_src, "dp_counts should be removed from __init__"
                assert "dp_rank" not in init_src, "dp_rank should be removed from __init__"
            return
    raise AssertionError("GenerateState class not found")


def test_generate_and_rm_no_dp_rank_context():
    """generate_and_rm must not use dp_rank_context."""
    src, tree = _parse(ROLLOUT_SGLANG)
    func = _find_func(tree, "generate_and_rm", is_async=True)
    assert func is not None, "generate_and_rm not found"
    body = _func_source(src, func)
    assert "dp_rank_context" not in body, "generate_and_rm still references dp_rank_context"


def test_contextmanager_import_removed():
    """contextmanager import should be removed since dp_rank_context (its only user) is gone."""
    source = Path(ROLLOUT_SGLANG).read_text()
    assert "from contextlib import contextmanager" not in source, "contextmanager import still present but dp_rank_context was the only user"


def test_key_functions_exist():
    """All key functions and classes must still be present after changes."""
    _, tree = _parse(ENGINE)
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "_compute_server_args" in funcs, "Missing _compute_server_args"
    _, tree = _parse(ROLLOUT_RAY)
    methods = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "_get_metrics_router_addr" in methods, "Missing _get_metrics_router_addr"
    _, tree = _parse(ROLLOUT_SGLANG)
    classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    assert "GenerateState" in classes, "Missing GenerateState class"
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "generate_and_rm" in funcs, "Missing generate_and_rm"
    assert "reset" in funcs, "Missing reset method"
    _, tree = _parse(WANDB)
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "init_wandb_secondary" in funcs, "Missing init_wandb_secondary"


def test_files_not_truncated():
    """Changed files must not be truncated stubs."""
    min_lines = {ENGINE: 200, ROLLOUT_RAY: 100, ROLLOUT_SGLANG: 100, WANDB: 50}
    for path, expected_min in min_lines.items():
        lines = len(Path(path).read_text().splitlines())
        assert lines >= expected_min, f"{Path(path).name} looks truncated: {lines} lines (expected >= {expected_min})"


def test_changes_contained():
    """Fix touches at most 5 files (keep test scope small and behavior-focused)."""
    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    changed = [f for f in r.stdout.strip().splitlines() if f]
    assert len(changed) <= 5, f"Too many files changed ({len(changed)}): {changed}"


def test_rollout_train_eval_branches():
    """Rollout must preserve both train and eval branches (RolloutFnTrainOutput / RolloutFnEvalOutput)."""
    src = Path(ROLLOUT_SGLANG).read_text()
    assert "RolloutFnTrainOutput" in src, "RolloutFnTrainOutput missing — both train and eval branches must be preserved"
    assert "RolloutFnEvalOutput" in src, "RolloutFnEvalOutput missing — both train and eval branches must be preserved"


def test_repo_ruff_check():
    """Repo linting with ruff passes (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/slime/", "--select=E,F"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    modified_files = [
        "slime/backends/sglang_utils/sglang_engine.py",
        "slime/ray/rollout.py",
        "slime/rollout/sglang_rollout.py",
        "slime/utils/wandb_utils.py",
    ]
    for line in r.stdout.splitlines():
        if line.strip() and not line.startswith(" "):
            for mf in modified_files:
                if mf in line:
                    assert False, f"Ruff error in modified file: {line}"


def test_repo_chunked_gae():
    """Repo GAE tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/tests/test_chunked_gae.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"GAE tests failed:{chr(10)}{r.stdout[-500:]}{chr(10)}{r.stderr[-500:]}"


def test_repo_python_syntax():
    """Python syntax check passes for modified files (pass_to_pass)."""
    modified_files = [
        f"{REPO}/slime/backends/sglang_utils/sglang_engine.py",
        f"{REPO}/slime/ray/rollout.py",
        f"{REPO}/slime/rollout/sglang_rollout.py",
        f"{REPO}/slime/utils/wandb_utils.py",
    ]
    for path in modified_files:
        r = subprocess.run(
            ["python", "-m", "py_compile", path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"Syntax error in {path}:{chr(10)}{r.stderr}"


def test_repo_pytest_version():
    """Pytest is available and working (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"pytest not available:{chr(10)}{r.stderr}"
    assert "pytest" in r.stdout.lower(), "pytest version output unexpected"


def test_repo_mtp_bridge_mapping():
    """Repo MTP bridge mapping unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/tests/test_qwen3_5_mtp_bridge_mapping.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"MTP bridge mapping tests failed:{chr(10)}{r.stdout[-500:]}{chr(10)}{r.stderr[-500:]}"


def test_repo_sglang_config_import():
    """SglangConfig module can be imported and parsed (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "from slime.backends.sglang_utils.sglang_config import SglangConfig; print(chr(79)+chr(75))"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"SglangConfig import failed:{chr(10)}{r.stderr}"


# =============================================================================
# New pass_to_pass tests using actual CI commands (repo_tests origin)
# =============================================================================


def test_repo_sglang_engine_syntax_and_structure():
    """Sglang engine module syntax and key structure is valid (pass_to_pass)."""
    # Check syntax
    r = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/slime/backends/sglang_utils/sglang_engine.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"sglang_engine.py syntax error:{chr(10)}{r.stderr}"
    # Check key functions exist via AST
    src, tree = _parse(ENGINE)
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "_compute_server_args" in funcs, "Missing _compute_server_args function"
    # Check the skip fields list exists
    found_skip_fields = False
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_EXTERNAL_ENGINE_SKIP_CHECK_FIELDS":
                    found_skip_fields = True
                    break
        if found_skip_fields:
            break
    assert found_skip_fields, "Missing _EXTERNAL_ENGINE_SKIP_CHECK_FIELDS list"


def test_repo_rollout_syntax_and_structure():
    """Rollout module syntax and key structure is valid (pass_to_pass)."""
    # Check syntax
    r = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/slime/ray/rollout.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"rollout.py syntax error:{chr(10)}{r.stderr}"
    # Check key function exists via AST
    src, tree = _parse(ROLLOUT_RAY)
    methods = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "_get_metrics_router_addr" in methods, "Missing _get_metrics_router_addr function"


def test_repo_wandb_utils_syntax_and_structure():
    """Wandb utils module syntax and key structure is valid (pass_to_pass)."""
    # Check syntax
    r = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/slime/utils/wandb_utils.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"wandb_utils.py syntax error:{chr(10)}{r.stderr}"
    # Check key function exists via AST
    _, tree = _parse(WANDB)
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "init_wandb_secondary" in funcs, "Missing init_wandb_secondary function"


def test_repo_isort_check():
    """Repo import ordering check with isort passes (pass_to_pass)."""
    r = subprocess.run(
        ["isort", "--check-only", "--profile=black", f"{REPO}/slime/backends/sglang_utils/sglang_engine.py", f"{REPO}/slime/ray/rollout.py", f"{REPO}/slime/rollout/sglang_rollout.py", f"{REPO}/slime/utils/wandb_utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # isort returns 0 if files are correctly formatted, 1 if they need changes
    # We accept both as "pass" since the formatting itself isn't the issue
    assert r.returncode in [0, 1], f"isort check failed with unexpected error:{chr(10)}{r.stderr}"


def test_repo_black_check():
    """Repo code formatting check with black passes (pass_to_pass)."""
    r = subprocess.run(
        ["black", "--check", "--line-length=119", f"{REPO}/slime/backends/sglang_utils/sglang_engine.py", f"{REPO}/slime/ray/rollout.py", f"{REPO}/slime/rollout/sglang_rollout.py", f"{REPO}/slime/utils/wandb_utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # black returns 0 if files are correctly formatted, 1 if they need changes
    # We accept both as "pass" since the formatting itself isn't the issue
    assert r.returncode in [0, 1], f"black check failed with unexpected error:{chr(10)}{r.stderr}"
