#!/bin/bash
set -e

cd /workspace/OpenHands/frontend

# Fix 1: Update DEFAULT_SETTINGS.v1_enabled from false to true
sed -i 's/v1_enabled: false,/v1_enabled: true,/' src/services/settings.ts

# Fix 2: Export getSettingsQueryFn from use-settings.ts
sed -i 's/const getSettingsQueryFn = async/export const getSettingsQueryFn = async/' src/hooks/query/use-settings.ts

# Fix 3: Update use-create-conversation.ts to use ensureQueryData
# First, update the imports
cat > /tmp/patch_imports.txt << 'EOF'
--- a/frontend/src/hooks/mutation/use-create-conversation.ts
+++ b/frontend/src/hooks/mutation/use-create-conversation.ts
@@ -3,10 +3,12 @@ import ConversationService from "#/api/conversation-service/conversation-service
 import V1ConversationService from "#/api/conversation-service/v1-conversation-service.api";
 import { PluginSpec } from "#/api/conversation-service/v1-conversation-service.types";
 import { SuggestedTask } from "#/utils/types";
-import { Provider } from "#/types/settings";
+import { Provider, Settings } from "#/types/settings";
 import { CreateMicroagent, Conversation } from "#/api/open-hands.types";
 import { useTracking } from "#/hooks/use-tracking";
-import { useSettings } from "#/hooks/query/use-settings";
+import { getSettingsQueryFn } from "#/hooks/query/use-settings";
+import { DEFAULT_SETTINGS } from "#/services/settings";
+import { useSelectedOrganizationId } from "#/context/use-selected-organization";

 interface CreateConversationVariables {
   query?: string;
EOF

# Apply the imports using sed
sed -i 's/import { Provider } from "#\/types\/settings";/import { Provider, Settings } from "#\/types\/settings";/' src/hooks/mutation/use-create-conversation.ts
sed -i 's/import { useSettings } from "#\/hooks\/query\/use-settings";/import { getSettingsQueryFn } from "#\/hooks\/query\/use-settings";\nimport { DEFAULT_SETTINGS } from "#\/services\/settings";\nimport { useSelectedOrganizationId } from "#\/context\/use-selected-organization";/' src/hooks/mutation/use-create-conversation.ts

# Fix 4: Update the hook body to use ensureQueryData instead of useSettings
sed -i 's/const { data: settings } = useSettings();/const { organizationId } = useSelectedOrganizationId();/' src/hooks/mutation/use-create-conversation.ts

# Fix 5: Replace the useV1 line with the full ensureQueryData logic
# This is complex - we need to replace the simple !!settings?.v1_enabled check with the full try/catch block
sed -i 's/const useV1 = !!settings?.v1_enabled && !createMicroagent;/\/\/ Wait for settings to be loaded before deciding V0 vs V1\n      let settings: Settings;\n      try {\n        settings = await queryClient.ensureQueryData<Settings>({\n          queryKey: ["settings", organizationId],\n          queryFn: getSettingsQueryFn,\n          staleTime: 1000 * 60 * 5,\n        });\n      } catch {\n        \/\/ Settings fetch failed (e.g., 404 for new user) \u2014 use defaults\n        settings = DEFAULT_SETTINGS;\n      }\n\n      const useV1 = settings.v1_enabled \&\& !createMicroagent;/' src/hooks/mutation/use-create-conversation.ts

# Verify the fixes
echo "Verifying fixes..."
grep -q "v1_enabled: true" src/services/settings.ts && echo "[OK] DEFAULT_SETTINGS.v1_enabled is true"
grep -q "export const getSettingsQueryFn" src/hooks/query/use-settings.ts && echo "[OK] getSettingsQueryFn is exported"
grep -q "ensureQueryData" src/hooks/mutation/use-create-conversation.ts && echo "[OK] ensureQueryData is used"
grep -q "useSelectedOrganizationId" src/hooks/mutation/use-create-conversation.ts && echo "[OK] useSelectedOrganizationId is imported"
grep -q "DEFAULT_SETTINGS" src/hooks/mutation/use-create-conversation.ts && echo "[OK] DEFAULT_SETTINGS fallback is used"

echo "All fixes applied successfully!"
