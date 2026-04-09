"""Benchmark tests for Slack resolver org routing.

These tests verify that the Slack view correctly:
1. Imports and calls resolve_org_for_repo
2. Passes resolver_org_id through V0 and V1 conversation paths
3. Handles the case when no repository is selected

Pass-to-Pass (p2p) tests verify that the repo's CI/CD checks pass
on both the base commit and after the fix is applied.
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/openhands")
SLACK_VIEW_PATH = REPO / "enterprise/integrations/slack/slack_view.py"

# CI discovered commands from the repo:
# - make lint (via pre-commit/ruff)
# - poetry check (validate pyproject.toml)
# - pytest tests/unit (unit tests)
# - pytest tests/test_fileops.py (basic file tests)


def test_slack_view_imports_resolve_org_for_repo():
    """Verify that slack_view.py imports the resolve_org_for_repo function."""
    assert SLACK_VIEW_PATH.exists(), f"File not found: {SLACK_VIEW_PATH}"

    code = SLACK_VIEW_PATH.read_text()
    tree = ast.parse(code)

    # Check for the import: from integrations.resolver_org_router import resolve_org_for_repo
    found_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "integrations.resolver_org_router":
                for alias in node.names:
                    if alias.name == "resolve_org_for_repo":
                        found_import = True
                        break

    assert found_import, "slack_view.py must import resolve_org_for_repo from integrations.resolver_org_router"


def test_slack_view_imports_saas_conversation_store():
    """Verify that slack_view.py imports SaasConversationStore."""
    assert SLACK_VIEW_PATH.exists(), f"File not found: {SLACK_VIEW_PATH}"

    code = SLACK_VIEW_PATH.read_text()
    tree = ast.parse(code)

    found_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "storage.saas_conversation_store":
                for alias in node.names:
                    if alias.name == "SaasConversationStore":
                        found_import = True
                        break

    assert found_import, "slack_view.py must import SaasConversationStore"


def test_slack_view_imports_start_conversation():
    """Verify that slack_view.py imports start_conversation instead of create_new_conversation."""
    assert SLACK_VIEW_PATH.exists(), f"File not found: {SLACK_VIEW_PATH}"

    code = SLACK_VIEW_PATH.read_text()
    tree = ast.parse(code)

    found_start_conversation = False
    found_create_new_conversation = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "conversation_service" in node.module:
                for alias in node.names:
                    if alias.name == "start_conversation":
                        found_start_conversation = True
                    if alias.name == "create_new_conversation":
                        found_create_new_conversation = True

    assert found_start_conversation, "slack_view.py must import start_conversation"
    assert not found_create_new_conversation, "slack_view.py should not import create_new_conversation (replaced by start_conversation)"


def test_slack_view_has_resolved_org_id_attribute():
    """Verify that the Slack view sets resolved_org_id as an instance attribute."""
    assert SLACK_VIEW_PATH.exists(), f"File not found: {SLACK_VIEW_PATH}"

    code = SLACK_VIEW_PATH.read_text()

    # Check for self.resolved_org_id assignment
    assert "self.resolved_org_id" in code, "slack_view.py must set self.resolved_org_id attribute"

    # Check that resolve_org_for_repo is called
    assert "resolve_org_for_repo(" in code, "slack_view.py must call resolve_org_for_repo()"


def test_v0_path_uses_saas_conversation_store():
    """Verify that V0 conversation path uses SaasConversationStore.get_resolver_instance."""
    assert SLACK_VIEW_PATH.exists(), f"File not found: {SLACK_VIEW_PATH}"

    code = SLACK_VIEW_PATH.read_text()

    # Check for get_resolver_instance call
    assert "SaasConversationStore.get_resolver_instance" in code, \
        "V0 path must use SaasConversationStore.get_resolver_instance()"

    # Check that resolved_org_id is passed to get_resolver_instance
    # This is typically the third argument
    assert "self.resolved_org_id" in code, \
        "V0 path must pass resolved_org_id to get_resolver_instance"


def test_v0_path_uses_start_conversation():
    """Verify that V0 path calls start_conversation instead of create_new_conversation."""
    assert SLACK_VIEW_PATH.exists(), f"File not found: {SLACK_VIEW_PATH}"

    code = SLACK_VIEW_PATH.read_text()

    # Should call start_conversation
    assert "await start_conversation(" in code, \
        "V0 path must call start_conversation()"

    # Should not call create_new_conversation
    assert "create_new_conversation(" not in code, \
        "V0 path should not call create_new_conversation() (should use start_conversation)"


def test_v0_path_saves_conversation_metadata():
    """Verify that V0 path creates and saves ConversationMetadata."""
    assert SLACK_VIEW_PATH.exists(), f"File not found: {SLACK_VIEW_PATH}"

    code = SLACK_VIEW_PATH.read_text()

    # Check for ConversationMetadata creation
    assert "ConversationMetadata(" in code, \
        "V0 path must create ConversationMetadata object"

    # Check that metadata is saved
    assert "store.save_metadata" in code, \
        "V0 path must call store.save_metadata()"


def test_v1_path_passes_resolver_org_id_to_context():
    """Verify that V1 path passes resolver_org_id to ResolverUserContext."""
    assert SLACK_VIEW_PATH.exists(), f"File not found: {SLACK_VIEW_PATH}"

    code = SLACK_VIEW_PATH.read_text()

    # Check that ResolverUserContext is instantiated with resolver_org_id
    # This requires looking for the pattern: ResolverUserContext(..., resolver_org_id=...)
    assert "resolver_org_id=self.resolved_org_id" in code or \
           "resolver_org_id=resolved_org_id" in code or \
           "ResolverUserContext(" in code and "resolver_org_id" in code, \
        "V1 path must pass resolver_org_id to ResolverUserContext"


def test_v1_path_uses_resolved_git_provider():
    """Verify that V1 path uses self._resolved_git_provider instead of computing git_provider locally."""
    assert SLACK_VIEW_PATH.exists(), f"File not found: {SLACK_VIEW_PATH}"

    code = SLACK_VIEW_PATH.read_text()

    # Check for usage of _resolved_git_provider
    assert "self._resolved_git_provider" in code, \
        "V1 path should use self._resolved_git_provider (set in create_or_update_conversation)"


def test_git_provider_resolved_early():
    """Verify that git provider is resolved early in create_or_update_conversation."""
    assert SLACK_VIEW_PATH.exists(), f"File not found: {SLACK_VIEW_PATH}"

    code = SLACK_VIEW_PATH.read_text()

    # Check for early resolution of git provider
    assert "_resolved_git_provider" in code, \
        "slack_view.py should have _resolved_git_provider attribute for early git provider resolution"


def test_enterprise_unit_tests_pass():
    """Run the enterprise unit tests for the slack view."""
    # First check if the test file exists (it will only exist after the PR)
    test_file = REPO / "enterprise/tests/unit/test_slack_view.py"

    if not test_file.exists():
        pytest.skip("test_slack_view.py doesn't exist at base commit (added by PR)")

    # Run the unit tests
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Enterprise unit tests failed:\n{result.stdout}\n{result.stderr}"


# ============================================================
# PASS-TO-PASS TESTS - Repo CI/CD checks
# These tests verify the repo's CI/CD pipeline passes on both
# the base commit and after the gold fix is applied.
# ============================================================


def test_repo_poetry_check():
    """Repo's poetry configuration is valid (pass_to_pass)."""
    r = subprocess.run(
        ["poetry", "check"],
        capture_output=True, text=True, cwd=REPO, timeout=60
    )
    # Poetry check returns warnings but should have returncode 0
    # Warnings are acceptable, errors are not
    if r.returncode != 0:
        # Check if it's just warnings (contains "Warning:") vs actual errors
        if "Error:" in r.stderr or "Error:" in r.stdout:
            assert False, f"Poetry check failed with errors:\n{r.stderr}\n{r.stdout}"


def test_repo_syntax_valid():
    """Key Python files have valid syntax (pass_to_pass)."""
    key_files = [
        REPO / "enterprise/integrations/slack/slack_view.py",
        REPO / "openhands/core/config/agent_config.py",
        REPO / "openhands/server/services/conversation_service.py",
    ]

    for filepath in key_files:
        if not filepath.exists():
            continue
        code = filepath.read_text()
        try:
            ast.parse(code)
        except SyntaxError as e:
            assert False, f"Syntax error in {filepath}: {e}"


def test_repo_imports_resolve():
    """Key imports can be resolved after package installation (pass_to_pass)."""
    # Install the package in editable mode
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", ".", "-q"],
        capture_output=True, text=True, cwd=REPO, timeout=180
    )
    assert r.returncode == 0, f"pip install failed: {r.stderr[-500:]}"

    # Test that key imports work
    test_imports = [
        "from openhands.server.services.conversation_service import start_conversation",
        "from openhands.storage.data_models.conversation_metadata import ConversationMetadata",
        "from openhands.utils.conversation_summary import get_default_conversation_title",
    ]

    for import_stmt in test_imports:
        r = subprocess.run(
            [sys.executable, "-c", import_stmt],
            capture_output=True, text=True, cwd=REPO, timeout=30
        )
        assert r.returncode == 0, f"Import failed: {import_stmt}\n{r.stderr}"


def test_repo_unit_tests_basic():
    """Basic unit tests pass (pass_to_pass)."""
    # Install the package and pytest
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", ".", "-q"],
        capture_output=True, text=True, cwd=REPO, timeout=180
    )
    if r.returncode != 0:
        pytest.skip(f"Could not install package: {r.stderr}")

    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio", "-q"],
        capture_output=True, text=True, timeout=60
    )
    if r.returncode != 0:
        pytest.skip("Could not install pytest")

    # Run a simple test file that should always pass
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_fileops.py", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=REPO, timeout=120
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
