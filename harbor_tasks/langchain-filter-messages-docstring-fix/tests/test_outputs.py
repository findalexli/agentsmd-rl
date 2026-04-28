"""Tests for filter_messages docstring fix.

This test suite verifies that the docstring example for filter_messages
uses the correct parameter names that match the actual function signature.
"""

import ast
import json
import textwrap
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


def test_docstring_example_runs():
    """The docstring example for filter_messages must execute without TypeError.

    This test extracts the example code from the filter_messages docstring
    and runs it. If the example uses incorrect parameter names, it will
    raise TypeError.

    Fail-to-pass: Base commit docstring has incorrect parameter names.
    Pass-to-pass: Fixed docstring example runs successfully.
    """
    docstring = get_filter_messages_docstring()

    # Find the first python code block containing a filter_messages call
    blocks = re.findall(r"```python\s*\n(.*?)```", docstring, re.DOTALL)
    example_code = None
    for block in blocks:
        if "filter_messages(" in block:
            example_code = block
            break

    assert example_code is not None, (
        "Could not find a code example calling filter_messages in the docstring"
    )

    # Build a script that imports and runs the example
    script = f'''
import sys
sys.path.insert(0, "{REPO / "libs" / "core"}")

from langchain_core.messages import filter_messages, SystemMessage, HumanMessage, AIMessage

{textwrap.dedent(example_code)}
print("DOCSTRING_EXAMPLE_OK")
'''

    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )

    assert result.returncode == 0, (
        f"Docstring example failed to run. This usually means the example uses "
        f"parameter names that don't match the function signature.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    assert "TypeError" not in result.stderr, (
        f"Docstring example raised TypeError:\n{result.stderr}"
    )
    assert "unexpected keyword argument" not in result.stderr, (
        f"Docstring example raised unexpected keyword argument:\n{result.stderr}"
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


def test_docstring_example_filtered_output():
    """Fail-to-pass: The docstring example must produce correct filtered output.

    Extracts the keyword argument names from the docstring's filter_messages
    example call, then runs filter_messages with those same kwargs against
    the example's messages. Verifies the returned list has 2 messages
    (SystemMessage + HumanMessage id='foo'; AIMessage id='bar' excluded).

    On base: docstring has incl_names/incl_types/excl_ids → TypeError → fails.
    On gold: docstring has include_names/include_types/exclude_ids → passes
    with correct 2-message output.
    """
    docstring = get_filter_messages_docstring()
    blocks = re.findall(r"```python\s*\n(.*?)```", docstring, re.DOTALL)
    example_code = None
    for block in blocks:
        if "filter_messages(" in block:
            example_code = block
            break
    assert example_code is not None, (
        "Could not find a code example calling filter_messages in the docstring"
    )

    # Parse the example to extract kwarg names and values from the
    # filter_messages() call, then build a call using the exact kwargs
    tree = ast.parse(textwrap.dedent(example_code))
    kwargs = {}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "filter_messages"):
            for kw in node.keywords:
                if kw.arg:
                    kwargs[kw.arg] = ast.unparse(kw.value)
            break

    assert kwargs, "Could not extract kwargs from filter_messages call in docstring example"

    kw_lines = ",\n".join(f"    {name}={value}" for name, value in kwargs.items())

    script = f'''
import sys, json
sys.path.insert(0, "{REPO / "libs" / "core"}")
from langchain_core.messages import filter_messages, SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage("you're a good assistant."),
    HumanMessage("what's your name", id="foo", name="example_user"),
    AIMessage("steve-o", id="bar", name="example_assistant"),
    HumanMessage("what's your favorite color", id="baz"),
    AIMessage("silicon blue", id="blah"),
]

result = filter_messages(
    messages,
{kw_lines}
)

_ids = sorted(
    getattr(m, "id", None) for m in result
    if getattr(m, "id", None) is not None
)
_count = len(result)
print(json.dumps({{"count": _count, "ids": _ids}}))
'''

    r = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )

    if r.returncode != 0:
        has_type_error = (
            "TypeError" in r.stderr
            and "unexpected keyword argument" in r.stderr
        )
        assert not has_type_error, (
            f"filter_messages raised TypeError with these kwargs: {list(kwargs.keys())}. "
            f"The docstring example uses parameter names that don't match "
            f"the function signature.\n"
            f"stderr: {r.stderr}"
        )
        pytest.fail(
            f"Example execution failed for an unexpected reason:\n"
            f"stdout: {r.stdout}\nstderr: {r.stderr}"
        )

    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert data["count"] == 2, (
        f"Expected 2 filtered messages, got {data['count']}: {data}"
    )
    assert "foo" in data["ids"], (
        f"Expected message id 'foo' in result, got ids: {data['ids']}"
    )
    assert "bar" not in data["ids"], (
        f"Message id 'bar' should be excluded, got ids: {data['ids']}"
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
