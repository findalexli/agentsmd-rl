#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the fix patch
cat <<'PATCH' | git apply -
diff --git a/frontend/__tests__/components/v1/get-event-content.test.tsx b/frontend/__tests__/components/v1/get-event-content.test.tsx
index 45d6512fbd83..91851cd772de 100644
--- a/frontend/__tests__/components/v1/get-event-content.test.tsx
+++ b/frontend/__tests__/components/v1/get-event-content.test.tsx
@@ -62,7 +62,7 @@ describe("getEventContent", () => {
   it("uses the action summary as the full action title", () => {
     const { title } = getEventContent(terminalActionEvent);

-    render(<>{title}</>);
+    render(<span>{title}</span>);

     expect(screen.getByText("Check repository status")).toBeInTheDocument();
     expect(screen.queryByText("$ git status")).not.toBeInTheDocument();
@@ -72,7 +72,7 @@ describe("getEventContent", () => {
     const actionWithoutSummary = { ...terminalActionEvent, summary: undefined };
     const { title } = getEventContent(actionWithoutSummary);

-    render(<>{title}</>);
+    render(<span>{title}</span>);

     // Without i18n loaded, the translation key renders as the raw key
     expect(screen.getByText("ACTION_MESSAGE$RUN")).toBeInTheDocument();
@@ -81,13 +81,66 @@ describe("getEventContent", () => {
     ).not.toBeInTheDocument();
   });

+  it("returns empty details for file view action instead of 'Unknown event'", () => {
+    const fileViewAction: ActionEvent = {
+      id: "action-2",
+      timestamp: new Date().toISOString(),
+      source: "agent",
+      thought: [],
+      thinking_blocks: [],
+      action: {
+        kind: "FileEditorAction",
+        command: "view",
+        path: "/workspace/README.md",
+        file_text: null,
+        old_str: null,
+        new_str: null,
+        insert_line: null,
+        view_range: null,
+      },
+      tool_name: "file_editor",
+      tool_call_id: "tool-2",
+      tool_call: {
+        id: "tool-2",
+        type: "function",
+        function: {
+          name: "file_editor",
+          arguments: '{"command":"view","path":"/workspace/README.md"}',
+        },
+      },
+      llm_response_id: "response-2",
+      security_risk: SecurityRisk.LOW,
+    };
+
+    const { title, details } = getEventContent(fileViewAction);
+
+    render(<span>{title}</span>);
+    expect(screen.getByText("ACTION_MESSAGE$READ")).toBeInTheDocument();
+    expect(details).toBe("");
+  });
+
+  it("shows action kind for action-like events missing tool_name/tool_call_id", () => {
+    // Simulate an event that has an action object but fails the strict isActionEvent() guard
+    const malformedEvent = {
+      id: "action-3",
+      timestamp: new Date().toISOString(),
+      source: "agent" as const,
+      action: { kind: "FileEditorAction" },
+    };
+
+    const { title, details } = getEventContent(malformedEvent as any);
+
+    expect(title).toBe("FILEEDITOR");
+    expect(details).toBe("");
+  });
+
   it("reuses the action summary as the full paired observation title", () => {
     const { title } = getEventContent(
       terminalObservationEvent,
       terminalActionEvent,
     );

-    render(<>{title}</>);
+    render(<span>{title}</span>);

     expect(screen.getByText("Check repository status")).toBeInTheDocument();
     expect(screen.queryByText("$ git status")).not.toBeInTheDocument();
diff --git a/frontend/src/components/features/chat/event-content-helpers/get-event-content.tsx b/frontend/src/components/features/chat/event-content-helpers/get-event-content.tsx
index ee75007a053f..da9fa3d3da10 100644
--- a/frontend/src/components/features/chat/event-content-helpers/get-event-content.tsx
+++ b/frontend/src/components/features/chat/event-content-helpers/get-event-content.tsx
@@ -85,6 +85,6 @@ export const getEventContent = (

   return {
     title: title ?? i18n.t("EVENT$UNKNOWN_EVENT"),
-    details: details ?? i18n.t("EVENT$UNKNOWN_EVENT"),
+    details,
   };
 };
diff --git a/frontend/src/components/v1/chat/event-content-helpers/get-event-content.tsx b/frontend/src/components/v1/chat/event-content-helpers/get-event-content.tsx
index 6e6e847639b8..76de6950dd1f 100644
--- a/frontend/src/components/v1/chat/event-content-helpers/get-event-content.tsx
+++ b/frontend/src/components/v1/chat/event-content-helpers/get-event-content.tsx
@@ -263,10 +263,22 @@ export const getEventContent = (
     } else {
       details = getObservationContent(event);
     }
+  } else if (
+    // Lenient fallback for action-like events that fail the strict isActionEvent() guard
+    // (e.g., missing tool_name or tool_call_id). Extract a title from the action kind
+    // so the UI shows something meaningful instead of "Unknown event".
+    event.source === "agent" &&
+    "action" in event &&
+    event.action !== null &&
+    typeof event.action === "object" &&
+    "kind" in event.action &&
+    typeof event.action.kind === "string"
+  ) {
+    title = String(event.action.kind).replace("Action", "").toUpperCase();
   }

   return {
     title: title || i18n.t("EVENT$UNKNOWN_EVENT"),
-    details: details || i18n.t("EVENT$UNKNOWN_EVENT"),
+    details,
   };
 };
PATCH

echo "Fix applied successfully"
