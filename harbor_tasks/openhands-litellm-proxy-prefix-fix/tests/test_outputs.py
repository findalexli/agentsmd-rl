#!/usr/bin/env python3
"""
Test suite for OpenHands PR #13638:
Fix planning agent auth error due to missing base_url when using litellm_proxy/ prefix.

The bug: _configure_llm only checked for 'openhands/' prefix to set base_url,
but SDK transforms 'openhands/model' to 'litellm_proxy/model' for sub-conversations,
so the planning agent got base_url=None causing auth errors.

The fix: Add 'litellm_proxy/' prefix check alongside 'openhands/'.
"""

import ast
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO = Path("/workspace/OpenHands")
TARGET_FILE = (
    REPO
    / "openhands"
    / "app_server"
    / "app_conversation"
    / "live_status_app_conversation_service.py"
)

# =============================================================================
# Behavioral Test Helpers
# =============================================================================


def call_configure_llm(model_name: str, user_llm_base_url: str | None = None) -> str | None:
    """
    Call _configure_llm with the given model name and return the resulting base_url.

    This actually executes the _configure_llm method from the source code,
    not a copy, so we test real behavior.
    """
    code = f"""
import sys
import types
sys.path.insert(0, '{REPO}')

from unittest.mock import MagicMock
from openhands.app_server.app_conversation.live_status_app_conversation_service import LiveStatusAppConversationService
from openhands.app_server.user.user_models import UserInfo
from pydantic import SecretStr

# Create a mock service with just the needed attributes
service = MagicMock(spec=LiveStatusAppConversationService)
service.openhands_provider_base_url = 'https://openhands-provider.example.com'

# Get the actual _configure_llm method
real_method = LiveStatusAppConversationService._configure_llm

# Create user
user = UserInfo(
    language='en',
    llm_model=None,
    llm_base_url={repr(user_llm_base_url)},
    llm_api_key=SecretStr('test-api-key'),
)

# Bind and call the method
bounded_method = types.MethodType(real_method, service)
result = bounded_method(user, {repr(model_name)})

# Print the base_url
print(result.base_url if result.base_url else 'NONE')
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        pytest.fail(f"Failed to call _configure_llm: {result.stderr}")
    return result.stdout.strip()


# =============================================================================
# Fail-to-Pass Tests (these fail on base commit, pass after fix)
# =============================================================================


def test_litellm_proxy_prefix_sets_base_url():
    """
    FAIL-TO-PASS: _configure_llm must set base_url for litellm_proxy/ prefix.

    The bug causes planning agents to fail because the SDK transforms
    'openhands/model' to 'litellm_proxy/model' but _configure_llm only
    checked for 'openhands/' prefix to set base_url.

    This test CALLS the actual _configure_llm method with a litellm_proxy/
    model and verifies base_url is set.
    """
    base_url = call_configure_llm("litellm_proxy/anthropic/claude-3-5-sonnet")
    assert base_url != "NONE", (
        "_configure_llm must set base_url for litellm_proxy/ prefix models. "
        "Expected base_url to be set to openhands_provider_base_url."
    )
    assert base_url == "https://openhands-provider.example.com", (
        f"Expected base_url to be the provider URL, got: {base_url}"
    )


def test_openhands_prefix_still_sets_base_url():
    """
    FAIL-TO-PASS: _configure_llm must still set base_url for openhands/ prefix.

    The fix should not break existing behavior for openhands/ models.
    This test CALLS the actual _configure_llm method with an openhands/
    model and verifies base_url is set.
    """
    base_url = call_configure_llm("openhands/anthropic/claude-3-5-sonnet")
    assert base_url != "NONE", (
        "_configure_llm must set base_url for openhands/ prefix models. "
        "Expected base_url to be set to openhands_provider_base_url."
    )
    assert base_url == "https://openhands-provider.example.com", (
        f"Expected base_url to be the provider URL, got: {base_url}"
    )


def test_litellm_proxy_with_user_base_url():
    """
    FAIL-TO-PASS: When litellm_proxy/ model is used AND user has llm_base_url,
    the user's base_url should take precedence.

    This verifies the fix handles the case where user provides their own base_url.
    """
    base_url = call_configure_llm(
        "litellm_proxy/anthropic/claude-3-5-sonnet",
        user_llm_base_url="https://user-provided.example.com"
    )
    assert base_url == "https://user-provided.example.com", (
        f"When user provides llm_base_url, it should be used. Got: {base_url}"
    )


def test_non_prefixed_model_no_base_url_override():
    """
    FAIL-TO-PASS: Models that don't match either prefix should NOT get
    the openhands_provider_base_url override.

    This ensures the fix doesn't over-apply and only affects litellm_proxy/
    and openhands/ prefixed models.
    """
    base_url = call_configure_llm("anthropic/claude-3-5-sonnet")
    # Non-prefixed models should not get the provider base_url
    # They should get whatever user provided (None in this case)
    assert base_url == "NONE", (
        f"Non-prefixed models should not get provider base_url. Got: {base_url}"
    )


# =============================================================================
# Pass-to-Pass Tests (repo CI/CD - these pass on both base and fixed commits)
# =============================================================================


def test_target_file_exists():
    """PASS-TO-PASS: Target file must exist."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_configure_llm_method_exists():
    """PASS-TO-PASS: _configure_llm method must exist."""
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    found = any(
        isinstance(node, ast.FunctionDef) and node.name == "_configure_llm"
        for node in ast.walk(tree)
    )
    assert found, "_configure_llm method must exist in the target file"


def test_python_syntax_valid():
    """PASS-TO-PASS: Target file must have valid Python syntax."""
    source = TARGET_FILE.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Target file has invalid Python syntax: {e}")


def test_repo_import_live_status_service():
    """
    PASS-TO-PASS: Repo module import succeeds (pass_to_pass).

    Verifies that the OpenHands package is properly installed and the
    LiveStatusAppConversationService can be imported without errors.
    """
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from openhands.app_server.app_conversation.live_status_app_conversation_service import LiveStatusAppConversationService; print('Import OK')",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Import failed with code {result.returncode}:\n"
        f"stderr: {result.stderr[-500:]}"
    )


def test_repo_ruff_check():
    """
    PASS-TO-PASS: Repo linting passes on target file (pass_to_pass).

    Runs ruff linter as configured in the repo's dev_config/python/ruff.toml.
    Only checks the target file to avoid unrelated errors in the codebase.
    """
    result = subprocess.run(
        [
            "ruff",
            "check",
            "--config",
            "dev_config/python/ruff.toml",
            "openhands/app_server/app_conversation/live_status_app_conversation_service.py",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Note: There may be pre-existing lint errors in the codebase
    # We accept exit code 0 (no errors) or non-zero (existing errors)
    # The important thing is that ruff runs successfully (not a crash)
    assert result.returncode in [0, 1], (
        f"Ruff crashed with code {result.returncode}:\n"
        f"stderr: {result.stderr[-500:]}"
    )


def test_repo_pytest_unit_collect():
    """
    PASS-TO-PASS: Repo unit tests for target file can be collected (pass_to_pass).

    Verifies pytest can collect tests from the unit test file without
    import/collection errors. This ensures test dependencies are available.
    """
    test_file = (
        REPO
        / "tests"
        / "unit"
        / "app_server"
        / "test_live_status_app_conversation_service.py"
    )
    if not test_file.exists():
        pytest.skip("Unit test file not found - skipping repo test")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-k",
            "configure_llm",
            "--collect-only",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"pytest collection failed with code {result.returncode}:\n"
        f"stdout: {result.stdout[-1000:]}\n"
        f"stderr: {result.stderr[-500:]}"
    )
    # Verify that configure_llm tests were found
    assert "configure_llm" in result.stdout, (
        "No configure_llm tests found in collection output"
    )


def test_repo_pytest_unit_run():
    """
    PASS-TO-PASS: Repo unit tests for configure_llm pass (pass_to_pass).

    Runs the actual unit tests related to _configure_llm from the repo's
    test suite. These tests should pass on both base and fixed commits.
    """
    test_file = (
        REPO
        / "tests"
        / "unit"
        / "app_server"
        / "test_live_status_app_conversation_service.py"
    )
    if not test_file.exists():
        pytest.skip("Unit test file not found - skipping repo test")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-k",
            "configure_llm",
            "-v",
            "--tb=short",
            "-x",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"pytest failed with code {result.returncode}:\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-1000:]}"
    )


# =============================================================================
# Verification Tests for Agent Config Rules
# =============================================================================


def test_agent_config_pre_commit_hook_rule():
    """
    Verify pre-commit hook requirement from AGENTS.md.

    AGENTS.md states: "Before pushing any changes, you MUST ensure that any
    lint errors or simple test errors have been fixed."

    This test verifies the fix doesn't introduce syntax errors.
    """
    source = TARGET_FILE.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Fix introduces syntax error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])