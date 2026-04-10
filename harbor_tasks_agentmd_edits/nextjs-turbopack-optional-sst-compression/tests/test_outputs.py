"""Behavioral tests for the process_file refactoring task."""

import subprocess
import tempfile
import os
from pathlib import Path

REPO = "/workspace/repo"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def test_process_file_returns_uppercase_content():
    """The function reads a file and returns its content in uppercase."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("hello world")
        temp_path = f.name

    try:
        r = _run_python(f"""
import sys
sys.path.insert(0, '{REPO}')
from main import process_file
from pathlib import Path
result = process_file(Path('{temp_path}'))
print(result)
""")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        assert "HELLO WORLD" in r.stdout, f"Expected 'HELLO WORLD', got: {r.stdout}"
    finally:
        os.unlink(temp_path)


def test_process_file_uses_pathlib():
    """The function accepts and properly uses pathlib.Path objects."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content")
        temp_path = f.name

    try:
        r = _run_python(f"""
import sys
sys.path.insert(0, '{REPO}')
from main import process_file
from pathlib import Path

# Test that function accepts Path objects
result = process_file(Path('{temp_path}'))
assert result is not None, "Function should work with pathlib.Path"

# Test that Path type hint is properly declared in signature
import inspect
sig = inspect.signature(process_file)
assert sig.parameters['filepath'].annotation == Path, "filepath parameter should be annotated as Path"
print("PASS")
""")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(temp_path)


def test_process_file_has_type_hints():
    """The function has type hints for parameters and return values."""
    r = _run_python(f"""
import sys
sys.path.insert(0, '{REPO}')
import inspect
from main import process_file
sig = inspect.signature(process_file)
params = sig.parameters
returns = sig.return_annotation

# Check that filepath parameter has annotation
assert params['filepath'].annotation != inspect.Parameter.empty, "filepath missing type hint"

# Check that return type is annotated
assert returns != inspect.Parameter.empty, "return type missing annotation"
assert returns == str, f"Expected return type str, got {{returns}}"

# Check that Path type hint is used
from pathlib import Path
assert params['filepath'].annotation == Path, f"Expected Path type, got {{params['filepath'].annotation}}"
print("PASS")
""")
    assert r.returncode == 0, f"Type hints missing: {r.stderr}"
    assert "PASS" in r.stdout


def test_process_file_has_docstring():
    """The function has a docstring with Args and Returns sections."""
    r = _run_python(f"""
import sys
sys.path.insert(0, '{REPO}')
from main import process_file

doc = process_file.__doc__
assert doc is not None, "Function missing docstring"
assert "Args:" in doc, "Docstring missing Args section"
assert "Returns:" in doc, "Docstring missing Returns section"
print("PASS")
""")
    assert r.returncode == 0, f"Docstring check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_process_file_uses_custom_exception():
    """The function raises FileProcessingError for missing files."""
    r = _run_python(f"""
import sys
sys.path.insert(0, '{REPO}')
from main import process_file, FileProcessingError
from pathlib import Path

try:
    process_file(Path('/nonexistent/file.txt'))
    print("ERROR: Should have raised exception")
except FileProcessingError as e:
    print(f"PASS: Caught FileProcessingError: {{e}}")
except Exception as e:
    print(f"ERROR: Wrong exception type: {{type(e).__name__}}: {{e}}")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Custom exception not used properly: {r.stdout}"


def test_no_bare_except_clause():
    """The function does not use bare 'except:' clauses."""
    r = _run_python(f"""
import ast

with open('{REPO}/main.py', 'r') as f:
    tree = ast.parse(f.read())

# Check for bare except clauses
for node in ast.walk(tree):
    if isinstance(node, ast.ExceptHandler):
        if node.type is None:
            print("ERROR: Found bare except clause")
            exit(1)

print("PASS: No bare except clauses found")
""")
    assert r.returncode == 0, f"Bare except check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_fileprocessingerror_class_exists():
    """FileProcessingError custom exception class is defined."""
    r = _run_python(f"""
import sys
sys.path.insert(0, '{REPO}')
from main import FileProcessingError

# Verify it's an Exception subclass
assert issubclass(FileProcessingError, Exception), "FileProcessingError should extend Exception"

# Verify it can be instantiated with a message
try:
    raise FileProcessingError("test message")
except FileProcessingError as e:
    assert "test message" in str(e), "Exception should preserve message"
    print("PASS")
""")
    assert r.returncode == 0, f"Custom exception check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_uses_pathlib_read_text():
    """The function uses Path.read_text() instead of open()."""
    r = _run_python(f"""
with open('{REPO}/main.py', 'r') as f:
    source = f.read()

# Should use read_text() from pathlib
if 'read_text()' in source:
    print("PASS: Uses pathlib.Path.read_text()")
else:
    print("ERROR: Should use pathlib.Path.read_text() for file reading")
    exit(1)
""")
    assert r.returncode == 0, f"Pathlib check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_handles_specific_exceptions():
    """The function handles FileNotFoundError and IOError specifically."""
    r = _run_python(f"""
with open('{REPO}/main.py', 'r') as f:
    source = f.read()

# Check for specific exception handling
if 'FileNotFoundError' not in source or 'IOError' not in source:
    print("ERROR: Should handle FileNotFoundError and IOError specifically")
    exit(1)

print("PASS: Handles specific exceptions")
""")
    assert r.returncode == 0, f"Exception handling check failed: {r.stderr}"
    assert "PASS" in r.stdout


# Pass-to-pass tests - verify the repo works correctly

def test_python_syntax_valid():
    """main.py has valid Python syntax."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/main.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in main.py: {r.stderr}"
