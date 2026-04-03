"""
Task: pytorch-einops-lrucache-logspam
Repo: pytorch/pytorch @ 98e35020c7423c304778a7044f6baa3c8a98ba6d
PR:   175442

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import builtins
import types
from pathlib import Path

REPO = "/workspace/pytorch"
TARGET = f"{REPO}/torch/_dynamo/decorators.py"


def _extract_and_exec():
    """Extract _allow_in_graph_einops, execute with mocked allow_in_graph.

    Returns a list of function names that allow_in_graph was called on.
    AST-only extraction because: decorators.py imports torch internals
    (torch._dynamo.trace_rules etc.) that aren't installed in the test env.
    The extracted function is then EXEC'd with mocks to test behavior.
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_allow_in_graph_einops":
            func_node = node
            break
    assert func_node is not None, "_allow_in_graph_einops not found in source"

    lines = source.splitlines(keepends=True)
    func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])

    called = []

    def mock_allow_in_graph(fn):
        called.append(getattr(fn, "__name__", str(fn)))

    # Minimal torch mock — only needs torch.randn for the backend registration call
    torch_mock = types.ModuleType("torch")
    torch_mock.randn = lambda *a, **kw: None

    orig_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        # _torch_specific doesn't exist in standalone einops install
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

    return called


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: decorators.py imports torch internals that aren't installed
def test_syntax_check():
    """Target file must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_allow_in_graph_wraps_core_ops():
    """allow_in_graph must be called for rearrange and reduce.

    On the base commit, the version check causes an early return for
    einops >= 0.8.2, so allow_in_graph is never called. The fix must
    ensure these core ops are always wrapped.
    """
    called = _extract_and_exec()
    for op in ["rearrange", "reduce"]:
        assert op in called, (
            f"{op} not wrapped via allow_in_graph; called={called}"
        )


# [pr_diff] fail_to_pass
def test_multiple_einops_functions_wrapped():
    """At least 4 of 6 einops functions must be registered with allow_in_graph.

    einops exposes: rearrange, reduce, repeat, einsum, pack, unpack.
    A correct fix should wrap most/all of them (the except ImportError branch
    wraps all 6 for older einops, so a fix for 0.8.2+ should wrap at least 4).
    """
    called = _extract_and_exec()
    expected = {"rearrange", "reduce", "repeat", "einsum", "pack", "unpack"}
    found = set(called) & expected
    assert len(found) >= 4, f"Only {len(found)} einops functions wrapped: {sorted(found)}"


# [pr_diff] fail_to_pass
def test_version_check_does_not_skip_wrapping():
    """The version check must not cause allow_in_graph to be skipped.

    On base commit, einops 0.8.2 hits the version check and returns early
    without calling allow_in_graph at all. A correct fix ensures the function
    reaches the allow_in_graph calls regardless of einops version.
    """
    called = _extract_and_exec()
    # If allow_in_graph was never called, the version check is still skipping
    assert len(called) > 0, (
        "allow_in_graph was never called — version check is still causing early return"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: decorators.py imports torch internals; checking structure
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
    assert False, "_allow_in_graph_einops function not found"


# [static] pass_to_pass
# AST-only because: decorators.py imports torch internals; counting statements
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
    assert False, "_allow_in_graph_einops function not found"
