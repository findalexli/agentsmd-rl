#!/bin/bash
set -e

cd /workspace/excalidraw

# Apply the gold patch that fixes the input focus issue during generation
cat <<'PATCH' | git apply -
diff --git a/packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx b/packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx
index b26aa9bc7033..312c49ac9cf9 100644
--- a/packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx
+++ b/packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx
@@ -90,7 +90,9 @@ export const ChatInterface = ({
   const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
     if (event.key === KEYS.ENTER && !event.shiftKey) {
       event.preventDefault();
-      handleSubmit();
+      if (!isGenerating) {
+        handleSubmit();
+      }
     }
   };

@@ -143,7 +145,14 @@ export const ChatInterface = ({

       <div className="chat-interface__input-container">
         <div className="chat-interface__input-outer">
-          <div className="chat-interface__input-wrapper">
+          <div
+            className="chat-interface__input-wrapper"
+            style={{
+              borderColor: isGenerating
+                ? "var(--dialog-border-color)"
+                : undefined,
+            }}
+          >
             <textarea
               ref={textareaRef}
               autoFocus
@@ -152,13 +161,15 @@ export const ChatInterface = ({
               onChange={handleInputChange}
               onKeyDown={handleKeyDown}
               placeholder={
-                rateLimits?.rateLimitRemaining === 0
+                isGenerating
+                  ? t("chat.generating")
+                  : rateLimits?.rateLimitRemaining === 0
                   ? t("chat.rateLimit.messageLimitInputPlaceholder")
                   : messages.length > 0
                   ? t("chat.inputPlaceholderWithMessages")
                   : t("chat.inputPlaceholder", { shortcut: "Shift + Enter" })
               }
-              disabled={isGenerating || rateLimits?.rateLimitRemaining === 0}
+              disabled={rateLimits?.rateLimitRemaining === 0}
               rows={1}
               cols={30}
               onInput={onInput}
diff --git a/packages/excalidraw/locales/en.json b/packages/excalidraw/locales/en.json
index 48cbc8b2d6ac..dd69162c3f35 100644
--- a/packages/excalidraw/locales/en.json
+++ b/packages/excalidraw/locales/en.json
@@ -623,6 +623,7 @@
   "chat": {
     "inputPlaceholder": "Start typing your diagram idea here... ({{shortcut}} for new line)",
     "inputPlaceholderWithMessages": "Continue refining your diagram...",
+    "generating": "Generating...",
     "rateLimitRemaining": "{{count}} requests left today",
     "role": {
       "user": "You",
PATCH

# Verify the patch was applied
if ! grep -q 'if (!isGenerating)' packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx; then
    echo "ERROR: Patch was not applied successfully"
    exit 1
fi

echo "Patch applied successfully!"
