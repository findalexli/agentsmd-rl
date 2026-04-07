#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q 'queued_message_interrupt' packages/agent-runtime/src/types/event.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply --whitespace=fix <<'PATCH_EOF_13343'
diff --git a/.agents/skills/electron-testing/SKILL.md b/.agents/skills/electron-testing/SKILL.md
new file mode 100644
index 00000000000..184fd95bd31
--- /dev/null
+++ b/.agents/skills/electron-testing/SKILL.md
@@ -0,0 +1,215 @@
+---
+name: electron-testing
+description: Electron desktop app automation testing using agent-browser CLI. Use when testing UI features in the running Electron app, verifying visual state, interacting with the desktop app, or running manual QA scenarios. Triggers on 'test in electron', 'test desktop', 'electron test', 'manual test', or UI verification tasks.
+---
+
+# Electron Automation Testing with agent-browser
+
+Use the `agent-browser` CLI to automate and test the LobeHub desktop Electron app.
+
+## Prerequisites
+
+- `agent-browser` CLI installed globally (`agent-browser --version`)
+- Working directory must be `apps/desktop/` when starting Electron
+
+## Quick Start
+
+```bash
+# 1. Kill existing instances
+pkill -f "Electron" 2> /dev/null
+pkill -f "electron-vite" 2> /dev/null
+pkill -f "agent-browser" 2> /dev/null
+sleep 3
+
+# 2. Start Electron with CDP (MUST cd to apps/desktop first)
+cd apps/desktop && ELECTRON_ENABLE_LOGGING=1 npx electron-vite dev -- --remote-debugging-port=9222 > /tmp/electron-dev.log 2>&1 &
+
+# 3. Wait for startup (poll for "starting electron" in logs)
+for i in $(seq 1 12); do
+  sleep 5
+  if strings /tmp/electron-dev.log 2> /dev/null | grep -q "starting electron"; then
+    echo "ready"
+    break
+  fi
+done
+
+# 4. Wait for renderer to load, then connect
+sleep 15 && agent-browser --cdp 9222 wait 3000
+```
+
+**Critical:** `npx electron-vite dev` MUST run from `apps/desktop/` directory, not project root. Running from root will fail silently (no `initUrl` in logs).
+
+## Connecting to Electron
+
+```bash
+agent-browser --cdp 9222 snapshot -i    # Interactive elements only
+agent-browser --cdp 9222 snapshot -i -C # Include contenteditable elements
+```
+
+Always use `--cdp 9222`. The `--auto-connect` flag is unreliable.
+
+## Core Workflow
+
+### 1. Snapshot → Find Elements
+
+```bash
+agent-browser --cdp 9222 snapshot -i
+```
+
+Returns element refs like `@e1`, `@e2`. **Refs are ephemeral** — re-snapshot after any page change (click, navigation, HMR).
+
+### 2. Interact
+
+```bash
+agent-browser --cdp 9222 click @e5
+agent-browser --cdp 9222 type @e3 "text" # Character by character (for contenteditable)
+agent-browser --cdp 9222 fill @e3 "text" # Bulk fill (for regular inputs)
+agent-browser --cdp 9222 press Enter
+agent-browser --cdp 9222 scroll down 500
+```
+
+### 3. Wait
+
+```bash
+agent-browser --cdp 9222 wait 2000               # Wait ms
+agent-browser --cdp 9222 wait --load networkidle # Wait for network
+```
+
+Avoid `agent-browser wait` for long durations (>30s) — it blocks the daemon. Use `sleep N` in bash instead, then take a new snapshot/screenshot.
+
+### 4. Screenshot & Verify
+
+```bash
+agent-browser --cdp 9222 screenshot   # Save to ~/.agent-browser/tmp/screenshots/
+agent-browser --cdp 9222 get text @e1 # Get element text
+agent-browser --cdp 9222 get url      # Get current URL
+```
+
+Read screenshots with the `Read` tool for visual verification.
+
+### 5. Evaluate JavaScript
+
+```bash
+agent-browser --cdp 9222 eval "document.title"
+```
+
+For multi-line JS, use `--stdin`:
+
+```bash
+agent-browser --cdp 9222 eval --stdin << 'EVALEOF'
+(function() {
+  var chat = window.__LOBE_STORES.chat();
+  return JSON.stringify({
+    totalOps: Object.keys(chat.operations).length,
+    queue: chat.queuedMessages,
+  });
+})()
+EVALEOF
+```
+
+## LobeHub-Specific Patterns
+
+### Access Zustand Store State
+
+The app exposes stores via `window.__LOBE_STORES` (dev mode only):
+
+```bash
+agent-browser --cdp 9222 eval --stdin << 'EVALEOF'
+(function() {
+  var chat = window.__LOBE_STORES.chat();
+  var ops = Object.values(chat.operations);
+  return JSON.stringify({
+    ops: ops.map(function(o) { return { type: o.type, status: o.status }; }),
+    activeAgent: chat.activeAgentId,
+    activeTopic: chat.activeTopicId,
+  });
+})()
+EVALEOF
+```
+
+### Find the Chat Input
+
+The chat input is a contenteditable div. Regular `snapshot -i` won't find it — use `-C`:
+
+```bash
+agent-browser --cdp 9222 snapshot -i -C 2>&1 | grep "editable"
+# Output: - generic [ref=e48] editable [contenteditable]:
+```
+
+### Navigate to an Agent
+
+```bash
+# Snapshot to find agent links in sidebar
+agent-browser --cdp 9222 snapshot -i 2>&1 | grep -i "agent-name"
+# Click the agent link
+agent-browser --cdp 9222 click @e<ref>
+agent-browser --cdp 9222 wait 2000
+```
+
+### Send a Chat Message
+
+```bash
+# 1. Find contenteditable input
+agent-browser --cdp 9222 snapshot -i -C 2>&1 | grep "editable"
+# 2. Click, type, send
+agent-browser --cdp 9222 click @e<ref>
+agent-browser --cdp 9222 type @e<ref> "Hello world"
+agent-browser --cdp 9222 press Enter
+```
+
+### Wait for Agent to Complete
+
+Don't use `agent-browser wait` for long AI generation. Use `sleep` + screenshot:
+
+```bash
+sleep 60 && agent-browser --cdp 9222 scroll down 5000 && agent-browser --cdp 9222 screenshot
+```
+
+Or poll the store for operation status:
+
+```bash
+agent-browser --cdp 9222 eval --stdin << 'EVALEOF'
+(function() {
+  var chat = window.__LOBE_STORES.chat();
+  var ops = Object.values(chat.operations);
+  var running = ops.filter(function(o) { return o.status === 'running'; });
+  return running.length === 0 ? 'done' : 'running: ' + running.length;
+})()
+EVALEOF
+```
+
+### Install Error Interceptor
+
+Capture `console.error` from the app for debugging:
+
+```bash
+agent-browser --cdp 9222 eval --stdin << 'EVALEOF'
+(function() {
+  window.__CAPTURED_ERRORS = [];
+  var orig = console.error;
+  console.error = function() {
+    var msg = Array.from(arguments).map(function(a) {
+      if (a instanceof Error) return a.message;
+      return typeof a === 'object' ? JSON.stringify(a) : String(a);
+    }).join(' ');
+    window.__CAPTURED_ERRORS.push(msg);
+    orig.apply(console, arguments);
+  };
+  return 'installed';
+})()
+EVALEOF
+
+# Later, check captured errors:
+agent-browser --cdp 9222 eval "JSON.stringify(window.__CAPTURED_ERRORS)"
+```
+
+## Gotchas
+
+- **`npx electron-vite dev` must run from `apps/desktop/`** — running from project root fails silently
+- **HMR invalidates everything** — after code changes, refs break, page may crash. Re-snapshot or restart Electron
+- **`agent-browser wait` blocks the daemon** — for waits >30s, use bash `sleep` instead
+- **Daemon can get stuck** — if commands hang, `pkill -f agent-browser` to reset the daemon
+- **`snapshot -i` doesn't find contenteditable** — always use `snapshot -i -C` to find rich text editors
+- **`fill` doesn't work on contenteditable** — use `type` for the chat input
+- **Screenshots go to `~/.agent-browser/tmp/screenshots/`** — read them with the `Read` tool
+- **Store is at `window.__LOBE_STORES`** not `window.__ZUSTAND_STORES__` — use `.chat()` to get current state
diff --git a/packages/agent-runtime/src/agents/GeneralChatAgent.ts b/packages/agent-runtime/src/agents/GeneralChatAgent.ts
index c5b09110c98..43bb1a12255 100644
--- a/packages/agent-runtime/src/agents/GeneralChatAgent.ts
+++ b/packages/agent-runtime/src/agents/GeneralChatAgent.ts
@@ -547,6 +547,10 @@ export class GeneralChatAgent implements Agent {
           };
         }
 
+        if (context.stepContext?.hasQueuedMessages) {
+          return { reason: 'queued_message_interrupt', type: 'finish' };
+        }
+
         // No pending tools, continue to call LLM with tool results
         return this.toLLMCall({
           messages: state.messages,
@@ -577,6 +581,12 @@ export class GeneralChatAgent implements Agent {
           };
         }
 
+        // If there are queued user messages, finish early so the queue
+        // can be processed as a new operation with full context
+        if (context.stepContext?.hasQueuedMessages) {
+          return { reason: 'queued_message_interrupt', type: 'finish' };
+        }
+
         // No pending tools, continue to call LLM with tool results
         return this.toLLMCall({
           messages: state.messages,
@@ -605,6 +615,10 @@ export class GeneralChatAgent implements Agent {
         // Async tasks batch completed, continue to call LLM with results
         const { parentMessageId } = context.payload as TasksBatchResultPayload;
 
+        if (context.stepContext?.hasQueuedMessages) {
+          return { reason: 'queued_message_interrupt', type: 'finish' };
+        }
+
         // Inject a virtual user message to force the model to summarize or continue
         // This fixes an issue where some models (e.g., Kimi K2) return empty content
         // when the last message is a task result, thinking the task is already done
diff --git a/packages/agent-runtime/src/types/event.ts b/packages/agent-runtime/src/types/event.ts
index c2a972c31dd..eb82a6860ee 100644
--- a/packages/agent-runtime/src/types/event.ts
+++ b/packages/agent-runtime/src/types/event.ts
@@ -66,6 +66,7 @@ export type FinishReason =
   | 'cost_limit_exceeded' // Reached cost limit
   | 'timeout' // Execution timeout
   | 'agent_decision' // Agent decided to finish
+  | 'queued_message_interrupt' // Soft interrupt: user queued a message during execution
   | 'error_recovery' // Finished due to unrecoverable error
   | 'system_shutdown'; // System is shutting down
 
diff --git a/packages/agent-runtime/src/utils/stepContextComputer.ts b/packages/agent-runtime/src/utils/stepContextComputer.ts
index 606c53e51ff..556068556fc 100644
--- a/packages/agent-runtime/src/utils/stepContextComputer.ts
+++ b/packages/agent-runtime/src/utils/stepContextComputer.ts
@@ -13,6 +13,10 @@ export interface ComputeStepContextParams {
    * Activated tool identifiers accumulated from lobe-activator messages
    */
   activatedToolIds?: string[];
+  /**
+   * Whether there are queued user messages waiting to be processed
+   */
+  hasQueuedMessages?: boolean;
   /**
    * Pre-computed todos state from message selector
    * Should be computed using selectTodosFromMessages in chat store selectors
@@ -36,11 +40,13 @@ export interface ComputeStepContextParams {
 export const computeStepContext = ({
   activatedSkills,
   activatedToolIds,
+  hasQueuedMessages,
   todos,
 }: ComputeStepContextParams): RuntimeStepContext => {
   return {
     ...(activatedSkills?.length && { activatedSkills }),
     ...(activatedToolIds?.length && { activatedToolIds }),
+    ...(hasQueuedMessages && { hasQueuedMessages }),
     ...(todos && { todos }),
   };
 };
diff --git a/packages/types/src/stepContext.ts b/packages/types/src/stepContext.ts
index b6a48182b70..f758a93e9c5 100644
--- a/packages/types/src/stepContext.ts
+++ b/packages/types/src/stepContext.ts
@@ -130,6 +130,12 @@ export interface RuntimeStepContext {
    * Tools once activated remain active for the rest of the conversation
    */
   activatedToolIds?: string[];
+  /**
+   * Whether there are queued user messages waiting to be processed.
+   * When true after tool completion, the agent should finish early
+   * so the queued messages can be sent as a new operation.
+   */
+  hasQueuedMessages?: boolean;
   /**
    * Page Editor context for current step
    * Contains the latest XML structure fetched at each step
diff --git a/src/features/Conversation/ChatInput/QueueTray.tsx b/src/features/Conversation/ChatInput/QueueTray.tsx
new file mode 100644
index 00000000000..2e7d3ae2719
--- /dev/null
+++ b/src/features/Conversation/ChatInput/QueueTray.tsx
@@ -0,0 +1,87 @@
+'use client';
+
+import { ActionIcon, Flexbox, Icon } from '@lobehub/ui';
+import { createStaticStyles } from 'antd-style';
+import { ListEnd, Trash2 } from 'lucide-react';
+import { memo, useMemo } from 'react';
+
+import { useChatStore } from '@/store/chat';
+import { operationSelectors } from '@/store/chat/selectors';
+import { messageMapKey } from '@/store/chat/utils/messageMapKey';
+
+import { useConversationStore } from '../store';
+
+const styles = createStaticStyles(({ css, cssVar }) => ({
+  container: css`
+    border: 1px solid ${cssVar.colorBorderSecondary};
+    border-block-end: none;
+    border-radius: 12px 12px 0 0;
+    background: ${cssVar.colorBgContainer};
+  `,
+  icon: css`
+    flex-shrink: 0;
+    color: ${cssVar.colorTextDescription};
+  `,
+  item: css`
+    padding-block: 6px 4px;
+    padding-inline: 12px 8px;
+  `,
+  itemDivider: css`
+    border-block-start: 1px solid ${cssVar.colorBorderSecondary};
+  `,
+  text: css`
+    overflow: hidden;
+
+    font-size: 13px;
+    line-height: 1.4;
+    text-overflow: ellipsis;
+    white-space: nowrap;
+  `,
+}));
+
+const QueueTray = memo(() => {
+  const context = useConversationStore((s) => s.context);
+
+  const contextKey = useMemo(
+    () =>
+      messageMapKey({
+        agentId: context.agentId,
+        groupId: context.groupId,
+        topicId: context.topicId,
+      }),
+    [context.agentId, context.groupId, context.topicId],
+  );
+
+  const queuedMessages = useChatStore((s) => operationSelectors.getQueuedMessages(context)(s));
+  const removeQueuedMessage = useChatStore((s) => s.removeQueuedMessage);
+
+  if (queuedMessages.length === 0) return null;
+
+  return (
+    <Flexbox className={styles.container} gap={0}>
+      {queuedMessages.map((msg, index) => (
+        <Flexbox
+          horizontal
+          align="center"
+          className={index > 0 ? `${styles.item} ${styles.itemDivider}` : styles.item}
+          gap={8}
+          key={msg.id}
+        >
+          <Icon className={styles.icon} icon={ListEnd} size={14} />
+          <Flexbox className={styles.text} flex={1}>
+            {msg.content}
+          </Flexbox>
+          <ActionIcon
+            icon={Trash2}
+            size="small"
+            onClick={() => removeQueuedMessage(contextKey, msg.id)}
+          />
+        </Flexbox>
+      ))}
+    </Flexbox>
+  );
+});
+
+QueueTray.displayName = 'QueueTray';
+
+export default QueueTray;
diff --git a/src/features/Conversation/ChatInput/index.tsx b/src/features/Conversation/ChatInput/index.tsx
index e4d901acb88..e28d50139bd 100644
--- a/src/features/Conversation/ChatInput/index.tsx
+++ b/src/features/Conversation/ChatInput/index.tsx
@@ -15,10 +15,12 @@ import {
   type SendButtonProps,
 } from '@/features/ChatInput/store/initialState';
 import { useChatStore } from '@/store/chat';
+import { operationSelectors } from '@/store/chat/selectors';
 import { fileChatSelectors, useFileStore } from '@/store/file';
 
 import WideScreenContainer from '../../WideScreenContainer';
 import { messageStateSelectors, useConversationStore } from '../store';
+import QueueTray from './QueueTray';
 
 export interface ChatInputProps {
   /**
@@ -106,6 +108,7 @@ const ChatInput = memo<ChatInputProps>(
     const { t } = useTranslation('chat');
 
     // ConversationStore state
+    const context = useConversationStore((s) => s.context);
     const [agentId, inputMessage, sendMessage, stopGenerating] = useConversationStore((s) => [
       s.context.agentId,
       s.inputMessage,
@@ -127,9 +130,15 @@ const ChatInput = memo<ChatInputProps>(
     const contextList = useFileStore(fileChatSelectors.chatContextSelections);
     const isUploadingFiles = useFileStore(fileChatSelectors.isUploadingFiles);
 
+    // Queue state
+    const hasQueuedMessages = useChatStore(
+      (s) => operationSelectors.queuedMessageCount(context)(s) > 0,
+    );
+
     // Computed state
     const isInputEmpty = !inputMessage.trim() && fileList.length === 0 && contextList.length === 0;
-    const disabled = isInputEmpty || isUploadingFiles || isInputLoading;
+    // Input stays enabled during agent execution — messages are queued
+    const disabled = isInputEmpty || isUploadingFiles;
 
     // Send handler - gets message, clears editor immediately, then sends
     const handleSend: SendButtonHandler = useCallback(
@@ -140,7 +149,7 @@ const ChatInput = memo<ChatInputProps>(
         const currentIsUploading = fileChatSelectors.isUploadingFiles(fileStore);
         const currentContextList = fileChatSelectors.chatContextSelections(fileStore);
 
-        if (currentIsUploading || isInputLoading) return;
+        if (currentIsUploading) return;
 
         // Get content before clearing
         const message = getMarkdownContent();
@@ -166,7 +175,7 @@ const ChatInput = memo<ChatInputProps>(
         // Fire and forget - send with captured message
         await sendMessage({ editorData, files: currentFileList, message, pageSelections });
       },
-      [isInputLoading, sendMessage],
+      [sendMessage],
     );
 
     const sendButtonProps: SendButtonProps = {
@@ -177,7 +186,9 @@ const ChatInput = memo<ChatInputProps>(
     };
 
     const defaultContent = (
-      <WideScreenContainer style={skipScrollMarginWithList ? { marginTop: -12 } : undefined}>
+      <WideScreenContainer
+        style={skipScrollMarginWithList ? { marginTop: -12, position: 'relative' } : undefined}
+      >
         {sendMessageErrorMsg && (
           <Flexbox paddingBlock={'0 6px'} paddingInline={12}>
             <Alert
@@ -188,6 +199,20 @@ const ChatInput = memo<ChatInputProps>(
             />
           </Flexbox>
         )}
+        {hasQueuedMessages && (
+          <Flexbox
+            paddingInline={12}
+            style={{
+              position: 'absolute',
+              zIndex: 10,
+              bottom: '100%',
+              left: 12,
+              right: 12,
+            }}
+          >
+            <QueueTray />
+          </Flexbox>
+        )}
         <DesktopChatInput
           actionBarStyle={actionBarStyle}
           borderRadius={12}
diff --git a/src/store/chat/slices/aiChat/actions/conversationLifecycle.ts b/src/store/chat/slices/aiChat/actions/conversationLifecycle.ts
index 90a412cf425..d6888a4b367 100644
--- a/src/store/chat/slices/aiChat/actions/conversationLifecycle.ts
+++ b/src/store/chat/slices/aiChat/actions/conversationLifecycle.ts
@@ -206,6 +206,30 @@ export class ConversationLifecycleActionImpl {
     // if message is empty or no files, then stop
     if (!message && !hasFile) return;
 
+    // ━━━ Message Queue: enqueue if agent is currently running ━━━
+    // Check if there's a running execAgentRuntime operation in the current context.
+    // If so, enqueue the message instead of starting a new operation.
+    const currentContextKey = messageMapKey(operationContext);
+    const contextOpIds = this.#get().operationsByContext[currentContextKey] || [];
+    const runningAgentOp = contextOpIds
+      .map((id) => this.#get().operations[id])
+      .find((op) => op && op.type === 'execAgentRuntime' && op.status === 'running');
+
+    if (runningAgentOp) {
+      this.#get().enqueueMessage(
+        currentContextKey,
+        {
+          id: nanoid(),
+          content: message,
+          files: fileIdList,
+          interruptMode: 'soft',
+          createdAt: Date.now(),
+        },
+        runningAgentOp.id,
+      );
+      return;
+    }
+
     if (onlyAddUserMessage) {
       await this.#get().addUserMessage({ message, fileList: fileIdList });
 
diff --git a/src/store/chat/slices/aiChat/actions/streamingExecutor.ts b/src/store/chat/slices/aiChat/actions/streamingExecutor.ts
index eed9334339e..d37a29ddb61 100644
--- a/src/store/chat/slices/aiChat/actions/streamingExecutor.ts
+++ b/src/store/chat/slices/aiChat/actions/streamingExecutor.ts
@@ -27,7 +27,7 @@ import { messageService } from '@/services/message';
 import { getAgentStoreState } from '@/store/agent';
 import { agentSelectors } from '@/store/agent/selectors';
 import { createAgentExecutors } from '@/store/chat/agents/createAgentExecutors';
-import { type ChatStore } from '@/store/chat/store';
+import { type ChatStore, useChatStore } from '@/store/chat/store';
 import { pageAgentRuntime } from '@/store/tool/slices/builtin/executors/lobe-page-agent';
 import { type StoreSetter } from '@/store/types';
 import { toolInterventionSelectors } from '@/store/user/selectors';
@@ -42,6 +42,7 @@ import {
   selectActivatedToolIdsFromMessages,
   selectTodosFromMessages,
 } from '../../message/selectors/dbMessage';
+import { mergeQueuedMessages } from '../../operation/types';
 
 const log = debug('lobe-store:streaming-executor');
 
@@ -486,6 +487,9 @@ export class StreamingExecutorActionImpl {
       nextContext.phase,
     );
 
+    // Compute contextKey for message queue (per-context, not per-operation)
+    const contextKey = messageKey;
+
     // Execute the agent runtime loop
     let stepCount = 0;
     while (state.status !== 'done' && state.status !== 'error') {
@@ -516,7 +520,13 @@ export class StreamingExecutorActionImpl {
       const activatedToolIds = selectActivatedToolIdsFromMessages(currentDBMessages);
       // Accumulate activated skills from activateSkill messages
       const activatedSkills = selectActivatedSkillsFromMessages(currentDBMessages);
-      const stepContext = computeStepContext({ activatedSkills, activatedToolIds, todos });
+      const hasQueuedMessages = (this.#get().queuedMessages[contextKey]?.length ?? 0) > 0;
+      const stepContext = computeStepContext({
+        activatedSkills,
+        activatedToolIds,
+        hasQueuedMessages,
+        todos,
+      });
 
       // If page agent is enabled, get the latest XML for stepPageEditor
       if (nextContext.initialContext?.pageEditor) {
@@ -658,6 +668,46 @@ export class StreamingExecutorActionImpl {
       log('[internal_execAgentRuntime] afterCompletion callbacks executed');
     }
 
+    // If completed successfully and queue has messages, drain and trigger new sendMessage.
+    // Only drain on success — on error the queue is left intact so messages aren't lost.
+    if (state.status === 'done') {
+      const remainingQueued = this.#get().drainQueuedMessages(contextKey);
+      if (remainingQueued.length > 0) {
+        const merged = mergeQueuedMessages(remainingQueued);
+        log(
+          '[internal_execAgentRuntime] %d queued messages after completion, triggering new sendMessage',
+          remainingQueued.length,
+        );
+
+        this.#get().completeOperation(operationId);
+
+        const completedOp = this.#get().operations[operationId];
+        if (completedOp?.context.agentId) {
+          this.#get().markUnreadCompleted(completedOp.context.agentId, completedOp.context.topicId);
+        }
+
+        const execContext = { ...context };
+        const mergedContent = merged.content;
+        // Convert file id strings — sendMessage only reads f.id from each item
+        const mergedFiles =
+          merged.files.length > 0 ? merged.files.map((id) => ({ id }) as any) : undefined;
+
+        setTimeout(() => {
+          useChatStore
+            .getState()
+            .sendMessage({ message: mergedContent, files: mergedFiles, context: execContext })
+            .catch((e: unknown) => {
+              console.error(
+                '[internal_execAgentRuntime] sendMessage for queued content failed:',
+                e,
+              );
+            });
+        }, 100);
+
+        return; // Skip the normal completion below
+      }
+    }
+
     // Complete operation based on final state
     switch (state.status) {
       case 'done': {
diff --git a/src/store/chat/slices/operation/actions.ts b/src/store/chat/slices/operation/actions.ts
index 6e5c53d76bb..c78e1275472 100644
--- a/src/store/chat/slices/operation/actions.ts
+++ b/src/store/chat/slices/operation/actions.ts
@@ -17,6 +17,7 @@ import {
   type OperationMetadata,
   type OperationStatus,
   type OperationType,
+  type QueuedMessage,
 } from './types';
 
 const n = setNamespace('operation');
@@ -159,11 +160,7 @@ export class OperationActionsImpl {
 
         // Update context index (if agentId exists)
         if (context.agentId) {
-          const contextKey = messageMapKey({
-            agentId: context.agentId,
-            groupId: context.groupId,
-            topicId: context.topicId !== undefined ? context.topicId : null,
-          });
+          const contextKey = messageMapKey(context as MessageMapKeyInput);
           if (!state.operationsByContext[contextKey]) {
             state.operationsByContext[contextKey] = [];
           }
@@ -581,11 +578,7 @@ export class OperationActionsImpl {
 
           // Remove from context index
           if (op.context.agentId) {
-            const contextKey = messageMapKey({
-              agentId: op.context.agentId,
-              groupId: op.context.groupId,
-              topicId: op.context.topicId !== undefined ? op.context.topicId : null,
-            });
+            const contextKey = messageMapKey(op.context as MessageMapKeyInput);
             const contextIndex = state.operationsByContext[contextKey];
             if (contextIndex) {
               state.operationsByContext[contextKey] = contextIndex.filter(
@@ -689,6 +682,87 @@ export class OperationActionsImpl {
       n(`clearUnreadCompleted/topic/${topicId}`),
     );
   };
+  // ━━━ Message Queue Actions ━━━
+
+  /**
+   * Enqueue a message for a conversation context.
+   * If a hard interrupt, also cancel the running operation.
+   */
+  enqueueMessage = (
+    contextKey: string,
+    message: QueuedMessage,
+    runningOperationId?: string,
+  ): void => {
+    log(
+      '[enqueueMessage] contextKey=%s, messageId=%s, mode=%s',
+      contextKey,
+      message.id,
+      message.interruptMode,
+    );
+
+    this.#set(
+      produce((state: ChatStore) => {
+        const queue = state.queuedMessages[contextKey] ?? [];
+        queue.push(message);
+        state.queuedMessages[contextKey] = queue;
+      }),
+      false,
+      n(`enqueueMessage/${contextKey}`),
+    );
+
+    // Hard interrupt: cancel the running operation
+    if (message.interruptMode === 'hard' && runningOperationId) {
+      const op = this.#get().operations[runningOperationId];
+      if (op?.status === 'running') {
+        log('[enqueueMessage] Hard interrupt, cancelling operation %s', runningOperationId);
+        this.#get().cancelOperation(runningOperationId, 'hard_interrupt');
+      }
+    }
+  };
+
+  /**
+   * Drain all queued messages for a context (atomic take-all).
+   */
+  drainQueuedMessages = (contextKey: string): QueuedMessage[] => {
+    const queue = this.#get().queuedMessages[contextKey];
+    if (!queue || queue.length === 0) return [];
+
+    const messages = [...queue];
+
+    this.#set(
+      produce((state: ChatStore) => {
+        state.queuedMessages[contextKey] = [];
+      }),
+      false,
+      n(`drainQueuedMessages/${contextKey}`),
+    );
+
+    log('[drainQueuedMessages] contextKey=%s, drained %d', contextKey, messages.length);
+    return messages;
+  };
+
+  removeQueuedMessage = (contextKey: string, messageId: string): void => {
+    this.#set(
+      produce((state: ChatStore) => {
+        const queue = state.queuedMessages[contextKey];
+        if (!queue) return;
+        const idx = queue.findIndex((m) => m.id === messageId);
+        if (idx >= 0) queue.splice(idx, 1);
+      }),
+      false,
+      n(`removeQueuedMessage/${contextKey}/${messageId}`),
+    );
+  };
+
+  clearMessageQueue = (contextKey: string): void => {
+    this.#set(
+      produce((state: ChatStore) => {
+        delete state.queuedMessages[contextKey];
+      }),
+      false,
+      n(`clearMessageQueue/${contextKey}`),
+    );
+  };
 }
 
 export type OperationActions = Pick<OperationActionsImpl, keyof OperationActionsImpl>;
diff --git a/src/store/chat/slices/operation/initialState.ts b/src/store/chat/slices/operation/initialState.ts
index 5358aa548c5..c663f431766 100644
--- a/src/store/chat/slices/operation/initialState.ts
+++ b/src/store/chat/slices/operation/initialState.ts
@@ -1,4 +1,4 @@
-import { type Operation, type OperationType } from './types';
+import { type Operation, type OperationType, type QueuedMessage } from './types';
 
 /**
  * Chat Operation State
@@ -34,6 +34,14 @@ export interface ChatOperationState {
    */
   operationsByType: Record<OperationType, string[]>;
 
+  /**
+   * Message queue per conversation context.
+   * key: contextKey (messageMapKey), value: queued messages
+   * Messages are consumed either by the running step loop (injection)
+   * or by triggering a new sendMessage when no operation is running.
+   */
+  queuedMessages: Record<string, QueuedMessage[]>;
+
   /**
    * Agent IDs with unread completed generation
    */
@@ -51,6 +59,7 @@ export const initialOperationState: ChatOperationState = {
   operationsByContext: {},
   operationsByMessage: {},
   operationsByType: {} as Record<OperationType, string[]>,
+  queuedMessages: {},
   unreadCompletedAgentIds: new Set(),
   unreadCompletedTopicIds: new Set(),
 };
diff --git a/src/store/chat/slices/operation/selectors.ts b/src/store/chat/slices/operation/selectors.ts
index 78a87c4cdfb..e44758cfe6c 100644
--- a/src/store/chat/slices/operation/selectors.ts
+++ b/src/store/chat/slices/operation/selectors.ts
@@ -532,6 +532,38 @@ const isTopicUnreadCompleted =
     return s.unreadCompletedTopicIds.has(topicId);
   };
 
+// ━━━ Message Queue Selectors ━━━
+
+/**
+ * Get queued messages count for a context
+ */
+const queuedMessageCount =
+  (context: { agentId?: string; groupId?: string; topicId?: string | null }) =>
+  (s: ChatStoreState): number => {
+    if (!context.agentId) return 0;
+    const contextKey = messageMapKey({
+      agentId: context.agentId,
+      groupId: context.groupId,
+      topicId: context.topicId,
+    });
+    return s.queuedMessages[contextKey]?.length ?? 0;
+  };
+
+/**
+ * Get all queued messages for a context
+ */
+const getQueuedMessages =
+  (context: { agentId?: string; groupId?: string; topicId?: string | null }) =>
+  (s: ChatStoreState) => {
+    if (!context.agentId) return [];
+    const contextKey = messageMapKey({
+      agentId: context.agentId,
+      groupId: context.groupId,
+      topicId: context.topicId,
+    });
+    return s.queuedMessages[contextKey] ?? [];
+  };
+
 /**
  * Operation Selectors
  */
@@ -578,4 +610,8 @@ export const operationSelectors = {
   isRegenerating,
   isSendingMessage,
   isTopicUnreadCompleted,
+
+  // Message Queue
+  getQueuedMessages,
+  queuedMessageCount,
 };
diff --git a/src/store/chat/slices/operation/types.ts b/src/store/chat/slices/operation/types.ts
index 04e6ca2c2ee..2a84ca87443 100644
--- a/src/store/chat/slices/operation/types.ts
+++ b/src/store/chat/slices/operation/types.ts
@@ -181,6 +181,37 @@ export interface Operation {
   type: OperationType; // Operation type
 }
 
+/**
+ * Queued message waiting to be injected into agent runtime
+ */
+export interface QueuedMessage {
+  content: string;
+  createdAt: number;
+  files?: string[];
+  id: string;
+  interruptMode: 'soft' | 'hard';
+}
+
+/**
+ * Merged message ready for injection
+ */
+export interface MergedQueuedMessage {
+  content: string;
+  files: string[];
+}
+
+/**
+ * Merge multiple queued messages into a single message.
+ * Sorted by creation time, content joined with double newlines.
+ */
+export const mergeQueuedMessages = (messages: QueuedMessage[]): MergedQueuedMessage => {
+  const sorted = [...messages].sort((a, b) => a.createdAt - b.createdAt);
+  return {
+    content: sorted.map((m) => m.content).join('\n\n'),
+    files: sorted.flatMap((m) => m.files ?? []),
+  };
+};
+
 /**
  * Operation filter for querying operations
  */

PATCH_EOF_13343

echo "Patch applied successfully."
