"""
Task: slime-wandb-sglang-metrics
Repo: THUDM/slime @ d4c4d3fb24d45c3cd12f47b64b30fc3301286778
PR:   1768

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/slime"

WANDB_UTILS = Path(f"{REPO}/slime/utils/wandb_utils.py")
LOGGING_UTILS = Path(f"{REPO}/slime/utils/logging_utils.py")
ROLLOUT = Path(f"{REPO}/slime/ray/rollout.py")
TRAIN = Path(f"{REPO}/train.py")
TRAIN_ASYNC = Path(f"{REPO}/train_async.py")

MODIFIED_FILES = [WANDB_UTILS, LOGGING_UTILS, ROLLOUT, TRAIN, TRAIN_ASYNC]


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text())


def _find_func(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _func_arg_names(func: ast.FunctionDef) -> list[str]:
    return [a.arg for a in func.args.args] + [a.arg for a in func.args.kwonlyargs]


def _non_docstring_stmts(func: ast.FunctionDef) -> list[ast.stmt]:
    return [
        s for s in func.body
        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
    ]


def _extract_func_source(path: Path, name: str) -> str:
    """Extract a top-level function's source code by AST line range."""
    src_lines = path.read_text().splitlines(keepends=True)
    tree = _parse(path)
    func = _find_func(tree, name)
    assert func is not None, f"{name} not found in {path.name}"
    return textwrap.dedent("".join(src_lines[func.lineno - 1 : func.end_lineno]))


def _make_mock_args(**overrides):
    """Create a mock args object with common wandb attributes."""
    args = MagicMock()
    args.use_wandb = True
    args.wandb_run_id = "test-run-id"
    args.wandb_team = "test-team"
    args.wandb_project = "test-project"
    args.wandb_dir = None
    for k, v in overrides.items():
        setattr(args, k, v)
    return args


def _exec_reinit_func():
    """Extract reinit_wandb_primary_with_open_metrics, exec with mocks, return (func, wandb_mock)."""
    src = _extract_func_source(WANDB_UTILS, "reinit_wandb_primary_with_open_metrics")

    mock_wandb = MagicMock()
    mock_sglang = MagicMock()
    mock_sglang.__version__ = "slime-custom-0.1"

    # Keep mock installed in sys.modules so the function can `import sglang_router`
    # when called by tests (the import runs at call time, not at exec/definition time).
    sys.modules["sglang_router"] = mock_sglang

    namespace = {
        "wandb": mock_wandb,
        "logger": MagicMock(),
        "_is_offline_mode": lambda args: False,
        "_init_wandb_common": MagicMock(),
    }
    exec(compile(src, "<test>", "exec"), namespace)
    return namespace["reinit_wandb_primary_with_open_metrics"], mock_wandb


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified Python files must parse without errors."""
    for f in MODIFIED_FILES:
        ast.parse(f.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_router_addr_removed_from_secondary():
    """init_wandb_secondary must not accept router_addr parameter."""
    # AST-only because: init_wandb_secondary body uses wandb internal Settings that can't be mocked cleanly
    tree = _parse(WANDB_UTILS)
    func = _find_func(tree, "init_wandb_secondary")
    assert func is not None, "init_wandb_secondary function not found"
    params = _func_arg_names(func)
    assert "router_addr" not in params, (
        f"router_addr still in init_wandb_secondary signature: {params}"
    )


# [pr_diff] fail_to_pass
def test_reinit_function_exists():
    """reinit_wandb_primary_with_open_metrics must exist with args + router_addr params."""
    tree = _parse(WANDB_UTILS)
    func = _find_func(tree, "reinit_wandb_primary_with_open_metrics")
    assert func is not None, "reinit_wandb_primary_with_open_metrics not found"
    params = _func_arg_names(func)
    assert "args" in params, "reinit function must accept 'args'"
    assert "router_addr" in params, "reinit function must accept 'router_addr'"


# [pr_diff] fail_to_pass
def test_reinit_calls_wandb_finish_and_init():
    """reinit function calls wandb.finish() then wandb.init() to re-initialize."""
    func, mock_wandb = _exec_reinit_func()

    call_order = []
    mock_wandb.finish.side_effect = lambda *a, **k: call_order.append("finish")
    mock_wandb.init.side_effect = lambda *a, **k: call_order.append("init")

    func(_make_mock_args(), "http://10.0.0.1:30000")

    assert "finish" in call_order, "reinit must call wandb.finish()"
    assert "init" in call_order, "reinit must call wandb.init()"
    assert call_order.index("finish") < call_order.index("init"), (
        "wandb.finish() must be called before wandb.init()"
    )


# [pr_diff] fail_to_pass
def test_reinit_configures_metrics_endpoints():
    """reinit function configures sgl_engine metrics endpoints with resume mode."""
    func, mock_wandb = _exec_reinit_func()

    # Test with multiple different router addresses to prevent hardcoding
    for addr in ["http://10.0.0.1:30000", "http://192.168.1.5:8080", "http://localhost:9090"]:
        mock_wandb.reset_mock()
        func(_make_mock_args(), addr)

        # Must call wandb.init with resume mode
        assert mock_wandb.init.called, f"wandb.init not called for addr={addr}"
        init_kwargs = mock_wandb.init.call_args.kwargs
        assert init_kwargs.get("resume"), f"resume not set in init kwargs for addr={addr}"

        # Must call wandb.Settings with metrics endpoint containing the router address
        assert mock_wandb.Settings.called, f"wandb.Settings not called for addr={addr}"
        settings_kwargs = mock_wandb.Settings.call_args.kwargs
        endpoints = settings_kwargs.get("x_stats_open_metrics_endpoints", {})
        assert any(addr in str(v) for v in endpoints.values()), (
            f"Router addr {addr} not in metrics endpoints: {endpoints}"
        )


# [pr_diff] fail_to_pass
def test_reinit_noop_when_no_router():
    """reinit returns early without touching wandb when router_addr is None."""
    func, mock_wandb = _exec_reinit_func()

    func(_make_mock_args(), None)

    assert not mock_wandb.finish.called, (
        "wandb.finish() must not be called when router_addr is None"
    )
    assert not mock_wandb.init.called, (
        "wandb.init() must not be called when router_addr is None"
    )


# [pr_diff] fail_to_pass
def test_update_tracking_bridge_exists():
    """logging_utils exposes update_tracking_open_metrics bridging to wandb_utils."""
    # AST-only because: logging_utils imports wandb_utils at module level (heavy deps)
    tree = _parse(LOGGING_UTILS)
    func = _find_func(tree, "update_tracking_open_metrics")
    assert func is not None, "update_tracking_open_metrics not found in logging_utils"
    params = _func_arg_names(func)
    assert "args" in params, "must accept args"
    assert "router_addr" in params, "must accept router_addr"
    src = ast.unparse(func)
    assert "reinit_wandb_primary_with_open_metrics" in src, (
        "must delegate to reinit_wandb_primary_with_open_metrics"
    )


# [pr_diff] fail_to_pass
def test_public_get_metrics_router_addr():
    """Rollout manager exposes public get_metrics_router_addr method."""
    # AST-only because: rollout.py requires ray, placement groups, GPU servers
    tree = _parse(ROLLOUT)
    func = _find_func(tree, "get_metrics_router_addr")
    assert func is not None, "get_metrics_router_addr not found in rollout.py"
    body = _non_docstring_stmts(func)
    assert len(body) >= 1, "get_metrics_router_addr must have a real body"
    src = ast.unparse(func)
    assert "_get_metrics_router_addr" in src or "router" in src.lower(), (
        "get_metrics_router_addr must return router address info"
    )


# [pr_diff] fail_to_pass
def test_train_calls_update_tracking():
    """train.py imports and calls update_tracking_open_metrics after rollout manager."""
    # AST-only because: train.py orchestrates ray actors, cannot execute
    src = TRAIN.read_text()
    assert "update_tracking_open_metrics" in src, (
        "train.py must reference update_tracking_open_metrics"
    )
    tree = _parse(TRAIN)
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and (
            (isinstance(node.func, ast.Name) and node.func.id == "update_tracking_open_metrics")
            or (isinstance(node.func, ast.Attribute) and node.func.attr == "update_tracking_open_metrics")
        )
    ]
    assert len(calls) >= 1, "train.py must call update_tracking_open_metrics"


# [pr_diff] fail_to_pass
def test_train_async_calls_update_tracking():
    """train_async.py imports and calls update_tracking_open_metrics after rollout manager."""
    # AST-only because: train_async.py orchestrates ray actors, cannot execute
    src = TRAIN_ASYNC.read_text()
    assert "update_tracking_open_metrics" in src, (
        "train_async.py must reference update_tracking_open_metrics"
    )
    tree = _parse(TRAIN_ASYNC)
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and (
            (isinstance(node.func, ast.Name) and node.func.id == "update_tracking_open_metrics")
            or (isinstance(node.func, ast.Attribute) and node.func.attr == "update_tracking_open_metrics")
        )
    ]
    assert len(calls) >= 1, "train_async.py must call update_tracking_open_metrics"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_reinit_not_stub():
    """reinit_wandb_primary_with_open_metrics has substantial implementation."""
    tree = _parse(WANDB_UTILS)
    func = _find_func(tree, "reinit_wandb_primary_with_open_metrics")
    assert func is not None, "reinit function not found"
    body = _non_docstring_stmts(func)
    assert len(body) >= 5, (
        f"reinit body too small ({len(body)} stmts) — likely a stub"
    )


# [static] pass_to_pass
def test_secondary_still_functional():
    """init_wandb_secondary must still exist and have non-trivial body."""
    tree = _parse(WANDB_UTILS)
    func = _find_func(tree, "init_wandb_secondary")
    assert func is not None, "init_wandb_secondary must still exist"
    body = _non_docstring_stmts(func)
    assert len(body) >= 3, (
        f"init_wandb_secondary body too small ({len(body)} stmts)"
    )
