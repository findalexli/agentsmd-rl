# Add message queue mechanism for agent runtime

## Problem

When the AI agent is running (executing tools, generating responses), the chat input is disabled. Users cannot send follow-up messages while the agent works — they must wait for the entire operation to complete before sending anything new. This creates a poor UX, especially during long tool-calling chains.

## What's Needed

Implement a per-context message queue that allows users to send messages while the agent is executing. Messages should be enqueued, displayed in a queue tray UI, and consumed when the agent reaches a suitable stopping point.

### Code changes needed:

1. **Types** (`src/store/chat/slices/operation/types.ts`): Define `QueuedMessage` and `MergedQueuedMessage` interfaces, plus a `mergeQueuedMessages` utility that sorts messages by creation time and joins their content with double newlines.

2. **State** (`src/store/chat/slices/operation/initialState.ts`): Add `queuedMessages` state field (keyed by context) to the operation slice.

3. **Actions** (`src/store/chat/slices/operation/actions.ts`): Implement queue operations — `enqueueMessage`, `drainQueuedMessages`, `removeQueuedMessage`, `clearMessageQueue`.

4. **Selectors** (`src/store/chat/slices/operation/selectors.ts`): Add `queuedMessageCount` and `getQueuedMessages` selectors.

5. **Message lifecycle** (`src/store/chat/slices/aiChat/actions/conversationLifecycle.ts`): When `sendMessage` is called while an agent operation is running, enqueue the message instead of starting a new operation.

6. **Streaming executor** (`src/store/chat/slices/aiChat/actions/streamingExecutor.ts`): After agent execution completes, drain the queue and trigger a new `sendMessage` with merged content. Also signal `hasQueuedMessages` via step context so the agent can finish early after tool calls.

7. **Agent** (`packages/agent-runtime/src/agents/GeneralChatAgent.ts`): Check `hasQueuedMessages` after tool completion and finish early with a `queued_message_interrupt` reason.

8. **Step context** (`packages/agent-runtime/src/utils/stepContextComputer.ts`, `packages/types/src/stepContext.ts`): Add `hasQueuedMessages` flag to step context.

9. **Event types** (`packages/agent-runtime/src/types/event.ts`): Add `queued_message_interrupt` finish reason.

10. **UI** (`src/features/Conversation/ChatInput/index.tsx`): Keep input enabled during agent execution. Show the queue tray above the input when messages are queued.

11. **QueueTray component** (`src/features/Conversation/ChatInput/QueueTray.tsx`): New component showing queued messages with delete buttons.

### Config/documentation update needed:

The project uses agent skill files in `.agents/skills/` for development guidance. After implementing the message queue feature, create a new skill file `.agents/skills/electron-testing/SKILL.md` that documents how to automate testing of Electron desktop features using the `agent-browser` CLI. This skill should cover connecting to Electron via CDP, taking snapshots, interacting with elements, evaluating JavaScript, and patterns specific to this project (like accessing Zustand stores via `window.__LOBE_STORES`).

## Files to Look At

- `src/store/chat/slices/operation/types.ts` — queue types and merge utility
- `src/store/chat/slices/operation/initialState.ts` — state shape
- `src/store/chat/slices/operation/actions.ts` — queue actions
- `src/store/chat/slices/operation/selectors.ts` — queue selectors
- `src/store/chat/slices/aiChat/actions/conversationLifecycle.ts` — send message flow
- `src/store/chat/slices/aiChat/actions/streamingExecutor.ts` — agent execution loop
- `src/features/Conversation/ChatInput/index.tsx` — chat input component
- `.agents/skills/` — existing skill files for format reference
