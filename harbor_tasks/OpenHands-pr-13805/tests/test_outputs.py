"""Test outputs for Jira resolver routing task.

This module validates that the Jira resolver conversation routing
has been properly implemented to route conversations to claimed org workspaces.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = Path('/workspace/OpenHands')
JIRA_VIEW_PATH = REPO / 'enterprise' / 'integrations' / 'jira' / 'jira_view.py'
TEST_FILE_PATH = REPO / 'enterprise' / 'tests' / 'unit' / 'integrations' / 'jira' / 'test_jira_view.py'


def get_source_code(path: Path) -> str:
    """Read source code from file."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text()


def parse_ast(path: Path) -> ast.AST:
    """Parse Python file into AST."""
    source = get_source_code(path)
    return ast.parse(source)


# =============================================================================
# Fail-to-Pass Tests (verify fix was applied)
# =============================================================================


def test_imports_resolve_org_router():
    """FAIL-TO-PASS: jira_view.py imports resolve_org_for_repo from resolver_org_router."""
    tree = parse_ast(JIRA_VIEW_PATH)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == 'integrations.resolver_org_router':
                for alias in node.names:
                    if alias.name == 'resolve_org_for_repo':
                        return True

    raise AssertionError(
        "jira_view.py must import 'resolve_org_for_repo' from 'integrations.resolver_org_router'"
    )


def test_imports_saas_conversation_store():
    """FAIL-TO-PASS: jira_view.py imports SaasConversationStore."""
    tree = parse_ast(JIRA_VIEW_PATH)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == 'storage.saas_conversation_store':
                for alias in ast.walk(node):
                    if isinstance(alias, ast.alias) and alias.name == 'SaasConversationStore':
                        return True

    raise AssertionError(
        "jira_view.py must import 'SaasConversationStore' from 'storage.saas_conversation_store'"
    )


def test_imports_conversation_metadata():
    """FAIL-TO-PASS: jira_view.py imports ConversationMetadata class."""
    tree = parse_ast(JIRA_VIEW_PATH)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if 'conversation_metadata' in str(node.module):
                for alias in node.names:
                    if alias.name == 'ConversationMetadata':
                        return True

    raise AssertionError(
        "jira_view.py must import 'ConversationMetadata' from conversation_metadata module"
    )


def test_uses_start_conversation_not_create_new():
    """FAIL-TO-PASS: create_or_update_conversation uses start_conversation instead of create_new_conversation."""
    tree = parse_ast(JIRA_VIEW_PATH)

    # Check that start_conversation is imported
    has_start_conversation_import = False
    has_create_new_conversation_import = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if 'conversation_service' in str(node.module):
                for alias in node.names:
                    if alias.name == 'start_conversation':
                        has_start_conversation_import = True
                    if alias.name == 'create_new_conversation':
                        has_create_new_conversation_import = True

    # The fix should import start_conversation, not create_new_conversation
    if not has_start_conversation_import:
        raise AssertionError(
            "jira_view.py must import 'start_conversation' from conversation_service"
        )

    if has_create_new_conversation_import:
        raise AssertionError(
            "jira_view.py should NOT import 'create_new_conversation' (replaced by start_conversation)"
        )


def test_calls_resolve_org_for_repo():
    """FAIL-TO-PASS: Code calls resolve_org_for_repo with correct parameters."""
    tree = parse_ast(JIRA_VIEW_PATH)
    source = get_source_code(JIRA_VIEW_PATH)

    # Check that resolve_org_for_repo is called
    has_resolve_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'resolve_org_for_repo':
                has_resolve_call = True
                break
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'resolve_org_for_repo':
                has_resolve_call = True
                break

    if not has_resolve_call:
        raise AssertionError(
            "jira_view.py must call 'resolve_org_for_repo' in create_or_update_conversation"
        )


def test_calls_get_resolver_instance():
    """FAIL-TO-PASS: Code calls SaasConversationStore.get_resolver_instance."""
    tree = parse_ast(JIRA_VIEW_PATH)

    has_get_resolver_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == 'get_resolver_instance':
                    has_get_resolver_call = True
                    break

    if not has_get_resolver_call:
        raise AssertionError(
            "jira_view.py must call 'SaasConversationStore.get_resolver_instance'"
        )


def test_creates_conversation_metadata():
    """FAIL-TO-PASS: Code creates ConversationMetadata with git_provider field."""
    tree = parse_ast(JIRA_VIEW_PATH)

    has_conversation_metadata_call = False
    has_git_provider_kwarg = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'ConversationMetadata':
                has_conversation_metadata_call = True
                # Check for git_provider keyword
                for keyword in node.keywords:
                    if keyword.arg == 'git_provider':
                        has_git_provider_kwarg = True
                break

    if not has_conversation_metadata_call:
        raise AssertionError(
            "jira_view.py must create a 'ConversationMetadata' instance"
        )

    if not has_git_provider_kwarg:
        raise AssertionError(
            "ConversationMetadata must include 'git_provider' field"
        )


def test_generates_uuid_conversation_id():
    """FAIL-TO-PASS: Code generates conversation_id using uuid4().hex."""
    source = get_source_code(JIRA_VIEW_PATH)

    # Check for uuid4 import
    if 'from uuid import uuid4' not in source and 'import uuid' not in source:
        raise AssertionError("jira_view.py must import uuid4 to generate conversation IDs")

    # Check for uuid4().hex usage
    if 'uuid4().hex' not in source:
        raise AssertionError("jira_view.py must use 'uuid4().hex' to generate conversation_id")


def test_calls_start_conversation():
    """FAIL-TO-PASS: Code calls start_conversation (not create_new_conversation)."""
    tree = parse_ast(JIRA_VIEW_PATH)

    has_start_conversation_call = False
    has_create_new_conversation_call = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name == 'start_conversation':
                has_start_conversation_call = True
            if func_name == 'create_new_conversation':
                has_create_new_conversation_call = True

    if not has_start_conversation_call:
        raise AssertionError(
            "jira_view.py must call 'start_conversation' function"
        )

    if has_create_new_conversation_call:
        raise AssertionError(
            "jira_view.py should NOT call 'create_new_conversation' (replaced by start_conversation)"
        )


# =============================================================================
# Pass-to-Pass Tests (repo's own tests)
# =============================================================================


def test_repo_lint_jira_view():
    """PASS-TO-PASS: Modified jira_view.py passes ruff lint check.

    Runs ruff check on the modified file to ensure it follows the repo's
    code style and has no syntax errors.
    """
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    r = subprocess.run(
        ["ruff", "check", "--select", "E9", str(JIRA_VIEW_PATH)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr}\n{r.stdout}"


def test_repo_syntax_jira_view():
    """PASS-TO-PASS: Modified jira_view.py has valid Python syntax.

    Uses py_compile to verify the file has no syntax errors.
    """
    r = subprocess.run(
        ["python", "-m", "py_compile", str(JIRA_VIEW_PATH)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


def test_test_file_has_routing_tests():
    """PASS-TO-PASS: Test file contains routing-specific tests."""
    if not TEST_FILE_PATH.exists():
        raise AssertionError(f"Test file not found: {TEST_FILE_PATH}")

    source = get_source_code(TEST_FILE_PATH)

    # Check for the new test class
    if 'TestJiraV0ConversationRouting' not in source:
        raise AssertionError(
            "test_jira_view.py must contain 'TestJiraV0ConversationRouting' test class"
        )

    # Check for routing test methods
    required_tests = [
        'test_routes_to_claimed_org_when_user_is_member',
        'test_falls_back_to_personal_workspace_when_no_claim',
    ]

    for test_name in required_tests:
        if f'def {test_name}' not in source:
            raise AssertionError(
                f"test_jira_view.py must contain test method '{test_name}'"
            )


def test_test_file_imports_provider_type():
    """PASS-TO-PASS: Test file imports ProviderType for routing tests."""
    tree = parse_ast(TEST_FILE_PATH)

    has_provider_type_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if 'service_types' in str(node.module):
                for alias in node.names:
                    if alias.name == 'ProviderType':
                        has_provider_type_import = True
                        break

    if not has_provider_type_import:
        raise AssertionError(
            "test_jira_view.py must import 'ProviderType' from service_types"
        )


def test_test_file_uses_async_mocks():
    """PASS-TO-PASS: Test file patches new dependencies with AsyncMock."""
    tree = parse_ast(TEST_FILE_PATH)

    source = get_source_code(TEST_FILE_PATH)

    # Check for resolve_org_for_repo patch
    if 'resolve_org_for_repo' not in source:
        raise AssertionError(
            "Tests must patch 'resolve_org_for_repo'"
        )

    # Check for SaasConversationStore patch
    if 'SaasConversationStore.get_resolver_instance' not in source:
        raise AssertionError(
            "Tests must patch 'SaasConversationStore.get_resolver_instance'"
        )

    # Check for start_conversation patch
    if "@patch('integrations.jira.jira_view.start_conversation'" not in source:
        raise AssertionError(
            "Tests must patch 'start_conversation'"
        )


def test_syntax_valid():
    """PASS-TO-PASS: Both files have valid Python syntax."""
    # Test jira_view.py
    try:
        compile(get_source_code(JIRA_VIEW_PATH), str(JIRA_VIEW_PATH), 'exec')
    except SyntaxError as e:
        raise AssertionError(f"jira_view.py has syntax error: {e}")

    # Test test file
    if TEST_FILE_PATH.exists():
        try:
            compile(get_source_code(TEST_FILE_PATH), str(TEST_FILE_PATH), 'exec')
        except SyntaxError as e:
            raise AssertionError(f"test_jira_view.py has syntax error: {e}")
