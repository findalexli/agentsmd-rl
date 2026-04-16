#!/bin/bash
set -e

cd /workspace/continue

# Apply the gold patch for hiding thinking indicator when content is empty
patch -p1 <<'PATCH'
diff --git a/gui/src/components/StepContainer/StepContainer.tsx b/gui/src/components/StepContainer/StepContainer.tsx
index abc123..def456 100644
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
index abc123..def456 100644
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

# Idempotency check - verify the patch was applied
grep -q "props.item.reasoning?.text?.trim()" gui/src/components/StepContainer/StepContainer.tsx || {
    echo "ERROR: Patch not applied correctly to StepContainer.tsx"
    exit 1
}

grep -q "thinkingContent?.trim()" gui/src/pages/gui/Chat.tsx || {
    echo "ERROR: Patch not applied correctly to Chat.tsx"
    exit 1
}

echo "Patch applied successfully"
