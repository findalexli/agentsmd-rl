"""
Task: Dummy Template Validation
Repo: dummy/template @ main

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/dummy-repo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile
    py_compile.compile(f"{REPO}/math_ops.py", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_core_bug_fixed():
    """The broken_add function returns correct result after fix."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, '/workspace/dummy-repo')
from math_ops import broken_add
result = broken_add(2, 3)
assert result == 5, f"Expected 5, got {result}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_edge_case():
    """Test edge case with zero values."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, '/workspace/dummy-repo')
from math_ops import broken_add
result = broken_add(0, 5)
assert result == 5, f"Expected 5, got {result}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified function has real logic, not just pass/return."""
    import ast

    src = Path(f"{REPO}/math_ops.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "broken_add":
            stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
            assert len(stmts) >= 1, "Function body is a stub"
            return
    raise AssertionError("Function not found")


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo code passes ruff linter (pass_to_pass)."""
    # Install ruff first
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "math_ops.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's existing unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, '/workspace/dummy-repo')
from math_ops import add
# Test the working add function
assert add(2, 3) == 5, "add(2, 3) failed"
assert add(-1, 1) == 0, "add(-1, 1) failed"
assert add(0, 0) == 0, "add(0, 0) failed"
print("All unit tests passed")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"
    assert "passed" in r.stdout.lower(), "Tests did not report success"
