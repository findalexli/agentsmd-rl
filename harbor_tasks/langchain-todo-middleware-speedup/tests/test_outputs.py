"""Behavioral tests for TodoListMiddleware optimization."""

import subprocess
import time
from pathlib import Path

import pytest

REPO = Path("/workspace/langchain")
TODO_FILE = REPO / "libs/langchain_v1/langchain/agents/middleware/todo.py"


def test_todo_file_exists():
    """Target file exists."""
    assert TODO_FILE.exists(), f"Todo file not found at {TODO_FILE}"


def _run_in_uv_env(code: str, timeout: int = 60) -> tuple[int, str, str]:
    """Run Python code inside the uv environment."""
    test_script = REPO / "test_script.py"
    test_script.write_text(code)
    result = subprocess.run(
        ["uv", "run", "--group", "test", "python", str(test_script)],
        cwd=REPO / "libs/langchain_v1",
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    test_script.unlink(missing_ok=True)
    return result.returncode, result.stdout, result.stderr


def test_todo_list_middleware_instantiation():
    """TodoListMiddleware should be instantiable without errors."""
    code = """
import sys
sys.path.insert(0, '/workspace/langchain/libs/langchain_v1')
sys.path.insert(0, '/workspace/langchain/libs/core')

from langchain.agents.middleware.todo import TodoListMiddleware

middleware = TodoListMiddleware()
assert middleware is not None
assert hasattr(middleware, 'tools')
assert len(middleware.tools) == 1
print("SUCCESS: TodoListMiddleware instantiation works")
"""
    returncode, stdout, stderr = _run_in_uv_env(code, timeout=60)
    if returncode != 0:
        pytest.fail(f"TodoListMiddleware instantiation failed:\n{stderr}")
    assert "SUCCESS" in stdout


def test_tool_is_structured_tool_named_write_todos():
    """The tool should be a StructuredTool with name 'write_todos'."""
    code = """
import sys
sys.path.insert(0, '/workspace/langchain/libs/langchain_v1')
sys.path.insert(0, '/workspace/langchain/libs/core')

from langchain.agents.middleware.todo import TodoListMiddleware
from langchain_core.tools import StructuredTool

middleware = TodoListMiddleware()
tool = middleware.tools[0]

assert isinstance(tool, StructuredTool), f"Tool should be StructuredTool, got {type(tool)}"
assert tool.name == "write_todos", f"Tool name should be 'write_todos', got {tool.name}"

print("SUCCESS: Tool is StructuredTool with name write_todos")
"""
    returncode, stdout, stderr = _run_in_uv_env(code, timeout=60)
    if returncode != 0:
        pytest.fail(f"StructuredTool test failed:\n{stderr}")
    assert "SUCCESS" in stdout


def test_tool_has_args_schema():
    """The tool should have an args_schema that is a Pydantic model."""
    code = """
import sys
sys.path.insert(0, '/workspace/langchain/libs/langchain_v1')
sys.path.insert(0, '/workspace/langchain/libs/core')

from langchain.agents.middleware.todo import TodoListMiddleware
from pydantic import BaseModel

middleware = TodoListMiddleware()
tool = middleware.tools[0]

assert hasattr(tool, 'args_schema'), "Tool should have args_schema attribute"
args_schema = tool.args_schema
assert args_schema is not None, "args_schema should not be None"
assert issubclass(args_schema, BaseModel), f"args_schema should be a Pydantic model, got {args_schema}"

# The schema should have some field
schema = args_schema.model_json_schema()
props = schema.get("properties", {})
assert len(props) > 0, "args_schema should have at least one property"

print("SUCCESS: Tool has valid args_schema Pydantic model")
"""
    returncode, stdout, stderr = _run_in_uv_env(code, timeout=60)
    if returncode != 0:
        pytest.fail(f"args_schema test failed:\n{stderr}")
    assert "SUCCESS" in stdout


def test_initialization_performance():
    """TodoListMiddleware initialization should be fast (under 1 second for 100)."""
    code = """
import sys
import time
sys.path.insert(0, '/workspace/langchain/libs/langchain_v1')
sys.path.insert(0, '/workspace/langchain/libs/core')

from langchain.agents.middleware.todo import TodoListMiddleware

# Warm up
for _ in range(5):
    _ = TodoListMiddleware()

# Time 100 instantiations
start = time.perf_counter()
for _ in range(100):
    _ = TodoListMiddleware()
elapsed = time.perf_counter() - start

print(f"Time for 100 instantiations: {elapsed:.4f}s")

if elapsed < 1.0:
    print("SUCCESS: Initialization is fast")
else:
    print(f"SLOW: Initialization took {elapsed:.4f}s for 100 instantiations")
    sys.exit(1)
"""
    returncode, stdout, stderr = _run_in_uv_env(code, timeout=60)
    if returncode != 0:
        pytest.fail(f"Performance test failed:\n{stdout}\n{stderr}")
    assert "SUCCESS" in stdout


def test_write_todos_schema_has_todos_field():
    """WriteTodosInput schema should have a 'todos' field."""
    code = """
import sys
sys.path.insert(0, '/workspace/langchain/libs/langchain_v1')
sys.path.insert(0, '/workspace/langchain/libs/core')

from langchain.agents.middleware.todo import WriteTodosInput
from pydantic import BaseModel

assert issubclass(WriteTodosInput, BaseModel), "WriteTodosInput should inherit from BaseModel"

schema = WriteTodosInput.model_json_schema()
props = schema.get("properties", {})
assert "todos" in props, f"WriteTodosInput schema should have 'todos' property, got {list(props.keys())}"

print("SUCCESS: WriteTodosInput has todos field in schema")
"""
    returncode, stdout, stderr = _run_in_uv_env(code, timeout=60)
    if returncode != 0:
        pytest.fail(f"WriteTodosInput todos field test failed:\n{stderr}")
    assert "SUCCESS" in stdout


# --- Pass-to-pass tests ---

def test_repo_unit_tests():
    """Run existing repo unit tests (pass_to_pass)."""
    result = subprocess.run(
        [
            "uv", "run", "--group", "test", "python", "-m", "pytest",
            "tests/unit_tests/",
            "-v", "--tb=short",
            "--ignore=tests/unit_tests/test_pytest_config.py",
        ],
        cwd=REPO / "libs/langchain_v1",
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        if "No module named" in result.stderr or "ImportError" in result.stderr:
            pytest.skip(f"Unit tests skipped due to import issues: {result.stderr[:500]}")
    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"


def test_repo_todo_tests():
    """Run repo unit tests for todo middleware (pass_to_pass)."""
    result = subprocess.run(
        [
            "uv", "run", "--group", "test", "python", "-m", "pytest",
            "tests/unit_tests/agents/middleware/implementations/test_todo.py",
            "-v", "--tb=short",
        ],
        cwd=REPO / "libs/langchain_v1",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Todo tests failed:\n{result.stderr[-1000:]}"


def test_repo_middleware_tests():
    """Run repo unit tests for all middleware (pass_to_pass)."""
    result = subprocess.run(
        [
            "uv", "run", "--group", "test", "python", "-m", "pytest",
            "tests/unit_tests/agents/middleware/",
            "-v", "--tb=short",
        ],
        cwd=REPO / "libs/langchain_v1",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Middleware tests failed:\n{result.stderr[-1000:]}"


def test_repo_lint_package():
    """Run repo lint checks on package code (pass_to_pass)."""
    result = subprocess.run(
        ["make", "lint_package"],
        cwd=REPO / "libs/langchain_v1",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Package lint failed:\n{result.stderr[-500:]}"


def test_repo_lint_tests():
    """Run repo lint checks on test code (pass_to_pass)."""
    result = subprocess.run(
        ["make", "lint_tests"],
        cwd=REPO / "libs/langchain_v1",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Test lint failed:\n{result.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
