#!/bin/bash
set -e

cd /workspace/openhands

# Apply the gold patch for Slack resolver org routing
cat <<'PATCH' | git apply -
diff --git a/enterprise/integrations/slack/slack_view.py b/enterprise/integrations/slack/slack_view.py
index eb336404a346..cfcc28be1d52 100644
--- a/enterprise/integrations/slack/slack_view.py
+++ b/enterprise/integrations/slack/slack_view.py
@@ -4,6 +4,7 @@

 from integrations.models import Message
 from integrations.resolver_context import ResolverUserContext
+from integrations.resolver_org_router import resolve_org_for_repo
 from integrations.slack.slack_types import (
     SlackMessageView,
     SlackViewInterface,
@@ -17,7 +18,9 @@ from integrations.slack.slack_user_store import (
     get_user_v1_enabled_setting,
 )
 from jinja2 import Environment
+from server.config import get_config
 from slack_sdk import WebClient
+from storage.saas_conversation_store import SaasConversationStore
 from storage.slack_conversation import SlackConversation
 from storage.slack_conversation_store import SlackConversationStore
 from storage.slack_team_store import SlackTeamStore
@@ -36,18 +39,20 @@ from openhands.core.schema.agent import AgentState
 from openhands.events.action import MessageAction
 from openhands.events.serialization.event import event_to_dict
-from openhands.integrations.provider import ProviderHandler, ProviderType
+from openhands.integrations.provider import ProviderHandler
 from openhands.sdk import TextContent
 from openhands.server.services.conversation_service import (
-    create_new_conversation,
     setup_init_conversation_settings,
+    start_conversation,
 )
 from openhands.server.shared import ConversationStoreImpl, config, conversation_manager
 from openhands.server.user_auth.user_auth import UserAuth
 from openhands.storage.data_models.conversation_metadata import (
+    ConversationMetadata,
     ConversationTrigger,
 )
 from openhands.utils.async_utils import GENERAL_TIMEOUT
+from openhands.utils.conversation_summary import get_default_conversation_title

 # =================================================
 # SECTION: Slack view types
@@ -202,6 +207,22 @@ async def create_or_update_conversation(self, jinja: Environment) -> str:
         provider_tokens = await self.saas_user_auth.get_provider_tokens()
         user_secrets = await self.saas_user_auth.get_secrets()

+        # Determine git provider from repository (needed for both org routing and conversation creation)
+        self._resolved_git_provider = None
+        if self.selected_repo and provider_tokens:
+            provider_handler = ProviderHandler(provider_tokens)
+            repository = await provider_handler.verify_repo_provider(self.selected_repo)
+            self._resolved_git_provider = repository.git_provider
+
+        # Resolve target org based on claimed git organizations
+        self.resolved_org_id = None
+        if self._resolved_git_provider and self.selected_repo:
+            self.resolved_org_id = await resolve_org_for_repo(
+                provider=self._resolved_git_provider.value,
+                full_repo_name=self.selected_repo,
+                keycloak_user_id=self.slack_to_openhands_user.keycloak_user_id,
+            )
+
         # Check if V1 conversations are enabled for this user
         self.v1_enabled = await is_v1_enabled_for_slack_resolver(
             self.slack_to_openhands_user.keycloak_user_id
@@ -224,30 +245,44 @@ async def _create_v0_conversation(
             jinja
         )

-        # Determine git provider from repository
-        git_provider = None
-        if self.selected_repo and provider_tokens:
-            provider_handler = ProviderHandler(provider_tokens)
-            repository = await provider_handler.verify_repo_provider(self.selected_repo)
-            git_provider = repository.git_provider
+        user_id = self.slack_to_openhands_user.keycloak_user_id

-        agent_loop_info = await create_new_conversation(
-            user_id=self.slack_to_openhands_user.keycloak_user_id,
-            git_provider_tokens=provider_tokens,
+        # Create the conversation store with resolver org routing
+        # (bypasses initialize_conversation to avoid threading enterprise-only
+        # resolver_org_id through the generic OSS interface)
+        store = await SaasConversationStore.get_resolver_instance(
+            get_config(),
+            user_id,
+            self.resolved_org_id,
+        )
+
+        conversation_id = uuid4().hex
+        conversation_metadata = ConversationMetadata(
+            trigger=ConversationTrigger.SLACK,
+            conversation_id=conversation_id,
+            title=get_default_conversation_title(conversation_id),
+            user_id=user_id,
             selected_repository=self.selected_repo,
             selected_branch=None,
+            git_provider=self._resolved_git_provider,
+        )
+        await store.save_metadata(conversation_metadata)
+
+        await start_conversation(
+            user_id=user_id,
+            git_provider_tokens=provider_tokens,
+            custom_secrets=user_secrets.custom_secrets if user_secrets else None,
             initial_user_msg=user_instructions,
+            image_urls=None,
+            replay_json=None,
+            conversation_id=conversation_id,
+            conversation_metadata=conversation_metadata,
             conversation_instructions=(
                 conversation_instructions if conversation_instructions else None
             ),
-            image_urls=None,
-            replay_json=None,
-            conversation_trigger=ConversationTrigger.SLACK,
-            custom_secrets=user_secrets.custom_secrets if user_secrets else None,
-            git_provider=git_provider,
         )

-        self.conversation_id = agent_loop_info.conversation_id
+        self.conversation_id = conversation_id
         logger.info(f'[Slack]: Created V0 conversation: {self.conversation_id}')
         await self.save_slack_convo(v1_enabled=False)

@@ -265,13 +300,8 @@ async def _create_v1_conversation(self, jinja: Environment) -> None:
         # Create the Slack V1 callback processor
         slack_callback_processor = self._create_slack_v1_callback_processor()

-        # Determine git provider from repository
-        git_provider = None
-        provider_tokens = await self.saas_user_auth.get_provider_tokens()
-        if self.selected_repo and provider_tokens:
-            provider_handler = ProviderHandler(provider_tokens)
-            repository = await provider_handler.verify_repo_provider(self.selected_repo)
-            git_provider = ProviderType(repository.git_provider.value)
+        # Use git provider resolved in create_or_update_conversation
+        git_provider = self._resolved_git_provider

         # Get the app conversation service and start the conversation
         injector_state = InjectorState()
@@ -292,7 +322,10 @@ async def _create_v1_conversation(self, jinja: Environment) -> None:
         )

         # Set up the Slack user context for the V1 system
-        slack_user_context = ResolverUserContext(saas_user_auth=self.saas_user_auth)
+        slack_user_context = ResolverUserContext(
+            saas_user_auth=self.saas_user_auth,
+            resolver_org_id=self.resolved_org_id,
+        )
         setattr(injector_state, USER_CONTEXT_ATTR, slack_user_context)

         async with get_app_conversation_service(
PATCH

echo "Gold patch applied successfully"
