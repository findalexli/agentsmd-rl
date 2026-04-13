"""Tests for the conversation routes refactoring.

This validates that the PR reduces sandbox service queries by:
1. Using AppConversationInfoService instead of AppConversationService
2. Calling the service only once per request (not 3 times)
3. Returning AppConversationInfo directly instead of separate is_v1 + get_config calls
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/openhands")
CONVERSATION_PY = REPO / "openhands" / "server" / "routes" / "conversation.py"


# =============================================================================
# Pass-to-Pass Tests (verify repo CI checks pass on both base and fixed code)
# =============================================================================

def test_repo_precommit_lint():
    """Repo's pre-commit lint checks pass (pass_to_pass)."""
    # Install pre-commit first
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pre-commit"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # Run pre-commit (hooks should already be cached from image build)
    r = subprocess.run(
        ["pre-commit", "run", "--all-files", "--show-diff-on-failure",
         "--config", "./dev_config/python/.pre-commit-config.yaml"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_unit_tests_conversation():
    """Repo's unit tests for conversation routes pass (pass_to_pass)."""
    test_file = REPO / "tests" / "unit" / "server" / "routes" / "test_conversation_routes.py"
    if not test_file.exists():
        pytest.skip("Conversation routes test file not found")

    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": ".:" + os.environ.get("PYTHONPATH", "")},
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_unit_tests_app_conversation_service():
    """Repo's unit tests for app conversation service pass (pass_to_pass).

    Tests AppConversationInfoService which is imported in the refactored code.
    """
    test_file = REPO / "tests" / "unit" / "app_server" / "test_sql_app_conversation_info_service.py"
    if not test_file.exists():
        pytest.skip("App conversation info service test file not found")

    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": ".:" + os.environ.get("PYTHONPATH", "")},
    )
    assert r.returncode == 0, f"App conversation service tests failed:\n{r.stderr[-500:]}"


def test_repo_unit_tests_conversation_id_validation():
    """Repo's unit tests for conversation ID validation pass (pass_to_pass)."""
    test_file = REPO / "tests" / "unit" / "server" / "routes" / "test_conversation_id_validation.py"
    if not test_file.exists():
        pytest.skip("Conversation ID validation test file not found")

    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": ".:" + os.environ.get("PYTHONPATH", "")},
    )
    assert r.returncode == 0, f"Conversation ID validation tests failed:\n{r.stderr[-500:]}"


# =============================================================================
# Fail-to-Pass Tests (verify the specific fix is applied correctly)
# =============================================================================


def test_uses_app_conversation_info_service():
    """Verify the code uses AppConversationInfoService, not AppConversationService."""
    content = CONVERSATION_PY.read_text()

    # Should import AppConversationInfoService
    assert "AppConversationInfoService" in content, \
        "Should import AppConversationInfoService"

    # Should NOT import AppConversationService (old implementation)
    assert "AppConversationService" not in content, \
        "Should NOT import AppConversationService (old service causing thrashing)"


def test_has_get_v1_conversation_info_function():
    """Verify the new helper function _get_v1_conversation_info exists."""
    content = CONVERSATION_PY.read_text()

    # Should have the new consolidated function
    assert "_get_v1_conversation_info" in content, \
        "Should have _get_v1_conversation_info function"

    # Should return AppConversationInfo | None
    assert "-> AppConversationInfo | None" in content, \
        "Should return AppConversationInfo | None type"


def test_no_is_v1_conversation_function():
    """Verify the old _is_v1_conversation function is removed."""
    content = CONVERSATION_PY.read_text()

    # Should NOT have the old separate check function
    assert "_is_v1_conversation" not in content, \
        "Should NOT have _is_v1_conversation (caused extra service call)"


def test_no_get_v1_conversation_config_function():
    """Verify the old _get_v1_conversation_config function is removed."""
    content = CONVERSATION_PY.read_text()

    # Should NOT have the old separate getter function
    assert "_get_v1_conversation_config" not in content, \
        "Should NOT have _get_v1_conversation_config (caused extra service call)"


def test_service_called_only_once_per_request():
    """Verify the service is called only once, not 3 times.

    This test analyzes the AST to count service method calls in get_remote_runtime_config.
    """
    content = CONVERSATION_PY.read_text()
    tree = ast.parse(content)

    # Find get_remote_runtime_config function
    target_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "get_remote_runtime_config":
            target_func = node
            break

    assert target_func is not None, "Should find get_remote_runtime_config function"

    # Count calls to any app_conversation method in this function
    method_calls = []
    for node in ast.walk(target_func):
        if isinstance(node, ast.Await):
            # Look for calls like await x.y()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    # Get the full attribute chain
                    if isinstance(child.func, ast.Attribute):
                        attr_chain = []
                        current = child.func
                        while isinstance(current, ast.Attribute):
                            attr_chain.append(current.attr)
                            current = current.value
                        if isinstance(current, ast.Name):
                            attr_chain.append(current.id)
                        full_name = ".".join(reversed(attr_chain))
                        method_calls.append(full_name)

    # Should have at most 1 call to get_app_conversation_info
    info_calls = [c for c in method_calls if "get_app_conversation_info" in c]
    assert len(info_calls) <= 1, \
        f"Should call service at most once, but found {len(info_calls)} calls: {info_calls}"


def test_endpoint_returns_json_response_directly_for_v1():
    """Verify V1 conversations return JSONResponse directly without extra calls."""
    content = CONVERSATION_PY.read_text()

    # In the V1 branch, should return JSONResponse directly
    # Check that after getting v1_conversation_info, we return directly
    lines = content.split('\n')

    # Find the pattern: after getting info, should return JSONResponse directly
    found_return = False
    in_v1_branch = False

    for i, line in enumerate(lines):
        if 'v1_conversation_info = await _get_v1_conversation_info' in line:
            # Check next few lines for the return pattern
            for j in range(i+1, min(i+10, len(lines))):
                if 'if v1_conversation_info:' in lines[j]:
                    in_v1_branch = True
                if in_v1_branch and 'return JSONResponse(' in lines[j]:
                    found_return = True
                    break

    assert found_return, \
        "V1 branch should return JSONResponse directly after getting info (no extra calls)"


def test_imports_app_conversation_info_model():
    """Verify the code imports AppConversationInfo model."""
    content = CONVERSATION_PY.read_text()

    assert "AppConversationInfo" in content, \
        "Should import AppConversationInfo model for return type"


def test_syntax_valid():
    """Verify the Python file is syntactically valid."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(CONVERSATION_PY)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"Syntax error in conversation.py: {result.stderr}"


def test_unit_tests_pass():
    """Run the existing unit tests for conversation routes."""
    # First check if test file exists
    test_file = REPO / "tests" / "unit" / "server" / "routes" / "test_conversation_routes.py"
    if not test_file.exists():
        pytest.skip("Test file not found")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file),
         "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO)
    )

    # Check for specific tests related to our changes
    output = result.stdout + result.stderr

    # Look for the new test functions that should exist after the fix
    new_tests = [
        "test_get_remote_runtime_config_v1_conversation",
        "test_get_remote_runtime_config_v0_conversation",
    ]

    for test_name in new_tests:
        assert test_name in output or result.returncode == 0, \
            f"Test {test_name} should exist and pass"

    assert result.returncode == 0, \
        f"Unit tests failed:\n{output[-1000:]}"
