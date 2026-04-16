"""Tests for filter_messages docstring fix.

This test suite verifies that the docstring example for filter_messages
uses the correct parameter names that match the actual function signature.
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/langchain")
UTILS_PATH = REPO / "libs" / "core" / "langchain_core" / "messages" / "utils.py"


def get_filter_messages_docstring() -> str:
    """Extract the docstring from the filter_messages function."""
    source = UTILS_PATH.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "filter_messages":
            return ast.get_docstring(node) or ""
    return ""


def test_docstring_example_uses_correct_params():
    """The docstring example must use valid parameter names.

    The example in the docstring should use parameter names that actually
    exist in the function signature: include_names, include_types, exclude_ids.

    Fail-to-pass: Base commit has incorrect params (incl_names, incl_types, excl_ids).
    Pass-to-pass: Fixed version has correct params.
    """
    docstring = get_filter_messages_docstring()

    # Check that the old incorrect parameter names are NOT present in docstring example
    bad_patterns = [
        r"incl_names\s*=",
        r"incl_types\s*=",
        r"excl_ids\s*=",
    ]

    for pattern in bad_patterns:
        match = re.search(pattern, docstring)
        assert match is None, (
            f"Docstring example uses incorrect parameter name: {pattern}. "
            f"Use include_names, include_types, exclude_ids instead."
        )

    # Verify the correct parameter names ARE present
    good_patterns = [
        r"include_names\s*=",
        r"include_types\s*=",
        r"exclude_ids\s*=",
    ]

    for pattern in good_patterns:
        match = re.search(pattern, docstring)
        assert match is not None, (
            f"Docstring example missing parameter: {pattern}"
        )


def test_docstring_example_with_correct_params_runs():
    """The correct docstring example should be executable without TypeError.

    Run the example from the docstring with correct parameter names
    and verify it works without raising TypeError.

    Pass-to-pass: Fixed version runs successfully.
    """
    # Create a test script using the CORRECT parameter names
    test_script = f'''
import sys
sys.path.insert(0, "{REPO / "libs" / "core"}")

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages.utils import filter_messages

messages = [
    SystemMessage("example_system", id="foo"),
    HumanMessage("example_user", name="example_user"),
    AIMessage("example_assistant", name="example_assistant"),
]

result = filter_messages(
    messages,
    include_names=("example_user", "example_assistant"),
    include_types=("system",),
    exclude_ids=("bar",),
)
print("Success: filter_messages executed without TypeError")
'''

    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )

    assert result.returncode == 0, (
        f"Docstring example code with correct params failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )


def test_old_params_cause_typeerror():
    """Old parameter names should cause TypeError.

    This test verifies that the old parameter names (incl_names, etc.)
    are actually invalid and would cause an error if used.

    Fail-to-pass: Old params cause TypeError (confirms bug exists).
    Pass-to-pass: N/A (this is a fail-only test, always passes on both).
    """
    # Test with OLD (incorrect) parameter names
    test_script = f'''
import sys
sys.path.insert(0, "{REPO / "libs" / "core"}")

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages.utils import filter_messages

messages = [
    SystemMessage("example_system", id="foo"),
    HumanMessage("example_user", name="example_user"),
    AIMessage("example_assistant", name="example_assistant"),
]

result = filter_messages(
    messages,
    incl_names=("example_user", "example_assistant"),
    incl_types=("system",),
    excl_ids=("bar",),
)
print("Success")
'''

    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )

    # Old params should cause TypeError
    assert result.returncode != 0 and "TypeError" in result.stderr, (
        f"Expected TypeError for old param names, but got:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )


def test_ruff_check():
    """The repo's linter should pass on the modified file.

    Pass-to-pass: Code follows project style guidelines.
    """
    result = subprocess.run(
        ["python", "-m", "ruff", "check", str(UTILS_PATH)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )

    assert result.returncode == 0, (
        f"Ruff linting failed:\n{result.stdout}\n{result.stderr}"
    )


def test_syntax_valid():
    """Modified file must have valid Python syntax.

    Pass-to-pass: Python can parse the file.
    """
    source = UTILS_PATH.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in {UTILS_PATH}: {e}")


def test_repo_filter_messages_unit():
    """Repo's filter_messages unit tests pass (pass_to_pass).

    Runs the specific unit tests for the filter_messages function
    from the langchain-core test suite.
    """
    # Install required test dependencies
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "blockbuster", "pytest-asyncio",
         "responses", "freezegun", "syrupy", "pytest-mock", "pytest-xdist"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    # Install succeeds or is already installed

    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/unit_tests/messages/test_utils.py::test_filter_message",
         "tests/unit_tests/messages/test_utils.py::test_filter_message_exclude_tool_calls",
         "tests/unit_tests/messages/test_utils.py::test_filter_message_exclude_tool_calls_content_blocks",
         "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO / "libs" / "core"),
    )

    assert r.returncode == 0, (
        f"filter_messages unit tests failed:\n"
        f"stdout: {r.stdout[-1000:]}\n"
        f"stderr: {r.stderr[-1000:]}"
    )


def test_repo_messages_utils_unit():
    """Repo's messages utils unit tests pass (pass_to_pass).

    Runs the complete test_utils.py unit tests for the messages module
    to ensure all utility functions work correctly.
    """
    # Install required test dependencies
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "blockbuster", "pytest-asyncio",
         "responses", "freezegun", "syrupy", "pytest-mock", "pytest-xdist"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )

    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/unit_tests/messages/test_utils.py",
         "-x", "--tb=short", "-q"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=str(REPO / "libs" / "core"),
    )

    assert r.returncode == 0, (
        f"messages utils unit tests failed:\n"
        f"stdout: {r.stdout[-1000:]}\n"
        f"stderr: {r.stderr[-1000:]}"
    )


def test_repo_messages_imports():
    """Repo's messages imports test passes (pass_to_pass).

    Verifies that all message module imports work correctly.
    """
    # Install required test dependencies
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "blockbuster", "pytest-asyncio",
         "responses", "freezegun", "syrupy", "pytest-mock", "pytest-xdist"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )

    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/unit_tests/messages/test_imports.py",
         "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO / "libs" / "core"),
    )

    assert r.returncode == 0, (
        f"messages imports test failed:\n"
        f"stdout: {r.stdout[-1000:]}\n"
        f"stderr: {r.stderr[-1000:]}"
    )
