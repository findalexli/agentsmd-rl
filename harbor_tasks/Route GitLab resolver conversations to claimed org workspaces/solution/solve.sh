#!/bin/bash
set -e

cd /workspace/openhands

# Apply the gold patch for GitLab resolver org routing
git apply <<'EOF'
diff --git a/enterprise/integrations/github/github_view.py b/enterprise/integrations/github/github_view.py
index cf1a68378c37..ba439c0d9a9e 100644
--- a/enterprise/integrations/github/github_view.py
+++ b/enterprise/integrations/github/github_view.py
@@ -342,7 +342,7 @@ def _create_github_v1_callback_processor(self):
                 'full_repo_name': self.full_repo_name,
                 'installation_id': self.installation_id,
             },
-            send_summary_instruction=self.send_summary_instruction,
+            should_request_summary=self.send_summary_instruction,
         )


@@ -496,7 +496,7 @@ def _create_github_v1_callback_processor(self):
                 'comment_id': self.comment_id,
             },
             inline_pr_comment=True,
-            send_summary_instruction=self.send_summary_instruction,
+            should_request_summary=self.send_summary_instruction,
         )


diff --git a/enterprise/integrations/gitlab/gitlab_view.py b/enterprise/integrations/gitlab/gitlab_view.py
index 4b719406405a..59222484a651 100644
--- a/enterprise/integrations/gitlab/gitlab_view.py
+++ b/enterprise/integrations/gitlab/gitlab_view.py
@@ -3,6 +3,7 @@

 from integrations.models import Message
 from integrations.resolver_context import ResolverUserContext
+from integrations.resolver_org_router import resolve_org_for_repo
 from integrations.types import ResolverViewInterface, UserData
 from integrations.utils import (
     ENABLE_V1_GITLAB_RESOLVER,
@@ -14,6 +15,7 @@
 from jinja2 import Environment
 from server.auth.token_manager import TokenManager
 from server.config import get_config
+from storage.saas_conversation_store import SaasConversationStore
 from storage.saas_secrets_store import SaasSecretsStore

 from openhands.agent_server.models import SendMessageRequest
@@ -29,15 +31,13 @@
 from openhands.integrations.provider import PROVIDER_TOKEN_TYPE, ProviderType
 from openhands.integrations.service_types import Comment
 from openhands.sdk import TextContent
-from openhands.server.services.conversation_service import (
-    initialize_conversation,
-    start_conversation,
-)
+from openhands.server.services.conversation_service import start_conversation
 from openhands.server.user_auth.user_auth import UserAuth
 from openhands.storage.data_models.conversation_metadata import (
     ConversationMetadata,
     ConversationTrigger,
 )
+from openhands.utils.conversation_summary import get_default_conversation_title

 OH_LABEL, INLINE_OH_LABEL = get_oh_labels(HOST)
 CONFIDENTIAL_NOTE = 'confidential_note'
@@ -118,6 +118,14 @@ async def _get_user_secrets(self):
     async def initialize_new_conversation(self) -> ConversationMetadata:
         # v1_enabled is already set at construction time in the factory method
         # This is the source of truth for the conversation type
+
+        # Resolve target org based on claimed git organizations
+        self.resolved_org_id = await resolve_org_for_repo(
+            provider='gitlab',
+            full_repo_name=self.full_repo_name,
+            keycloak_user_id=self.user_info.keycloak_user_id,
+        )
+
         if self.v1_enabled:
             # Create dummy conversation metadata
             # Don't save to conversation store
@@ -128,16 +136,28 @@ async def initialize_new_conversation(self) -> ConversationMetadata:
                 selected_repository=self.full_repo_name,
             )

-        conversation_metadata: ConversationMetadata = await initialize_conversation(  # type: ignore[assignment]
+        # Create the conversation store with resolver org routing
+        # (bypasses initialize_conversation to avoid threading enterprise-only
+        # resolver_org_id through the generic OSS interface)
+        store = await SaasConversationStore.get_resolver_instance(
+            get_config(),
+            self.user_info.keycloak_user_id,
+            self.resolved_org_id,
+        )
+
+        conversation_id = uuid4().hex
+        conversation_metadata = ConversationMetadata(
+            trigger=ConversationTrigger.RESOLVER,
+            conversation_id=conversation_id,
+            title=get_default_conversation_title(conversation_id),
             user_id=self.user_info.keycloak_user_id,
-            conversation_id=None,
             selected_repository=self.full_repo_name,
             selected_branch=self._get_branch_name(),
-            conversation_trigger=ConversationTrigger.RESOLVER,
             git_provider=ProviderType.GITLAB,
         )
+        await store.save_metadata(conversation_metadata)

-        self.conversation_id = conversation_metadata.conversation_id
+        self.conversation_id = conversation_id
         return conversation_metadata

     async def create_new_conversation(
@@ -228,7 +248,10 @@ async def _create_v1_conversation(
         )

         # Set up the GitLab user context for the V1 system
-        gitlab_user_context = ResolverUserContext(saas_user_auth=saas_user_auth)
+        gitlab_user_context = ResolverUserContext(
+            saas_user_auth=saas_user_auth,
+            resolver_org_id=self.resolved_org_id,
+        )
         setattr(injector_state, USER_CONTEXT_ATTR, gitlab_user_context)

         async with get_app_conversation_service(
@@ -260,7 +283,7 @@ def _create_gitlab_v1_callback_processor(self):
                 'is_mr': self.is_mr,
                 'discussion_id': getattr(self, 'discussion_id', None),
             },
-            send_summary_instruction=self.send_summary_instruction,
+            should_request_summary=self.send_summary_instruction,
         )

EOF

# Verify the patch was applied (idempotency check)
if ! grep -q "resolve_org_for_repo" enterprise/integrations/gitlab/gitlab_view.py; then
    echo "ERROR: Patch not applied - resolve_org_for_repo not found"
    exit 1
fi

echo "Patch applied successfully"
