"""
Task: vllm-multinode-allreduce-fusion
Repo: vllm-project/vllm @ f26fcdfb9e50fef30381ed27fa956f7a43b0b1aa
PR:   38136

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/vllm"
TARGET = f"{REPO}/vllm/distributed/device_communicators/flashinfer_all_reduce.py"
ENVS = f"{REPO}/vllm/envs.py"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo environment."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """Both modified files must parse without syntax errors."""
    for path in [TARGET, ENVS]:
        src = Path(path).read_text()
        ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_default_backend_is_auto():
    """envs.py defaults VLLM_FLASHINFER_ALLREDUCE_BACKEND to 'auto'."""
    r = _run_py("""
import ast
from pathlib import Path

src = Path("vllm/envs.py").read_text()
tree = ast.parse(src)

# Check class-level annotation default
for node in ast.walk(tree):
    if isinstance(node, ast.AnnAssign) and hasattr(node.target, "id"):
        if node.target.id == "VLLM_FLASHINFER_ALLREDUCE_BACKEND":
            assert isinstance(node.value, ast.Constant), "Expected constant default"
            assert node.value.value == "auto", (
                f"Default should be 'auto', got '{node.value.value}'"
            )
            print("PASS")
            exit(0)

# Fallback: check env_with_choices call
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "env_with_choices":
        if (
            len(node.args) >= 2
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "VLLM_FLASHINFER_ALLREDUCE_BACKEND"
        ):
            assert isinstance(node.args[1], ast.Constant) and node.args[1].value == "auto", (
                "env_with_choices default should be 'auto'"
            )
            print("PASS")
            exit(0)

raise AssertionError("VLLM_FLASHINFER_ALLREDUCE_BACKEND default not found")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_resolve_backend_auto_selects_by_node_count():
    """_resolve_fi_ar_backend selects mnnvl for multi-node, trtllm for single-node."""
    r = _run_py("""
import ast, textwrap
from pathlib import Path
from unittest.mock import MagicMock

src = Path("vllm/distributed/device_communicators/flashinfer_all_reduce.py").read_text()
tree = ast.parse(src)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_resolve_fi_ar_backend":
        lines = src.splitlines(keepends=True)
        func_src = textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
        break

assert func_src is not None, "_resolve_fi_ar_backend not found"

for node_count, expected in [(1, "trtllm"), (2, "mnnvl"), (4, "mnnvl"), (8, "mnnvl")]:
    ns = {
        "envs": MagicMock(VLLM_FLASHINFER_ALLREDUCE_BACKEND="auto"),
        "get_node_count": lambda nc=node_count: nc,
        "logger": MagicMock(),
    }
    exec(func_src, ns)
    result = ns["_resolve_fi_ar_backend"]()
    assert result == expected, f"node_count={node_count}: expected '{expected}', got '{result}'"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_resolve_backend_explicit_passthrough():
    """_resolve_fi_ar_backend returns explicit backend without auto-selection."""
    r = _run_py("""
import ast, textwrap
from pathlib import Path
from unittest.mock import MagicMock

src = Path("vllm/distributed/device_communicators/flashinfer_all_reduce.py").read_text()
tree = ast.parse(src)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_resolve_fi_ar_backend":
        lines = src.splitlines(keepends=True)
        func_src = textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
        break

assert func_src is not None, "_resolve_fi_ar_backend not found"

for explicit_backend in ["mnnvl", "trtllm"]:
    for node_count in [1, 2, 4]:
        ns = {
            "envs": MagicMock(VLLM_FLASHINFER_ALLREDUCE_BACKEND=explicit_backend),
            "get_node_count": lambda nc=node_count: nc,
            "logger": MagicMock(),
        }
        exec(func_src, ns)
        result = ns["_resolve_fi_ar_backend"]()
        assert result == explicit_backend, (
            f"Explicit '{explicit_backend}' with node_count={node_count}: "
            f"expected '{explicit_backend}', got '{result}'"
        )

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_trtllm_multinode_raises_valueerror():
    """get_fi_ar_workspace raises ValueError when trtllm backend on multi-node."""
    r = _run_py("""
import ast, textwrap
from pathlib import Path
from unittest.mock import MagicMock

src = Path("vllm/distributed/device_communicators/flashinfer_all_reduce.py").read_text()
tree = ast.parse(src)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_fi_ar_workspace":
        lines = src.splitlines(keepends=True)
        func_src = textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
        break

assert func_src is not None, "get_fi_ar_workspace not found"

for node_count in [2, 4, 8]:
    ns = {
        "__annotations__": {},
        "torch": MagicMock(),
        "ProcessGroup": MagicMock(),
        "_fi_ar_workspace": None,
        "_fi_ar_quant_workspace": None,
        "_resolve_fi_ar_backend": lambda: "trtllm",
        "get_node_count": lambda nc=node_count: nc,
        "envs": MagicMock(VLLM_FLASHINFER_ALLREDUCE_BACKEND="trtllm"),
        "_create_workspace": MagicMock(),
        "logger": MagicMock(),
    }
    exec(func_src, ns)
    fn = ns["get_fi_ar_workspace"]

    try:
        fn(8, 0, 1024, 4096, "float16", None)
        raise AssertionError(f"Should have raised ValueError for node_count={node_count}")
    except ValueError as e:
        msg = str(e).lower()
        assert "multi" in msg or "trtllm" in msg, f"Wrong error message: {e}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_quant_workspace_none_for_multinode():
    """get_fi_ar_quant_workspace returns None for multi-node, creates workspace for single-node."""
    r = _run_py("""
import ast, textwrap
from pathlib import Path
from unittest.mock import MagicMock

src = Path("vllm/distributed/device_communicators/flashinfer_all_reduce.py").read_text()
tree = ast.parse(src)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_fi_ar_quant_workspace":
        lines = src.splitlines(keepends=True)
        func_src = textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
        break

assert func_src is not None, "get_fi_ar_quant_workspace not found"

sentinel = object()

# Multi-node (>1) must return None
for node_count in [2, 4, 8]:
    ns = {
        "__annotations__": {},
        "torch": MagicMock(),
        "ProcessGroup": MagicMock(),
        "_fi_ar_quant_workspace": None,
        "_fi_ar_workspace": None,
        "get_node_count": lambda nc=node_count: nc,
        "_create_workspace": lambda *a, **kw: sentinel,
        "logger": MagicMock(),
    }
    exec(func_src, ns)
    result = ns["get_fi_ar_quant_workspace"](8, 0, 1024, 4096, "float16", None)
    assert result is None, f"Expected None for node_count={node_count}, got {result}"

# Single-node (1) must NOT return None (should create workspace)
ns2 = {
    "__annotations__": {},
    "torch": MagicMock(),
    "ProcessGroup": MagicMock(),
    "_fi_ar_quant_workspace": None,
    "_fi_ar_workspace": None,
    "get_node_count": lambda: 1,
    "_create_workspace": lambda *a, **kw: sentinel,
    "logger": MagicMock(),
}
exec(func_src, ns2)
result2 = ns2["get_fi_ar_quant_workspace"](8, 0, 1024, 4096, "float16", None)
assert result2 is not None, "Single-node should create workspace, not return None"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_resolve_function_exists():
    """_resolve_fi_ar_backend exists with meaningful logic (conditionals, returns)."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_resolve_fi_ar_backend":
            stmts = [
                s
                for s in ast.walk(node)
                if isinstance(s, (ast.If, ast.Return, ast.Assign))
            ]
            assert len(stmts) >= 4, (
                f"_resolve_fi_ar_backend too shallow ({len(stmts)} key statements)"
            )
            return
    raise AssertionError("_resolve_fi_ar_backend not found")
