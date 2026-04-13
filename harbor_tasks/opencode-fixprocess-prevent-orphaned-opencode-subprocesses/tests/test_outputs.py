import subprocess
import sys
import os

REPO = "/workspace/myrepo"


def test_add_function_correct():
    """The add function should actually add numbers (fail_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, 'src')
from calculator import add
result = add(2, 3)
assert result == 5, f"Expected 5, got {result}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout


# ============================================================================
# Pass-to-Pass Tests (repo_tests) - CI/CD gates that should pass at base commit
# ============================================================================


def test_multiply_function():
    """Repo: Multiply function works correctly (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, 'src')
from calculator import multiply
result = multiply(3, 4)
assert result == 12, f"Expected 12, got {result}"
result2 = multiply(-2, 5)
assert result2 == -10, f"Expected -10, got {result2}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout


def test_repo_python_syntax():
    """Repo: Python source files have valid syntax (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-m", "py_compile", "src/calculator.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Syntax check failed: {result.stderr}"


def test_repo_module_imports():
    """Repo: Calculator module can be imported without errors (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, 'src')
import calculator
print("Import successful")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "Import successful" in result.stdout


def test_repo_functions_have_docstrings():
    """Repo: All functions have docstrings (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", """
import ast
import sys

tree = ast.parse(open('src/calculator.py').read())
funcs = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
missing = [f.name for f in funcs if not ast.get_docstring(f)]

if missing:
    print(f"Functions missing docstrings: {missing}")
    sys.exit(1)
else:
    print(f"All {len(funcs)} functions have docstrings")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Docstring check failed: {result.stdout}{result.stderr}"
    assert "functions have docstrings" in result.stdout
