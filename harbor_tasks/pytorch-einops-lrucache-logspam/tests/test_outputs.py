"""
Task: pytorch-einops-lrucache-logspam
Repo: pytorch/pytorch @ 98e35020c7423c304778a7044f6baa3c8a98ba6d
PR:   175442

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path
import os

REPO = "/workspace/pytorch"
TARGET = f"{REPO}/torch/_dynamo/decorators.py"

# Reusable subprocess script that extracts _allow_in_graph_einops, mocks
# allow_in_graph / torch / einops, executes the function, and prints which einops
# function names were passed to allow_in_graph (one per line).
_MOCK_EXEC_SCRIPT = r"""
import ast, builtins, types, json, sys
from pathlib import Path

TARGET = "/workspace/pytorch/torch/_dynamo/decorators.py"
source = Path(TARGET).read_text()
tree = ast.parse(source)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_allow_in_graph_einops":
        lines = source.splitlines(keepends=True)
        func_src = "".join(lines[node.lineno - 1 : node.end_lineno])
        break

assert func_src is not None, "_allow_in_graph_einops not found in source"

called = []

def mock_allow_in_graph(fn):
    called.append(getattr(fn, "__name__", str(fn)))

# Create mock einops module with trackable functions
class MockFn:
    def __init__(self, name):
        self.__name__ = name
    def __call__(self, *a, **kw):
        return None

mock_einops = types.ModuleType("einops")
mock_einops.__version__ = "0.8.2"
for fn_name in ["rearrange", "reduce", "repeat", "einsum", "pack", "unpack"]:
    setattr(mock_einops, fn_name, MockFn(fn_name))

# Mock einops.einops submodule
mock_einops.einops = types.ModuleType("einops.einops")
mock_einops.einops.get_backend = lambda x: None

torch_mock = types.ModuleType("torch")
torch_mock.randn = lambda *a, **kw: None

orig_import = builtins.__import__

def mock_import(name, *args, **kwargs):
    name_str = str(name)
    if "_torch_specific" in name_str:
        raise ImportError("mocked")
    if name_str == "einops" or name_str.startswith("einops."):
        # Return mock einops or its submodules
        if name_str == "einops":
            return mock_einops
        parts = name_str.split(".")
        obj = mock_einops
        for p in parts[1:]:
            obj = getattr(obj, p, mock_einops)
        return obj
    return orig_import(name, *args, **kwargs)

builtins.__import__ = mock_import

# Pre-populate sys.modules with our mock
sys.modules["einops"] = mock_einops
sys.modules["einops.einops"] = mock_einops.einops

try:
    ns = {
        "allow_in_graph": mock_allow_in_graph,
        "torch": torch_mock,
        "__builtins__": builtins,
    }
    exec(func_src, ns)
    ns["_allow_in_graph_einops"]()
finally:
    builtins.__import__ = orig_import

print(json.dumps(called))
"""


def _run_mock_exec(timeout: int = 30) -> list[str]:
    """Run the mock-execution script in a subprocess, return list of wrapped names."""
    import json

    script = Path(REPO) / "_eval_mock_exec.py"
    script.write_text(_MOCK_EXEC_SCRIPT)
    try:
        r = subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
        assert r.returncode == 0, f"Mock-exec script failed:\n{r.stderr}"
        return json.loads(r.stdout.strip())
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (subprocess)
# ---------------------------------------------------------------------------


def test_allow_in_graph_wraps_core_ops():
    """allow_in_graph must be called for rearrange and reduce.

    On the base commit the version check causes an early return for
    einops >= 0.8.2, so allow_in_graph is never called. The fix must
    ensure these core ops are always wrapped.
    """
    called = _run_mock_exec()
    for op in ["rearrange", "reduce"]:
        assert op in called, f"{op} not wrapped via allow_in_graph; called={called}"


def test_multiple_einops_functions_wrapped():
    """At least 4 of 6 einops functions must be registered with allow_in_graph.

    einops exposes: rearrange, reduce, repeat, einsum, pack, unpack.
    A correct fix should wrap most or all of them.
    """
    called = _run_mock_exec()
    expected = {"rearrange", "reduce", "repeat", "einsum", "pack", "unpack"}
    found = set(called) & expected
    assert len(found) >= 4, f"Only {len(found)} einops functions wrapped: {sorted(found)}"


def test_version_check_does_not_skip_wrapping():
    """The version check must not cause allow_in_graph to be skipped.

    On base commit, einops 0.8.2 hits the version check and returns early
    without calling allow_in_graph at all. A correct fix ensures the
    function reaches the allow_in_graph calls regardless of einops version.
    """
    called = _run_mock_exec()
    assert len(called) > 0, (
        "allow_in_graph was never called — version check is still causing early return"
    )


def test_version_check_is_commented_out():
    """The version check comparing einops.__version__ must be commented out.

    The base commit has an active `if einops.__version__ >= "0.8.2":`
    comparison that causes the early return. The fix comments this out.
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_allow_in_graph_einops":
            lines = source.splitlines(keepends=True)
            func_src = "".join(lines[node.lineno - 1 : node.end_lineno])
            break
    else:
        raise AssertionError("_allow_in_graph_einops not found")
    func_tree = ast.parse(func_src)
    for node in ast.walk(func_tree):
        if isinstance(node, ast.Compare):
            if isinstance(node.left, ast.Attribute) and node.left.attr == "__version__":
                raise AssertionError(
                    "Active version check still present — "
                    "the `if einops.__version__ >= '0.8.2':` block must be commented out"
                )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Target file must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


def test_repo_python_syntax():
    """Repo's Python syntax check passes (pass_to_pass).

    Uses py_compile to verify no syntax errors in the modified file.
    """
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_flake8_errors():
    """Repo's flake8 error check passes (pass_to_pass).

    Runs flake8 with only error-level checks (E9, F63, F7, F82) to catch
    syntax errors and undefined names without enforcing style rules.
    """
    subprocess.run(
        ["python3", "-m", "pip", "install", "flake8", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # pip install result is optional; flake8 might already be installed

    r = subprocess.run(
        ["flake8", "--select=E9,F63,F7,F82", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Flake8 error check failed:\n{r.stdout}{r.stderr}"


def test_repo_tools_tests():
    """Repo's tools tests pass (pass_to_pass).

    Runs lightweight tests from tools/test/ that don't require torch build.
    """
    subprocess.run(
        ["python3", "-m", "pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = REPO
    r = subprocess.run(
        ["python3", "-m", "pytest", "tools/test/test_docstring_linter.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"Tools tests failed:\n{r.stderr[-500:]}"


def test_repo_github_scripts_tests():
    """Repo's .github/scripts tests pass (pass_to_pass).

    Runs lightweight tests from .github/scripts/ that don't require torch build.
    """
    subprocess.run(
        ["python3", "-m", "pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = REPO
    r = subprocess.run(
        ["python3", "-m", "pytest", ".github/scripts/test_gitutils.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f".github/scripts tests failed:\n{r.stderr[-500:]}"


def test_function_imports_einops():
    """_allow_in_graph_einops must exist and contain 'import einops'."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_allow_in_graph_einops":
            has_import = any(
                isinstance(n, ast.Import) and any(a.name == "einops" for a in n.names)
                for n in ast.walk(node)
            )
            assert has_import, "function does not contain 'import einops'"
            return
    raise AssertionError("_allow_in_graph_einops function not found")


def test_not_stub():
    """Function has substantive body (>=4 AST statements), not just pass/return."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_allow_in_graph_einops":
            stmt_count = sum(
                1
                for n in ast.walk(node)
                if isinstance(
                    n,
                    (ast.Expr, ast.Assign, ast.Call, ast.Import, ast.ImportFrom,
                     ast.If, ast.Try, ast.For, ast.While, ast.With, ast.Return),
                )
            )
            assert stmt_count >= 4, f"Only {stmt_count} statements; function appears to be a stub"
            return
    raise AssertionError("_allow_in_graph_einops function not found")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — additional CI tests added by p2p enrichment
# ---------------------------------------------------------------------------


def test_repo_ruff_check():
    """Repo's ruff check passes on modified file (pass_to_pass).

    Runs ruff with only error-level checks (E9, F63, F7, F82) to catch
    syntax errors and undefined names without enforcing style rules.
    """
    subprocess.run(
        ["python3", "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    r = subprocess.run(
        ["ruff", "check", "--select=E9,F63,F7,F82", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}{r.stderr}"


def test_repo_label_utils_tests():
    """Repo's label_utils tests pass (pass_to_pass).

    Runs lightweight tests from .github/scripts/ that don't require torch build.
    """
    subprocess.run(
        ["python3", "-m", "pip", "install", "pytest", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = REPO
    r = subprocess.run(
        ["python3", "-m", "pytest", ".github/scripts/test_label_utils.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"label_utils tests failed:\n{r.stderr[-500:]}"


def test_repo_delete_old_branches_tests():
    """Repo's delete_old_branches tests pass (pass_to_pass).

    Runs lightweight tests from .github/scripts/ that don't require torch build.
    """
    subprocess.run(
        ["python3", "-m", "pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = REPO
    r = subprocess.run(
        ["python3", "-m", "pytest", ".github/scripts/test_delete_old_branches.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"delete_old_branches tests failed:\n{r.stderr[-500:]}"
