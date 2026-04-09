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
