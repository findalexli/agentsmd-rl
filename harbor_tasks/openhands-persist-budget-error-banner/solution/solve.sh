#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch for PR #13786
# Fix: prevent budget/credit error banner from disappearing immediately

# Patch 1: Source file changes
cat > /tmp/fix.patch << 'PATCH'
diff --git a/frontend/src/contexts/conversation-websocket-context.tsx b/frontend/src/contexts/conversation-websocket-context.tsx
index abc123..def456 100644
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

# Apply the source patch
git apply /tmp/fix.patch

# Patch 2: Update test file to match new behavior (raw error instead of i18n key)
cat > /tmp/test.patch << 'TESTPATCH'
diff --git a/frontend/__tests__/conversation-websocket-handler.test.tsx b/frontend/__tests__/conversation-websocket-handler.test.tsx
index abc123..def456 100644
--- a/frontend/__tests__/conversation-websocket-handler.test.tsx
+++ b/frontend/__tests__/conversation-websocket-handler.test.tsx
@@ -337,7 +337,7 @@ describe("Conversation WebSocket Handler", () => {
       });
     });

-    it("should show friendly i18n message for budget/credit errors", async () => {
+    it("should show raw error message for budget/credit errors", async () => {
       // Create a mock AgentErrorEvent with budget-related error message
       const mockBudgetErrorEvent = createMockAgentErrorEvent({
         error:
@@ -356,10 +356,10 @@ describe("Conversation WebSocket Handler", () => {
       expect(screen.getByTestId("error-message")).toHaveTextContent("none");

       // Wait for connection and error event processing
-      // Should show the i18n key instead of raw error message
+      // Should show the raw error message (fix shows error directly without i18n translation)
       await waitFor(() => {
         expect(screen.getByTestId("error-message")).toHaveTextContent(
-          "STATUS$ERROR_LLM_OUT_OF_CREDITS",
+          "litellm.BadRequestError: Litellm_proxyException - ExceededBudget: User=xxx over budget.",
         );
       });
     });
TESTPATCH

# Apply the test patch
git apply /tmp/test.patch

# Idempotency check: verify distinctive line exists
grep -q "Budget errors persist until agent proves LLM is working" frontend/src/contexts/conversation-websocket-context.tsx

echo "Patch applied successfully"
