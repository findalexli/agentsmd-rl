"""
Test outputs for OpenHands PR #13676: Git Organizations API

This tests:
1. The new /git-organizations API endpoint in enterprise
2. The new get_user_groups method in GitLabService
3. The new get_github_organizations and get_gitlab_groups methods in ProviderHandler
"""

import subprocess
import sys
import os
from types import MappingProxyType
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from pydantic import SecretStr

# Add paths for imports
REPO = "/workspace/OpenHands"
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "enterprise"))


# ==================== FAIL TO PASS TESTS ====================

@pytest.mark.asyncio
async def test_gitlab_service_has_get_user_groups():
    """Test that GitLabService has the get_user_groups method."""
    from openhands.integrations.gitlab.gitlab_service import GitLabService

    service = GitLabService(token=SecretStr('test-token'))

    # Check method exists
    assert hasattr(service, 'get_user_groups'), "GitLabService should have get_user_groups method"
    assert callable(getattr(service, 'get_user_groups', None)), "get_user_groups should be callable"


@pytest.mark.asyncio
async def test_gitlab_get_user_groups_returns_group_paths():
    """Test that get_user_groups returns group paths extracted from API response.

    Verifies behavior: given groups from GitLab API with 'path' field,
    the method returns a list of path strings.
    """
    from openhands.integrations.gitlab.gitlab_service import GitLabService

    service = GitLabService(token=SecretStr('test-token'))

    mock_groups = [
        {'path': 'my-team', 'name': 'My Team', 'id': 1},
        {'path': 'open-source', 'name': 'Open Source Projects', 'id': 2},
    ]

    with patch.object(service, '_make_request') as mock_request:
        mock_request.return_value = (mock_groups, {})

        groups = await service.get_user_groups()

        # Verify the BEHAVIOR: correct paths are extracted from group data
        assert groups == ['my-team', 'open-source'], f"Expected ['my-team', 'open-source'], got {groups}"
        # Verify _make_request was called (implementation detail NOT asserted)


@pytest.mark.asyncio
async def test_gitlab_get_user_groups_returns_empty_on_error():
    """Test that get_user_groups returns empty list when the API call fails."""
    from openhands.integrations.gitlab.gitlab_service import GitLabService

    service = GitLabService(token=SecretStr('test-token'))

    with patch.object(service, '_make_request') as mock_request:
        mock_request.side_effect = Exception('API error')

        groups = await service.get_user_groups()

        assert groups == [], f"Expected empty list on error, got {groups}"


@pytest.mark.asyncio
async def test_provider_handler_has_get_github_organizations():
    """Test that ProviderHandler has get_github_organizations method."""
    from openhands.integrations.provider import ProviderHandler, ProviderToken
    from openhands.integrations.service_types import ProviderType

    tokens = MappingProxyType(
        {ProviderType.GITHUB: ProviderToken(token=SecretStr('gh-token'))}
    )
    handler = ProviderHandler(provider_tokens=tokens)

    assert hasattr(handler, 'get_github_organizations'), "ProviderHandler should have get_github_organizations method"
    assert callable(getattr(handler, 'get_github_organizations', None)), "get_github_organizations should be callable"


@pytest.mark.asyncio
async def test_provider_handler_has_get_gitlab_groups():
    """Test that ProviderHandler has get_gitlab_groups method."""
    from openhands.integrations.provider import ProviderHandler, ProviderToken
    from openhands.integrations.service_types import ProviderType

    tokens = MappingProxyType(
        {ProviderType.GITLAB: ProviderToken(token=SecretStr('gl-token'))}
    )
    handler = ProviderHandler(provider_tokens=tokens)

    assert hasattr(handler, 'get_gitlab_groups'), "ProviderHandler should have get_gitlab_groups method"
    assert callable(getattr(handler, 'get_gitlab_groups', None)), "get_gitlab_groups should be callable"


@pytest.mark.asyncio
async def test_get_github_organizations_delegates_to_service():
    """Test that get_github_organizations returns organizations from the GitHub service.

    Verifies behavior: when GitHub service returns organizations,
    get_github_organizations passes them through correctly.
    """
    from openhands.integrations.provider import ProviderHandler, ProviderToken
    from openhands.integrations.service_types import ProviderType

    tokens = MappingProxyType(
        {ProviderType.GITHUB: ProviderToken(token=SecretStr('gh-token'))}
    )
    handler = ProviderHandler(provider_tokens=tokens)

    with patch.object(handler, 'get_service') as mock_get_service:
        mock_service = mock_get_service.return_value
        mock_service.get_organizations_from_installations = AsyncMock(
            return_value=['org1', 'org2']
        )

        result = await handler.get_github_organizations()

        # Verify the BEHAVIOR: correct organizations are returned
        assert result == ['org1', 'org2'], f"Expected ['org1', 'org2'], got {result}"
        # Verify delegation happened (implementation detail NOT asserted)


@pytest.mark.asyncio
async def test_get_github_organizations_returns_empty_on_error():
    """Test that get_github_organizations returns empty list when the service call fails."""
    from openhands.integrations.provider import ProviderHandler, ProviderToken
    from openhands.integrations.service_types import ProviderType

    tokens = MappingProxyType(
        {ProviderType.GITHUB: ProviderToken(token=SecretStr('gh-token'))}
    )
    handler = ProviderHandler(provider_tokens=tokens)

    with patch.object(handler, 'get_service') as mock_get_service:
        mock_service = mock_get_service.return_value
        mock_service.get_organizations_from_installations = AsyncMock(
            side_effect=Exception('API error')
        )

        result = await handler.get_github_organizations()

        assert result == [], f"Expected empty list on error, got {result}"


@pytest.mark.asyncio
async def test_get_gitlab_groups_delegates_to_service():
    """Test that get_gitlab_groups returns groups from the GitLab service.

    Verifies behavior: when GitLab service returns groups,
    get_gitlab_groups passes them through correctly.
    """
    from openhands.integrations.provider import ProviderHandler, ProviderToken
    from openhands.integrations.service_types import ProviderType

    tokens = MappingProxyType(
        {ProviderType.GITLAB: ProviderToken(token=SecretStr('gl-token'))}
    )
    handler = ProviderHandler(provider_tokens=tokens)

    with patch.object(handler, 'get_service') as mock_get_service:
        mock_service = mock_get_service.return_value
        mock_service.get_user_groups = AsyncMock(return_value=['group-a', 'group-b'])

        result = await handler.get_gitlab_groups()

        # Verify the BEHAVIOR: correct groups are returned
        assert result == ['group-a', 'group-b'], f"Expected ['group-a', 'group-b'], got {result}"
        # Verify delegation happened (implementation detail NOT asserted)


@pytest.mark.asyncio
async def test_enterprise_api_endpoint_exists():
    """Test that the saas_get_user_git_organizations function exists in enterprise routes."""
    try:
        from server.routes.user import saas_get_user_git_organizations
        assert callable(saas_get_user_git_organizations), "saas_get_user_git_organizations should be callable"
    except ImportError as e:
        # If keycloak or other enterprise deps are missing, check via file inspection
        user_py_path = os.path.join(REPO, "enterprise/server/routes/user.py")
        with open(user_py_path, 'r') as f:
            content = f.read()
        assert 'saas_get_user_git_organizations' in content, "saas_get_user_git_organizations should exist in user.py"
        assert 'async def saas_get_user_git_organizations(' in content, "saas_get_user_git_organizations should be defined as async function"


@pytest.mark.asyncio
async def test_enterprise_api_unsupported_provider_returns_400():
    """Test that the API returns 400 for unsupported providers."""
    try:
        from server.routes.user import saas_get_user_git_organizations
        from openhands.integrations.provider import ProviderToken
        from openhands.integrations.service_types import ProviderType
        from fastapi.responses import JSONResponse
    except ImportError as e:
        pytest.skip(f"Enterprise dependencies not available: {e}")

    # Create Azure DevOps tokens (unsupported)
    tokens = MappingProxyType(
        {ProviderType.AZURE_DEVOPS: ProviderToken(token=SecretStr('az-token'))}
    )

    with patch('server.routes.user.ProviderHandler'):
        result = await saas_get_user_git_organizations(
            provider_tokens=tokens,
            access_token=SecretStr('token'),
            user_id='user-1',
        )

    assert isinstance(result, JSONResponse), f"Expected JSONResponse for unsupported provider, got {type(result)}"
    assert result.status_code == 400, f"Expected status code 400, got {result.status_code}"


# ==================== PASS TO PASS TESTS (Repo CI/CD) ====================

def test_unit_tests_gitlab():
    """Run the GitLab unit tests from the repo (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/integrations/gitlab/test_gitlab.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": f"{REPO}:{REPO}/enterprise"}
    )
    assert result.returncode == 0, f"GitLab unit tests failed:\n{result.stderr[-1000:]}"


def test_unit_tests_gitlab_branches():
    """Run the GitLab branches unit tests from the repo (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/integrations/gitlab/test_gitlab_branches.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": f"{REPO}:{REPO}/enterprise"}
    )
    assert result.returncode == 0, f"GitLab branches tests failed:\n{result.stderr[-1000:]}"


def test_unit_tests_github():
    """Run the GitHub service unit tests from the repo (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/integrations/github/test_github_service.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": f"{REPO}:{REPO}/enterprise"}
    )
    assert result.returncode == 0, f"GitHub service tests failed:\n{result.stderr[-1000:]}"


def test_unit_tests_provider():
    """Run the provider immutability tests from the repo (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/integrations/test_provider_immutability.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": f"{REPO}:{REPO}/enterprise"}
    )
    assert result.returncode == 0, f"Provider immutability tests failed:\n{result.stderr[-1000:]}"


def test_unit_tests_provider_and_gitlab():
    """Run all provider and GitLab related unit tests from the repo (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/integrations/", "-v", "--tb=short", "-k", "provider or gitlab", "-x"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": f"{REPO}:{REPO}/enterprise"}
    )
    assert result.returncode == 0, f"Provider/GitLab tests failed:\n{result.stderr[-1000:]}"


def test_syntax_check():
    """Basic Python syntax check on the key files."""
    files_to_check = [
        "openhands/integrations/gitlab/service/repos.py",
        "openhands/integrations/provider.py",
    ]

    for file_path in files_to_check:
        full_path = os.path.join(REPO, file_path)
        result = subprocess.run(
            ["python", "-m", "py_compile", full_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO
        )
        assert result.returncode == 0, f"Syntax error in {file_path}:\n{result.stderr}"


def test_ruff_lint():
    """Run ruff linter on modified modules (pass_to_pass)."""
    # Install ruff if not present
    subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=60,
        cwd=REPO
    )
    result = subprocess.run(
        ["ruff", "check", "--config", "dev_config/python/ruff.toml", "openhands/integrations/gitlab/", "openhands/integrations/provider.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff lint failed:\n{result.stderr[-500:]}"


def test_ruff_format():
    """Run ruff format check on modified modules (pass_to_pass)."""
    # Install ruff if not present
    subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=60,
        cwd=REPO
    )
    result = subprocess.run(
        ["ruff", "format", "--config", "dev_config/python/ruff.toml", "--check", "openhands/integrations/gitlab/", "openhands/integrations/provider.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stderr[-500:]}"


# ==================== STRUCTURAL TESTS (Gated by behavioral) ====================

@pytest.mark.asyncio
async def test_api_returns_expected_structure_for_github():
    """Test that the API returns the expected JSON structure for GitHub."""
    # Only run if core methods exist (gated test)
    from openhands.integrations.provider import ProviderHandler
    if not hasattr(ProviderHandler, 'get_github_organizations'):
        pytest.skip("get_github_organizations not implemented")

    try:
        from server.routes.user import saas_get_user_git_organizations
    except ImportError as e:
        pytest.skip(f"Enterprise dependencies not available: {e}")

    from openhands.integrations.provider import ProviderToken
    from openhands.integrations.service_types import ProviderType

    tokens = MappingProxyType(
        {ProviderType.GITHUB: ProviderToken(token=SecretStr('gh-token'))}
    )

    with patch(
        'openhands.integrations.provider.ProviderHandler.get_service'
    ) as mock_get_service:
        mock_service = mock_get_service.return_value
        mock_service.get_organizations_from_installations = AsyncMock(
            return_value=['org1', 'org2']
        )

        result = await saas_get_user_git_organizations(
            provider_tokens=tokens,
            access_token=SecretStr('token'),
            user_id='user-1',
        )

    assert result == {
        'provider': 'github',
        'organizations': ['org1', 'org2'],
    }, f"Unexpected result structure: {result}"


@pytest.mark.asyncio
async def test_api_returns_expected_structure_for_gitlab():
    """Test that the API returns the expected JSON structure for GitLab."""
    # Only run if core methods exist (gated test)
    from openhands.integrations.provider import ProviderHandler
    if not hasattr(ProviderHandler, 'get_gitlab_groups'):
        pytest.skip("get_gitlab_groups not implemented")

    try:
        from server.routes.user import saas_get_user_git_organizations
    except ImportError as e:
        pytest.skip(f"Enterprise dependencies not available: {e}")

    from openhands.integrations.provider import ProviderToken
    from openhands.integrations.service_types import ProviderType

    tokens = MappingProxyType(
        {ProviderType.GITLAB: ProviderToken(token=SecretStr('gl-token'))}
    )

    with patch(
        'openhands.integrations.provider.ProviderHandler.get_service'
    ) as mock_get_service:
        mock_service = mock_get_service.return_value
        mock_service.get_user_groups = AsyncMock(return_value=['group1', 'group2'])

        result = await saas_get_user_git_organizations(
            provider_tokens=tokens,
            access_token=SecretStr('token'),
            user_id='user-1',
        )

    assert result == {
        'provider': 'gitlab',
        'organizations': ['group1', 'group2'],
    }, f"Unexpected result structure: {result}"


@pytest.mark.asyncio
async def test_api_returns_expected_structure_for_bitbucket():
    """Test that the API returns the expected JSON structure for Bitbucket."""
    try:
        from server.routes.user import saas_get_user_git_organizations
    except ImportError as e:
        pytest.skip(f"Enterprise dependencies not available: {e}")

    from openhands.integrations.provider import ProviderToken
    from openhands.integrations.service_types import ProviderType

    tokens = MappingProxyType(
        {ProviderType.BITBUCKET: ProviderToken(token=SecretStr('bb-token'))}
    )

    with patch(
        'openhands.integrations.provider.ProviderHandler.get_service'
    ) as mock_get_service:
        mock_service = mock_get_service.return_value
        mock_service.get_installations = AsyncMock(return_value=['workspace1'])

        result = await saas_get_user_git_organizations(
            provider_tokens=tokens,
            access_token=SecretStr('token'),
            user_id='user-1',
        )

    assert result == {
        'provider': 'bitbucket',
        'organizations': ['workspace1'],
    }, f"Unexpected result structure: {result}"