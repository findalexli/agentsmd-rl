#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch for APP-1093
# Fixes status display to show "Starting" when server reports STARTING
cat <<'PATCH' | git apply -
diff --git a/frontend/__tests__/utils/status.test.ts b/frontend/__tests__/utils/status.test.ts
index 66dea4c799f9..8ce1aca72421 100644
--- a/frontend/__tests__/utils/status.test.ts
+++ b/frontend/__tests__/utils/status.test.ts
@@ -19,16 +19,17 @@ describe("getStatusCode", () => {
   });

   it("should show runtime status when agent is not ready", () => {
-    // Test case: Agent is loading and runtime is starting
+    // Test case: Agent is loading - but since conversationStatus is not STARTING,
+    // it should fall through to runtime status check
     const result = getStatusCode(
       { id: "", message: "", type: "info", status_update: true }, // statusMessage
       "CONNECTED", // webSocketStatus
-      "STARTING", // conversationStatus
+      "RUNNING", // conversationStatus (not STARTING)
       "STATUS$STARTING_RUNTIME", // runtimeStatus
       AgentState.LOADING, // agentState (not ready)
     );

-    // Should return runtime status since agent is not ready
+    // Should return runtime status since conversation is RUNNING
     expect(result).toBe("STATUS$STARTING_RUNTIME");
   });

@@ -74,8 +75,8 @@ describe("getStatusCode", () => {
     expect(result).toBe(I18nKey.CHAT_INTERFACE$STOPPED);
   });

-  it("should handle null agent state with runtime status", () => {
-    // Test case: No agent state, runtime is starting
+  it("should handle null agent state with conversation status STARTING", () => {
+    // Test case: No agent state, conversation is STARTING
     const result = getStatusCode(
       { id: "", message: "", type: "info", status_update: true }, // statusMessage
       "CONNECTED", // webSocketStatus
@@ -84,8 +85,8 @@ describe("getStatusCode", () => {
       null, // agentState
     );

-    // Should return runtime status since no agent state
-    expect(result).toBe("STATUS$STARTING_RUNTIME");
+    // Should return STARTING since conversationStatus takes priority
+    expect(result).toBe(I18nKey.COMMON$STARTING);
   });

   it("should prioritize task ERROR status over websocket CONNECTING state", () => {
@@ -103,6 +104,20 @@ describe("getStatusCode", () => {
     expect(result).toBe(I18nKey.AGENT_STATUS$ERROR_OCCURRED);
   });

+  it("should show Starting when conversation status is STARTING even with disconnected websocket", () => {
+    // Test case: Server reports STARTING but websocket is disconnected (e.g., during resume)
+    const result = getStatusCode(
+      { id: "", message: "", type: "info", status_update: true }, // statusMessage
+      "DISCONNECTED", // webSocketStatus
+      "STARTING", // conversationStatus (server reports STARTING)
+      "STATUS$STARTING_RUNTIME", // runtimeStatus
+      null, // agentState
+    );
+
+    // Should return STARTING status, not DISCONNECTED
+    expect(result).toBe(I18nKey.COMMON$STARTING);
+  });
+
   it("should show Connecting when task is working and websocket is connecting", () => {
     // Test case: Task is in progress and websocket is connecting normally
     const result = getStatusCode(
diff --git a/frontend/src/utils/status.ts b/frontend/src/utils/status.ts
index e64820b291b9..29e336dcf21a 100644
--- a/frontend/src/utils/status.ts
+++ b/frontend/src/utils/status.ts
@@ -119,6 +119,14 @@ export function getStatusCode(
     return I18nKey.CHAT_INTERFACE$STOPPED;
   }

+  // PRIORITY 2.5: Handle conversation starting state
+  // This must come before WebSocket status check to show "Starting" when
+  // the server reports STARTING, even if WebSocket is temporarily disconnected
+  // during the resume process
+  if (conversationStatus === "STARTING") {
+    return I18nKey.COMMON$STARTING;
+  }
+
   // Prioritize agent state when it indicates readiness, even if runtime status is stale
   const agentIsReady =
     agentState &&
PATCH

# Verify the fix was applied by checking for the distinctive line
grep -q "PRIORITY 2.5: Handle conversation starting state" frontend/src/utils/status.ts
echo "Fix applied successfully: Found 'PRIORITY 2.5' comment in status.ts"
