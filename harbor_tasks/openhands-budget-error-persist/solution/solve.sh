#!/bin/bash
set -e

REPO_DIR="/workspace/openhands"
TARGET_FILE="frontend/src/contexts/conversation-websocket-context.tsx"

cd "$REPO_DIR"

# Check if already patched (idempotency)
if grep -q "handleNonErrorEvent" "$TARGET_FILE"; then
    echo "Already patched - handleNonErrorEvent helper found"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/frontend/src/contexts/conversation-websocket-context.tsx b/frontend/src/contexts/conversation-websocket-context.tsx
index 3a51e5c015b4..59aa241fc334 100644
--- a/frontend/src/contexts/conversation-websocket-context.tsx
+++ b/frontend/src/contexts/conversation-websocket-context.tsx
@@ -139,6 +139,25 @@ export function ConversationWebSocketProvider({
   const isPlanFilePath = (path: string | null): boolean =>
     path?.toUpperCase().endsWith("PLAN.MD") ?? false;

+  // Helper to handle error clearing logic for non-error events.
+  // Budget/credit errors persist until an agent event proves the LLM is working.
+  const handleNonErrorEvent = useCallback(
+    (event: { source?: string }) => {
+      const currentError = useErrorMessageStore.getState().errorMessage;
+      const isBudgetError =
+        currentError === I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS;
+      const isAgentEvent = event.source === "agent";
+
+      // Budget errors persist until agent proves LLM is working
+      if (isBudgetError && !isAgentEvent) {
+        return; // Keep budget error visible
+      }
+
+      removeErrorMessage();
+    },
+    [removeErrorMessage],
+  );
+
   // Helper function to update metrics from stats event
   const updateMetricsFromStats = useCallback(
     (event: ConversationStateUpdateEventStats) => {
@@ -380,8 +399,7 @@ export function ConversationWebSocketProvider({
               setErrorMessage(errorEvent.detail);
             }
           } else {
-            // Clear error message on any non-ConversationErrorEvent
-            removeErrorMessage();
+            handleNonErrorEvent(event);
           }

           // Track credit limit reached if AgentErrorEvent has budget-related error
@@ -396,15 +414,7 @@ export function ConversationWebSocketProvider({
               },
               posthog,
             });
-            // Use friendly i18n message for budget/credit errors instead of raw error
-            if (isBudgetOrCreditError(event.error)) {
-              setErrorMessage(I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS);
-              trackCreditLimitReached({
-                conversationId: conversationId || "unknown",
-              });
-            } else {
-              setErrorMessage(event.error);
-            }
+            setErrorMessage(event.error);
           }

           // Clear optimistic user message when a user message is confirmed
@@ -546,8 +556,7 @@ export function ConversationWebSocketProvider({
               setErrorMessage(errorEvent.detail);
             }
           } else {
-            // Clear error message on any non-ConversationErrorEvent
-            removeErrorMessage();
+            handleNonErrorEvent(event);
           }

           // Handle AgentErrorEvent specifically
@@ -562,15 +571,7 @@ export function ConversationWebSocketProvider({
               },
               posthog,
             });
-            // Use friendly i18n message for budget/credit errors instead of raw error
-            if (isBudgetOrCreditError(event.error)) {
-              setErrorMessage(I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS);
-              trackCreditLimitReached({
-                conversationId: conversationId || "unknown",
-              });
-            } else {
-              setErrorMessage(event.error);
-            }
+            setErrorMessage(event.error);
           }

           // Clear optimistic user message when a user message is confirmed
PATCH

echo "Patch applied successfully"
