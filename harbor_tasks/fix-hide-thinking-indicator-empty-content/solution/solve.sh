#!/bin/bash
set -e

cd /workspace/continuedev_continue

# Apply the gold patch for hiding thinking indicator for empty content
patch -p1 <<'PATCH'
diff --git a/gui/src/components/StepContainer/StepContainer.tsx b/gui/src/components/StepContainer/StepContainer.tsx
index 540f7cda35f..fc6981d0558 100644
--- a/gui/src/components/StepContainer/StepContainer.tsx
+++ b/gui/src/components/StepContainer/StepContainer.tsx
@@ -85,7 +85,7 @@ export default function StepContainer(props: StepContainerProps) {
           </pre>
         ) : (
           <>
-            {props.item.reasoning?.text && (
+            {props.item.reasoning?.text?.trim() && (
               <ThinkingBlockPeek
                 content={props.item.reasoning.text}
                 index={props.index}
diff --git a/gui/src/pages/gui/Chat.tsx b/gui/src/pages/gui/Chat.tsx
index 45929ec12e2..d37ff2efcef 100644
--- a/gui/src/pages/gui/Chat.tsx
+++ b/gui/src/pages/gui/Chat.tsx
@@ -393,10 +393,14 @@ export function Chat() {
       }

       if (message.role === "thinking") {
+        const thinkingContent = renderChatMessage(message);
+        if (!thinkingContent?.trim()) {
+          return null;
+        }
         return (
           <div className={isBeforeLatestSummary ? "opacity-50" : ""}>
             <ThinkingBlockPeek
-              content={renderChatMessage(message)}
+              content={thinkingContent}
               redactedThinking={message.redactedThinking}
               index={index}
               prevItem={index > 0 ? history[index - 1] : null}
PATCH

echo "Applied gold patch for empty thinking content fix"
