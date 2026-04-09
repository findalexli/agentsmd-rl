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

REPO = "/workspace/pytorch"
TARGET = f"{REPO}/torch/_dynamo/decorators.py"

# Reusable subprocess script that extracts _allow_in_graph_einops, mocks
# allow_in_graph / torch, executes the function, and prints which einops
# function names were passed to allow_in_graph (one per line).
_MOCK_EXEC_SCRIPT = r"""
import ast, builtins, types, json
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

torch_mock = types.ModuleType("torch")
torch_mock.randn = lambda *a, **kw: None

orig_import = builtins.__import__

def mock_import(name, *args, **kwargs):
    if "_torch_specific" in str(name):
        raise ImportError("mocked")
    return orig_import(name, *args, **kwargs)

builtins.__import__ = mock_import
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