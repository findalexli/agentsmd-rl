"""Tests for langchain todo middleware async implementation."""

import asyncio
import inspect
import subprocess
import sys
from pathlib import Path

# Add the langchain_v1 package to the path
REPO = Path("/workspace/langchain")
LIBS_PATH = REPO / "libs" / "langchain_v1"
sys.path.insert(0, str(LIBS_PATH))


def test_awrite_todos_function_exists():
    """Fail-to-pass: _awrite_todos async function must exist in todo module."""
    from langchain.agents.middleware.todo import _awrite_todos

    assert _awrite_todos is not None, "_awrite_todos function does not exist"
    assert asyncio.iscoroutinefunction(_awrite_todos), \
        "_awrite_todos must be an async function (coroutine)"


def test_awrite_todos_has_correct_signature():
    """Fail-to-pass: _awrite_todos must have correct type hints and signature."""
    from langchain.agents.middleware.todo import _awrite_todos

    sig = inspect.signature(_awrite_todos)
    params = list(sig.parameters.keys())

    assert "runtime" in params, "_awrite_todos must have 'runtime' parameter"
    assert "todos" in params, "_awrite_todos must have 'todos' parameter"

    # Check return type annotation exists
    assert sig.return_annotation != inspect.Signature.empty, \
        "_awrite_todos must have return type annotation"


def test_todo_middleware_tool_has_coroutine():
    """Fail-to-pass: TodoListMiddleware tool must have coroutine registered."""
    from langchain.agents.middleware.todo import TodoListMiddleware, _awrite_todos

    middleware = TodoListMiddleware()
    write_todos_tool = None

    for tool in middleware.tools:
        if tool.name == "write_todos":
            write_todos_tool = tool
            break

    assert write_todos_tool is not None, "write_todos tool not found in middleware"
    assert write_todos_tool.coroutine is not None, \
        "write_todos tool must have coroutine registered for async support"
    assert write_todos_tool.coroutine is _awrite_todos, \
        "write_todos tool coroutine must be _awrite_todos"


def test_awrite_todos_docstring():
    """Fail-to-pass: _awrite_todos must have appropriate docstring."""
    from langchain.agents.middleware.todo import _awrite_todos

    assert _awrite_todos.__doc__ is not None, "_awrite_todos must have a docstring"
    assert len(_awrite_todos.__doc__.strip()) > 0, "_awrite_todos docstring must not be empty"


def test_awrite_todos_functional_behavior():
    """Fail-to-pass: _awrite_todos must correctly delegate to _write_todos."""
    import asyncio
    from unittest.mock import MagicMock

    from langchain.agents.middleware.todo import _awrite_todos, Todo

    async def run_test():
        # Create a mock runtime
        mock_runtime = MagicMock()
        mock_runtime.tool_call_id = "test_call_123"

        # Create test todos
        test_todos: list[Todo] = [
            {"content": "Test task", "status": "pending"},
        ]

        # Call the async function
        result = await _awrite_todos(mock_runtime, test_todos)

        # Verify result is a Command
        assert result is not None, "_awrite_todos must return a Command"
        assert hasattr(result, 'update'), "Result must be a Command with update attribute"
        assert 'todos' in result.update, "Command update must contain 'todos'"
        assert result.update['todos'] == test_todos, \
            f"Expected todos {test_todos}, got {result.update['todos']}"

    asyncio.run(run_test())


def test_upstream_tests_pass():
    """Pass-to-pass: Run the existing upstream unit tests for todo middleware."""
    test_file = LIBS_PATH / "tests" / "unit_tests" / "agents" / "middleware" / "implementations" / "test_todo.py"

    result = subprocess.run(
        ["python", "-m", "pytest", str(test_file), "-v", "--tb=short", "-x"],
        cwd=LIBS_PATH,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, \
        f"Upstream tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_ruff_linting():
    """Pass-to-pass: Code must pass ruff linting."""
    result = subprocess.run(
        ["ruff", "check", str(LIBS_PATH / "langchain" / "agents" / "middleware" / "todo.py")],
        cwd=LIBS_PATH,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, \
        f"Ruff linting failed:\n{result.stdout}\n{result.stderr}"


def test_mypy_type_checking():
    """Pass-to-pass: Code must pass mypy type checking."""
    result = subprocess.run(
        ["mypy", str(LIBS_PATH / "langchain" / "agents" / "middleware" / "todo.py")],
        cwd=LIBS_PATH,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # mypy returns 0 for success, 1 for type errors
    assert result.returncode == 0, \
        f"MyPy type checking failed:\n{result.stdout}\n{result.stderr}"


def test_ruff_formatting():
    """Pass-to-pass: Code must pass ruff formatting check (repo_tests)."""
    result = subprocess.run(
        ["ruff", "format", "--diff", str(LIBS_PATH / "langchain" / "agents" / "middleware" / "todo.py")],
        cwd=LIBS_PATH,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, \
        f"Ruff formatting check failed:\n{result.stdout}\n{result.stderr}"


def test_all_middleware_tests_pass():
    """Pass-to-pass: All agent middleware unit tests pass (repo_tests)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/agents/middleware/", "-v", "--tb=short", "-x", "--disable-socket", "--allow-unix-socket"],
        cwd=LIBS_PATH,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, \
        f"Middleware tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_todo_module_imports():
    """Pass-to-pass: Todo module imports work correctly (repo_tests)."""
    # Note: _awrite_todos is added by the fix, so only test imports that work at base commit
    result = subprocess.run(
        ["python", "-c", "from langchain.agents.middleware.todo import TodoListMiddleware, _write_todos, Todo, WriteTodosInput, PlanningState; print('All imports successful')"],
        cwd=LIBS_PATH,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, \
        f"Todo module imports failed:\n{result.stderr}"
