"""Tests for the external run ID refcount fix in langchain-core tracers."""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/langchain/libs/core")


def _run_in_venv(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run Python code in the uv venv environment."""
    return subprocess.run(
        ["uv", "run", "python", "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def test_external_run_id_cleanup_single_child():
    """Test that external RunTree is cleaned up after its single child finishes.

    This is the core fail-to-pass test for the memory leak fix.
    """
    code = """
import gc
import sys
from unittest.mock import MagicMock

from langsmith import Client, traceable
from langsmith.run_helpers import tracing_context

from langchain_core.callbacks.manager import CallbackManager
from langchain_core.runnables.base import RunnableLambda
from langchain_core.tracers.langchain import LangChainTracer


def _create_tracer_with_mocked_client():
    mock_session = MagicMock()
    mock_client = Client(
        session=mock_session, api_key="test", auto_batch_tracing=False
    )
    return LangChainTracer(
        client=mock_client, project_name="test-project"
    )


def test():
    tracer = _create_tracer_with_mocked_client()

    @RunnableLambda
    def child(x: str) -> str:
        return x

    with tracing_context(client=tracer.client, enabled=True):

        @traceable
        def parent(x: str) -> str:
            return child.invoke(x, config={"callbacks": [tracer]})

        result = parent("hello")

    gc.collect()

    if tracer.run_map:
        print(f"FAIL: run_map not empty: {list(tracer.run_map.keys())}")
        return False
    return True


success = test()
sys.exit(0 if success else 1)
"""
    result = _run_in_venv(code, timeout=60)
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_external_run_id_cleanup_sibling_children():
    """Test that external parent survives until ALL sibling children finish.

    This verifies the refcount mechanism works correctly for chains with
    multiple steps (e.g., prompt | llm).
    """
    code = """
import gc
import sys
from unittest.mock import MagicMock

from langsmith import Client, traceable
from langsmith.run_helpers import tracing_context

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tracers.langchain import LangChainTracer


def _create_tracer_with_mocked_client():
    mock_session = MagicMock()
    mock_client = Client(
        session=mock_session, api_key="test", auto_batch_tracing=False
    )
    return LangChainTracer(
        client=mock_client, project_name="test-project"
    )


def test():
    tracer = _create_tracer_with_mocked_client()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "bot"), ("human", "{input}")
    ])
    llm = FakeListChatModel(responses=["hi"])
    chain = prompt | llm

    with tracing_context(client=tracer.client, enabled=True):

        @traceable
        def parent(x: dict):
            return chain.invoke(x, config={"callbacks": [tracer]})

        result = parent({"input": "hello"})

    gc.collect()

    if tracer.run_map:
        print(f"FAIL: run_map not empty: {list(tracer.run_map.keys())}")
        return False
    if result is None:
        print("FAIL: result is None")
        return False
    return True


success = test()
sys.exit(0 if success else 1)
"""
    result = _run_in_venv(code, timeout=60)
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_runtree_no_accumulation():
    """Test that RunTree objects don't accumulate across multiple calls.

    This is the memory-level regression test.
    """
    code = """
import gc
import sys
from unittest.mock import MagicMock

from langsmith import Client, traceable
from langsmith.run_helpers import tracing_context

from langchain_core.runnables.base import RunnableLambda
from langchain_core.tracers.langchain import LangChainTracer


def _create_tracer_with_mocked_client():
    mock_session = MagicMock()
    mock_client = Client(
        session=mock_session, api_key="test", auto_batch_tracing=False
    )
    return LangChainTracer(
        client=mock_client, project_name="test-project"
    )


def test():
    tracer = _create_tracer_with_mocked_client()

    @RunnableLambda
    def child(x: str) -> str:
        return x

    counts = []
    with tracing_context(client=tracer.client, enabled=True):

        @traceable
        def parent(x: str) -> str:
            return child.invoke(x, config={"callbacks": [tracer]})

        for _ in range(5):
            parent("hello")
            gc.collect()
            run_map_runtrees = sum(
                1 + len(v.child_runs) for v in tracer.run_map.values()
            )
            counts.append(run_map_runtrees)

    expected = [0, 0, 0, 0, 0]
    if counts != expected:
        print(f"FAIL: RunTree objects accumulated: {counts}")
        return False
    return True


success = test()
sys.exit(0 if success else 1)
"""
    result = _run_in_venv(code, timeout=60)
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_core_unit_tests_pass():
    """Run the core unit tests for the tracing_interops module.

    Pass-to-pass test - these tests should pass with the fix applied.
    """
    result = subprocess.run(
        [
            "uv", "run",
            "pytest",
            "tests/unit_tests/runnables/test_tracing_interops.py",
            "-v",
            "--tb=short",
            "-x",
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-1000:]}"


def test_import_core_modules():
    """Test that core modules can be imported without errors."""
    code = """
from langchain_core.tracers.core import _TracerCore
from langchain_core.tracers.base import BaseTracer
from langchain_core.tracers.langchain import LangChainTracer
from langchain_core.callbacks.manager import CallbackManager

# Check that _external_run_ids attribute exists
tracer = LangChainTracer()
assert hasattr(tracer, '_external_run_ids'), "Missing _external_run_ids attribute"
assert isinstance(tracer._external_run_ids, dict), "_external_run_ids should be a dict"
print("OK")
"""
    result = _run_in_venv(code, timeout=30)
    assert result.returncode == 0, f"Import test failed:\n{result.stderr}"


def test_repo_lint_tracers():
    """Ruff linting passes for tracers and callbacks modules (pass_to_pass)."""
    result = subprocess.run(
        ["uv", "run", "ruff", "check", "langchain_core/tracers/", "langchain_core/callbacks/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_repo_format_tracers():
    """Ruff format check passes for tracers and callbacks modules (pass_to_pass)."""
    result = subprocess.run(
        ["uv", "run", "ruff", "format", "--diff", "langchain_core/tracers/", "langchain_core/callbacks/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Format check failed:\n{result.stderr[-500:]}"


def test_repo_tracer_unit_tests():
    """Unit tests for tracers module pass (pass_to_pass)."""
    result = subprocess.run(
        ["uv", "run", "pytest", "tests/unit_tests/tracers/", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Tracer tests failed:\n{result.stderr[-1000:]}"


def test_repo_callback_unit_tests():
    """Unit tests for callbacks module pass (pass_to_pass)."""
    result = subprocess.run(
        ["uv", "run", "pytest", "tests/unit_tests/callbacks/", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Callback tests failed:\n{result.stderr[-1000:]}"


def test_repo_manager_imports():
    """Callback manager module imports correctly (pass_to_pass)."""
    code = """
from langchain_core.callbacks.manager import CallbackManager, _configure

# Verify the _configure function exists and is importable
assert callable(_configure), "_configure should be callable"
print("OK")
"""
    result = _run_in_venv(code, timeout=30)
    assert result.returncode == 0, f"Import test failed:\n{result.stderr}"
