#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch for Linear resolver org routing
patch -p1 <<'PATCH'
diff --git a/enterprise/integrations/linear/linear_view.py b/enterprise/integrations/linear/linear_view.py
index abc123..def456 100644
--- a/enterprise/integrations/linear/linear_view.py
+++ b/enterprise/integrations/linear/linear_view.py
@@ -1,25 +1,34 @@
 from dataclasses import dataclass
+from uuid import uuid4

 from integrations.linear.linear_types import LinearViewInterface, StartingConvoException
 from integrations.models import JobContext
+from integrations.resolver_org_router import resolve_org_for_repo
 from integrations.utils import CONVERSATION_URL, get_final_agent_observation
 from jinja2 import Environment
+from server.config import get_config
 from storage.linear_conversation import LinearConversation
 from storage.linear_integration_store import LinearIntegrationStore
 from storage.linear_user import LinearUser
 from storage.linear_workspace import LinearWorkspace
+from storage.saas_conversation_store import SaasConversationStore

 from openhands.core.logger import openhands_logger as logger
 from openhands.core.schema.agent import AgentState
 from openhands.events.action import MessageAction
 from openhands.events.serialization.event import event_to_dict
+from openhands.integrations.provider import ProviderHandler
 from openhands.server.services.conversation_service import (
-    create_new_conversation,
     setup_init_conversation_settings,
+    start_conversation,
 )
 from openhands.server.shared import ConversationStoreImpl, config, conversation_manager
 from openhands.server.user_auth.user_auth import UserAuth
-from openhands.storage.data_models.conversation_metadata import ConversationTrigger
+from openhands.storage.data_models.conversation_metadata import (
+    ConversationMetadata,
+    ConversationTrigger,
+)
+from openhands.utils.conversation_summary import get_default_conversation_title

 integration_store = LinearIntegrationStore.get_instance()

@@ -61,20 +70,70 @@ async def create_or_update_conversation(self, jinja_env: Environment) -> str:
         instructions, user_msg = await self._get_instructions(jinja_env)

         try:
-            agent_loop_info = await create_new_conversation(
-                user_id=self.linear_user.keycloak_user_id,
-                git_provider_tokens=provider_tokens,
+            user_id = self.linear_user.keycloak_user_id
+
+            # Resolve git provider from repository
+            resolved_git_provider = None
+            if provider_tokens:
+                try:
+                    provider_handler = ProviderHandler(provider_tokens)
+                    repository = await provider_handler.verify_repo_provider(
+                        self.selected_repo
+                    )
+                    resolved_git_provider = repository.git_provider
+                except Exception as e:
+                    logger.warning(
+                        f'[Linear] Failed to resolve git provider for {self.selected_repo}: {e}'
+                    )
+
+            # Resolve target org based on claimed git organizations
+            resolved_org_id = None
+            if resolved_git_provider and self.selected_repo:
+                try:
+                    resolved_org_id = await resolve_org_for_repo(
+                        provider=resolved_git_provider.value,
+                        full_repo_name=self.selected_repo,
+                        keycloak_user_id=user_id,
+                    )
+                except Exception as e:
+                    logger.warning(
+                        f'[Linear] Failed to resolve org for {self.selected_repo}: {e}'
+                    )
+
+            # Create the conversation store with resolver org routing
+            # (bypasses initialize_conversation to avoid threading enterprise-only
+            # resolver_org_id through the generic OSS interface)
+            store = await SaasConversationStore.get_resolver_instance(
+                get_config(),
+                user_id,
+                resolved_org_id,
+            )
+
+            conversation_id = uuid4().hex
+            conversation_metadata = ConversationMetadata(
+                trigger=ConversationTrigger.LINEAR,
+                conversation_id=conversation_id,
+                title=get_default_conversation_title(conversation_id),
+                user_id=user_id,
                 selected_repository=self.selected_repo,
                 selected_branch=None,
+                git_provider=resolved_git_provider,
+            )
+            await store.save_metadata(conversation_metadata)
+
+            await start_conversation(
+                user_id=user_id,
+                git_provider_tokens=provider_tokens,
+                custom_secrets=user_secrets.custom_secrets if user_secrets else None,
                 initial_user_msg=user_msg,
-                conversation_instructions=instructions,
                 image_urls=None,
                 replay_json=None,
-                conversation_trigger=ConversationTrigger.LINEAR,
-                custom_secrets=user_secrets.custom_secrets if user_secrets else None,
+                conversation_id=conversation_id,
+                conversation_metadata=conversation_metadata,
+                conversation_instructions=instructions,
             )

-            self.conversation_id = agent_loop_info.conversation_id
+            self.conversation_id = conversation_id

             logger.info(f'[Linear] Created conversation {self.conversation_id}')
PATCH

# Patch the unit tests to use start_conversation instead of create_new_conversation
sed -i "s/@patch('integrations.linear.linear_view.create_new_conversation')/@patch('integrations.linear.linear_view.start_conversation')/g" enterprise/tests/unit/integrations/linear/test_linear_view.py
sed -i 's/# Verify create_new_conversation was called/# Verify start_conversation was called/g' enterprise/tests/unit/integrations/linear/test_linear_view.py

# Create a Python script to patch the test file more comprehensively
cat > /tmp/patch_tests.py << 'EOF'
import re

with open('enterprise/tests/unit/integrations/linear/test_linear_view.py', 'r') as f:
    content = f.read()

# Replace the test_create_or_update_conversation_success test with a properly mocked version
old_test = '''    @patch('integrations.linear.linear_view.start_conversation')
    @patch('integrations.linear.linear_view.integration_store')
    async def test_create_or_update_conversation_success(
        self,
        mock_store,
        mock_create_conversation,
        new_conversation_view,
        mock_jinja_env,
        mock_agent_loop_info,
    ):
        """Test successful conversation creation"""
        mock_create_conversation.return_value = mock_agent_loop_info
        mock_store.create_conversation = AsyncMock()

        result = await new_conversation_view.create_or_update_conversation(
            mock_jinja_env
        )

        assert result == 'conv-123'
        mock_create_conversation.assert_called_once()
        mock_store.create_conversation.assert_called_once()'''

new_test = '''    @patch('integrations.linear.linear_view.start_conversation')
    @patch('integrations.linear.linear_view.get_default_conversation_title')
    @patch('integrations.linear.linear_view.uuid4')
    @patch('integrations.linear.linear_view.resolve_org_for_repo')
    @patch('integrations.linear.linear_view.ProviderHandler')
    @patch('storage.user_store.UserStore')
    @patch('integrations.linear.linear_view.get_config')
    @patch('integrations.linear.linear_view.integration_store')
    async def test_create_or_update_conversation_success(
        self,
        mock_integration_store,
        mock_get_config,
        mock_user_store_class,
        mock_provider_handler_class,
        mock_resolve_org,
        mock_uuid4,
        mock_get_title,
        mock_start_conversation,
        new_conversation_view,
        mock_jinja_env,
        mock_agent_loop_info,
    ):
        """Test successful conversation creation"""
        from unittest.mock import AsyncMock, MagicMock
        from openhands.integrations.service_types import ProviderType, Repository

        # Setup mocks - mock the UserStore to avoid DB calls
        from storage.user_store import User
        mock_user = MagicMock(spec=User)
        mock_user.current_org_id = None
        mock_user_store_class.get_user_by_id = AsyncMock(return_value=mock_user)

        mock_get_config.return_value = MagicMock()
        mock_provider_handler = MagicMock()
        mock_provider_handler.verify_repo_provider = AsyncMock(
            return_value=Repository(id='test-repo-id', full_name='test/repo1', git_provider=ProviderType.GITHUB, is_public=True)
        )
        mock_provider_handler_class.return_value = mock_provider_handler
        mock_resolve_org.return_value = 'test-org-id'
        mock_uuid4.return_value.hex = 'conv-123'
        mock_get_title.return_value = 'Conversation conv-123'

        result = await new_conversation_view.create_or_update_conversation(
            mock_jinja_env
        )

        assert result == 'conv-123'
        mock_start_conversation.assert_called_once()'''

content = content.replace(old_test, new_test)

# Also patch test_conversation_creation_with_no_user_secrets similarly
old_no_secrets_test = '''    @patch('integrations.linear.linear_view.start_conversation')
    @patch('integrations.linear.linear_view.integration_store')
    async def test_conversation_creation_with_no_user_secrets(
        self,
        mock_store,
        mock_create_conversation,
        new_conversation_view,
        mock_jinja_env,
        mock_agent_loop_info,
    ):
        """Test conversation creation when user has no secrets"""
        new_conversation_view.selected_repo = None
        mock_create_conversation.return_value = mock_agent_loop_info
        mock_store.create_conversation = AsyncMock()

        # Should still work without user secrets
        new_conversation_view.user_secrets = None

        result = await new_conversation_view.create_or_update_conversation(
            mock_jinja_env
        )

        # Verify the result
        assert result == 'conv-123'

        # Verify start_conversation was called with custom_secrets=None
        mock_create_conversation.assert_called_once()'''

new_no_secrets_test = '''    @patch('integrations.linear.linear_view.start_conversation')
    @patch('storage.user_store.UserStore')
    @patch('integrations.linear.linear_view.get_config')
    @patch('integrations.linear.linear_view.integration_store')
    async def test_conversation_creation_with_no_user_secrets(
        self,
        mock_integration_store,
        mock_get_config,
        mock_user_store_class,
        mock_start_conversation,
        new_conversation_view,
        mock_jinja_env,
        mock_agent_loop_info,
    ):
        """Test conversation creation when user has no secrets"""
        from unittest.mock import AsyncMock, MagicMock

        # Setup mocks - mock the UserStore to avoid DB calls
        from storage.user_store import User
        mock_user = MagicMock(spec=User)
        mock_user.current_org_id = None
        mock_user_store_class.get_user_by_id = AsyncMock(return_value=mock_user)

        new_conversation_view.selected_repo = None
        mock_get_config.return_value = MagicMock()
        new_conversation_view.user_secrets = None

        result = await new_conversation_view.create_or_update_conversation(
            mock_jinja_env
        )

        assert result == 'conv-123'
        mock_start_conversation.assert_called_once()'''

content = content.replace(old_no_secrets_test, new_no_secrets_test)

with open('enterprise/tests/unit/integrations/linear/test_linear_view.py', 'w') as f:
    f.write(content)

print("Test file patched successfully")
EOF

python3 /tmp/patch_tests.py

# Fix the keycloak_user_id fixture to use a valid UUID
sed -i "s/keycloak_user_id = 'test_keycloak_id'/keycloak_user_id = '12345678-1234-1234-1234-123456789abc'/" enterprise/tests/unit/integrations/linear/conftest.py

# Verify a distinctive line from the patch was applied
grep -q "resolve_org_for_repo" enterprise/integrations/linear/linear_view.py || exit 1
grep -q "SaasConversationStore.get_resolver_instance" enterprise/integrations/linear/linear_view.py || exit 1
echo "Patch applied successfully"
