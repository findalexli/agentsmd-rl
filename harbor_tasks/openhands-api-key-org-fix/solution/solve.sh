#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the fix for API key organization association
patch -p1 <<'PATCH'
diff --git a/enterprise/server/utils/saas_app_conversation_info_injector.py b/enterprise/server/utils/saas_app_conversation_info_injector.py
index 987f42ca10dc..a9432c76b3f1 100644
--- a/enterprise/server/utils/saas_app_conversation_info_injector.py
+++ b/enterprise/server/utils/saas_app_conversation_info_injector.py
@@ -354,6 +354,15 @@ async def save_app_conversation_info(
             user = result.scalar_one_or_none()
             assert user

+            # Determine org_id: prefer API key's org_id if authenticated via API key
+            org_id = user.current_org_id  # Default fallback
+            if hasattr(self.user_context, 'user_auth'):
+                user_auth = self.user_context.user_auth
+                if hasattr(user_auth, 'get_api_key_org_id'):
+                    api_key_org_id = user_auth.get_api_key_org_id()
+                    if api_key_org_id is not None:
+                        org_id = api_key_org_id
+
             # Check if SAAS metadata already exists
             saas_query = select(StoredConversationMetadataSaas).where(
                 StoredConversationMetadataSaas.conversation_id == str(info.id)
@@ -362,16 +371,15 @@ async def save_app_conversation_info(
             existing_saas_metadata = result.scalar_one_or_none()
             assert existing_saas_metadata is None or (
                 existing_saas_metadata.user_id == user_id_uuid
-                and existing_saas_metadata.org_id == user.current_org_id
+                and existing_saas_metadata.org_id == org_id
             )

             if not existing_saas_metadata:
-                # Create new SAAS metadata
-                # Set org_id to user_id as specified in requirements
+                # Create new SAAS metadata with the determined org_id
                 saas_metadata = StoredConversationMetadataSaas(
                     conversation_id=str(info.id),
                     user_id=user_id_uuid,
-                    org_id=user.current_org_id,
+                    org_id=org_id,
                 )
                 self.db_session.add(saas_metadata)

PATCH

echo "Patch applied successfully"
