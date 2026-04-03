"""
Task: transformers-docstring-checker-ast-cache
Repo: huggingface/transformers @ 1f553bdc1703c78e272656ab8fb86d6494593e18
PR:   #45009

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import inspect
import os
import subprocess
import sys
import tempfile
import textwrap
from unittest.mock import patch

sys.path.insert(0, "/workspace/transformers/utils")

from check_docstrings import (
    _build_ast_indexes,
    _find_typed_dict_classes,
    _get_auto_docstring_names,
    has_auto_docstring_decorator,
)

REPO = "/workspace/transformers"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    path = os.path.join(REPO, "utils/check_docstrings.py")
    with open(path) as f:
        source = f.read()
    ast.parse(source, filename=path)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_get_auto_docstring_names_detects_decorated():
    """_get_auto_docstring_names returns the set of @auto_docstring-decorated names."""
    src = textwrap.dedent("""\
        @auto_docstring
        class Foo:
            pass

        class Bar:
            pass

        @auto_docstring()
        class Baz:
            pass

        @auto_docstring
        def qux():
            pass

        @other_decorator
        class NotThis:
            pass
    """)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        names = _get_auto_docstring_names(path)
        assert isinstance(names, set), f"Expected set, got {type(names)}"
        assert names == {"Foo", "Baz", "qux"}, f"Expected {{Foo, Baz, qux}}, got {names}"
    finally:
        os.unlink(path)


# [pr_diff] fail_to_pass
def test_get_auto_docstring_names_caching():
    """Repeated calls with the same cache return the identical object."""
    src = textwrap.dedent("""\
        @auto_docstring
        class X:
            pass

        @auto_docstring()
        def y():
            pass
    """)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        cache = {}
        r1 = _get_auto_docstring_names(path, cache=cache)
        r2 = _get_auto_docstring_names(path, cache=cache)
        assert r1 is r2, "Cache must return the same object on repeated calls"
        assert path in cache, "Path must be stored in cache dict"
        assert r1 == {"X", "y"}, f"Expected {{X, y}}, got {r1}"
    finally:
        os.unlink(path)


# [pr_diff] fail_to_pass
def test_build_ast_indexes_uses_provided_tree():
    """_build_ast_indexes uses the tree= parameter instead of re-parsing."""
    source = textwrap.dedent("""\
        @auto_docstring
        class Alpha:
            def __init__(self, size=10):
                self.size = size

        @auto_docstring
        class Beta:
            def __init__(self, dim=20):
                self.dim = dim
    """)
    # Full tree should find both
    full_tree = ast.parse(source)
    full_items = _build_ast_indexes(source, tree=full_tree)
    full_names = {it.name for it in full_items}
    assert full_names == {"Alpha", "Beta"}, f"Full tree: expected both, got {full_names}"

    # Pruned tree (remove Beta) — function must respect the tree
    mod_tree = ast.parse(source)
    mod_tree.body = [n for n in mod_tree.body if not (isinstance(n, ast.ClassDef) and n.name == "Beta")]
    mod_items = _build_ast_indexes(source, tree=mod_tree)
    mod_names = {it.name for it in mod_items}
    assert "Beta" not in mod_names, f"Function ignored tree param — found Beta in pruned tree: {mod_names}"
    assert "Alpha" in mod_names, f"Alpha should still be found, got {mod_names}"


# [pr_diff] fail_to_pass
def test_find_typed_dict_classes_uses_provided_tree():
    """_find_typed_dict_classes uses the tree= parameter instead of re-parsing."""
    source = textwrap.dedent("""\
        class FooKwargs(TypedDict):
            x: int
            y: str

        class BarKwargs(TypedDict):
            a: float
    """)
    # Full tree should find both
    full_tree = ast.parse(source)
    full_result = _find_typed_dict_classes(source, tree=full_tree)
    assert len(full_result) == 2, f"Expected 2 TypedDicts, got {len(full_result)}"

    # Pruned tree (remove BarKwargs) — function must respect the tree
    mod_tree = ast.parse(source)
    mod_tree.body = [n for n in mod_tree.body if not (isinstance(n, ast.ClassDef) and n.name == "BarKwargs")]
    mod_result = _find_typed_dict_classes(source, tree=mod_tree)
    mod_names = {r["name"] for r in mod_result}
    assert "BarKwargs" not in mod_names, f"Function ignored tree param: {mod_names}"
    assert "FooKwargs" in mod_names, f"FooKwargs should still be found: {mod_names}"


# [pr_diff] fail_to_pass
def test_has_auto_docstring_decorator_uses_cache():
    """has_auto_docstring_decorator accepts a cache parameter for file-level lookups."""
    src = "@auto_docstring\nclass Cached:\n    pass\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        cache = {path: {"Cached"}}
        Cached = type("Cached", (), {})
        Other = type("Other", (), {})
        with patch.object(inspect, "getfile", return_value=path):
            assert has_auto_docstring_decorator(Cached, cache=cache) is True
            assert has_auto_docstring_decorator(Other, cache=cache) is False
    finally:
        os.unlink(path)


# [pr_diff] fail_to_pass
def test_get_auto_docstring_names_syntax_error():
    """Files with syntax errors return empty set instead of raising."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def broken(\n")
        path = f.name
    try:
        result = _get_auto_docstring_names(path)
        assert result == set(), f"Syntax-error file should return empty set, got {result}"
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — backward compatibility
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_build_ast_indexes_backward_compat():
    """_build_ast_indexes still works when called without tree parameter."""
    source = textwrap.dedent("""\
        @auto_docstring
        def my_func(x, y=10):
            pass

        @auto_docstring
        class MyModel:
            def __init__(self, hidden=768):
                self.hidden = hidden
    """)
    items = _build_ast_indexes(source)
    names = {it.name for it in items}
    assert "my_func" in names, f"my_func not found: {names}"
    assert "MyModel" in names, f"MyModel not found: {names}"
    func = next(it for it in items if it.name == "my_func")
    assert "x" in func.args and "y" in func.args, f"Expected args x,y got {func.args}"


# [pr_diff] pass_to_pass
def test_find_typed_dict_classes_backward_compat():
    """_find_typed_dict_classes still works when called without tree parameter."""
    source = textwrap.dedent("""\
        class MyKwargs(TypedDict):
            x: int
            y: str

        class AnotherKwargs(TypedDict):
            z: float
    """)
    result = _find_typed_dict_classes(source)
    names = {r["name"] for r in result}
    assert "MyKwargs" in names, f"MyKwargs not found: {names}"
    assert "AnotherKwargs" in names, f"AnotherKwargs not found: {names}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:17 @ 1f553bdc
def test_ruff_lint():
    """Code style check: ruff lint must pass on modified file."""
    r = subprocess.run(
        ["ruff", "check", "--select=E,W,F", "--ignore=E501", "--no-fix", "utils/check_docstrings.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [agent_config] pass_to_pass — AGENTS.md:2 @ 1f553bdc
def test_ruff_format():
    """Code style check: ruff format must pass on modified file (make style runs formatters and linters)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "utils/check_docstrings.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr}"
