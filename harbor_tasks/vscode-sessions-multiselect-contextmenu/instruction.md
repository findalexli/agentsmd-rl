# Bug Report: Context menu actions only apply to single session when multiple sessions are selected

## Problem

In the Sessions view, users can multi-select sessions in the list. However, when right-clicking to open the context menu on a multi-selected set of sessions, the resulting actions (delete, archive, pin, etc.) only operate on the single session that was right-clicked, completely ignoring the rest of the selection. This makes bulk operations via context menu impossible.

## Expected Behavior

When multiple sessions are selected in the sessions list and the user right-clicks to open a context menu, the triggered action should apply to all selected sessions. The right-clicked session should be treated as the primary target, with the full selection passed along as context so that commands can operate in bulk.

## Actual Behavior

The context menu always passes only the single right-clicked session element as the argument to menu actions. The tree's current multi-selection state is never consulted. Additionally, the bridged Copilot session commands only handle a single session object, so even if an array were passed, they would fail to process it correctly.

## Files to Look At

- `src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts`
- `src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts`
- `src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts`
