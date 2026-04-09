#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch for ServerErrorEvent handling
cat <<'PATCH' | git apply -
diff --git a/frontend/__tests__/conversation-websocket-handler.test.tsx b/frontend/__tests__/conversation-websocket-handler.test.tsx
index c60309704019..8a86f5a82085 100644
--- a/frontend/__tests__/conversation-websocket-handler.test.tsx
+++ b/frontend/__tests__/conversation-websocket-handler.test.tsx
@@ -21,6 +21,7 @@ import {
   createMockMessageEvent,
   createMockUserMessageEvent,
   createMockConversationErrorEvent,
+  createMockServerErrorEvent,
   createMockAgentErrorEvent,
   createMockBrowserObservationEvent,
   createMockBrowserNavigateActionEvent,
@@ -364,6 +365,119 @@ describe("Conversation WebSocket Handler", () => {
       });
     });

+    it("should update error message store on ServerErrorEvent", async () => {
+      // ServerErrorEvent represents server-side errors (e.g., MCP configuration errors)
+      // that should be shown as a banner to the user.
+      const mockServerErrorEvent = createMockServerErrorEvent();
+
+      // Set up MSW to send the error event when connection is established
+      mswServer.use(
+        wsLink.addEventListener("connection", ({ client, server }) => {
+          server.connect();
+          // Send the mock error event after connection
+          client.send(JSON.stringify(mockServerErrorEvent));
+        }),
+      );
+
+      // Render components that use both WebSocket and error message store
+      renderWithWebSocketContext(<ErrorMessageStoreComponent />);
+
+      // Initially should show "none"
+      expect(screen.getByTestId("error-message")).toHaveTextContent("none");
+
+      // Wait for connection and error event processing
+      await waitFor(() => {
+        expect(screen.getByTestId("error-message")).toHaveTextContent(
+          "MCP server connection failed: Invalid configuration",
+        );
+      });
+    });
+
+    it("should handle different ServerErrorEvent error codes", async () => {
+      // Test different error codes for ServerErrorEvent
+      const mockServerErrorEvent = createMockServerErrorEvent({
+        code: "RuntimeError",
+        detail: "Agent server runtime error: Out of memory",
+      });
+
+      mswServer.use(
+        wsLink.addEventListener("connection", ({ client, server }) => {
+          server.connect();
+          client.send(JSON.stringify(mockServerErrorEvent));
+        }),
+      );
+
+      renderWithWebSocketContext(<ErrorMessageStoreComponent />);
+
+      await waitFor(() => {
+        expect(screen.getByTestId("error-message")).toHaveTextContent(
+          "Agent server runtime error: Out of memory",
+        );
+      });
+    });
+
+    it("should clear error message when a successful event is received after a ServerErrorEvent", async () => {
+      // This test verifies that error banners disappear when follow-up messages
+      // are sent and received after a ServerErrorEvent.
+      // Note: This test was originally commented out because the implementation
+      // didn't properly clear ServerErrorEvent errors on subsequent events.
+      // After the fix using isDisplayableErrorEvent, this now works correctly.
+      const conversationId = "test-server-error-clear";
+
+      // Set up MSW to mock event count API and send events
+      mswServer.use(
+        http.get(
+          `http://localhost:3000/api/conversations/${conversationId}/events/count`,
+          () => HttpResponse.json(2),
+        ),
+        wsLink.addEventListener("connection", ({ client, server }) => {
+          server.connect();
+
+          // Send ServerErrorEvent first (sets the error banner)
+          const mockServerErrorEvent = createMockServerErrorEvent();
+          client.send(JSON.stringify(mockServerErrorEvent));
+
+          // Send a successful (non-error) event immediately after
+          // This simulates the user sending a follow-up message and receiving a response
+          const mockSuccessEvent = createMockMessageEvent({
+            id: "success-event-after-server-error",
+          });
+          client.send(JSON.stringify(mockSuccessEvent));
+        }),
+      );
+
+      // Verify error message store is initially empty
+      expect(useErrorMessageStore.getState().errorMessage).toBeNull();
+
+      // Render with WebSocket context (minimal component just to trigger connection)
+      renderWithWebSocketContext(
+        <ConnectionStatusComponent />,
+        conversationId,
+        `http://localhost:3000/api/conversations/${conversationId}`,
+      );
+
+      // Wait for connection
+      await waitFor(
+        () => {
+          expect(screen.getByTestId("connection-state")).toHaveTextContent(
+            "OPEN",
+          );
+        },
+        { timeout: 5000 },
+      );
+
+      // Wait for both events to be received and error to be cleared
+      // The error was set by the first event (ServerErrorEvent),
+      // then cleared by the second successful event (MessageEvent).
+      await waitFor(
+        () => {
+          expect(useEventStore.getState().events.length).toBe(2);
+          expect(useErrorMessageStore.getState().errorMessage).toBeNull();
+        },
+        { timeout: 5000 },
+      );
+    });
+
     it("should show friendly i18n message for budget ConversationErrorEvent", async () => {
       const mockBudgetConversationError = createMockConversationErrorEvent({
         detail:
@@ -936,7 +1050,9 @@ describe("Conversation WebSocket Handler", () => {
         http.get(
           `http://localhost:3000/api/v1/conversation/${conversationId}/events/search`,
           async () => {
-            await new Promise((resolve) => setTimeout(resolve, 10));
+            await new Promise<void>((resolve) => {
+              setTimeout(resolve, 10);
+            });
             return HttpResponse.json({
               items: mockHistoryEvents,
             });
@@ -1057,7 +1173,9 @@ describe("Conversation WebSocket Handler", () => {
         http.get(
           `http://localhost:3000/api/v1/conversation/${conversationId}/events/search`,
           async () => {
-            await new Promise((resolve) => setTimeout(resolve, 10));
+            await new Promise<void>((resolve) => {
+              setTimeout(resolve, 10);
+            });
             return HttpResponse.json({
               items: mockHistoryEvents,
             });
diff --git a/frontend/src/contexts/conversation-websocket-context.tsx b/frontend/src/contexts/conversation-websocket-context.tsx
index 3e56c3d2899b..3a51e5c015b4 100644
--- a/frontend/src/contexts/conversation-websocket-context.tsx
+++ b/frontend/src/contexts/conversation-websocket-context.tsx
@@ -27,12 +27,16 @@ import {
   isStatsConversationStateUpdateEvent,
   isExecuteBashActionEvent,
   isExecuteBashObservationEvent,
-  isConversationErrorEvent,
+  isDisplayableErrorEvent,
   isPlanningFileEditorObservationEvent,
   isBrowserObservationEvent,
   isBrowserNavigateActionEvent,
 } from "#/types/v1/type-guards";
 import { ConversationStateUpdateEventStats } from "#/types/v1/core/events/conversation-state-event";
+import type {
+  ConversationErrorEvent,
+  ServerErrorEvent,
+} from "#/types/v1/core/events/conversation-state-event";
 import { handleActionEventCacheInvalidation } from "#/utils/cache-utils";
 import { buildWebSocketUrl } from "#/utils/websocket-url";
 import type {
@@ -352,25 +356,28 @@ export function ConversationWebSocketProvider({
         if (isV1Event(event)) {
           addEvent(event);

-          // Handle ConversationErrorEvent specifically - show error banner
+          // Handle displayable error events - show error banner
           // AgentErrorEvent errors are displayed inline in the chat, not as banners
-          if (isConversationErrorEvent(event)) {
+          if (isDisplayableErrorEvent(event)) {
+            const errorEvent = event as
+              | ConversationErrorEvent
+              | ServerErrorEvent;
             trackError({
-              message: event.detail,
+              message: errorEvent.detail,
               source: "conversation",
               metadata: {
-                eventId: event.id,
-                errorCode: event.code,
+                eventId: errorEvent.id,
+                errorCode: errorEvent.code,
               },
               posthog,
             });
-            if (isBudgetOrCreditError(event.detail)) {
+            if (isBudgetOrCreditError(errorEvent.detail)) {
               setErrorMessage(I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS);
               trackCreditLimitReached({
                 conversationId: conversationId || "unknown",
               });
             } else {
-              setErrorMessage(event.detail);
+              setErrorMessage(errorEvent.detail);
             }
           } else {
             // Clear error message on any non-ConversationErrorEvent
@@ -515,25 +522,28 @@ export function ConversationWebSocketProvider({
           };
           addEvent(eventWithPlanningFlag);

-          // Handle ConversationErrorEvent specifically - show error banner
+          // Handle displayable error events - show error banner
           // AgentErrorEvent errors are displayed inline in the chat, not as banners
-          if (isConversationErrorEvent(event)) {
+          if (isDisplayableErrorEvent(event)) {
+            const errorEvent = event as
+              | ConversationErrorEvent
+              | ServerErrorEvent;
             trackError({
-              message: event.detail,
+              message: errorEvent.detail,
               source: "planning_conversation",
               metadata: {
-                eventId: event.id,
-                errorCode: event.code,
+                eventId: errorEvent.id,
+                errorCode: errorEvent.code,
               },
               posthog,
             });
-            if (isBudgetOrCreditError(event.detail)) {
+            if (isBudgetOrCreditError(errorEvent.detail)) {
               setErrorMessage(I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS);
               trackCreditLimitReached({
                 conversationId: conversationId || "unknown",
               });
             } else {
-              setErrorMessage(event.detail);
+              setErrorMessage(errorEvent.detail);
             }
           } else {
             // Clear error message on any non-ConversationErrorEvent
diff --git a/frontend/src/mocks/mock-ws-helpers.ts b/frontend/src/mocks/mock-ws-helpers.ts
index 84bfb3398973..b9584720c978 100644
--- a/frontend/src/mocks/mock-ws-helpers.ts
+++ b/frontend/src/mocks/mock-ws-helpers.ts
@@ -7,7 +7,10 @@ import {
 import { AgentStateChangeObservation } from "#/types/core/observations";
 import { MessageEvent } from "#/types/v1/core";
 import { AgentErrorEvent } from "#/types/v1/core/events/observation-event";
-import { ConversationErrorEvent } from "#/types/v1/core/events/conversation-state-event";
+import {
+  ConversationErrorEvent,
+  ServerErrorEvent,
+} from "#/types/v1/core/events/conversation-state-event";
 import { MockSessionMessaage } from "./session-history.mock";

 export const generateAgentStateChangeObservation = (
@@ -253,3 +256,19 @@ export const createMockConversationErrorEvent = (
   detail: "Your session has expired. Please log in again.",
   ...overrides,
 });
+
+/**
+ * Creates a mock ServerErrorEvent for testing server-level error handling
+ * These are errors from the agent server (e.g., MCP configuration errors) that should show error banners
+ */
+export const createMockServerErrorEvent = (
+  overrides: Partial<ServerErrorEvent> = {},
+): ServerErrorEvent => ({
+  id: "server-error-123",
+  timestamp: new Date().toISOString(),
+  source: "environment",
+  kind: "ServerErrorEvent",
+  code: "MCPError",
+  detail: "MCP server connection failed: Invalid configuration",
+  ...overrides,
+});
diff --git a/frontend/src/types/v1/core/events/conversation-state-event.ts b/frontend/src/types/v1/core/events/conversation-state-event.ts
index 38105f0adee2..566318f20719 100644
--- a/frontend/src/types/v1/core/events/conversation-state-event.ts
+++ b/frontend/src/types/v1/core/events/conversation-state-event.ts
@@ -130,3 +130,26 @@ export interface ConversationErrorEvent extends BaseEvent {
    */
   detail: string;
 }
+
+// Server error event - contains error information
+export interface ServerErrorEvent extends BaseEvent {
+  /**
+   * Discriminator field for type guards
+   */
+  kind: "ServerErrorEvent";
+
+  /**
+   * The source is always "environment" for server error events
+   */
+  source: "environment";
+
+  /**
+   * Error code (e.g., "MCPError")
+   */
+  code: string;
+
+  /**
+   * Detailed error message
+   */
+  detail: string;
+}
diff --git a/frontend/src/types/v1/core/openhands-event.ts b/frontend/src/types/v1/core/openhands-event.ts
index fc3a46f714fd..5f9b7451393c 100644
--- a/frontend/src/types/v1/core/openhands-event.ts
+++ b/frontend/src/types/v1/core/openhands-event.ts
@@ -13,6 +13,7 @@ import {
   ConversationErrorEvent,
   HookExecutionEvent,
   PauseEvent,
+  ServerErrorEvent,
 } from "./events/index";

 /**
@@ -36,4 +37,5 @@ export type OpenHandsEvent =
   | ConversationStateUpdateEvent
   | ConversationErrorEvent
   // Control events
-  | PauseEvent;
+  | PauseEvent
+  | ServerErrorEvent;
diff --git a/frontend/src/types/v1/type-guards.ts b/frontend/src/types/v1/type-guards.ts
index b4fa1c9f5fa5..cdf0766fe996 100644
--- a/frontend/src/types/v1/type-guards.ts
+++ b/frontend/src/types/v1/type-guards.ts
@@ -19,6 +19,7 @@ import {
   ConversationStateUpdateEventFullState,
   ConversationStateUpdateEventStats,
   ConversationErrorEvent,
+  ServerErrorEvent,
 } from "./core/events/conversation-state-event";
 import { HookExecutionEvent } from "./core/events/hook-execution-event";
 import { SystemPromptEvent } from "./core/events/system-event";
@@ -193,6 +194,21 @@ export const isConversationErrorEvent = (
 ): event is ConversationErrorEvent =>
   "kind" in event && event.kind === "ConversationErrorEvent";

+/**
+ * Type guard function to check if an event is a server error event
+ */
+export const isServerErrorEvent = (
+  event: OpenHandsEvent,
+): event is ServerErrorEvent =>
+  "kind" in event && event.kind === "ServerErrorEvent";
+
+/**
+ * Type guard function to check if an event is a displayable error event
+ * (ConversationErrorEvent or ServerErrorEvent) - both should show as error banners
+ */
+export const isDisplayableErrorEvent = (event: OpenHandsEvent): boolean =>
+  isConversationErrorEvent(event) || isServerErrorEvent(event);
+
 /**
  * Type guard function to check if an event is a hook execution event
  */
PATCH

echo "Patch applied successfully"
