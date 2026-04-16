"""Tests for Linear resolver org routing functionality.

This validates that the LinearNewConversationView correctly routes conversations
to claimed organization workspaces based on repository ownership.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Path to the OpenHands repo
REPO = Path("/workspace/OpenHands")
TARGET_FILE = REPO / "enterprise" / "integrations" / "linear" / "linear_view.py"


class TestLinearViewImports:
    """Test that necessary imports are present for org routing."""

    def test_resolve_org_for_repo_imported(self):
        """resolve_org_for_repo must be imported for org routing."""
        source = TARGET_FILE.read_text()
        assert "from integrations.resolver_org_router import resolve_org_for_repo" in source, \
            "resolve_org_for_repo import missing - needed for org routing"

    def test_saas_conversation_store_imported(self):
        """SaasConversationStore must be imported for resolver instance creation."""
        source = TARGET_FILE.read_text()
        assert "from storage.saas_conversation_store import SaasConversationStore" in source, \
            "SaasConversationStore import missing - needed for resolver routing"

    def test_provider_handler_imported(self):
        """ProviderHandler must be imported for git provider resolution."""
        source = TARGET_FILE.read_text()
        assert "from openhands.integrations.provider import ProviderHandler" in source, \
            "ProviderHandler import missing - needed for git provider resolution"

    def test_uuid_imported(self):
        """uuid4 must be imported for conversation ID generation."""
        source = TARGET_FILE.read_text()
        assert "from uuid import uuid4" in source, \
            "uuid4 import missing - needed for conversation ID generation"

    def test_conversation_metadata_imported(self):
        """ConversationMetadata must be imported."""
        source = TARGET_FILE.read_text()
        assert "ConversationMetadata" in source, \
            "ConversationMetadata import missing - needed for metadata creation"

    def test_get_default_conversation_title_imported(self):
        """get_default_conversation_title must be imported."""
        source = TARGET_FILE.read_text()
        assert "from openhands.utils.conversation_summary import get_default_conversation_title" in source, \
            "get_default_conversation_title import missing"

    def test_start_conversation_imported(self):
        """start_conversation must be imported (replacing create_new_conversation)."""
        source = TARGET_FILE.read_text()
        assert "from openhands.server.services.conversation_service import" in source and \
               "start_conversation" in source, \
            "start_conversation must be imported from conversation_service"


class TestLinearViewRoutingLogic:
    """Test that org routing logic is correctly implemented."""

    def test_provider_handler_verify_repo_provider_called(self):
        """ProviderHandler.verify_repo_provider must be called to resolve git provider."""
        source = TARGET_FILE.read_text()
        assert "provider_handler.verify_repo_provider" in source, \
            "verify_repo_provider call missing - needed to resolve git provider from repo"

    def test_resolve_org_for_repo_called(self):
        """resolve_org_for_repo must be called with correct parameters."""
        source = TARGET_FILE.read_text()
        assert "await resolve_org_for_repo(" in source, \
            "resolve_org_for_repo call missing - this is the core org routing logic"

    def test_resolve_org_for_repo_params(self):
        """resolve_org_for_repo must be called with provider, full_repo_name, keycloak_user_id."""
        source = TARGET_FILE.read_text()
        # Check for the three key parameters
        assert "provider=" in source or "resolved_git_provider.value" in source, \
            "provider parameter missing in resolve_org_for_repo call"
        assert "full_repo_name=" in source or "self.selected_repo" in source, \
            "full_repo_name parameter missing in resolve_org_for_repo call"
        assert "keycloak_user_id=" in source or "user_id" in source, \
            "keycloak_user_id parameter missing in resolve_org_for_repo call"

    def test_get_resolver_instance_called(self):
        """SaasConversationStore.get_resolver_instance must be called with resolver_org_id."""
        source = TARGET_FILE.read_text()
        assert "SaasConversationStore.get_resolver_instance" in source, \
            "get_resolver_instance call missing - needed for org-aware conversation store"

    def test_get_resolver_instance_params(self):
        """get_resolver_instance must receive user_id and resolved_org_id."""
        source = TARGET_FILE.read_text()
        assert "resolved_org_id" in source, \
            "resolved_org_id must be passed to get_resolver_instance"

    def test_start_conversation_called(self):
        """start_conversation must be called instead of create_new_conversation."""
        source = TARGET_FILE.read_text()
        # Check that start_conversation is called
        assert "await start_conversation(" in source, \
            "start_conversation call missing - must be used instead of create_new_conversation"

    def test_conversation_id_generation(self):
        """conversation_id must be generated using uuid4."""
        source = TARGET_FILE.read_text()
        assert "uuid4().hex" in source, \
            "uuid4().hex must be used to generate conversation_id"

    def test_conversation_metadata_created(self):
        """ConversationMetadata must be created with proper trigger and git_provider."""
        source = TARGET_FILE.read_text()
        assert "ConversationMetadata(" in source, \
            "ConversationMetadata must be instantiated"
        assert "trigger=ConversationTrigger.LINEAR" in source, \
            "ConversationTrigger.LINEAR must be set in metadata"

    def test_save_metadata_called(self):
        """store.save_metadata must be called to persist conversation metadata."""
        source = TARGET_FILE.read_text()
        assert "store.save_metadata(" in source or "await store.save_metadata(" in source, \
            "save_metadata call missing - needed to persist conversation metadata"


class TestLinearViewErrorHandling:
    """Test error handling for org routing."""

    def test_verify_repo_provider_exception_handled(self):
        """Exceptions from verify_repo_provider must be caught and logged."""
        source = TARGET_FILE.read_text()
        # Look for try/except around verify_repo_provider
        tree = ast.parse(source)

        def has_exception_handling_for_verify_repo_provider(node):
            """Check if there's try/except with logging for verify_repo_provider."""
            if isinstance(node, ast.Try):
                # Check if the try block contains verify_repo_provider
                for stmt in node.body:
                    stmt_src = ast.unparse(stmt) if hasattr(ast, 'unparse') else ""
                    if "verify_repo_provider" in stmt_src:
                        # Check if there's except block with logger
                        for handler in node.handlers:
                            handler_src = ast.unparse(handler) if hasattr(ast, 'unparse') else ""
                            if "logger" in handler_src or "warning" in handler_src:
                                return True
                # Check for generic exception handling that would catch verify_repo_provider errors
                for handler in node.handlers:
                    if handler.type is None or (isinstance(handler.type, ast.Name) and handler.type.id == 'Exception'):
                        handler_src = ast.unparse(handler) if hasattr(ast, 'unparse') else ""
                        if "logger" in handler_src:
                            return True
            return False

        found = any(has_exception_handling_for_verify_repo_provider(node) for node in ast.walk(tree))
        assert found, "Exception handling with logging required around verify_repo_provider"

    def test_resolve_org_failure_handled(self):
        """Exceptions from resolve_org_for_repo must be caught and logged."""
        source = TARGET_FILE.read_text()
        assert "Failed to resolve org" in source, \
            "Warning log for org resolution failure missing"

    def test_fallback_to_personal_workspace(self):
        """When org resolution fails, should fall back to personal workspace (None)."""
        source = TARGET_FILE.read_text()
        # The code should handle resolved_org_id being None gracefully
        # This is tested by the fact that get_resolver_instance is called with resolved_org_id
        # which may be None
        tree = ast.parse(source)

        def check_resolver_instance_call(node):
            """Check that get_resolver_instance receives resolved_org_id which can be None."""
            if isinstance(node, ast.Call):
                func_str = ast.unparse(node.func) if hasattr(ast, 'unparse') else ""
                if "get_resolver_instance" in func_str:
                    return True
            return False

        found = any(check_resolver_instance_call(node) for node in ast.walk(tree))
        assert found, "get_resolver_instance call required for proper fallback behavior"


class TestLinearViewStructure:
    """Test overall structure changes."""

    def test_create_new_conversation_not_used(self):
        """create_new_conversation should not be called (replaced by V0 pattern)."""
        source = TARGET_FILE.read_text()
        # Allow the import (for backward compatibility tests) but not the call
        assert "create_new_conversation(" not in source, \
            "create_new_conversation should not be called - use start_conversation instead"

    def test_import_structure(self):
        """Verify correct imports from conversation_service."""
        source = TARGET_FILE.read_text()
        # Should have start_conversation imported
        assert "start_conversation," in source or "start_conversation\n" in source, \
            "start_conversation must be in imports from conversation_service"


class TestRepoTests:
    """Run the repository's own CI tests for Linear resolver (pass_to_pass)."""

    def test_enterprise_linear_view_unit_tests(self):
        """Enterprise linear view unit tests pass (pass_to_pass)."""
        r = subprocess.run(
            ["poetry", "run", "pytest", "tests/unit/integrations/linear/test_linear_view.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO / "enterprise",
        )
        assert r.returncode == 0, f"Linear view unit tests failed:\n{r.stderr[-1000:]}"

    def test_enterprise_linear_module_tests(self):
        """All Linear module tests pass (pass_to_pass)."""
        r = subprocess.run(
            ["poetry", "run", "pytest", "tests/unit/integrations/linear/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO / "enterprise",
        )
        assert r.returncode == 0, f"Linear module tests failed:\n{r.stderr[-1000:]}"

    def test_enterprise_resolver_org_router_tests(self):
        """Resolver org router tests pass (pass_to_pass)."""
        r = subprocess.run(
            ["poetry", "run", "pytest", "tests/unit/integrations/test_resolver_org_router.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO / "enterprise",
        )
        assert r.returncode == 0, f"Resolver org router tests failed:\n{r.stderr[-1000:]}"

    def test_linear_view_syntax_valid(self):
        """Linear view file has valid Python syntax (pass_to_pass)."""
        r = subprocess.run(
            ["python", "-m", "py_compile", "enterprise/integrations/linear/linear_view.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"

    def test_linear_view_importable(self):
        """Linear view module can be imported (pass_to_pass)."""
        r = subprocess.run(
            ["poetry", "run", "python", "-c", "from integrations.linear.linear_view import LinearNewConversationView; print('Import OK')"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO / "enterprise",
        )
        assert r.returncode == 0, f"Import check failed:\n{r.stderr[-500:]}"

    def test_enterprise_linear_view_tests_exist(self):
        """The repo should have unit tests for linear view (static check)."""
        test_file = REPO / "enterprise" / "tests" / "unit" / "integrations" / "linear" / "test_linear_view.py"
        assert test_file.exists(), f"Test file should exist: {test_file}"

    def test_file_syntax_valid(self):
        """Test that the modified file has valid Python syntax."""
        # Parse the file to check for syntax errors
        source = TARGET_FILE.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            assert False, f"Syntax error in {TARGET_FILE}: {e}"

    def test_key_patterns_present(self):
        """Test that all required implementation patterns are present."""
        source = TARGET_FILE.read_text()

        # Check that the key new patterns are all present
        patterns = [
            ("resolve_org_for_repo import", "from integrations.resolver_org_router import resolve_org_for_repo"),
            ("SaasConversationStore import", "from storage.saas_conversation_store import SaasConversationStore"),
            ("ProviderHandler import", "from openhands.integrations.provider import ProviderHandler"),
            ("uuid4 import", "from uuid import uuid4"),
            ("start_conversation import", "start_conversation"),
            ("verify_repo_provider call", "provider_handler.verify_repo_provider"),
            ("resolve_org_for_repo call", "await resolve_org_for_repo("),
            ("get_resolver_instance call", "SaasConversationStore.get_resolver_instance"),
            ("start_conversation call", "await start_conversation("),
            ("uuid4 generation", "uuid4().hex"),
            ("save_metadata call", "save_metadata"),
        ]

        for name, pattern in patterns:
            assert pattern in source, f"Required pattern '{name}' not found: {pattern}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
