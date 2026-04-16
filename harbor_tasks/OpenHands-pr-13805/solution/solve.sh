#!/bin/bash
set -e

cd /workspace/OpenHands

# Check if already patched (idempotency)
if grep -q "resolve_org_for_repo" enterprise/integrations/jira/jira_view.py 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Use Python to apply the changes reliably
python3 << 'PYTHON_SCRIPT'
import re

# Read the original files
with open('enterprise/integrations/jira/jira_view.py', 'r') as f:
    jira_view = f.read()

with open('enterprise/tests/unit/integrations/jira/test_jira_view.py', 'r') as f:
    test_file = f.read()

# ============ Update jira_view.py ============

# 1. Add uuid4 import after "from dataclasses import dataclass, field"
jira_view = jira_view.replace(
    "from dataclasses import dataclass, field\n",
    "from dataclasses import dataclass, field\nfrom uuid import uuid4\n"
)

# 2. Add resolve_org_for_repo import
jira_view = jira_view.replace(
    "from integrations.jira.jira_types import (",
    "from integrations.resolver_org_router import resolve_org_for_repo\nfrom integrations.jira.jira_types import ("
)

# 3. Add server config import
jira_view = jira_view.replace(
    "from jinja2 import Environment",
    "from jinja2 import Environment\nfrom server.config import get_config"
)

# 4. Add SaasConversationStore import
jira_view = jira_view.replace(
    "from storage.jira_workspace import JiraWorkspace",
    "from storage.jira_workspace import JiraWorkspace\nfrom storage.saas_conversation_store import SaasConversationStore"
)

# 5. Replace create_new_conversation with start_conversation import
jira_view = jira_view.replace(
    "from openhands.server.services.conversation_service import create_new_conversation",
    "from openhands.server.services.conversation_service import start_conversation"
)

# 6. Expand ConversationMetadata import
jira_view = jira_view.replace(
    "from openhands.storage.data_models.conversation_metadata import ConversationTrigger",
    """from openhands.storage.data_models.conversation_metadata import (
    ConversationMetadata,
    ConversationTrigger,
)"""
)

# 7. Add get_default_conversation_title import
jira_view = jira_view.replace(
    "from openhands.utils.http_session import httpx_verify_option",
    "from openhands.utils.conversation_summary import get_default_conversation_title\nfrom openhands.utils.http_session import httpx_verify_option"
)

# 8. Replace the create_new_conversation call block
old_block = '''            agent_loop_info = await create_new_conversation(
                user_id=self.jira_user.keycloak_user_id,
                git_provider_tokens=provider_tokens,
                selected_repository=self.selected_repo,
                selected_branch=None,
                initial_user_msg=user_msg,
                conversation_instructions=instructions,
                image_urls=None,
                replay_json=None,
                conversation_trigger=ConversationTrigger.JIRA,
                custom_secrets=user_secrets.custom_secrets if user_secrets else None,
            )

            self.conversation_id = agent_loop_info.conversation_id'''

new_block = '''            user_id = self.jira_user.keycloak_user_id

            # Resolve git provider from repository
            resolved_git_provider = None
            if provider_tokens:
                try:
                    provider_handler = ProviderHandler(provider_tokens)
                    repository = await provider_handler.verify_repo_provider(
                        self.selected_repo
                    )
                    resolved_git_provider = repository.git_provider
                except Exception as e:
                    logger.warning(
                        f'[Jira] Failed to resolve git provider for {self.selected_repo}: {e}'
                    )

            # Resolve target org based on claimed git organizations
            resolved_org_id = None
            if resolved_git_provider and self.selected_repo:
                try:
                    resolved_org_id = await resolve_org_for_repo(
                        provider=resolved_git_provider.value,
                        full_repo_name=self.selected_repo,
                        keycloak_user_id=user_id,
                    )
                except Exception as e:
                    logger.warning(
                        f'[Jira] Failed to resolve org for {self.selected_repo}: {e}'
                    )

            # Create the conversation store with resolver org routing
            store = await SaasConversationStore.get_resolver_instance(
                get_config(),
                user_id,
                resolved_org_id,
            )

            conversation_id = uuid4().hex
            conversation_metadata = ConversationMetadata(
                trigger=ConversationTrigger.JIRA,
                conversation_id=conversation_id,
                title=get_default_conversation_title(conversation_id),
                user_id=user_id,
                selected_repository=self.selected_repo,
                selected_branch=None,
                git_provider=resolved_git_provider,
            )
            await store.save_metadata(conversation_metadata)

            await start_conversation(
                user_id=user_id,
                git_provider_tokens=provider_tokens,
                custom_secrets=user_secrets.custom_secrets if user_secrets else None,
                initial_user_msg=user_msg,
                image_urls=None,
                replay_json=None,
                conversation_id=conversation_id,
                conversation_metadata=conversation_metadata,
                conversation_instructions=instructions,
            )

            self.conversation_id = conversation_id'''

jira_view = jira_view.replace(old_block, new_block)

# 9. Update the logger.info call to include resolved_org_id
old_logger = """            logger.info(
                '[Jira] Created conversation',
                extra={
                    'conversation_id': self.conversation_id,
                    'issue_key': self.payload.issue_key,
                    'selected_repo': self.selected_repo,
                },
            )"""

new_logger = """            logger.info(
                '[Jira] Created conversation',
                extra={
                    'conversation_id': self.conversation_id,
                    'issue_key': self.payload.issue_key,
                    'selected_repo': self.selected_repo,
                    'resolved_org_id': str(resolved_org_id)
                    if resolved_org_id
                    else None,
                },
            )"""

jira_view = jira_view.replace(old_logger, new_logger)

with open('enterprise/integrations/jira/jira_view.py', 'w') as f:
    f.write(jira_view)

print("Updated jira_view.py")

# ============ Update test_jira_view.py ============

# 1. Add UUID import
test_file = test_file.replace(
    "from unittest.mock import AsyncMock, MagicMock, patch\n",
    "from unittest.mock import AsyncMock, MagicMock, patch\nfrom uuid import UUID\n"
)

# 2. Add ProviderType and UserAuth imports
test_file = test_file.replace(
    "from integrations.jira.jira_view import (",
    """from openhands.integrations.service_types import ProviderType
from openhands.server.user_auth.user_auth import UserAuth

from integrations.jira.jira_view import ("""
)

# 3. Update test_create_or_update_conversation_success
test_file = test_file.replace(
    """    @pytest.mark.asyncio
    @patch('integrations.jira.jira_view.create_new_conversation')
    @patch('integrations.jira.jira_view.integration_store')
    async def test_create_or_update_conversation_success(
        self,
        mock_store,
        mock_create_conversation,
        new_conversation_view,
        mock_jinja_env,
        mock_agent_loop_info,
    ):
        \"\"\"Test successful conversation creation\"\"\"
        new_conversation_view._issue_title = 'Test Issue'
        new_conversation_view._issue_description = 'Test description'
        mock_create_conversation.return_value = mock_agent_loop_info
        mock_store.create_conversation = AsyncMock()

        result = await new_conversation_view.create_or_update_conversation(
            mock_jinja_env
        )

        assert result == 'conv-123'
        mock_create_conversation.assert_called_once()
        mock_store.create_conversation.assert_called_once()""",

    """    @pytest.mark.asyncio
    @patch('integrations.jira.jira_view.resolve_org_for_repo', new_callable=AsyncMock)
    @patch('integrations.jira.jira_view.ProviderHandler')
    @patch(
        'integrations.jira.jira_view.SaasConversationStore.get_resolver_instance',
        new_callable=AsyncMock,
    )
    @patch('integrations.jira.jira_view.start_conversation', new_callable=AsyncMock)
    @patch('integrations.jira.jira_view.integration_store')
    async def test_create_or_update_conversation_success(
        self,
        mock_integration_store,
        mock_start_convo,
        mock_get_resolver_instance,
        mock_provider_handler_cls,
        mock_resolve_org,
        new_conversation_view,
        mock_jinja_env,
    ):
        \"\"\"Test successful conversation creation\"\"\"
        new_conversation_view._issue_title = 'Test Issue'
        new_conversation_view._issue_description = 'Test description'

        mock_repo = MagicMock()
        mock_repo.git_provider = ProviderType.GITHUB
        mock_handler = MagicMock()
        mock_handler.verify_repo_provider = AsyncMock(return_value=mock_repo)
        mock_provider_handler_cls.return_value = mock_handler

        mock_resolve_org.return_value = None
        mock_store = MagicMock()
        mock_store.save_metadata = AsyncMock()
        mock_get_resolver_instance.return_value = mock_store
        mock_integration_store.create_conversation = AsyncMock()

        result = await new_conversation_view.create_or_update_conversation(
            mock_jinja_env
        )

        assert result is not None
        assert isinstance(result, str)
        assert len(result) == 32  # uuid4().hex format
        mock_start_convo.assert_called_once()
        mock_integration_store.create_conversation.assert_called_once()"""
)

# 4. Add routing test class at the end before the last class or at end
# Find position to insert (before the last class TestJiraPayloadParser)
routing_tests = '''

CLAIMING_ORG_ID = UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')


class TestJiraV0ConversationRouting:
    """Test V0 conversation routing logic based on claimed git organizations."""

    @pytest.fixture
    def routing_view(
        self,
        sample_webhook_payload,
        sample_jira_user,
        sample_jira_workspace,
    ):
        """View with non-empty provider tokens for routing tests."""
        user_auth = MagicMock(spec=UserAuth)
        user_auth.get_provider_tokens = AsyncMock(
            return_value={ProviderType.GITHUB: MagicMock()}
        )
        user_auth.get_secrets = AsyncMock(return_value=None)
        return JiraNewConversationView(
            payload=sample_webhook_payload,
            saas_user_auth=user_auth,
            jira_user=sample_jira_user,
            jira_workspace=sample_jira_workspace,
            selected_repo='test/repo1',
            _issue_title='Test Issue',
            _issue_description='Test description',
            _decrypted_api_key='decrypted_key',
        )

    @pytest.mark.asyncio
    @patch('integrations.jira.jira_view.resolve_org_for_repo', new_callable=AsyncMock)
    @patch('integrations.jira.jira_view.ProviderHandler')
    @patch(
        'integrations.jira.jira_view.SaasConversationStore.get_resolver_instance',
        new_callable=AsyncMock,
    )
    @patch('integrations.jira.jira_view.start_conversation', new_callable=AsyncMock)
    @patch('integrations.jira.jira_view.integration_store')
    async def test_routes_to_claimed_org_when_user_is_member(
        self,
        mock_integration_store,
        mock_start_convo,
        mock_get_resolver_instance,
        mock_provider_handler_cls,
        mock_resolve_org,
        routing_view,
        mock_jinja_env,
    ):
        """When repo belongs to a claimed org and user is a member, conversation is created in that org."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.git_provider = ProviderType.GITHUB
        mock_handler = MagicMock()
        mock_handler.verify_repo_provider = AsyncMock(return_value=mock_repo)
        mock_provider_handler_cls.return_value = mock_handler

        mock_resolve_org.return_value = CLAIMING_ORG_ID
        mock_store = MagicMock()
        mock_store.save_metadata = AsyncMock()
        mock_get_resolver_instance.return_value = mock_store
        mock_integration_store.create_conversation = AsyncMock()

        # Act
        await routing_view.create_or_update_conversation(mock_jinja_env)

        # Assert
        mock_resolve_org.assert_called_once_with(
            provider='github',
            full_repo_name='test/repo1',
            keycloak_user_id='test_keycloak_id',
        )
        call_args = mock_get_resolver_instance.call_args
        assert call_args[0][1] == 'test_keycloak_id'  # user_id
        assert call_args[0][2] == CLAIMING_ORG_ID  # resolver_org_id
        saved_metadata = mock_store.save_metadata.call_args[0][0]
        assert saved_metadata.git_provider == ProviderType.GITHUB

    @pytest.mark.asyncio
    @patch('integrations.jira.jira_view.resolve_org_for_repo', new_callable=AsyncMock)
    @patch('integrations.jira.jira_view.ProviderHandler')
    @patch(
        'integrations.jira.jira_view.SaasConversationStore.get_resolver_instance',
        new_callable=AsyncMock,
    )
    @patch('integrations.jira.jira_view.start_conversation', new_callable=AsyncMock)
    @patch('integrations.jira.jira_view.integration_store')
    async def test_falls_back_to_personal_workspace_when_no_claim(
        self,
        mock_integration_store,
        mock_start_convo,
        mock_get_resolver_instance,
        mock_provider_handler_cls,
        mock_resolve_org,
        routing_view,
        mock_jinja_env,
    ):
        """When no org has claimed the git org, conversation goes to personal workspace."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.git_provider = ProviderType.GITHUB
        mock_handler = MagicMock()
        mock_handler.verify_repo_provider = AsyncMock(return_value=mock_repo)
        mock_provider_handler_cls.return_value = mock_handler

        mock_resolve_org.return_value = None
        mock_store = MagicMock()
        mock_store.save_metadata = AsyncMock()
        mock_get_resolver_instance.return_value = mock_store
        mock_integration_store.create_conversation = AsyncMock()

        # Act
        await routing_view.create_or_update_conversation(mock_jinja_env)

        # Assert
        call_args = mock_get_resolver_instance.call_args
        assert call_args[0][2] is None  # resolver_org_id is None

'''

# Insert before the last class (TestJiraPayloadParser)
if 'class TestJiraPayloadParser:' in test_file:
    test_file = test_file.replace(
        'class TestJiraPayloadParser:',
        routing_tests + 'class TestJiraPayloadParser:'
    )
else:
    test_file = test_file + routing_tests

with open('enterprise/tests/unit/integrations/jira/test_jira_view.py', 'w') as f:
    f.write(test_file)

print("Updated test_jira_view.py")
print("All patches applied successfully!")
PYTHON_SCRIPT

echo "Patch applied successfully"
