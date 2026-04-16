"""Test suite for the openrouter SDK API update task.

This tests that the langchain-openrouter package correctly imports and uses
the new openrouter SDK (v0.8.0+) class names (ChatXxxMessage) instead of
the old names (XxxMessage / ToolResponseMessage).
"""

import subprocess
import sys
from pathlib import Path

# Path to the openrouter package
REPO = Path("/workspace/langchain/libs/partners/openrouter")
PACKAGE_DIR = REPO / "langchain_openrouter"


def test_import_chat_models():
    """Test that chat_models module can be imported without ImportError.

    This is a fail-to-pass test: before the fix, the import fails because
    the old SDK class names don't exist in openrouter>=0.8.0.
    """
    code = """
# This import will fail before the fix due to missing components.*Message classes
from langchain_openrouter.chat_models import ChatOpenRouter, _wrap_messages_for_sdk
print("Import successful")
"""
    result = subprocess.run(
        ["uv", "run", "--group", "test", "python", "-c", code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Import failed:\n{result.stderr}"
    assert "Import successful" in result.stdout


def test_wrap_messages_with_file_blocks():
    """Test that _wrap_messages_for_sdk uses new ChatXxxMessage types for file content.

    This is a fail-to-pass test: before the fix, this will fail because
    the function tries to use the old class names which don't exist.
    The function only wraps messages when file content blocks are present.
    """
    code = '''
from langchain_openrouter.chat_models import _wrap_messages_for_sdk
from openrouter import components

# Messages with file content blocks - this triggers the SDK wrapping
msgs = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Please analyze this file"},
            {"type": "file", "file": {"file_data": "https://example.com/a.pdf"}},
        ],
    }
]

result = _wrap_messages_for_sdk(msgs)
assert len(result) == 1
assert isinstance(result[0], components.ChatUserMessage), f"Expected ChatUserMessage, got {type(result[0])}"

# Test system message with file blocks
msgs = [
    {
        "role": "system",
        "content": [{"type": "text", "text": "System instruction"}],
    },
    {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "Response"},
            {"type": "file", "file": {"file_data": "https://example.com/doc.pdf"}},
        ],
    },
]

result = _wrap_messages_for_sdk(msgs)
assert len(result) == 2
assert isinstance(result[0], components.ChatSystemMessage), f"Expected ChatSystemMessage, got {type(result[0])}"
assert isinstance(result[1], components.ChatAssistantMessage), f"Expected ChatAssistantMessage, got {type(result[1])}"

print("File block wrapping test passed")
'''
    result = subprocess.run(
        ["uv", "run", "--group", "test", "python", "-c", code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "File block wrapping test passed" in result.stdout


def test_wrap_messages_developer_and_tool():
    """Test wrapping developer and tool messages with file content blocks."""
    code = '''
from langchain_openrouter.chat_models import _wrap_messages_for_sdk
from openrouter import components

# Test developer message with file blocks
msgs = [
    {
        "role": "developer",
        "content": [
            {"type": "text", "text": "Dev instructions"},
            {"type": "file", "file": {"file_data": "data:text/plain;base64,SGVsbG8="}},
        ],
    }
]

result = _wrap_messages_for_sdk(msgs)
assert len(result) == 1
assert isinstance(result[0], components.ChatDeveloperMessage), f"Expected ChatDeveloperMessage, got {type(result[0])}"

# Test tool message with file block (required to trigger SDK wrapping)
msgs = [
    {
        "role": "tool",
        "content": [
            {"type": "text", "text": "Tool result"},
            {"type": "file", "file": {"file_data": "data:text/plain;base64,SGVsbG8="}},
        ],
        "tool_call_id": "call_1",
    }
]

result = _wrap_messages_for_sdk(msgs)
assert len(result) == 1
assert isinstance(result[0], components.ChatToolMessage), f"Expected ChatToolMessage, got {type(result[0])}"

print("Developer and tool messages test passed")
'''
    result = subprocess.run(
        ["uv", "run", "--group", "test", "python", "-c", code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "Developer and tool messages test passed" in result.stdout


def test_unit_tests_pass():
    """Run the repo's unit tests for the openrouter package (pass-to-pass).

    These tests should pass both before and after the fix - they verify
    the general functionality of the package.
    """
    result = subprocess.run(
        ["uv", "run", "--group", "test", "pytest", "tests/unit_tests/test_chat_models.py", "-v", "--tb=short", "-x"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-2000:]}"


def test_repo_lint_package():
    """Repo's package linting passes (pass_to_pass).

    Runs ruff check, ruff format check, and mypy on the package code.
    """
    result = subprocess.run(
        ["make", "lint_package"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Package lint failed:\n{result.stderr[-1000:]}"


def test_repo_lint_tests():
    """Repo's test linting passes (pass_to_pass).

    Runs ruff check, ruff format check, and mypy on the test code.
    """
    result = subprocess.run(
        ["make", "lint_tests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Test lint failed:\n{result.stderr[-1000:]}"


def test_repo_type_check():
    """Repo's type checking passes (pass_to_pass).

    Runs mypy on all Python files in the repo.
    """
    result = subprocess.run(
        ["make", "type"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Type check failed:\n{result.stderr[-1000:]}"


def test_repo_all_unit_tests():
    """All repo unit tests pass (pass_to_pass).

    Runs the full unit test suite with socket disabled (no network).
    """
    result = subprocess.run(
        ["make", "test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"All unit tests failed:\n{result.stderr[-2000:]}"


def test_import_structure():
    """Verify the public API exports ChatOpenRouter correctly."""
    code = '''
from langchain_openrouter import ChatOpenRouter

# Verify it's a class
assert isinstance(ChatOpenRouter, type)
print("Import structure test passed")
'''
    result = subprocess.run(
        ["uv", "run", "--group", "test", "python", "-c", code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stderr}"


def test_no_old_imports_remain():
    """Verify no old SDK class names remain in the source code.

    This is a structural test that verifies the fix was applied completely.
    """
    chat_models_file = PACKAGE_DIR / "chat_models.py"
    content = chat_models_file.read_text()

    # These old class names should not appear (unless in comments)
    old_names = [
        "components.UserMessage",
        "components.SystemMessage",
        "components.AssistantMessage",
        "components.ToolResponseMessage",
        "components.DeveloperMessage",
    ]

    for name in old_names:
        assert name not in content, f"Old import {name} still found in source code"

    # The new names should be present
    new_names = [
        "components.ChatUserMessage",
        "components.ChatSystemMessage",
        "components.ChatAssistantMessage",
        "components.ChatToolMessage",
        "components.ChatDeveloperMessage",
    ]

    for name in new_names:
        assert name in content, f"New import {name} not found in source code"

    print("Import verification passed")
