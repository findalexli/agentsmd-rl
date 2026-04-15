# Show interrupted hint and add queue edit button

## Problem

When a user stops AI generation mid-stream, the chat UI shows an infinite dotting animation with no indication that generation was interrupted. The user has no visual feedback about what happened or what to do next.

Additionally, when messages are queued during AI generation, users can delete queued messages but cannot edit them — there is no way to pull a queued message back into the input editor for modification.

## Expected Behavior

1. When the user stops AI generation, the assistant message should display an "Interrupted" hint below the message content. The hint should show the text "Interrupted · What should I do instead?" (or localized equivalent). This hint should appear for both `AssistantMessage` and `AssistantGroup` (tool use) message types.

   The hint must be implemented as a component named `InterruptedHint` at `src/features/Conversation/Messages/Assistant/components/InterruptedHint.tsx`. This component must:
   - Use `memo` from React
   - Use the i18n keys `'messageAction.interrupted'` and `'messageAction.interruptedHint'`
   - Display format: `{t('messageAction.interrupted')} · {t('messageAction.interruptedHint')}`

2. The message operation state system should track whether a message generation was interrupted. The `MessageOperationState` interface in `src/features/Conversation/types/operation.ts` must include:
   - Field: `isInterrupted: boolean`
   - Default value: `isInterrupted: false` in `DEFAULT_MESSAGE_OPERATION_STATE`

   The `useOperationState` hook in `src/hooks/useOperationState.ts` must compute `isInterrupted` by checking if the latest AI runtime operation was cancelled (not just overwritten to "completed" when tools resolve after cancellation). The logic should:
   - Find the latest runtime operation by reversing the operation list
   - Set `isInterrupted` to true only when no operations are running AND the latest runtime operation has status `'cancelled'`

   The selector `isMessageInterrupted` must be exported from `src/features/Conversation/store/slices/messageState/selectors.ts`:
   - Must be defined as `const isMessageInterrupted = (id: string) => (s: State) => ...`
   - Must be included in the `messageStateSelectors` export object

3. A pencil (edit) icon button should appear on each queued message in the queue tray at `src/features/Conversation/ChatInput/QueueTray.tsx`. Clicking it should:
   - Remove the message from the queue by calling `removeQueuedMessage`
   - Restore its content to the input editor by calling `setDocument` on the editor
   - Focus the editor

   Implementation details:
   - Import `Pencil` icon from `lucide-react`
   - Define a callback named `handleEdit` wrapped in `useCallback`
   - Use `editor.setDocument('markdown', content)` to restore content

4. The i18n keys must be added to locale files:
   - `src/locales/default/chat.ts`: Add `'messageAction.interrupted'` and `'messageAction.interruptedHint'` keys
   - `locales/en-US/chat.json`: Add `"messageAction.interrupted"` and `"messageAction.interruptedHint"` keys
   - `locales/zh-CN/chat.json`: Add `"messageAction.interrupted"` ("已中断") and `"messageAction.interruptedHint"` ("接下来需要做什么？") keys

5. The project's agent skill documentation should be updated to describe the new screen recording capability for the Electron app:
   - Update `.agents/skills/electron-testing/SKILL.md` to add a "Screen Recording" section that mentions:
     - `record-electron-demo.sh` script
     - `ffmpeg` for video capture
     - `agent-browser` for automation
   - Create `.agents/skills/electron-testing/record-electron-demo.sh` with:
     - Shebang: `#!/usr/bin/env bash`
     - Functions: `start_recording`, `stop_recording`
     - Variable: `CDP_PORT` for Chrome DevTools Protocol port
     - Must reference `ffmpeg` and `agent-browser`

## Files to Look At

- `src/features/Conversation/types/operation.ts` — defines `MessageOperationState` interface and default values
- `src/hooks/useOperationState.ts` — computes message operation states (generating, editing, etc.)
- `src/features/Conversation/store/slices/messageState/selectors.ts` — message state selectors including `isMessageInterrupted`
- `src/store/chat/slices/operation/actions.ts` — operation lifecycle actions (completeOperation)
- `src/features/Conversation/Messages/Assistant/index.tsx` — assistant message component
- `src/features/Conversation/Messages/Assistant/components/InterruptedHint.tsx` — interrupted hint component (to create)
- `src/features/Conversation/Messages/AssistantGroup/index.tsx` — assistant group message (tool use)
- `src/features/Conversation/ChatInput/QueueTray.tsx` — queued messages tray
- `src/locales/default/chat.ts` — i18n default keys
- `locales/en-US/chat.json` — English locale file
- `locales/zh-CN/chat.json` — Chinese locale file
- `.agents/skills/electron-testing/SKILL.md` — agent skill documentation for Electron testing
- `.agents/skills/electron-testing/record-electron-demo.sh` — screen recording script (to create)

After implementing the code changes, update the relevant documentation and skill files to reflect the new capabilities.
