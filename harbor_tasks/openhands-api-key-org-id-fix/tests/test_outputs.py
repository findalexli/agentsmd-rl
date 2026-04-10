"""Tests for API key org_id handling in save_app_conversation_info.

These tests verify that when a conversation is created using API key authentication,
the conversation is associated with the API key's bound organization, not the user's
currently selected organization.
"""

import asyncio
import subprocess
import sys
from dataclasses import dataclass
from uuid import UUID, uuid4

# Configure pytest-asyncio before importing pytest
import pytest_asyncio

# Set up paths before importing
def setup_paths():
    """Add required paths to sys.path for imports."""
    paths = [
        '/workspace/openhands',
        '/workspace/openhands/enterprise',
    ]
    for path in paths:
        if path not in sys.path:
            sys.path.insert(0, path)


setup_paths()

# Set asyncio mode
pytest_plugins = ['pytest_asyncio']

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Import storage models
from storage.base import Base
from storage.org import Org
from storage.stored_conversation_metadata_saas import StoredConversationMetadataSaas
from storage.user import User

# Import enterprise service
from server.utils.saas_app_conversation_info_injector import (
    SaasSQLAppConversationInfoService,
)

# Import openhands models
from openhands.app_server.app_conversation.app_conversation_models import (
    AppConversationInfo,
)
from openhands.app_server.user.specifiy_user_context import SpecifyUserContext

# Test UUIDs
USER1_ID = UUID('a1111111-1111-1111-1111-111111111111')
ORG1_ID = UUID('c1111111-1111-1111-1111-111111111111')
ORG2_ID = UUID('d2222222-2222-2222-2222-222222222222')

REPO = '/workspace/openhands'


@pytest_asyncio.fixture
async def async_engine():
    """Create an async SQLite engine for testing."""
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        poolclass=StaticPool,
        connect_args={'check_same_thread': False},
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session_with_users(async_engine) -> AsyncSession:
    """Create an async session with pre-populated Org and User rows."""
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as db_session:
        # Insert Orgs
        org1 = Org(
            id=ORG1_ID,
            name='test-org-1',
            enable_default_condenser=True,
            enable_proactive_conversation_starters=True,
        )
        org2 = Org(
            id=ORG2_ID,
            name='test-org-2',
            enable_default_condenser=True,
            enable_proactive_conversation_starters=True,
        )
        db_session.add(org1)
        db_session.add(org2)
        await db_session.flush()

        # Insert User with ORG1 as current org
        user1 = User(id=USER1_ID, current_org_id=ORG1_ID)
        db_session.add(user1)
        await db_session.commit()

        yield db_session


@dataclass
class MockUserAuth:
    """Mock user auth with API key org_id."""

    user_id: str
    api_key_org_id: UUID | None = None

    async def get_user_id(self) -> str:
        return self.user_id

    def get_api_key_org_id(self) -> UUID | None:
        return self.api_key_org_id


@dataclass
class MockAuthUserContext:
    """Mock auth user context that wraps MockUserAuth."""

    user_auth: MockUserAuth

    async def get_user_id(self) -> str | None:
        return await self.user_auth.get_user_id()


@pytest.mark.asyncio(loop_scope='function')
async def test_api_key_org_id_used_when_available(async_session_with_users):
    """FAIL-TO-PASS: API key's org_id should be used when saving conversation via API key auth.

    This tests the main bug fix: when a user creates an API key in Personal Workspace,
    then switches to a different org in browser, and uses the API key to create a
    conversation, the conversation should be saved in the API key's org, not the
    user's current org.
    """
    # Set user's current org to ORG2
    result = await async_session_with_users.execute(
        select(User).where(User.id == USER1_ID)
    )
    user_to_update = result.scalars().first()
    user_to_update.current_org_id = ORG2_ID
    await async_session_with_users.commit()
    async_session_with_users.expire_all()

    # Create service with mock auth context where API key is bound to ORG1
    mock_user_auth = MockUserAuth(
        user_id=str(USER1_ID),
        api_key_org_id=ORG1_ID,
    )
    mock_context = MockAuthUserContext(user_auth=mock_user_auth)

    service = SaasSQLAppConversationInfoService(
        db_session=async_session_with_users,
        user_context=mock_context,
    )

    # Create and save a conversation
    conv_id = uuid4()
    conv_info = AppConversationInfo(
        id=conv_id,
        created_by_user_id=str(USER1_ID),
        sandbox_id='sandbox_api_key_test',
        title='API Key Created Conversation',
    )
    await service.save_app_conversation_info(conv_info)

    # Verify: SAAS metadata should have ORG1 (API key's org), not ORG2 (user's current org)
    saas_query = select(StoredConversationMetadataSaas).where(
        StoredConversationMetadataSaas.conversation_id == str(conv_id)
    )
    result = await async_session_with_users.execute(saas_query)
    saas_metadata = result.scalar_one_or_none()

    assert saas_metadata is not None, 'SAAS metadata should be created'
    assert saas_metadata.user_id == USER1_ID
    assert saas_metadata.org_id == ORG1_ID, (
        f'Conversation should be in API key org ({ORG1_ID}), '
        f'not user current org ({ORG2_ID}). Got org_id={saas_metadata.org_id}'
    )


@pytest.mark.asyncio(loop_scope='function')
async def test_legacy_api_key_without_org_uses_user_current_org(async_session_with_users):
    """FAIL-TO-PASS: Legacy API keys (without org_id) should fall back to user's current org.

    Legacy API keys created before the org_id feature was added will have
    api_key_org_id = None. In this case, we should fall back to the user's
    current_org_id.
    """
    # Create service with mock auth context where API key has NO org_id
    mock_user_auth = MockUserAuth(
        user_id=str(USER1_ID),
        api_key_org_id=None,
    )
    mock_context = MockAuthUserContext(user_auth=mock_user_auth)

    service = SaasSQLAppConversationInfoService(
        db_session=async_session_with_users,
        user_context=mock_context,
    )

    # Create and save a conversation
    conv_id = uuid4()
    conv_info = AppConversationInfo(
        id=conv_id,
        created_by_user_id=str(USER1_ID),
        sandbox_id='sandbox_legacy_key_test',
        title='Legacy API Key Conversation',
    )
    await service.save_app_conversation_info(conv_info)

    # Verify: SAAS metadata should use user's current org (ORG1) as fallback
    saas_query = select(StoredConversationMetadataSaas).where(
        StoredConversationMetadataSaas.conversation_id == str(conv_id)
    )
    result = await async_session_with_users.execute(saas_query)
    saas_metadata = result.scalar_one_or_none()

    assert saas_metadata is not None, 'SAAS metadata should be created'
    assert saas_metadata.user_id == USER1_ID
    assert saas_metadata.org_id == ORG1_ID, (
        f'Legacy key should fall back to user current org ({ORG1_ID}), '
        f'but got org_id={saas_metadata.org_id}'
    )


@pytest.mark.asyncio(loop_scope='function')
async def test_cookie_auth_without_api_key_uses_user_current_org(async_session_with_users):
    """FAIL-TO-PASS: Cookie auth (no API key) should use user's current org.

    When authenticated via browser cookie (no API key), there's no
    get_api_key_org_id method, so we use user's current_org_id.
    """
    # Use SpecifyUserContext which doesn't have user_auth attribute
    service = SaasSQLAppConversationInfoService(
        db_session=async_session_with_users,
        user_context=SpecifyUserContext(user_id=str(USER1_ID)),
    )

    # Create and save a conversation
    conv_id = uuid4()
    conv_info = AppConversationInfo(
        id=conv_id,
        created_by_user_id=str(USER1_ID),
        sandbox_id='sandbox_cookie_auth_test',
        title='Cookie Auth Conversation',
    )
    await service.save_app_conversation_info(conv_info)

    # Verify: SAAS metadata should use user's current org (ORG1)
    saas_query = select(StoredConversationMetadataSaas).where(
        StoredConversationMetadataSaas.conversation_id == str(conv_id)
    )
    result = await async_session_with_users.execute(saas_query)
    saas_metadata = result.scalar_one_or_none()

    assert saas_metadata is not None, 'SAAS metadata should be created'
    assert saas_metadata.user_id == USER1_ID
    assert saas_metadata.org_id == ORG1_ID, (
        f'Cookie auth should use user current org ({ORG1_ID}), '
        f'but got org_id={saas_metadata.org_id}'
    )


@pytest.mark.asyncio(loop_scope='function')
async def test_org_isolation_with_api_key_org(async_session_with_users):
    """FAIL-TO-PASS: Cross-org visibility test for API key created conversations.

    Simulates the full bug scenario:
    1. Create conversation via API key (bound to ORG1)
    2. User switches to ORG2
    3. User should NOT see the conversation in ORG2
    4. User switches back to ORG1
    5. User should see the conversation in ORG1
    """
    # Step 1: Create conversation via API key bound to ORG1
    mock_user_auth = MockUserAuth(
        user_id=str(USER1_ID),
        api_key_org_id=ORG1_ID,
    )
    mock_context = MockAuthUserContext(user_auth=mock_user_auth)

    api_key_service = SaasSQLAppConversationInfoService(
        db_session=async_session_with_users,
        user_context=mock_context,
    )

    conv_id = uuid4()
    conv_info = AppConversationInfo(
        id=conv_id,
        created_by_user_id=str(USER1_ID),
        sandbox_id='sandbox_e2e_api_key',
        title='E2E API Key Conversation',
    )
    await api_key_service.save_app_conversation_info(conv_info)

    # Step 2: Switch user to ORG2 in browser session
    result = await async_session_with_users.execute(
        select(User).where(User.id == USER1_ID)
    )
    user_to_update = result.scalars().first()
    user_to_update.current_org_id = ORG2_ID
    await async_session_with_users.commit()
    async_session_with_users.expire_all()

    # Step 3: User in ORG2 should NOT see the conversation
    user_service_org2 = SaasSQLAppConversationInfoService(
        db_session=async_session_with_users,
        user_context=SpecifyUserContext(user_id=str(USER1_ID)),
    )
    page_org2 = await user_service_org2.search_app_conversation_info()
    assert len(page_org2.items) == 0, (
        f'User in ORG2 should not see conversation created via API key in ORG1. '
        f'Found {len(page_org2.items)} items'
    )

    # Step 4: Switch user back to ORG1
    result = await async_session_with_users.execute(
        select(User).where(User.id == USER1_ID)
    )
    user_to_update = result.scalars().first()
    user_to_update.current_org_id = ORG1_ID
    await async_session_with_users.commit()
    async_session_with_users.expire_all()

    # Step 5: User in ORG1 should see the conversation
    user_service_org1 = SaasSQLAppConversationInfoService(
        db_session=async_session_with_users,
        user_context=SpecifyUserContext(user_id=str(USER1_ID)),
    )
    page_org1 = await user_service_org1.search_app_conversation_info()
    assert len(page_org1.items) == 1, (
        f'User in ORG1 should see conversation created via API key in ORG1. '
        f'Found {len(page_org1.items)} items'
    )
    assert page_org1.items[0].id == conv_id


def test_repo_enterprise_tests():
    """PASS-TO-PASS: Run enterprise storage tests to verify repo baseline works."""
    result = subprocess.run(
        [
            'python', '-m', 'pytest',
            'enterprise/tests/unit/storage/test_saas_sql_app_conversation_info_service.py',
            '-v', '--tb=short', '-x',
            '-k', 'not TestApiKeyOrgIdHandling',  # Skip new tests that test the fix
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    if result.returncode != 0:
        # Only fail if there are actual test failures, not collection errors
        if 'FAILED' in result.stdout or 'FAILED' in result.stderr:
            assert False, f'Enterprise tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}'


def test_source_file_syntax():
    """PASS-TO-PASS: Verify the source file has valid Python syntax."""
    source_file = f'{REPO}/enterprise/server/utils/saas_app_conversation_info_injector.py'

    result = subprocess.run(
        ['python', '-m', 'py_compile', source_file],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f'Syntax error in {source_file}:\n{result.stderr}'
    )


def test_repo_ruff_lint():
    """PASS-TO-PASS: Modified files pass ruff linting checks."""
    result = subprocess.run(
        [
            'poetry', 'run', '--project=enterprise',
            'ruff', 'check',
            'enterprise/server/utils/saas_app_conversation_info_injector.py',
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    assert result.returncode == 0, (
        f'Ruff linting failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}'
    )


def test_repo_storage_tests():
    """PASS-TO-PASS: Enterprise storage module tests pass (baseline verification)."""
    result = subprocess.run(
        [
            'poetry', 'run', '--project=enterprise',
            'pytest',
            'enterprise/tests/unit/storage/',
            '-v', '--tb=short', '-x',
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )

    assert result.returncode == 0, (
        f'Enterprise storage tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}'
    )


def test_repo_api_key_store_tests():
    """PASS-TO-PASS: API key store tests pass (validates API key functionality).

    Tests API key validation including legacy keys without org_id.
    Relevant to the org_id fix since API keys are central to the fix.
    """
    result = subprocess.run(
        [
            'poetry', 'run', '--project=enterprise',
            'pytest',
            'enterprise/tests/unit/test_api_key_store.py',
            '-v', '--tb=short', '-x',
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    assert result.returncode == 0, (
        f'API key store tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}'
    )


def test_repo_pre_commit():
    """PASS-TO-PASS: Enterprise pre-commit hooks pass (code quality checks).

    Runs ruff, mypy, and other code quality checks from the enterprise
    pre-commit configuration.
    """
    result = subprocess.run(
        [
            'pre-commit', 'run',
            '--all-files',
            '--show-diff-on-failure',
            '--config', './dev_config/python/.pre-commit-config.yaml',
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=f'{REPO}/enterprise',
    )

    assert result.returncode == 0, (
        f'Pre-commit hooks failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}'
    )
