#!/bin/bash
set -e

cd /workspace/openhands

# Check if already patched (idempotency check)
if grep -q "matcher.hooks ?? \[\]" frontend/src/components/features/conversation-panel/hook-event-item.tsx 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/frontend/__tests__/components/features/conversation-panel/hooks-modal.test.tsx b/frontend/__tests__/components/features/conversation-panel/hooks-modal.test.tsx
index 7cb788068df1..8f78ca18e614 100644
--- a/frontend/__tests__/components/features/conversation-panel/hooks-modal.test.tsx
+++ b/frontend/__tests__/components/features/conversation-panel/hooks-modal.test.tsx
@@ -204,4 +204,84 @@ describe("HookEventItem", () => {
     );
     expect(screen.getByText("unknown_event")).toBeInTheDocument();
   });
+
+  it("should not crash when a matcher has undefined hooks", () => {
+    const hookEventWithUndefinedHooks: HookEvent = {
+      event_type: "stop",
+      matchers: [
+        {
+          matcher: "*",
+          hooks: undefined,
+        },
+      ],
+    };
+
+    expect(() =>
+      render(
+        <HookEventItem
+          {...defaultProps}
+          hookEvent={hookEventWithUndefinedHooks}
+        />,
+      ),
+    ).not.toThrow();
+
+    expect(screen.getByText("0 hooks")).toBeInTheDocument();
+  });
+
+  it("should not crash when a matcher has undefined hooks in expanded state", () => {
+    const hookEventWithUndefinedHooks: HookEvent = {
+      event_type: "stop",
+      matchers: [
+        {
+          matcher: "*",
+          hooks: undefined,
+        },
+      ],
+    };
+
+    expect(() =>
+      render(
+        <HookEventItem
+          {...defaultProps}
+          hookEvent={hookEventWithUndefinedHooks}
+          isExpanded={true}
+        />,
+      ),
+    ).not.toThrow();
+  });
+
+  it("should handle a mix of matchers with and without hooks", () => {
+    const mixedHookEvent: HookEvent = {
+      event_type: "pre_tool_use",
+      matchers: [
+        {
+          matcher: "terminal",
+          hooks: [
+            {
+              type: "command",
+              command: "check.sh",
+              timeout: 10,
+            },
+          ],
+        },
+        {
+          matcher: "browser",
+          hooks: undefined,
+        },
+      ],
+    };
+
+    expect(() =>
+      render(
+        <HookEventItem
+          {...defaultProps}
+          hookEvent={mixedHookEvent}
+          isExpanded={true}
+        />,
+      ),
+    ).not.toThrow();
+
+    // Should count only the valid hooks
+    expect(screen.getByText("1 hooks")).toBeInTheDocument();
+  });
 });
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

echo "Patch applied successfully"
