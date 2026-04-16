"""Tests for PR #3189: fix raise instead of return ValueError

This PR fixes a bug where ensure_vector_query() was returning ValueError
instead of raising it, causing silent failures instead of proper error handling.
"""

import ast
import subprocess
import sys
from pathlib import Path

# Path to the cloned repo inside Docker
REPO = Path("/workspace/lancedb/python/python")
QUERY_FILE = REPO / "lancedb" / "query.py"


def _get_ensure_vector_query_node():
    """Extract the ensure_vector_query function AST node from query.py."""
    source = QUERY_FILE.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "ensure_vector_query":
            return node
    return None


def test_ensure_vector_query_raises_on_empty_list():
    """F2P: ensure_vector_query([]) should raise ValueError, not return it."""
    # Run a test script in the repo directory to test the function behavior
    test_script = """
import sys
sys.path.insert(0, '/workspace/lancedb/python/python')

# Read and exec just the function to avoid import issues
import ast

source = open('/workspace/lancedb/python/python/lancedb/query.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'ensure_vector_query':
        func_source = ast.unparse(node)
        break

# Create minimal namespace
from typing import Any, List, Union

# Mock pyarrow
class MockArray:
    pass

class MockPA:
    Array = MockArray

namespace = {
    'Any': Any,
    'List': List,
    'Union': Union,
    'pa': MockPA(),
}

exec(func_source, namespace)
ensure_vector_query = namespace['ensure_vector_query']

# Test empty list - should raise ValueError
raised = False
try:
    result = ensure_vector_query([])
    if isinstance(result, ValueError):
        print("BUG: returned ValueError instead of raising")
        sys.exit(1)
    else:
        print(f"Unexpected result: {result}")
        sys.exit(1)
except ValueError as e:
    if "non-empty" in str(e):
        raised = True
        print("PASS: correctly raised ValueError")
    else:
        print(f"Wrong error message: {e}")
        sys.exit(1)

if not raised:
    print("FAIL: did not raise ValueError")
    sys.exit(1)
"""

    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        raise AssertionError(f"Test failed:\n{result.stdout}\n{result.stderr}")


def test_ensure_vector_query_raises_on_nested_empty_list():
    """F2P: ensure_vector_query([[]]) should raise ValueError, not return it."""
    test_script = """
import sys
sys.path.insert(0, '/workspace/lancedb/python/python')

import ast

source = open('/workspace/lancedb/python/python/lancedb/query.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'ensure_vector_query':
        func_source = ast.unparse(node)
        break

from typing import Any, List, Union

class MockArray:
    pass

class MockPA:
    Array = MockArray

namespace = {
    'Any': Any,
    'List': List,
    'Union': Union,
    'pa': MockPA(),
}

exec(func_source, namespace)
ensure_vector_query = namespace['ensure_vector_query']

# Test nested empty list - should raise ValueError
raised = False
try:
    result = ensure_vector_query([[]])
    if isinstance(result, ValueError):
        print("BUG: returned ValueError instead of raising")
        sys.exit(1)
    else:
        print(f"Unexpected result: {result}")
        sys.exit(1)
except ValueError as e:
    if "non-empty" in str(e):
        raised = True
        print("PASS: correctly raised ValueError")
    else:
        print(f"Wrong error message: {e}")
        sys.exit(1)

if not raised:
    print("FAIL: did not raise ValueError")
    sys.exit(1)
"""

    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        raise AssertionError(f"Test failed:\n{result.stdout}\n{result.stderr}")


def test_ensure_vector_query_accepts_valid_inputs():
    """P2P: ensure_vector_query should accept valid vector inputs."""
    test_script = """
import sys
sys.path.insert(0, '/workspace/lancedb/python/python')

import ast

source = open('/workspace/lancedb/python/python/lancedb/query.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'ensure_vector_query':
        func_source = ast.unparse(node)
        break

from typing import Any, List, Union

class MockArray:
    pass

class MockPA:
    Array = MockArray

namespace = {
    'Any': Any,
    'List': List,
    'Union': Union,
    'pa': MockPA(),
}

exec(func_source, namespace)
ensure_vector_query = namespace['ensure_vector_query']

# Test valid inputs
result = ensure_vector_query([1.0, 2.0, 3.0])
assert result == [1.0, 2.0, 3.0], f"Expected [1.0, 2.0, 3.0], got {result}"

result = ensure_vector_query([[1.0, 2.0], [3.0, 4.0]])
assert result == [[1.0, 2.0], [3.0, 4.0]], f"Expected nested list, got {result}"

print("PASS: valid inputs work correctly")
"""

    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        raise AssertionError(f"Test failed:\n{result.stdout}\n{result.stderr}")


def test_repo_python_syntax():
    """P2P: Repo Python files have valid syntax (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(QUERY_FILE)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )
    assert result.returncode == 0, f"Syntax error in query.py:\n{result.stderr}"


def test_repo_query_py_ast_parses():
    """P2P: query.py can be parsed with ast module (pass_to_pass)."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            f"""
import ast
import sys
source = open('{QUERY_FILE}').read()
try:
    tree = ast.parse(source)
    print('AST parse OK')
    sys.exit(0)
except SyntaxError as e:
    print(f'Syntax error: {{e}}')
    sys.exit(1)
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"AST parse failed:\n{result.stderr}"


def test_repo_function_exists():
    """P2P: ensure_vector_query function exists and has correct signature (pass_to_pass)."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            f"""
import ast
import sys

source = open('{QUERY_FILE}').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'ensure_vector_query':
        args = [arg.arg for arg in node.args.args]
        if 'val' in args:
            print('Function exists with val parameter')
            sys.exit(0)
        else:
            print(f'Missing val parameter. Found: {{args}}')
            sys.exit(1)

print('ensure_vector_query function not found')
sys.exit(1)
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Function check failed:\n{result.stderr}"


def test_repo_function_source_structure():
    """P2P: ensure_vector_query has expected code structure (pass_to_pass)."""
    func_node = _get_ensure_vector_query_node()
    assert func_node is not None, "ensure_vector_query function should exist in query.py"

    func_source = ast.unparse(func_node)

    # Check for expected code patterns
    assert "len(val) == 0" in func_source, "Should check len(val) == 0"
    assert "len(sample) == 0" in func_source, "Should check len(sample) == 0"
    assert "non-empty" in func_source, "Should have 'non-empty' error message"


def test_repo_no_tabs_in_query_py():
    """P2P: query.py uses spaces for indentation (pass_to_pass)."""
    content = QUERY_FILE.read_text()
    assert "\t" not in content, "query.py should not contain tab characters"
