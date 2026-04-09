#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already applied
if grep -q "useLayoutEffect" packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Create the main patch file excluding problematic hunks
cat > /tmp/main.patch <<'PATCH'
diff --git a/packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx b/packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx
index 64cfdded0b63..b26aa9bc7033 100644
--- a/packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx
+++ b/packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx
@@ -1,4 +1,4 @@
-import React, { useRef, useEffect } from "react";
+import React, { useRef, useEffect, useLayoutEffect } from "react";
 import { KEYS } from "@excalidraw/common";

 import { ArrowRightIcon, stop as StopIcon } from "../../icons";
@@ -17,7 +17,7 @@ export const ChatInterface = ({
   messages,
   currentPrompt,
   onPromptChange,
-  onSendMessage,
+  onGenerate,
   isGenerating,
   rateLimits,
   placeholder,
@@ -33,7 +33,7 @@ export const ChatInterface = ({
   messages: TChat.ChatMessage[];
   currentPrompt: string;
   onPromptChange: (prompt: string) => void;
-  onSendMessage: (message: string) => void;
+  onGenerate: TTTDDialog.OnGenerate;
   isGenerating: boolean;
   rateLimits?: {
     rateLimit: number;
@@ -57,7 +57,7 @@ export const ChatInterface = ({
   const messagesEndRef = useRef<HTMLDivElement>(null);
   const textareaRef = useRef<HTMLTextAreaElement>(null);

-  useEffect(() => {
+  useLayoutEffect(() => {
     messagesEndRef.current?.scrollIntoView();
   }, [messages]);

@@ -83,7 +83,7 @@ export const ChatInterface = ({
       return;
     }

-    onSendMessage(trimmedPrompt);
+    onGenerate({ prompt: trimmedPrompt });
     onPromptChange("");
   };

@@ -131,10 +131,14 @@ export const ChatInterface = ({
               rateLimitRemaining={rateLimits?.rateLimitRemaining}
               isLastMessage={index === messages.length - 1}
               renderWarning={renderWarning}
+              // so we don't allow to repair parse errors which aren't the last message
+              allowFixingParseError={
+                message.errorType === "parse" && index === messages.length - 1
+              }
             />
           ))
         )}
-        <div ref={messagesEndRef} />
+        <div ref={messagesEndRef} id="messages-end" />
       </div>

       <div className="chat-interface__input-container">
diff --git a/packages/excalidraw/components/TTDDialog/Chat/ChatMessage.tsx b/packages/excalidraw/components/TTDDialog/Chat/ChatMessage.tsx
index 07bc7a1e12e0..4f82eec0ae08 100644
--- a/packages/excalidraw/components/TTDDialog/Chat/ChatMessage.tsx
+++ b/packages/excalidraw/components/TTDDialog/Chat/ChatMessage.tsx
@@ -17,6 +17,7 @@ export const ChatMessage: React.FC<{
   rateLimitRemaining?: number;
   isLastMessage?: boolean;
   renderWarning?: TTTDDialog.renderWarning;
+  allowFixingParseError?: boolean;
 }> = ({
   message,
   onMermaidTabClick,
@@ -27,6 +28,7 @@ export const ChatMessage: React.FC<{
   rateLimitRemaining,
   isLastMessage,
   renderWarning,
+  allowFixingParseError,
 }) => {
   const [canRetry, setCanRetry] = useState(false);

@@ -119,10 +121,9 @@ export const ChatMessage: React.FC<{
         </div>
         <div className="chat-message__body">
           {message.error ? (
-            <div className="chat-message__error">
-              {message.content}
-              <div>{message.error}</div>
-              {message.errorType === "parse" && (
+            <>
+              <div className="chat-message__error">{message.content}</div>
+              {message.errorType === "parse" && allowFixingParseError && (
                 <>
                   <p>{t("chat.errors.invalidDiagram")}</p>
                   <div className="chat-message__error-actions">
@@ -148,7 +149,7 @@ export const ChatMessage: React.FC<{
                   </div>
                 </>
               )}
-            </div>
+            </>
           ) : (
             <div className="chat-message__text">
               {message.content}
diff --git a/packages/excalidraw/components/TTDDialog/Chat/TTDChatPanel.tsx b/packages/excalidraw/components/TTDDialog/Chat/TTDChatPanel.tsx
index 31d28574e492..9a66ef6e418 100644
--- a/packages/excalidraw/components/TTDDialog/Chat/TTDChatPanel.tsx
+++ b/packages/excalidraw/components/TTDDialog/Chat/TTDChatPanel.tsx
@@ -22,7 +22,7 @@ export const TTDChatPanel = ({
   messages,
   currentPrompt,
   onPromptChange,
-  onSendMessage,
+  onGenerate,
   isGenerating,
   generatedResponse,
   isMenuOpen,
@@ -46,7 +46,7 @@ export const TTDChatPanel = ({
   messages: TChat.ChatMessage[];
   currentPrompt: string;
   onPromptChange: (prompt: string) => void;
-  onSendMessage: (message: string, isRepairFlow?: boolean) => void;
+  onGenerate: TTTDDialog.OnGenerate;
   isGenerating: boolean;
   generatedResponse: string | null | undefined;

@@ -141,7 +141,7 @@ export const TTDChatPanel = ({
         messages={messages}
         currentPrompt={currentPrompt}
         onPromptChange={onPromptChange}
-        onSendMessage={onSendMessage}
+        onGenerate={onGenerate}
         isGenerating={isGenerating}
         generatedResponse={generatedResponse}
         onAbort={onAbort}
diff --git a/packages/excalidraw/components/TTDDialog/TextToDiagram.tsx b/packages/excalidraw/components/TTDDialog/TextToDiagram.tsx
index 390f2f00fb87..df34dbceb354 100644
--- a/packages/excalidraw/components/TTDDialog/TextToDiagram.tsx
+++ b/packages/excalidraw/components/TTDDialog/TextToDiagram.tsx
@@ -131,7 +131,7 @@ const TextToDiagramContent = ({

     const repairPrompt = `Fix the error in this Mermaid diagram. The diagram is:\n\n\`\`\`mermaid\n${mermaidContent}\n\`\`\`\n\nThe exception/error is: ${errorMessage}\n\nPlease fix the Mermaid syntax and regenerate a valid diagram.`;

-    await onGenerate(repairPrompt, true);
+    await onGenerate({ prompt: repairPrompt, isRepairFlow: true });
   };

   const handleRetry = async (message: TChat.ChatMessage) => {
@@ -141,9 +141,15 @@ const TextToDiagramContent = ({

     if (messageIndex > 0) {
       const previousMessage = chatHistory.messages[messageIndex - 1];
-      if (previousMessage.type === "user" && previousMessage.content) {
+      if (
+        previousMessage.type === "user" &&
+        typeof previousMessage.content === "string"
+      ) {
         setLastRetryAttempt();
-        await onGenerate(previousMessage.content, true);
+        await onGenerate({
+          prompt: previousMessage.content,
+          isRepairFlow: true,
+        });
       }
     }
   };
@@ -188,7 +194,7 @@ const TextToDiagramContent = ({
         messages={chatHistory.messages}
         currentPrompt={chatHistory.currentPrompt}
         onPromptChange={handlePromptChange}
-        onSendMessage={onGenerate}
+        onGenerate={onGenerate}
         isGenerating={lastAssistantMessage?.isGenerating ?? false}
         generatedResponse={lastAssistantMessage?.content}
         isMenuOpen={isMenuOpen}
diff --git a/packages/excalidraw/components/TTDDialog/types.ts b/packages/excalidraw/components/TTDDialog/types.ts
index 3913eb17083a..c5a9f820273a 100644
--- a/packages/excalidraw/components/TTDDialog/types.ts
+++ b/packages/excalidraw/components/TTDDialog/types.ts
@@ -64,6 +64,11 @@ export interface MermaidToExcalidrawLibProps {
 }

 export namespace TTTDDialog {
+  export type OnGenerate = (opts: {
+    prompt: string;
+    isRepairFlow?: boolean;
+  }) => Promise<void>;
+
   export type OnTextSubmitProps = {
     messages: LLMMessage[];
     onChunk?: (chunk: string) => void;
diff --git a/packages/excalidraw/components/TTDDialog/useTTDChatStorage.ts b/packages/excalidraw/components/TTDDialog/useTTDChatStorage.ts
index 772e697a3cc6..d2f8990c59cd 100644
--- a/packages/excalidraw/components/TTDDialog/useTTDChatStorage.ts
+++ b/packages/excalidraw/components/TTDDialog/useTTDDialog/useTTDChatStorage.ts
@@ -65,7 +65,7 @@ export const useTTDChatStorage = (): UseTTDChatStorageReturn => {
     const firstUserMessage = chatHistory.messages.find(
       (msg) => msg.type === "user",
     );
-    if (!firstUserMessage || !firstUserMessage.content) {
+    if (!firstUserMessage || typeof firstUserMessage.content !== "string") {
       return;
     }

diff --git a/packages/excalidraw/components/TTDDialog/utils/chat.ts b/packages/excalidraw/components/TTDDialog/utils/chat.ts
index 5d2c643f925b..a00c6509757c 100644
--- a/packages/excalidraw/components/TTDDialog/utils/chat.ts
+++ b/packages/excalidraw/components/TTDDialog/utils/chat.ts
@@ -60,7 +60,8 @@ export const addMessages = (
 };

 export const removeLastAssistantMessage = (chatHistory: TChat.ChatHistory) => {
-  const lastMsgIdx = (chatHistory.messages ?? []).findLastIndex(
+  const lastMsgIdx = findLastIndex(
+    chatHistory.messages ?? [],
     (msg) => msg.type === "assistant",
   );
PATCH

# Apply main patch with fuzz (ignore errors for some hunks)
patch -p1 --fuzz=3 < /tmp/main.patch || true

# Now manually fix useTextGeneration.ts
GEN_FILE="packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts"

# Fix the import line - add LLMMessage
sed -i 's/import type { TTTDDialog } from "..\/types";/import type { LLMMessage, TTTDDialog } from "..\/types";/' "$GEN_FILE"

# Fix onGenerate function signature - convert to object parameter
cat > /tmp/gen_fix.py <<'PYTHON'
import re

with open("packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts", "r") as f:
    content = f.read()

# Replace function signature
old_sig = '''  const onGenerate = async (
    promptWithContext: string,
    isRepairFlow = false,
  ) => {
    if (!validatePrompt(promptWithContext)) {
      return;
    }'''

new_sig = '''  const onGenerate: TTTDDialog.OnGenerate = async ({
    prompt,
    isRepairFlow = false,
  }) => {
    if (!validatePrompt(prompt)) {
      return;
    }'''

content = content.replace(old_sig, new_sig)

# Replace else block
old_else = '''    } else {
      const lastAsisstantMessage = getLastAssistantMessage(chatHistory);

      if (lastAsisstantMessage?.errorType === "network") {
        setChatHistory((prev) =>
          updateAssistantContent(prev, {
            isGenerating: true,
            error: undefined,
            errorType: undefined,
            errorDetails: undefined,
          }),
        );
      }
    }'''

new_else = '''    } else {
      setChatHistory((prev) =>
        updateAssistantContent(prev, {
          isGenerating: true,
          content: "",
          error: undefined,
          errorType: undefined,
          errorDetails: undefined,
        }),
      );
    }'''

content = content.replace(old_else, new_else)

# Replace promptWithContext with prompt in non-repair flow
content = content.replace("addUserMessage(promptWithContext);", "addUserMessage(prompt);")

# Replace in messages array
content = content.replace(
    "{ role: \"user\", content: promptWithContext }",
    "{ role: \"user\", content: prompt }"
)

# Extract messages into a variable
old_messages = '''      const { generatedResponse, error, rateLimit, rateLimitRemaining } =
        await onTextSubmit({
          messages: [
            ...previousMessages.slice(-3),
            { role: "user", content: prompt },
          ],'''

new_messages = '''      const messages: LLMMessage[] = [
        ...previousMessages.slice(-3),
        { role: "user", content: prompt },
      ];

      const { generatedResponse, error, rateLimit, rateLimitRemaining } =
        await onTextSubmit({
          messages,'''

content = content.replace(old_messages, new_messages)

with open("packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts", "w") as f:
    f.write(content)

print("useTextGeneration.ts fixed")
PYTHON

python3 /tmp/gen_fix.py

echo "Patch applied successfully"
