"""Tests for API key organization association fix.

These tests verify that the save_app_conversation_info() method correctly uses
the API key's org_id when available, falling back to user.current_org_id for
legacy API keys and cookie-based authentication.
"""

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock, patch

# Add enterprise code to path
sys.path.insert(0, str(Path('/workspace/OpenHands')))

import pytest


# Repo path for pass-to-pass tests
REPO = Path('/workspace/OpenHands')


# ===== Behavioral Tests for the Fix =====

@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.expire_all = MagicMock()
    return session


@pytest.fixture
def mock_user():
    """Create a mock user with current_org_id."""
    user = MagicMock()
    user.id = uuid4()
    user.current_org_id = uuid4()  # User's current org (Organization B)
    return user


@pytest.fixture
def mock_conversation_info():
    """Create mock AppConversationInfo."""
    info = MagicMock()
    info.id = uuid4()
    info.created_by_user_id = str(uuid4())
    info.conversation_version = 'V1'
    info.title = 'Test Conversation'
    info.sandbox_id = 'test-sandbox'
    return info


class MockUserAuthWithOrg:
    """Mock UserAuth that has API key with org_id."""
    def __init__(self, user_id: str, api_key_org_id: UUID | None):
        self._user_id = user_id
        self._api_key_org_id = api_key_org_id

    async def get_user_id(self) -> str:
        return self._user_id

    def get_api_key_org_id(self) -> UUID | None:
        return self._api_key_org_id


class MockUserAuthLegacy:
    """Mock UserAuth for legacy API key without org_id."""
    def __init__(self, user_id: str):
        self._user_id = user_id

    async def get_user_id(self) -> str:
        return self._user_id

    def get_api_key_org_id(self) -> None:
        return None


class MockUserContextWithAuth:
    """User context with user_auth attribute (API key auth)."""
    def __init__(self, user_id: str, user_auth):
        self._user_id = user_id
        self.user_auth = user_auth

    async def get_user_id(self) -> str | None:
        return self._user_id


class MockUserContextNoAuth:
    """User context without user_auth attribute (cookie auth)."""
    def __init__(self, user_id: str):
        self._user_id = user_id
        # No user_auth attribute

    async def get_user_id(self) -> str | None:
        return self._user_id


# ===== Fail-to-Pass Tests (regression tests) =====

@pytest.mark.asyncio
async def test_api_key_org_id_used_when_available(mock_db_session, mock_user, mock_conversation_info):
    """Test that API key's org_id is used when saving conversation via API key auth.

    This is the main bug fix test: when a user creates an API key bound to Organization A,
    then switches to Organization B in browser, and uses the API key to create a
    conversation, the conversation should be saved under Organization A (API key's org),
    not Organization B (user's current org).
    """
    # Setup: API key bound to Organization A
    api_key_org_id = uuid4()  # Organization A (from API key)
    user_current_org_id = uuid4()  # Organization B (user's current org)

    mock_user.current_org_id = user_current_org_id
    user_id = str(mock_user.id)

    # Create user context with API key auth that has org_id
    user_auth = MockUserAuthWithOrg(user_id, api_key_org_id)
    user_context = MockUserContextWithAuth(user_id, user_auth)

    # Mock the database query results
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    # Import and create the service
    from enterprise.server.utils.saas_app_conversation_info_injector import SaasSQLAppConversationInfoService

    service = SaasSQLAppConversationInfoService(
        db_session=mock_db_session,
        user_context=user_context
    )

    # Patch the parent class method to avoid actual DB operations
    with patch('openhands.app_server.app_conversation.sql_app_conversation_info_service.SQLAppConversationInfoService.save_app_conversation_info', new_callable=AsyncMock) as mock_parent_save:
        # Call the method under test
        await service.save_app_conversation_info(mock_conversation_info)

        # Verify that metadata was added with the API key's org_id, not user's current org
        added_objects = mock_db_session.add.call_args_list
        saas_metadata_calls = [call for call in added_objects if call and hasattr(call[0][0], 'org_id')]

        assert len(saas_metadata_calls) > 0, "No StoredConversationMetadataSaas was added"

        # Check that the metadata was created with API key's org_id (Organization A)
        metadata = saas_metadata_calls[0][0][0]
        assert metadata.org_id == api_key_org_id, (
            f"Expected org_id to be API key's org ({api_key_org_id}), "
            f"but got {metadata.org_id}. The fix should prefer API key's org_id."
        )


@pytest.mark.asyncio
async def test_legacy_api_key_falls_back_to_user_org(mock_db_session, mock_user, mock_conversation_info):
    """Test that legacy API keys (without org_id) fall back to user's current org.

    Legacy API keys created before the org_id feature was added will have
    api_key_org_id = None. In this case, we should fall back to the user's
    current_org_id.
    """
    # Setup: Legacy API key with no org_id
    user_current_org_id = uuid4()  # Organization B (user's current org)
    mock_user.current_org_id = user_current_org_id
    user_id = str(mock_user.id)

    # Create user context with legacy API key (returns None for get_api_key_org_id)
    user_auth = MockUserAuthLegacy(user_id)
    user_context = MockUserContextWithAuth(user_id, user_auth)

    # Mock the database query results
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    # Import and create the service
    from enterprise.server.utils.saas_app_conversation_info_injector import SaasSQLAppConversationInfoService

    service = SaasSQLAppConversationInfoService(
        db_session=mock_db_session,
        user_context=user_context
    )

    # Patch the parent class method
    with patch('openhands.app_server.app_conversation.sql_app_conversation_info_service.SQLAppConversationInfoService.save_app_conversation_info', new_callable=AsyncMock):
        # Call the method under test
        await service.save_app_conversation_info(mock_conversation_info)

        # Verify that metadata was added with user's current org (fallback behavior)
        added_objects = mock_db_session.add.call_args_list
        saas_metadata_calls = [call for call in added_objects if call and hasattr(call[0][0], 'org_id')]

        assert len(saas_metadata_calls) > 0, "No StoredConversationMetadataSaas was added"

        # Check that the metadata was created with user's current org_id (fallback)
        metadata = saas_metadata_calls[0][0][0]
        assert metadata.org_id == user_current_org_id, (
            f"Expected org_id to fall back to user's current org ({user_current_org_id}), "
            f"but got {metadata.org_id}. Legacy API keys should use user's current org."
        )


@pytest.mark.asyncio
async def test_cookie_auth_uses_user_current_org(mock_db_session, mock_user, mock_conversation_info):
    """Test that cookie auth (no API key) uses user's current org.

    When authenticated via browser cookie (no API key), there's no
    get_api_key_org_id method, so we use user's current_org_id.
    This preserves existing behavior for non-API-key authentication.
    """
    # Setup: Cookie auth with no user_auth attribute
    user_current_org_id = uuid4()
    mock_user.current_org_id = user_current_org_id
    user_id = str(mock_user.id)

    # Create user context without user_auth (simulates cookie auth)
    user_context = MockUserContextNoAuth(user_id)

    # Mock the database query results
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    # Import and create the service
    from enterprise.server.utils.saas_app_conversation_info_injector import SaasSQLAppConversationInfoService

    service = SaasSQLAppConversationInfoService(
        db_session=mock_db_session,
        user_context=user_context
    )

    # Patch the parent class method
    with patch('openhands.app_server.app_conversation.sql_app_conversation_info_service.SQLAppConversationInfoService.save_app_conversation_info', new_callable=AsyncMock):
        # Call the method under test - should NOT raise AttributeError
        # due to hasattr() checks in the fix
        await service.save_app_conversation_info(mock_conversation_info)

        # Verify that metadata was added with user's current org
        added_objects = mock_db_session.add.call_args_list
        saas_metadata_calls = [call for call in added_objects if call and hasattr(call[0][0], 'org_id')]

        assert len(saas_metadata_calls) > 0, "No StoredConversationMetadataSaas was added"

        # Check that the metadata was created with user's current org_id
        metadata = saas_metadata_calls[0][0][0]
        assert metadata.org_id == user_current_org_id, (
            f"Expected org_id to be user's current org ({user_current_org_id}) for cookie auth, "
            f"but got {metadata.org_id}."
        )


@pytest.mark.asyncio
async def test_code_can_be_imported_and_executed():
    """Verify the modified code can be imported and has expected structure."""
    # This test verifies the code is syntactically valid and can be imported
    from enterprise.server.utils.saas_app_conversation_info_injector import SaasSQLAppConversationInfoService

    # Verify the class exists and has the expected method
    assert hasattr(SaasSQLAppConversationInfoService, 'save_app_conversation_info')

    # Verify the method is async
    import inspect
    assert inspect.iscoroutinefunction(SaasSQLAppConversationInfoService.save_app_conversation_info)


# ===== Pass-to-Pass Tests (repo CI/CD checks) =====

def test_repo_syntax_check():
    """Repo's Python syntax is valid (pass_to_pass).

    This test verifies that the modified Python file has valid syntax
    and can be compiled without errors. Mirrors CI lint check.
    """
    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    r = subprocess.run(
        ['python3', '-m', 'py_compile', str(target_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_ast_parse():
    """Repo's modified file can be parsed by AST (pass_to_pass).

    This test verifies that the modified Python file can be parsed
    into an abstract syntax tree without errors.
    """
    import ast

    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    source_code = target_file.read_text()

    try:
        ast.parse(source_code)
    except SyntaxError as e:
        pytest.fail(f"AST parsing failed: {e}")


def test_repo_enterprise_syntax():
    """Enterprise module files have valid Python syntax (pass_to_pass).

    This test verifies that key Python files in the enterprise module
    have valid syntax and can be compiled.
    """
    enterprise_files = [
        'enterprise/server/utils/saas_app_conversation_info_injector.py',
        'enterprise/tests/unit/storage/test_saas_sql_app_conversation_info_service.py',
    ]

    for rel_path in enterprise_files:
        target_file = REPO / rel_path
        if target_file.exists():
            r = subprocess.run(
                ['python3', '-m', 'py_compile', str(target_file)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert r.returncode == 0, f"Syntax check failed for {rel_path}:\n{r.stderr}"


def test_repo_class_structure():
    """Repo's modified file has expected class structure (pass_to_pass).

    This test verifies that the expected classes and methods exist
    in the modified file.
    """
    import ast

    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    source_code = target_file.read_text()

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        pytest.fail(f"AST parsing failed: {e}")

    # Check for expected classes
    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    expected_classes = ['SaasSQLAppConversationInfoService', 'SaasAppConversationInfoServiceInjector']

    for cls in expected_classes:
        assert cls in class_names, f"Expected class '{cls}' not found in source file"

    # Check for expected method
    method_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == 'save_app_conversation_info'
    ]
    assert 'save_app_conversation_info' in method_names, "Method 'save_app_conversation_info' not found"


def test_repo_ruff_lint():
    """Repo's modified file passes ruff linting - critical errors only (pass_to_pass).

    This test verifies that the modified Python file passes ruff for critical
    linter, matching the CI/CD lint checks.
    """
    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    ruff_config = REPO / 'dev_config' / 'python' / 'ruff.toml'

    # First ensure ruff is installed
    install_r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )

    r = subprocess.run(
        ['ruff', 'check', '--no-cache', '--config', str(ruff_config),  '--select', 'F', str(target_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff found syntax errors:\n{r.stdout}\n{r.stderr}"


def test_repo_enterprise_ruff_check_target():
    """Enterprise module target file passes enterprise ruff config (pass_to_pass).

    This test runs ruff check with the enterprise-specific config on the
    modified file, matching the CI lint-enterprise-python workflow.
    """
    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    ruff_config = REPO / 'enterprise' / 'dev_config' / 'python' / 'ruff.toml'

    install_r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )

    r = subprocess.run(
        ['ruff', 'check', '--no-cache', '--config', str(ruff_config), '--ignore', 'I', str(target_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Enterprise ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_enterprise_ruff_format():
    """Enterprise target file passes ruff format check (pass_to_pass).

    This test verifies that the modified file is properly formatted according
    to the enterprise ruff config, matching CI format checks.
    """
    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    ruff_config = REPO / 'enterprise' / 'dev_config' / 'python' / 'ruff.toml'

    install_r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )

    r = subprocess.run(
        ['ruff', 'format', '--no-cache', '--config', str(ruff_config), '--check', str(target_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Enterprise ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_enterprise_storage_syntax():
    """Enterprise storage test file has valid syntax (pass_to_pass).

    This test verifies that the related enterprise storage test file
    has valid Python syntax, ensuring consistency with the modified module.
    """
    target_file = REPO / 'enterprise' / 'tests' / 'unit' / 'storage' / 'test_saas_sql_app_conversation_info_service.py'
    r = subprocess.run(
        ['python3', '-m', 'py_compile', str(target_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Enterprise storage test syntax check failed:\n{r.stderr}"


def test_repo_enterprise_pytest_unit():
    """Enterprise unit tests pass for related storage module (pass_to_pass).

    This test runs a quick subset of the enterprise unit tests for the
    storage module, verifying the modified code works correctly.
    Mirrors the CI test-enterprise workflow.
    """
    # Install poetry and dependencies
    install_r = subprocess.run(
        ['pip', 'install', 'poetry', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Install enterprise dependencies
    enterprise_dir = REPO / 'enterprise'
    poetry_install = subprocess.run(
        ['poetry', 'install', '--with', 'dev', '-q'],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=enterprise_dir,
    )

    # Run a quick test to verify the module works
    test_path = 'tests/unit/storage/test_saas_sql_app_conversation_info_service.py::TestSaasSQLAppConversationInfoService::test_service_initialization'
    r = subprocess.run(
        [
            'poetry', 'run', 'pytest',
            test_path,
            '-v', '--tb=short'
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=enterprise_dir,
        env={**os.environ, 'PYTHONPATH': '..:.'}
    )
    assert r.returncode == 0, f"Enterprise pytest failed:\n{r.stdout}\n{r.stderr}"


def test_repo_import_structure():
    """Modified file has valid import structure (pass_to_pass).

    This test verifies that all imports in the modified file are
    syntactically valid without actually importing the modules.
    """
    import ast

    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    source_code = target_file.read_text()

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        pytest.fail(f"AST parsing failed: {e}")

    # Collect all imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)

    # Verify we found expected imports (basic sanity check)
    assert len(imports) > 0, "No imports found in the file"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
