"""Tests for lancedb fast_search feature addition.

This module tests that the fast_search method was properly added to
LanceFtsQueryBuilder class in python/python/lancedb/query.py
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/lancedb")
QUERY_FILE = REPO / "python" / "python" / "lancedb" / "query.py"


def parse_file(filepath: Path) -> ast.AST:
    """Parse a Python file into an AST."""
    with open(filepath, "r") as f:
        return ast.parse(f.read())


def find_class(tree: ast.AST, class_name: str) -> ast.ClassDef:
    """Find a class definition in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def find_method(class_def: ast.ClassDef, method_name: str) -> ast.FunctionDef:
    """Find a method definition in a class."""
    for item in class_def.body:
        if isinstance(item, ast.FunctionDef) and item.name == method_name:
            return item
    return None


# =============================================================================
# Pass-to-Pass Tests: Repo CI Checks
# These tests run actual CI commands from the repo's test suite to verify
# the codebase is in a working state.
# =============================================================================


def test_repo_ruff_check():
    """Repo's ruff linter passes on query.py (pass_to_pass)."""
    # Install ruff if not present
    subprocess.run(["pip", "install", "ruff==0.9.9", "-q"], check=True, capture_output=True)
    r = subprocess.run(
        ["ruff", "check", str(REPO / "python" / "python" / "lancedb" / "query.py")],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on query.py (pass_to_pass)."""
    # Install ruff if not present
    subprocess.run(["pip", "install", "ruff==0.9.9", "-q"], check=True, capture_output=True)
    r = subprocess.run(
        ["ruff", "format", "--check", str(REPO / "python" / "python" / "lancedb" / "query.py")],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_python_syntax():
    """Python syntax validation passes for query.py (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", str(REPO / "python" / "python" / "lancedb" / "query.py")],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_fts_tests_syntax():
    """Python syntax validation passes for test_fts.py (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", str(REPO / "python" / "python" / "tests" / "test_fts.py")],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check for test_fts.py failed:\n{r.stderr}"


def test_repo_query_tests_syntax():
    """Python syntax validation passes for test_query.py (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", str(REPO / "python" / "python" / "tests" / "test_query.py")],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check for test_query.py failed:\n{r.stderr}"


# =============================================================================
# Fail-to-Pass Tests: Functional Tests for the Feature
# =============================================================================


def test_fast_search_method_exists():
    """F2P: LanceFtsQueryBuilder has fast_search method."""
    tree = parse_file(QUERY_FILE)
    class_def = find_class(tree, "LanceFtsQueryBuilder")
    assert class_def is not None, "LanceFtsQueryBuilder class not found"

    method = find_method(class_def, "fast_search")
    assert method is not None, "fast_search method not found in LanceFtsQueryBuilder"


def test_fast_search_init_attribute():
    """F2P: __init__ initializes _fast_search to None."""
    tree = parse_file(QUERY_FILE)
    class_def = find_class(tree, "LanceFtsQueryBuilder")
    assert class_def is not None, "LanceFtsQueryBuilder class not found"

    init_method = find_method(class_def, "__init__")
    assert init_method is not None, "__init__ method not found"

    # Check that _fast_search = None is in the method body
    init_has_attr = False
    for node in ast.walk(init_method):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute) and target.attr == "_fast_search":
                    if isinstance(node.value, ast.Constant) and node.value.value is None:
                        init_has_attr = True

    assert init_has_attr, "_fast_search not initialized to None in __init__"


def test_fast_search_sets_true():
    """F2P: fast_search method sets _fast_search to True."""
    tree = parse_file(QUERY_FILE)
    class_def = find_class(tree, "LanceFtsQueryBuilder")
    method = find_method(class_def, "fast_search")
    assert method is not None, "fast_search method not found"

    # Check that _fast_search = True is in the method body
    sets_true = False
    for node in ast.walk(method):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute) and target.attr == "_fast_search":
                    if isinstance(node.value, ast.Constant) and node.value.value is True:
                        sets_true = True

    assert sets_true, "fast_search method does not set _fast_search to True"


def test_fast_search_returns_self():
    """F2P: fast_search method returns self for chaining."""
    tree = parse_file(QUERY_FILE)
    class_def = find_class(tree, "LanceFtsQueryBuilder")
    method = find_method(class_def, "fast_search")
    assert method is not None, "fast_search method not found"

    # Check that return self is in the method body
    returns_self = False
    for node in ast.walk(method):
        if isinstance(node, ast.Return):
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                returns_self = True

    assert returns_self, "fast_search method does not return self"


def test_fast_search_to_query_object():
    """F2P: to_query_object passes fast_search to Query constructor."""
    tree = parse_file(QUERY_FILE)
    class_def = find_class(tree, "LanceFtsQueryBuilder")
    method = find_method(class_def, "to_query_object")
    assert method is not None, "to_query_object method not found"

    # Check that fast_search=self._fast_search is in the Query constructor call
    has_fast_search_arg = False
    for node in ast.walk(method):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "Query":
                for kw in node.keywords:
                    if kw.arg == "fast_search":
                        if isinstance(kw.value, ast.Attribute):
                            if kw.value.attr == "_fast_search":
                                has_fast_search_arg = True

    assert has_fast_search_arg, "to_query_object does not pass fast_search to Query"


def test_fast_search_docstring():
    """F2P: fast_search method has proper docstring."""
    tree = parse_file(QUERY_FILE)
    class_def = find_class(tree, "LanceFtsQueryBuilder")
    method = find_method(class_def, "fast_search")
    assert method is not None, "fast_search method not found"

    # Check for docstring
    has_docstring = False
    if ast.get_docstring(method):
        docstring = ast.get_docstring(method)
        if "unindexed" in docstring.lower() or "flat search" in docstring.lower():
            has_docstring = True

    assert has_docstring, "fast_search method missing proper docstring"


def test_fast_search_return_annotation():
    """F2P: fast_search has correct return type annotation."""
    tree = parse_file(QUERY_FILE)
    class_def = find_class(tree, "LanceFtsQueryBuilder")
    method = find_method(class_def, "fast_search")
    assert method is not None, "fast_search method not found"

    # Check return annotation
    has_correct_annotation = False
    if method.returns:
        if isinstance(method.returns, ast.Name):
            if "LanceFtsQueryBuilder" in method.returns.id:
                has_correct_annotation = True
        elif isinstance(method.returns, ast.Constant):
            if "LanceFtsQueryBuilder" in str(method.returns.value):
                has_correct_annotation = True
        elif isinstance(method.returns, ast.Subscript):
            # Handle LanceFtsQueryBuilder inside quotes or generic types
            has_correct_annotation = True

    assert has_correct_annotation, "fast_search missing correct return type annotation"


if __name__ == "__main__":
    sys.exit(0 if all([
        test_fast_search_method_exists(),
        test_fast_search_init_attribute(),
        test_fast_search_sets_true(),
        test_fast_search_returns_self(),
        test_fast_search_to_query_object(),
        test_fast_search_docstring(),
        test_fast_search_return_annotation(),
    ]) else 1)
