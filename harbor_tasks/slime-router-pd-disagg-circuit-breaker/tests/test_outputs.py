"""
Task: slime-router-pd-disagg-circuit-breaker
Repo: THUDM/slime @ 183e525f60fcf435f82f273e9eb69702d3ce431a
PR:   (internal sync)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Strategy: Each behavioral test uses subprocess.run() to exec the extracted
_start_router source with mocked GPU deps (ray/torch/sglang unavailable on CPU).
"""

import ast
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/slime"
TARGET_FILE = f"{REPO}/slime/ray/rollout.py"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo context via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# Shared preamble injected into every subprocess — extracts _start_router and
# provides lightweight mocks for heavy GPU dependencies.
_PREAMBLE = r"""
import ast, copy, sys, types, random, time

TARGET = '""" + TARGET_FILE + r"""'
source = open(TARGET).read()
tree = ast.parse(source)
func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_start_router":
        lines = source.splitlines()
        func_src = "\n".join(lines[node.lineno - 1 : node.end_lineno])
        break
if func_src is None:
    raise RuntimeError("_start_router not found in " + TARGET)

class MockRouterArgs:
    @classmethod
    def from_cli_args(cls, *a, **kw):
        return cls()

class MockLogger:
    def info(self, *a): pass
    def warning(self, *a): pass
    def error(self, *a): pass

for name in ["slime", "slime.router", "slime.router.router",
             "sglang_router", "sglang_router.launch_router",
             "slime.utils", "slime.utils.http_utils"]:
    sys.modules.setdefault(name, types.ModuleType(name))
sys.modules["slime.router.router"].run_router = lambda *a, **kw: None
sys.modules["sglang_router.launch_router"].RouterArgs = MockRouterArgs
sys.modules["slime.utils.http_utils"].run_router = lambda *a, **kw: None

def make_args(**kw):
    defaults = dict(use_slime_router=False, sglang_router_ip=None,
                    sglang_router_port=None, sglang_router_request_timeout_secs=30)
    defaults.update(kw)
    return type("Args", (), defaults)()

def run_start_router(args, **kwargs):
    captured = {}
    class Proc:
        daemon = False
        def __init__(self, target=None, args=None):
            captured["called"] = True
            captured["args"] = args
        def start(self): pass
        def is_alive(self): return True
    ns = {"time": time, "random": random, "copy": copy, "logger": MockLogger(),
          "_wrap_ipv6": lambda x: x, "find_available_port": lambda x: 12345,
          "get_host_info": lambda: ("host", "127.0.0.1"),
          "multiprocessing": type("mp", (), {"Process": Proc})()}
    exec(func_src, ns)
    result = ns["_start_router"](args, **kwargs)
    ra = captured["args"][0] if captured.get("args") else None
    return result, ra, captured.get("called", False)
"""


# ---------------------------------------------------------------------------
# pass_to_pass (static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """rollout.py must parse without syntax errors."""
    r = _run_python(
        f"import py_compile; py_compile.compile('{TARGET_FILE}', doraise=True); print('PASS')"
    )
    assert r.returncode == 0, f"Syntax error: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — subprocess-executed behavioral tests
# ---------------------------------------------------------------------------

def test_slime_router_pd_disagg_no_crash():
    """Slime router + PD disagg no longer crashes and spawns a Process returning (ip, port)."""
    r = _run_python(_PREAMBLE + """
args = make_args(use_slime_router=True)
result, router_args, called = run_start_router(args, has_pd_disaggregation=True)
assert called, "Process was not spawned"
assert isinstance(result, (tuple, list)) and len(result) >= 2, \
    f"Expected (ip, port) tuple, got {result}"
assert result[0] is not None and result[1] is not None, \
    f"ip or port is None: {result}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_slime_router_pd_flag_set():
    """Slime router with PD disagg sets slime_router_pd_disaggregation=True on router_args."""
    r = _run_python(_PREAMBLE + """
args = make_args(use_slime_router=True)
_, router_args, _ = run_start_router(args, has_pd_disaggregation=True)
assert router_args is not None, "router_args not captured"
assert getattr(router_args, "slime_router_pd_disaggregation", False) is True, \
    "slime_router_pd_disaggregation not set on router_args"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_circuit_breaker_disabled_with_pd():
    """Non-slime router with PD disagg sets disable_circuit_breaker=True on router_args."""
    r = _run_python(_PREAMBLE + """
args = make_args(use_slime_router=False)
_, router_args, called = run_start_router(args, has_pd_disaggregation=True)
assert called, "Process was not spawned"
assert router_args is not None, "router_args not captured"
assert getattr(router_args, "disable_circuit_breaker", False) is True, \
    "disable_circuit_breaker not set on router_args"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# pass_to_pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

def test_slime_router_without_pd_still_works():
    """Slime router without PD disagg still launches normally (regression)."""
    r = _run_python(_PREAMBLE + """
args = make_args(use_slime_router=True)
result, router_args, called = run_start_router(args, has_pd_disaggregation=False)
assert called, "Process was not spawned"
assert isinstance(result, (tuple, list)) and len(result) >= 2, \
    f"Expected (ip, port) tuple, got {result}"
assert result[0] is not None and result[1] is not None
assert getattr(router_args, "slime_router_pd_disaggregation", False) is not True, \
    "slime_router_pd_disaggregation should not be set without PD disagg"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_circuit_breaker_without_pd():
    """Non-slime router without PD disagg does not set disable_circuit_breaker (regression)."""
    r = _run_python(_PREAMBLE + """
args = make_args(use_slime_router=False)
_, router_args, called = run_start_router(args, has_pd_disaggregation=False)
assert called, "Process was not spawned"
assert router_args is not None, "router_args not captured"
assert getattr(router_args, "disable_circuit_breaker", False) is not True, \
    "disable_circuit_breaker should not be set without PD disagg"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

def test_not_stub():
    """_start_router has real logic, not stubbed out."""
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
