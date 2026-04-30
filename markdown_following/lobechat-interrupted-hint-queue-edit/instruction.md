# Show interrupted hint and add queue edit button

## Problem

When a user stops AI generation mid-stream, the chat UI shows an infinite dotting animation with no indication that generation was interrupted. The user has no visual feedback about what happened or what to do next.

Additionally, when messages are queued during AI generation, users can delete queued messages but cannot edit them — there is no way to pull a queued message back into the input editor for modification.

## Expected Behavior

1. **Interrupted hint component**: When the user stops AI generation, the assistant message should display an "Interrupted" hint below the message content. The hint should show the text "Interrupted · What should I do instead?" (or localized equivalent). This hint should appear for both `AssistantMessage` and `AssistantGroup` (tool use) message types.

   Create a component named `InterruptedHint` at `src/features/Conversation/Messages/Assistant/components/InterruptedHint.tsx`. Use `memo` from React. Use i18n keys `'messageAction.interrupted'` and `'messageAction.interruptedHint'`.

2. **Message operation state**: The `MessageOperationState` interface in `src/features/Conversation/types/operation.ts` must include a field `isInterrupted: boolean`. Set it to `false` in `DEFAULT_MESSAGE_OPERATION_STATE`.

   Compute `isInterrupted` by checking whether the latest AI runtime operation was cancelled, while no operations are currently running. The logic must handle the case where a cancelled operation is followed by a retry (the retry's status takes precedence). The selector `isMessageInterrupted` must be exported from `src/features/Conversation/store/slices/messageState/selectors.ts` and included in `messageStateSelectors`.

3. **Queue tray edit button**: A pencil (edit) icon button should appear on each queued message in the queue tray at `src/features/Conversation/ChatInput/QueueTray.tsx`. Clicking it should remove the message from the queue and restore its content to the input editor. Import `Pencil` from `lucide-react`. Use `useCallback` for the edit handler.

4. **Locale files**: Add i18n keys to:
   - `src/locales/default/chat.ts`: Add `'messageAction.interrupted'` and `'messageAction.interruptedHint'` keys
   - `locales/en-US/chat.json`: Add `"messageAction.interrupted"` and `"messageAction.interruptedHint"` keys
   - `locales/zh-CN/chat.json`: Add `"messageAction.interrupted"` ("已中断") and `"messageAction.interruptedHint"` ("接下来需要做什么？") keys

5. **Agent skill documentation**: Update `.agents/skills/electron-testing/SKILL.md` to document a Screen Recording capability for the Electron app. The documentation should reference `record-electron-demo.sh` script, `ffmpeg` for video capture, and `agent-browser` for automation. Create `.agents/skills/electron-testing/record-electron-demo.sh` as a bash script with shebang `#!/usr/bin/env bash`, containing `start_recording` and `stop_recording` functions, a `CDP_PORT` variable, and references to `ffmpeg` and `agent-browser`.

## Files to Look At

- `src/features/Conversation/types/operation.ts` — defines `MessageOperationState` interface and default values
- `src/hooks/useOperationState.ts` — computes message operation states (generating, editing, etc.)
- `src/features/Conversation/store/slices/messageState/selectors.ts` — message state selectors
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

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
