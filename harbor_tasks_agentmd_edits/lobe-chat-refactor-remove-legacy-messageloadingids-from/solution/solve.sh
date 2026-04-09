#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
# Check if messageLoadingIds is removed from initialState.ts
if ! grep -q "messageLoadingIds" src/store/chat/slices/message/initialState.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply patch
git apply - <<'PATCH'
diff --git a/.agents/skills/zustand/SKILL.md b/.agents/skills/zustand/SKILL.md
index 5fcef5a7c85..2499f727dd5 100644
--- a/.agents/skills/zustand/SKILL.md
+++ b/.agents/skills/zustand/SKILL.md
@@ -71,15 +71,18 @@ internal_createTopic: async (params) => {
 **Actions:**

 - Public: `createTopic`, `sendMessage`
+
 - Internal: `internal_createTopic`, `internal_updateMessageContent`
+
 - Dispatch: `internal_dispatchTopic`
-- Toggle: `internal_toggleMessageLoading`
+  **State:**

-**State:**
+- ID arrays: `topicEditingIds`

-- ID arrays: `messageLoadingIds`, `topicEditingIds`
 - Maps: `topicMaps`, `messagesMap`
+
 - Active: `activeTopicId`
+
 - Init flags: `topicsInit`

 ## Detailed Guides

diff --git a/.agents/skills/zustand/references/action-patterns.md b/.agents/skills/zustand/references/action-patterns.md
index 357f5cf8dc7..1244752c2eb 100644
--- a/.agents/skills/zustand/references/action-patterns.md
+++ b/.agents/skills/zustand/references/action-patterns.md
@@ -30,16 +30,13 @@ internal_createMessage: async (message, context) => {
   let tempId = context?.tempMessageId;
   if (!tempId) {
     tempId = internal_createTmpMessage(message);
-    internal_toggleMessageLoading(true, tempId);
   }

   try {
     const id = await messageService.createMessage(message);
     await refreshMessages();
-    internal_toggleMessageLoading(false, tempId);
     return id;
   } catch (e) {
-    internal_toggleMessageLoading(false, tempId);
     internal_dispatchMessage({
       id: tempId,
       type: 'updateMessage',
diff --git a/src/features/Conversation/store/slices/generation/action.ts b/src/features/Conversation/store/slices/generation/action.ts
index b58ee7bf72f..ec082d9485c 100644
--- a/src/features/Conversation/store/slices/generation/action.ts
+++ b/src/features/Conversation/store/slices/generation/action.ts
@@ -8,6 +8,7 @@ import {
   parseSelectedSkillsFromEditorData,
   parseSelectedToolsFromEditorData,
 } from '@/store/chat/slices/aiChat/actions/commandBus';
+import { operationSelectors } from '@/store/chat/slices/operation/selectors';
 import { INPUT_LOADING_OPERATION_TYPES } from '@/store/chat/slices/operation/types';

 import { type Store as ConversationStore } from '../../action';
@@ -314,8 +315,8 @@ export const generationSlice: StateCreator<
     const { context, displayMessages, hooks } = get();
     const chatStore = useChatStore.getState();

-    // Check if already regenerating
-    const isRegenerating = chatStore.messageLoadingIds.includes(messageId);
+    // Check if already regenerating via operation system
+    const isRegenerating = operationSelectors.isMessageProcessing(messageId)(chatStore);
     if (isRegenerating) return;

     // Find the message in current conversation messages

diff --git a/src/store/chat/slices/aiAgent/actions/agentGroup.ts b/src/store/chat/slices/aiAgent/actions/agentGroup.ts
index ab7a4404b7c..ae6ace49a17 100644
--- a/src/store/chat/slices/aiAgent/actions/agentGroup.ts
+++ b/src/store/chat/slices/aiAgent/actions/agentGroup.ts
@@ -89,10 +89,6 @@ export class ChatGroupChatActionImpl {
       { operationId: execOperationId, tempMessageId: tempAssistantId },
     );

-    // Start loading state for temp messages
-    this.#get().internal_toggleMessageLoading(true, tempUserId);
-    this.#get().internal_toggleMessageLoading(true, tempAssistantId);
-
     try {
       // 2. Call backend execGroupAgent - creates messages and triggers Agent
       // Pass AbortSignal to allow cancellation during the API call
@@ -153,8 +149,6 @@ export class ChatGroupChatActionImpl {
           message: result.error || 'Agent operation failed to start',
           type: 'AgentStartupError',
         });
-        // Stop loading state for assistant message
-        this.#get().internal_toggleMessageLoading(false, result.assistantMessageId);
         return;
       }

@@ -254,8 +248,6 @@ export class ChatGroupChatActionImpl {
         });
       }
     } finally {
-      this.#get().internal_toggleMessageLoading(false, tempUserId);
-      this.#get().internal_toggleMessageLoading(false, tempAssistantId);
       this.#set({ isCreatingMessage: false }, false, n('sendGroupMessage/end'));
     }
   };
diff --git a/src/store/chat/slices/aiAgent/actions/runAgent.ts b/src/store/chat/slices/aiAgent/actions/runAgent.ts
index 2497c6aedc4..0ea263d3e1a 100644
--- a/src/store/chat/slices/aiAgent/actions/runAgent.ts
+++ b/src/store/chat/slices/aiAgent/actions/runAgent.ts
@@ -73,8 +73,6 @@ export class AgentActionImpl {
     });

     // Stop loading state
-    this.#get().internal_toggleMessageLoading(false, assistantId);
-
     // Clean up operation (this will cancel the operation)
     this.#get().internal_cleanupAgentOperation(assistantId);
   };
@@ -131,7 +129,7 @@ export class AgentActionImpl {

         // Stop loading state
         log(`Stopping loading for completed agent runtime: ${assistantId}`);
-        this.#get().internal_toggleMessageLoading(false, assistantId);
+
         break;
       }

@@ -235,7 +233,6 @@ export class AgentActionImpl {

         // Stop loading state
         log(`Stopping loading for ${assistantId}`);
-        this.#get().internal_toggleMessageLoading(false, assistantId);

         // Show desktop notification
         if (isDesktop) {
@@ -290,7 +287,6 @@ export class AgentActionImpl {

           // Stop loading state, waiting for human intervention
           log(`Stopping loading for human approval: ${assistantId}`);
-          this.#get().internal_toggleMessageLoading(false, assistantId);
         } else if (phase === 'tool_execution' && toolCall) {
           log(`Tool execution started for ${assistantId}: ${toolCall.function?.name}`);
         }
@@ -312,7 +308,6 @@ export class AgentActionImpl {
           });

           log(`Stopping loading for completed agent: ${assistantId}`);
-          this.#get().internal_toggleMessageLoading(false, assistantId);
         }
         break;
       }
@@ -362,9 +357,6 @@ export class AgentActionImpl {
         operationId: messageOpId,
       });

-      // Resume loading state
-      this.#get().internal_toggleMessageLoading(true, assistantId);
-
       // Clear human intervention state
       this.#get().updateOperationMetadata(messageOpId, {
         needsHumanInput: false,
diff --git a/src/store/chat/slices/aiChat/actions/conversationLifecycle.ts b/src/store/chat/slices/aiChat/actions/conversationLifecycle.ts
index 80d7e7a6276..92ec3e249a4 100644
--- a/src/store/chat/slices/aiChat/actions/conversationLifecycle.ts
+++ b/src/store/chat/slices/aiChat/actions/conversationLifecycle.ts
@@ -329,7 +329,6 @@ export class ConversationLifecycleActionImpl {
       },
       { operationId, tempMessageId: tempAssistantId },
     );
-    this.#get().internal_toggleMessageLoading(true, tempId);

     // Associate temp messages with operation
     this.#get().associateMessageWithOperation(tempId, operationId);
@@ -495,8 +494,6 @@ export class ConversationLifecycleActionImpl {
       }
     }

-    this.#get().internal_toggleMessageLoading(false, tempId);
-
     // Clear editor temp state after message created
     if (data) {
       this.#get().updateOperationMetadata(operationId, { inputEditorTempState: null });
diff --git a/src/store/chat/slices/message/action.test.ts b/src/store/chat/slices/message/action.test.ts
index e0b846001cc..a3a99a61298 100644
--- a/src/store/chat/slices/message/action.test.ts
+++ b/src/store/chat/slices/message/action.test.ts
@@ -781,31 +781,6 @@ describe('chatMessage actions', () => {
     });
   });

-  describe('internal_toggleMessageLoading', () => {
-    it('should add message id to messageLoadingIds when loading is true', () => {
-      const { result } = renderHook(() => useChatStore());
-      const messageId = 'message-id';
-
-      act(() => {
-        result.current.internal_toggleMessageLoading(true, messageId);
-      });
-
-      expect(result.current.messageLoadingIds).toContain(messageId);
-    });
-
-    it('should remove message id from messageLoadingIds when loading is false', () => {
-      const { result } = renderHook(() => useChatStore());
-      const messageId = 'ddd-id';
-
-      act(() => {
-        result.current.internal_toggleMessageLoading(true, messageId);
-        result.current.internal_toggleMessageLoading(false, messageId);
-      });
-
-      expect(result.current.messageLoadingIds).not.toContain(messageId);
-    });
-  });
-
   describe('modifyMessageContent', () => {
     it('should call internal_traceMessage with correct parameters before updating', async () => {
       const messageId = 'message-id';
diff --git a/src/store/chat/slices/message/actions/optimisticUpdate.ts b/src/store/chat/slices/message/actions/optimisticUpdate.ts
index 4ec943bbaa7..de7683d9878 100644
--- a/src/store/chat/slices/message/actions/optimisticUpdate.ts
+++ b/src/store/chat/slices/message/actions/optimisticUpdate.ts
@@ -55,17 +55,11 @@ export class MessageOptimisticUpdateActionImpl {
       tempMessageId?: string;
     },
   ): Promise<{ id: string; messages: UIChatMessage[] } | undefined> => {
-    const {
-      optimisticCreateTmpMessage,
-      internal_toggleMessageLoading,
-      internal_dispatchMessage,
-      replaceMessages,
-    } = this.#get();
+    const { optimisticCreateTmpMessage, internal_dispatchMessage, replaceMessages } = this.#get();

     let tempId = context?.tempMessageId;
     if (!tempId) {
       tempId = optimisticCreateTmpMessage(message as any, context);
-      internal_toggleMessageLoading(true, tempId);
     }

     try {
@@ -75,10 +69,8 @@ export class MessageOptimisticUpdateActionImpl {
       const ctx = this.#get().internal_getConversationContext(context);
       replaceMessages(result.messages, { context: ctx });

-      internal_toggleMessageLoading(false, tempId);
       return result;
     } catch (e) {
-      internal_toggleMessageLoading(false, tempId);
       internal_dispatchMessage(
         {
           id: tempId,
diff --git a/src/store/chat/slices/message/actions/runtimeState.ts b/src/store/chat/slices/message/actions/runtimeState.ts
index 33e040e83c2..6fdd2824fa7 100644
--- a/src/store/chat/slices/message/actions/runtimeState.ts
+++ b/src/store/chat/slices/message/actions/runtimeState.ts
@@ -61,16 +61,6 @@ export class MessageRuntimeStateActionImpl {
       window.removeEventListener('beforeunload', preventLeavingFn);
     }
   };
-
-  internal_toggleMessageLoading = (loading: boolean, id: string): void => {
-    this.#set(
-      {
-        messageLoadingIds: toggleBooleanList(this.#get().messageLoadingIds, id, loading),
-      },
-      false,
-      `internal_toggleMessageLoading/${loading ? 'start' : 'end'}`,
-    );
-  };
 }

 export type MessageRuntimeStateAction = Pick<
diff --git a/src/store/chat/slices/message/initialState.ts b/src/store/chat/slices/message/initialState.ts
index 202098c97da..b71612140c9 100644
--- a/src/store/chat/slices/message/initialState.ts
+++ b/src/store/chat/slices/message/initialState.ts
@@ -17,10 +17,6 @@ export interface ChatMessageState {
    * is the message is editing
    */
   messageEditingIds: string[];
-  /**
-   * is the message is creating or updating in the service
-   */
-  messageLoadingIds: string[];
   /**
    * whether messages have fetched
    */
@@ -37,7 +33,6 @@ export const initialMessageState: ChatMessageState = {
   groupAgentMaps: {},
   isCreatingMessage: false,
   messageEditingIds: [],
-  messageLoadingIds: [],
   messagesInit: false,
   messagesMap: {},
 };
diff --git a/src/store/chat/slices/message/selectors/messageState.ts b/src/store/chat/slices/message/selectors/messageState.ts
index f241abe2241..dcc262c4ae3 100644
--- a/src/store/chat/slices/message/selectors/messageState.ts
+++ b/src/store/chat/slices/message/selectors/messageState.ts
@@ -1,23 +1,15 @@
 import { type ChatStoreState } from '../../../initialState';
 import { operationSelectors } from '../../operation/selectors';
-import { mainDisplayChatIDs } from './chat';
 import { getDbMessageByToolCallId } from './dbMessage';
 import { getDisplayMessageById } from './displayMessage';

 const isMessageEditing = (id: string) => (s: ChatStoreState) => s.messageEditingIds.includes(id);

 /**
- * Check if a message is in loading state
- * Priority: operation system (for AI flows) > legacy messageLoadingIds (for CRUD operations)
+ * Check if a message is in loading state via the operation system
  */
-const isMessageLoading = (id: string) => (s: ChatStoreState) => {
-  // First check operation system (sendMessage, etc.)
-  const hasOperation = operationSelectors.isMessageProcessing(id)(s);
-  if (hasOperation) return true;
-
-  // Fallback to legacy loading state (for non-operation CRUD)
-  return s.messageLoadingIds.includes(id);
-};
+const isMessageLoading = (id: string) => (s: ChatStoreState) =>
+  operationSelectors.isMessageProcessing(id)(s);

 // Use operation system for AI-related loading states
 const isMessageRegenerating = (id: string) => (s: ChatStoreState) =>
@@ -70,23 +62,8 @@ const isToolApiNameShining =

 const isCreatingMessage = (s: ChatStoreState) => s.isCreatingMessage;

-const isHasMessageLoading = (s: ChatStoreState) =>
-  s.messageLoadingIds.some((id) => mainDisplayChatIDs(s).includes(id));
-
-/**
- * this function is used to determine whether the send button should be disabled
- */
-const isSendButtonDisabledByMessage = (s: ChatStoreState) =>
-  // 1. when there is message loading
-  isHasMessageLoading(s) ||
-  // 2. when is creating the topic
-  s.creatingTopic ||
-  // 3. when is creating the message
-  isCreatingMessage(s);
-
 export const messageStateSelectors = {
   isCreatingMessage,
-  isHasMessageLoading,
   isInToolsCalling,
   isMessageCollapsed,
   isMessageContinuing,
@@ -97,7 +74,6 @@ export const messageStateSelectors = {
   isMessageLoading,
   isMessageRegenerating,
   isPluginApiInvoking,
-  isSendButtonDisabledByMessage,
   isToolApiNameShining,
   isToolCallStreaming,
 };
diff --git a/src/store/chat/slices/plugin/actions/optimisticUpdate.ts b/src/store/chat/slices/plugin/actions/optimisticUpdate.ts
index 75e15f21cd6..0ce11d98198 100644
--- a/src/store/chat/slices/plugin/actions/optimisticUpdate.ts
+++ b/src/store/chat/slices/plugin/actions/optimisticUpdate.ts
@@ -210,14 +210,11 @@ export class PluginOptimisticUpdateActionImpl {
     const message = dbMessageSelectors.getDbMessageById(id)(this.#get());
     if (!message || !message.tools) return;

-    const { internal_toggleMessageLoading, replaceMessages, internal_getConversationContext } =
-      this.#get();
+    const { replaceMessages, internal_getConversationContext } = this.#get();

     const ctx = internal_getConversationContext(context);

-    internal_toggleMessageLoading(true, id);
     const result = await messageService.updateMessage(id, { tools: message.tools }, ctx);
-    internal_toggleMessageLoading(false, id);

     if (result?.success && result.messages) {
       replaceMessages(result.messages, { context: ctx });

PATCH

echo "Patch applied successfully."
