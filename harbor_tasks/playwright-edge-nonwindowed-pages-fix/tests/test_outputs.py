"""
Task: Example calculator bug fix validation
Repo: example-repo
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/example-repo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import ast
    src = Path(f"{REPO}/calculator.py").read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_core_bug_fixed():
    """The add function returns the correct sum (not difference)."""
    r = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, '/workspace/example-repo')
from calculator import add
result = add(3, 5)
assert result == 8, f"Expected 8, got {result}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_edge_case():
    """Test add with negative numbers."""
    r = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, '/workspace/example-repo')
from calculator import add
result = add(-2, -3)
assert result == -5, f"Expected -5, got {result}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_check():
    """Repo CI: Python syntax check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/calculator.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_import_check():
    """Repo CI: Module imports without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import calculator"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_multiply_regression():
    """Repo CI: multiply function still works (regression test, pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import calculator; result = calculator.multiply(3, 4); assert result == 12, f'Expected 12, got {result}'"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Multiply test failed:\n{r.stderr}"


# [static] pass_to_pass
def test_existing_function_unchanged():
    """The multiply function still works correctly."""
    r = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, '/workspace/example-repo')
from calculator import multiply
result = multiply(4, 5)
assert result == 20, f"Expected 20, got {result}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_not_stub():
    """Modified function has real logic, not just pass/return."""
    import ast

    src = Path(f"{REPO}/calculator.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "add":
            # Check it has an actual return with an operation
            for stmt in node.body:
                if isinstance(stmt, ast.Return):
                    # Should have some operation, not just a constant
                    assert not isinstance(stmt.value, ast.Constant), "Function returns constant (stub)"
