"""
Task: slime-router-pd-disagg-circuit-breaker
Repo: THUDM/slime @ 183e525f60fcf435f82f273e9eb69702d3ce431a
PR:   (internal sync)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Strategy: AST-extract _start_router and exec with mocked globals, because the
module imports ray/torch/sglang (heavy GPU deps unavailable on CPU).
"""

import ast
import copy
import sys
import types
from pathlib import Path

import pytest

REPO = "/workspace/slime"
TARGET_FILE = f"{REPO}/slime/ray/rollout.py"


# ---------------------------------------------------------------------------
# Shared helpers — extract _start_router and run it with mocked globals
# ---------------------------------------------------------------------------

def _extract_function_source():
    """AST-extract _start_router source from rollout.py."""
    source = Path(TARGET_FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_start_router":
            lines = source.splitlines()
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    raise RuntimeError("_start_router not found in rollout.py")


class _MockRouterArgs:
    @classmethod
    def from_cli_args(cls, args, use_router_prefix=False):
        return cls()


class _MockLogger:
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def _install_mock_modules():
    """Install lightweight mock modules so `import slime.router...` works."""
    mock_slime_router = types.ModuleType("slime.router.router")
    mock_slime_router.run_router = lambda *a, **kw: None
    mock_sglang_router = types.ModuleType("sglang_router.launch_router")
    mock_sglang_router.RouterArgs = _MockRouterArgs
    mock_http_utils = types.ModuleType("slime.utils.http_utils")
    mock_http_utils.run_router = lambda *a, **kw: None

    for name, mod in [
        ("slime", types.ModuleType("slime")),
        ("slime.router", types.ModuleType("slime.router")),
        ("slime.router.router", mock_slime_router),
        ("sglang_router", types.ModuleType("sglang_router")),
        ("sglang_router.launch_router", mock_sglang_router),
        ("slime.utils", types.ModuleType("slime.utils")),
        ("slime.utils.http_utils", mock_http_utils),
    ]:
        sys.modules[name] = mod


def _make_base_ns():
    import random
    import time
    return {
        "time": time,
        "random": random,
        "copy": copy,
        "logger": _MockLogger(),
        "_wrap_ipv6": lambda x: x,
        "find_available_port": lambda x: 12345,
        "get_host_info": lambda: ("host", "127.0.0.1"),
    }


def _make_args(use_slime_router=False, sglang_router_ip=None,
               sglang_router_port=None, sglang_router_request_timeout_secs=30):
    return types.SimpleNamespace(
        use_slime_router=use_slime_router,
        sglang_router_ip=sglang_router_ip,
        sglang_router_port=sglang_router_port,
        sglang_router_request_timeout_secs=sglang_router_request_timeout_secs,
    )


def _run_start_router(func_source, base_ns, args, **kwargs):
    """Exec _start_router with a Process mock that captures router_args."""
    captured = {"called": False, "target_args": None}

    class CapturingProcess:
        daemon = False
        def __init__(self, target=None, args=None):
            captured["called"] = True
            captured["target_args"] = args
        def start(self): pass
        def is_alive(self): return True

    ns = dict(base_ns)
    ns["multiprocessing"] = types.SimpleNamespace(Process=CapturingProcess)
    exec(func_source, ns)
    result = ns["_start_router"](args, **kwargs)
    router_args = captured["target_args"][0] if captured["target_args"] else None
    return result, router_args, captured["called"]


# ---------------------------------------------------------------------------
# Module-level setup
# ---------------------------------------------------------------------------

_install_mock_modules()
_FUNC_SOURCE = _extract_function_source()
_BASE_NS = _make_base_ns()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """rollout.py must parse without syntax errors."""
    import py_compile
    py_compile.compile(TARGET_FILE, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_slime_router_pd_disagg_no_crash():
    """Slime router + PD disagg must not crash (old assertion removed) and must spawn a Process."""
    args = _make_args(use_slime_router=True)
    result, router_args, proc_called = _run_start_router(
        _FUNC_SOURCE, _BASE_NS, args, has_pd_disaggregation=True
    )
    assert proc_called, "Process was not spawned"
    assert isinstance(result, (tuple, list)) and len(result) >= 2, \
        f"Expected (ip, port) tuple, got {result}"
    assert result[0] is not None and result[1] is not None, \
        f"ip or port is None: {result}"


# [pr_diff] fail_to_pass
def test_slime_router_pd_flag_set():
    """Slime router with PD disagg must set slime_router_pd_disaggregation on router_args."""
    args = _make_args(use_slime_router=True)
    _, router_args, _ = _run_start_router(
        _FUNC_SOURCE, _BASE_NS, args, has_pd_disaggregation=True
    )
    assert router_args is not None, "router_args not captured"
    assert getattr(router_args, "slime_router_pd_disaggregation", False) is True, \
        "slime_router_pd_disaggregation not set on router_args"


# [pr_diff] fail_to_pass
def test_circuit_breaker_disabled_with_pd():
    """Non-slime router + PD disagg must set disable_circuit_breaker=True."""
    args = _make_args(use_slime_router=False)
    _, router_args, proc_called = _run_start_router(
        _FUNC_SOURCE, _BASE_NS, args, has_pd_disaggregation=True
    )
    assert proc_called, "Process was not spawned"
    assert router_args is not None, "router_args not captured"
    assert getattr(router_args, "disable_circuit_breaker", False) is True, \
        "disable_circuit_breaker not set on router_args"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_slime_router_without_pd_still_works():
    """Slime router without PD disagg must still launch normally."""
    args = _make_args(use_slime_router=True)
    result, router_args, proc_called = _run_start_router(
        _FUNC_SOURCE, _BASE_NS, args, has_pd_disaggregation=False
    )
    assert proc_called, "Process was not spawned"
    assert isinstance(result, (tuple, list)) and len(result) >= 2, \
        f"Expected (ip, port) tuple, got {result}"
    assert result[0] is not None and result[1] is not None
    # PD disagg flag should NOT be set when not requested
    assert getattr(router_args, "slime_router_pd_disaggregation", False) is not True, \
        "slime_router_pd_disaggregation should not be set without PD disagg"


# [pr_diff] pass_to_pass
def test_no_circuit_breaker_without_pd():
    """Non-slime router without PD disagg must NOT set disable_circuit_breaker."""
    args = _make_args(use_slime_router=False)
    _, router_args, proc_called = _run_start_router(
        _FUNC_SOURCE, _BASE_NS, args, has_pd_disaggregation=False
    )
    assert proc_called, "Process was not spawned"
    assert router_args is not None, "router_args not captured"
    assert getattr(router_args, "disable_circuit_breaker", False) is not True, \
        "disable_circuit_breaker should not be set without PD disagg"


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """_start_router must have real logic (not stubbed out)."""
    source = Path(TARGET_FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_start_router":
            body = [n for n in node.body
                    if not (isinstance(n, ast.Expr)
                            and isinstance(getattr(n, "value", None), ast.Constant))]
            assert len(body) >= 5, \
                f"Function body too short ({len(body)} stmts) — likely a stub"
            for n in ast.walk(node):
                if isinstance(n, ast.Raise) and isinstance(getattr(n, "exc", None), ast.Call):
                    if getattr(getattr(n.exc, "func", None), "id", "") == "NotImplementedError":
                        pytest.fail("Function raises NotImplementedError — likely a stub")
            return
    pytest.fail("_start_router not found in rollout.py")
