#!/bin/bash
set -e

cd /workspace/openhands

# Apply the fix for undefined matcher.hooks
cat <<'PATCH' | git apply -
diff --git a/frontend/src/api/conversation-service/v1-conversation-service.types.ts b/frontend/src/api/conversation-service/v1-conversation-service.types.ts
index 7793ad41eff4..ede1bdb492f7 100644
--- a/frontend/src/api/conversation-service/v1-conversation-service.types.ts
+++ b/frontend/src/api/conversation-service/v1-conversation-service.types.ts
@@ -153,7 +153,7 @@ export interface HookDefinition {

 export interface HookMatcher {
   matcher: string; // Pattern: '*', exact match, or regex
-  hooks: HookDefinition[];
+  hooks?: HookDefinition[]; // May be undefined while hooks are still executing on the server
 }

 export interface HookEvent {
diff --git a/frontend/src/components/features/conversation-panel/hook-event-item.tsx b/frontend/src/components/features/conversation-panel/hook-event-item.tsx
index add99f891b96..7adc7e0c3c8c 100644
--- a/frontend/src/components/features/conversation-panel/hook-event-item.tsx
+++ b/frontend/src/components/features/conversation-panel/hook-event-item.tsx
@@ -30,7 +30,7 @@ export function HookEventItem({
   const eventTypeLabel = i18nKey ? t(i18nKey) : hookEvent.event_type;

   const totalHooks = hookEvent.matchers.reduce(
-    (sum, matcher) => sum + matcher.hooks.length,
+    (sum, matcher) => sum + (matcher.hooks ?? []).length,
     0,
   );

diff --git a/frontend/src/components/features/conversation-panel/hook-matcher-content.tsx b/frontend/src/components/features/conversation-panel/hook-matcher-content.tsx
index 587653502fd3..acd288f7ad18 100644
--- a/frontend/src/components/features/conversation-panel/hook-matcher-content.tsx
+++ b/frontend/src/components/features/conversation-panel/hook-matcher-content.tsx
@@ -26,7 +26,7 @@ export function HookMatcherContent({ matcher }: HookMatcherContentProps) {
         <Typography.Text className="text-sm font-semibold text-gray-300 mb-2">
           {t(I18nKey.HOOKS_MODAL$COMMANDS)}
         </Typography.Text>
-        {matcher.hooks.map((hook, index) => (
+        {(matcher.hooks ?? []).map((hook, index) => (
           <div key={`${hook.command}-${index}`} className="mt-2">
             <Pre
               size="default"
PATCH

# Verify the changes were applied (idempotency check)
if ! grep -q "hooks?: HookDefinition\[\]" frontend/src/api/conversation-service/v1-conversation-service.types.ts; then
    echo "ERROR: Type change not applied"
    exit 1
fi

if ! grep -q "matcher.hooks ?? \[\]" frontend/src/components/features/conversation-panel/hook-event-item.tsx; then
    echo "ERROR: hook-event-item fix not applied"
    exit 1
fi

if ! grep -q "matcher.hooks ?? \[\]" frontend/src/components/features/conversation-panel/hook-matcher-content.tsx; then
    echo "ERROR: hook-matcher-content fix not applied"
    exit 1
fi

echo "Fix applied successfully"
