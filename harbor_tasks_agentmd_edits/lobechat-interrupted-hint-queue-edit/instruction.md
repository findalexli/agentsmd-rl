# Show interrupted hint and add queue edit button

## Problem

When a user stops AI generation mid-stream, the chat UI shows an infinite dotting animation with no indication that generation was interrupted. The user has no visual feedback about what happened or what to do next.

Additionally, when messages are queued during AI generation, users can delete queued messages but cannot edit them — there is no way to pull a queued message back into the input editor for modification.

## Expected Behavior

1. When the user stops AI generation, the assistant message should display an "Interrupted" hint below the message content (e.g., "Interrupted · What should I do instead?"). This hint should appear for both `AssistantMessage` and `AssistantGroup` (tool use) message types.

2. The message operation state system should track whether a message generation was interrupted, by checking if the latest AI runtime operation was cancelled (not just overwritten to "completed" when tools resolve after cancellation).

3. A pencil (edit) icon button should appear on each queued message in the queue tray. Clicking it should remove the message from the queue and restore its content to the input editor.

4. The project's agent skill documentation should be updated to describe the new screen recording capability for the Electron app, including the recording script.

## Files to Look At

- `src/features/Conversation/types/operation.ts` — defines `MessageOperationState` interface and default values
- `src/hooks/useOperationState.ts` — computes message operation states (generating, editing, etc.)
- `src/features/Conversation/store/slices/messageState/selectors.ts` — message state selectors
- `src/store/chat/slices/operation/actions.ts` — operation lifecycle actions (completeOperation)
- `src/features/Conversation/Messages/Assistant/index.tsx` — assistant message component
- `src/features/Conversation/Messages/AssistantGroup/index.tsx` — assistant group message (tool use)
- `src/features/Conversation/ChatInput/QueueTray.tsx` — queued messages tray
- `src/locales/default/chat.ts` — i18n default keys
- `.agents/skills/electron-testing/SKILL.md` — agent skill documentation for Electron testing

After implementing the code changes, update the relevant documentation and skill files to reflect the new capabilities.
