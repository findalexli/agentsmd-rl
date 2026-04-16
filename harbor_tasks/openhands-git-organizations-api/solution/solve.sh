#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch for PR #13676
cat <<'PATCH' | git apply -
diff --git a/enterprise/server/routes/user.py b/enterprise/server/routes/user.py
index 908f96281b5e..54fc93388a2c 100644
--- a/enterprise/server/routes/user.py
+++ b/enterprise/server/routes/user.py
@@ -9,6 +9,7 @@

 from openhands.integrations.provider import (
     PROVIDER_TOKEN_TYPE,
+    ProviderHandler,
 )
 from openhands.integrations.service_types import (
     Branch,
@@ -67,6 +68,53 @@ async def saas_get_user_installations(
     )


+@saas_user_router.get('/git-organizations')
+async def saas_get_user_git_organizations(
+    provider_tokens: PROVIDER_TOKEN_TYPE | None = Depends(get_provider_tokens),
+    access_token: SecretStr | None = Depends(get_access_token),
+    user_id: str | None = Depends(get_user_id),
+):
+    if not provider_tokens:
+        retval = await _check_idp(
+            access_token=access_token,
+            default_value={},
+        )
+        if retval is not None:
+            return retval
+        # _check_idp returned None (tokens refreshed on Keycloak side),
+        # but provider_tokens is still None for this request.
+        return JSONResponse(
+            content='Git provider token required.',
+            status_code=status.HTTP_401_UNAUTHORIZED,
+        )
+
+    client = ProviderHandler(
+        provider_tokens=provider_tokens,
+        external_auth_token=access_token,
+        external_auth_id=user_id,
+    )
+
+    # SaaS users sign in with one provider at a time
+    provider = next(iter(provider_tokens))
+
+    if provider == ProviderType.GITHUB:
+        orgs = await client.get_github_organizations()
+    elif provider == ProviderType.GITLAB:
+        orgs = await client.get_gitlab_groups()
+    elif provider == ProviderType.BITBUCKET:
+        orgs = await client.get_bitbucket_workspaces()
+    else:
+        return JSONResponse(
+            content=f"Provider {provider.value} doesn't support git organizations",
+            status_code=status.HTTP_400_BAD_REQUEST,
+        )
+
+    return {
+        'provider': provider.value,
+        'organizations': orgs,
+    }
+
+
 @saas_user_router.get('/repositories', response_model=list[Repository])
 async def saas_get_user_repositories(
     sort: str = 'pushed',
diff --git a/enterprise/tests/unit/test_user_git_organizations.py b/enterprise/tests/unit/test_user_git_organizations.py
new file mode 100644
index 000000000000..6f0b744e19a3
--- /dev/null
+++ b/enterprise/tests/unit/test_user_git_organizations.py
@@ -0,0 +1,141 @@
+"""Tests for the GET /api/user/git-organizations endpoint.
+
+This endpoint returns git organizations for the user's active provider
+in SaaS mode (single provider at a time).
+"""
+
+from types import MappingProxyType
+from unittest.mock import AsyncMock, patch
+
+import pytest
+from fastapi.responses import JSONResponse
+from pydantic import SecretStr
+
+from openhands.integrations.provider import ProviderToken
+from openhands.integrations.service_types import ProviderType
+
+
+@pytest.fixture
+def github_provider_tokens():
+    return MappingProxyType(
+        {ProviderType.GITHUB: ProviderToken(token=SecretStr('gh-token'))}
+    )
+
+
+@pytest.fixture
+def gitlab_provider_tokens():
+    return MappingProxyType(
+        {ProviderType.GITLAB: ProviderToken(token=SecretStr('gl-token'))}
+    )
+
+
+@pytest.fixture
+def bitbucket_provider_tokens():
+    return MappingProxyType(
+        {ProviderType.BITBUCKET: ProviderToken(token=SecretStr('bb-token'))}
+    )
+
+
+@pytest.fixture
+def azure_devops_provider_tokens():
+    return MappingProxyType(
+        {ProviderType.AZURE_DEVOPS: ProviderToken(token=SecretStr('az-token'))}
+    )
+
+
+@pytest.fixture
+def mock_check_idp():
+    with patch('server.routes.user._check_idp', new_callable=AsyncMock) as mock_fn:
+        yield mock_fn
+
+
+@pytest.mark.asyncio
+async def test_no_provider_tokens_falls_back_to_idp(mock_check_idp):
+    """When no provider tokens exist, falls back to IDP check."""
+    from server.routes.user import saas_get_user_git_organizations
+
+    mock_check_idp.return_value = {}
+
+    result = await saas_get_user_git_organizations(
+        provider_tokens=None,
+        access_token=SecretStr('token'),
+        user_id='user-1',
+    )
+
+    assert result == {}
+    mock_check_idp.assert_called_once()
+
+
+@pytest.mark.asyncio
+async def test_unsupported_provider_returns_400(azure_devops_provider_tokens):
+    """Unsupported provider returns a 400 error."""
+    from server.routes.user import saas_get_user_git_organizations
+
+    with patch('server.routes.user.ProviderHandler'):
+        result = await saas_get_user_git_organizations(
+            provider_tokens=azure_devops_provider_tokens,
+            access_token=SecretStr('token'),
+            user_id='user-1',
+        )
+
+    assert isinstance(result, JSONResponse)
+    assert result.status_code == 400
+
+
+@pytest.mark.asyncio
+@pytest.mark.parametrize(
+    'provider_tokens_fixture, mock_method, mock_return, expected_provider',
+    [
+        (
+            'github_provider_tokens',
+            'get_organizations_from_installations',
+            ['All-Hands-AI', 'OpenHands'],
+            'github',
+        ),
+        (
+            'gitlab_provider_tokens',
+            'get_user_groups',
+            ['my-team', 'open-source'],
+            'gitlab',
+        ),
+        (
+            'bitbucket_provider_tokens',
+            'get_installations',
+            ['my-workspace'],
+            'bitbucket',
+        ),
+    ],
+    ids=['github', 'gitlab', 'bitbucket'],
+)
+async def test_provider_routing_with_real_handler(
+    provider_tokens_fixture,
+    mock_method,
+    mock_return,
+    expected_provider,
+    request,
+):
+    """Each provider routes to the correct service method and returns the expected JSON structure.
+
+    Uses a real ProviderHandler so the endpoint's if/elif routing and ProviderHandler's
+    delegation are both exercised. Only the low-level git service call is mocked.
+    """
+    from server.routes.user import saas_get_user_git_organizations
+
+    provider_tokens = request.getfixturevalue(provider_tokens_fixture)
+
+    with patch(
+        'openhands.integrations.provider.ProviderHandler.get_service'
+    ) as mock_get_service:
+        mock_service = mock_get_service.return_value
+        setattr(mock_service, mock_method, AsyncMock(return_value=mock_return))
+
+        result = await saas_get_user_git_organizations(
+            provider_tokens=provider_tokens,
+            access_token=SecretStr('token'),
+            user_id='user-1',
+        )
+
+    assert result == {
+        'provider': expected_provider,
+        'organizations': mock_return,
+    }
diff --git a/openhands/integrations/gitlab/service/repos.py b/openhands/integrations/gitlab/service/repos.py
index fdfbe1d8df3b..08be876fbd95 100644
--- a/openhands/integrations/gitlab/service/repos.py
+++ b/openhands/integrations/gitlab/service/repos.py
@@ -1,3 +1,4 @@
+from openhands.core.logger import openhands_logger as logger
 from openhands.integrations.gitlab.service.base import GitLabMixinBase
 from openhands.integrations.service_types import OwnerType, ProviderType, Repository
 from openhands.server.types import AppMode
@@ -166,6 +167,18 @@ async def get_all_repositories(
         all_repos = all_repos[:MAX_REPOS]
         return [self._parse_repository(repo) for repo in all_repos]

+    async def get_user_groups(self) -> list[str]:
+        """Get list of GitLab group paths that the user is a member of."""
+        url = f'{self.BASE_URL}/groups'
+        try:
+            # min_access_level 10 = Guest (includes all membership levels)
+            params = {'min_access_level': '10', 'per_page': '100'}
+            response, _ = await self._make_request(url, params)
+            return [group['path'] for group in response]
+        except Exception as e:
+            logger.warning(f'Failed to get user groups: {e}')
+            return []
+
     async def get_repository_details_from_repo_name(
         self, repository: str
     ) -> Repository:
diff --git a/openhands/integrations/provider.py b/openhands/integrations/provider.py
index ddec99d03369..695f0a6ad699 100644
--- a/openhands/integrations/provider.py
+++ b/openhands/integrations/provider.py
@@ -239,6 +239,24 @@ async def get_bitbucket_dc_projects(self) -> list[str]:

         return []

+    async def get_github_organizations(self) -> list[str]:
+        service = self.get_service(ProviderType.GITHUB)
+        try:
+            return await service.get_organizations_from_installations()  # type: ignore[attr-defined]
+        except Exception as e:
+            logger.warning(f'Failed to get github organizations {e}')
+
+        return []
+
+    async def get_gitlab_groups(self) -> list[str]:
+        service = self.get_service(ProviderType.GITLAB)
+        try:
+            return await service.get_user_groups()  # type: ignore[attr-defined]
+        except Exception as e:
+            logger.warning(f'Failed to get gitlab groups {e}')
+
+        return []
+
     async def get_azure_devops_organizations(self) -> list[str]:
         service = cast(
             InstallationsService, self.get_service(ProviderType.AZURE_DEVOPS)
diff --git a/tests/unit/integrations/gitlab/test_gitlab.py b/tests/unit/integrations/gitlab/test_gitlab.py
index 2df301b7b71b..661992422c63 100644
--- a/tests/unit/integrations/gitlab/test_gitlab.py
+++ b/tests/unit/integrations/gitlab/test_gitlab.py
@@ -10,6 +10,41 @@
 from openhands.server.types import AppMode


+@pytest.mark.asyncio
+async def test_gitlab_get_user_groups_returns_group_paths():
+    """Test that get_user_groups returns group paths the user belongs to."""
+    service = GitLabService(token=SecretStr('test-token'))
+
+    mock_groups = [
+        {'path': 'my-team', 'name': 'My Team', 'id': 1},
+        {'path': 'open-source', 'name': 'Open Source Projects', 'id': 2},
+    ]
+
+    with patch.object(service, '_make_request') as mock_request:
+        mock_request.return_value = (mock_groups, {})
+
+        groups = await service.get_user_groups()
+
+        assert groups == ['my-team', 'open-source']
+        mock_request.assert_called_once_with(
+            f'{service.BASE_URL}/groups',
+            {'min_access_level': '10', 'per_page': '100'},
+        )
+
+
+@pytest.mark.asyncio
+async def test_gitlab_get_user_groups_returns_empty_on_error():
+    """Test that get_user_groups returns empty list when the API call fails."""
+    service = GitLabService(token=SecretStr('test-token'))
+
+    with patch.object(service, '_make_request') as mock_request:
+        mock_request.side_effect = Exception('API error')
+
+        groups = await service.get_user_groups()
+
+        assert groups == []
+
+
 @pytest.mark.asyncio
 async def test_gitlab_get_repositories_with_user_owner_type():
     """Test that get_repositories correctly sets owner_type field for user repositories."""
diff --git a/tests/unit/integrations/test_provider_immutability.py b/tests/unit/integrations/test_provider_immutability.py
index 48faf5625652..7dde3bcb13ff 100644
--- a/tests/unit/integrations/test_provider_immutability.py
+++ b/tests/unit/integrations/test_provider_immutability.py
@@ -1,4 +1,5 @@
 from types import MappingProxyType
+from unittest.mock import AsyncMock, patch

 import pytest
 from pydantic import SecretStr, ValidationError
@@ -338,3 +339,60 @@ def test_get_provider_env_key():
     """Test provider environment key generation"""
     assert ProviderHandler.get_provider_env_key(ProviderType.GITHUB) == 'github_token'
     assert ProviderHandler.get_provider_env_key(ProviderType.GITLAB) == 'gitlab_token'
+
+
+@pytest.mark.asyncio
+async def test_get_github_organizations_delegates_to_service():
+    """Test that get_github_organizations calls get_organizations_from_installations on the GitHub service."""
+    tokens = MappingProxyType(
+        {ProviderType.GITHUB: ProviderToken(token=SecretStr('gh-token'))}
+    )
+    handler = ProviderHandler(provider_tokens=tokens)
+
+    with patch.object(handler, 'get_service') as mock_get_service:
+        mock_service = mock_get_service.return_value
+        mock_service.get_organizations_from_installations = AsyncMock(
+            return_value=['org1', 'org2']
+        )
+
+        result = await handler.get_github_organizations()
+
+        assert result == ['org1', 'org2']
+        mock_get_service.assert_called_once_with(ProviderType.GITHUB)
+
+
+@pytest.mark.asyncio
+async def test_get_github_organizations_returns_empty_on_error():
+    """Test that get_github_organizations returns empty list when the service call fails."""
+    tokens = MappingProxyType(
+        {ProviderType.GITHUB: ProviderToken(token=SecretStr('gh-token'))}
+    )
+    handler = ProviderHandler(provider_tokens=tokens)
+
+    with patch.object(handler, 'get_service') as mock_get_service:
+        mock_service = mock_get_service.return_value
+        mock_service.get_organizations_from_installations = AsyncMock(
+            side_effect=Exception('API error')
+        )
+
+        result = await handler.get_github_organizations()
+
+        assert result == []
+
+
+@pytest.mark.asyncio
+async def test_get_gitlab_groups_delegates_to_service():
+    """Test that get_gitlab_groups calls get_user_groups on the GitLab service."""
+    tokens = MappingProxyType(
+        {ProviderType.GITLAB: ProviderToken(token=SecretStr('gl-token'))}
+    )
+    handler = ProviderHandler(provider_tokens=tokens)
+
+    with patch.object(handler, 'get_service') as mock_get_service:
+        mock_service = mock_get_service.return_value
+        mock_service.get_user_groups = AsyncMock(return_value=['group-a', 'group-b'])
+
+        result = await handler.get_gitlab_groups()
+
+        assert result == ['group-a', 'group-b']
+        mock_get_service.assert_called_once_with(ProviderType.GITLAB)
PATCH

# Verify the distinctive line was applied
grep -q "get_user_groups" openhands/integrations/gitlab/service/repos.py && echo "Patch applied successfully"
