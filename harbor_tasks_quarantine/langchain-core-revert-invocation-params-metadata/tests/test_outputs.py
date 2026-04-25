"""Tests for langchain-core invocation params revert.

This tests that the _get_metadata_invocation_params method and its usages
have been properly removed as part of the revert.
"""

import ast
import inspect
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# Path to the repo
REPO = Path("/workspace/langchain")
CORE_DIR = REPO / "libs" / "core"
CHAT_MODELS_FILE = CORE_DIR / "langchain_core" / "language_models" / "chat_models.py"
TEST_FILE = CORE_DIR / "tests" / "unit_tests" / "language_models" / "chat_models" / "test_base.py"


# =============================================================================
# Fail-to-pass tests: These should FAIL before the fix and PASS after
# =============================================================================


def test_get_metadata_invocation_params_method_removed() -> None:
    """The _get_metadata_invocation_params method should be removed from BaseChatModel.

    This test verifies the core change of the revert - the method that filters
    invocation params for metadata inclusion should no longer exist.
    """
    source = CHAT_MODELS_FILE.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "_get_metadata_invocation_params":
                pytest.fail(f"Method _get_metadata_invocation_params should be removed but found at line {node.lineno}")


def test_stream_method_no_invocation_params_in_metadata() -> None:
    """stream() should not call _get_metadata_invocation_params.

    The inheritable_metadata dict should only include user metadata and ls_params,
    NOT the invocation params from _get_metadata_invocation_params.
    """
    source = CHAT_MODELS_FILE.read_text()

    # Find the stream method
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "stream":
            # Convert method to string and check for the call
            method_source = ast.unparse(node)
            if "_get_metadata_invocation_params" in method_source:
                pytest.fail("stream() method should not reference _get_metadata_invocation_params")


def test_astream_method_no_invocation_params_in_metadata() -> None:
    """astream() should not call _get_metadata_invocation_params."""
    source = CHAT_MODELS_FILE.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "astream":
            method_source = ast.unparse(node)
            if "_get_metadata_invocation_params" in method_source:
                pytest.fail("astream() method should not reference _get_metadata_invocation_params")


def test_generate_method_no_invocation_params_in_metadata() -> None:
    """generate() should not call _get_metadata_invocation_params."""
    source = CHAT_MODELS_FILE.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "generate":
            method_source = ast.unparse(node)
            if "_get_metadata_invocation_params" in method_source:
                pytest.fail("generate() method should not reference _get_metadata_invocation_params")


def test_agenerate_method_no_invocation_params_in_metadata() -> None:
    """agenerate() should not call _get_metadata_invocation_params."""
    source = CHAT_MODELS_FILE.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "agenerate":
            method_source = ast.unparse(node)
            if "_get_metadata_invocation_params" in method_source:
                pytest.fail("agenerate() method should not reference _get_metadata_invocation_params")


def test_fake_chat_model_with_secrets_class_removed() -> None:
    """The FakeChatModelWithSecrets test class should be removed from test_base.py.

    This class was only used to test the invocation params metadata feature.
    """
    source = TEST_FILE.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name == "FakeChatModelWithSecrets":
                pytest.fail(f"FakeChatModelWithSecrets class should be removed but found at line {node.lineno}")


def test_init_params_tests_removed() -> None:
    """All tests related to init_params in metadata should be removed."""
    source = TEST_FILE.read_text()

    test_names_to_remove = [
        "test_init_params_in_metadata",
        "test_init_params_filter_none_values",
        "test_init_params_filter_secrets",
        "test_runtime_params_in_metadata",
        "test_runtime_secrets_filtered_from_metadata",
        "test_user_metadata_takes_precedence",
        "test_invocation_params_in_metadata_ainvoke",
        "test_invocation_params_in_metadata_stream",
        "test_invocation_params_in_metadata_astream",
    ]

    tree = ast.parse(source)
    found_tests = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name in test_names_to_remove:
                found_tests.append((node.name, node.lineno))

    if found_tests:
        test_list = ", ".join([f"{name} (line {line})" for name, line in found_tests])
        pytest.fail(f"Tests should be removed but found: {test_list}")


# =============================================================================
# Behavioral test: Verify actual runtime behavior
# =============================================================================


def test_invocation_params_not_in_run_metadata() -> None:
    """Behavioral test: Invocation params should NOT appear in run metadata.

    This test creates a fake model and verifies that its identifying params
    (which would have been included via _get_metadata_invocation_params)
    do NOT appear in the run metadata after the revert.
    """
    # Import after setting up path
    sys.path.insert(0, str(CORE_DIR))

    from langchain_core.callbacks.manager import CallbackManagerForLLMRun
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage, BaseMessage
    from langchain_core.outputs import ChatGeneration, ChatResult
    from langchain_core.tracers.context import collect_runs

    class SimpleFakeModel(BaseChatModel):
        """Simple fake model with identifying params."""

        model: str = "test-model"
        temperature: float = 0.7

        @property
        def _identifying_params(self) -> dict[str, Any]:
            return {
                "model": self.model,
                "temperature": self.temperature,
            }

        @property
        def _llm_type(self) -> str:
            return "simple-fake"

        def _generate(
            self,
            messages: list[BaseMessage],
            stop: list[str] | None = None,
            run_manager: CallbackManagerForLLMRun | None = None,
            **kwargs: Any,
        ) -> ChatResult:
            return ChatResult(
                generations=[ChatGeneration(message=AIMessage(content="test"))]
            )

    # Create model with specific params
    llm = SimpleFakeModel(model="my-test-model", temperature=0.5)

    # Collect runs to check metadata
    with collect_runs() as cb:
        llm.invoke("hello")

    assert len(cb.traced_runs) == 1
    run = cb.traced_runs[0]
    assert run.extra is not None
    metadata = run.extra.get("metadata", {})

    # These params should NOT be in metadata after the revert
    assert "model" not in metadata, f"model should not be in metadata but found: {metadata}"
    assert "temperature" not in metadata, f"temperature should not be in metadata but found: {metadata}"


# =============================================================================
# Pass-to-pass tests: Repo CI/CD tests that should pass before and after
# =============================================================================


def test_repo_unit_tests_pass() -> None:
    """Repo's unit tests for chat_models pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/language_models/chat_models/test_base.py", "-v", "--tb=short"],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_chat_models_tests_pass() -> None:
    """Repo's unit tests for chat_models (excluding cache tests) pass (pass_to_pass)."""
    # Run chat_models tests excluding test_cache.py which has unrelated failures
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/language_models/chat_models/", "--ignore=tests/unit_tests/language_models/chat_models/test_cache.py", "-v", "--tb=short"],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Chat models tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_ruff_lint_package() -> None:
    """Repo's ruff linter passes on package code (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--group", "lint", "ruff", "check", "langchain_core/language_models/"],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Ruff lint failed on package:\n{r.stderr[-500:]}"


def test_repo_ruff_lint_tests() -> None:
    """Repo's ruff linter passes on test code (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--group", "lint", "ruff", "check", "tests/unit_tests/language_models/chat_models/"],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Ruff lint failed on tests:\n{r.stderr[-500:]}"


def test_repo_mypy_typecheck() -> None:
    """Repo's mypy type checking passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "--group", "typing", "mypy", "langchain_core/language_models/chat_models.py", "--cache-dir", ".mypy_cache"],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"MyPy type check failed:\n{r.stderr[-500:]}"


def test_repo_syntax_check() -> None:
    """Verify Python syntax is valid in modified files."""
    for file in [CHAT_MODELS_FILE, TEST_FILE]:
        source = file.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {file}: {e}")


def test_import_langchain_core() -> None:
    """langchain_core imports work correctly."""
    sys.path.insert(0, str(CORE_DIR))

    try:
        from langchain_core.language_models.chat_models import BaseChatModel
        assert BaseChatModel is not None
    except ImportError as e:
        pytest.fail(f"Failed to import BaseChatModel: {e}")
