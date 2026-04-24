# Fix Right Panel Behavior When Unpinning Active Tab

## Problem Description

There's a UI inconsistency in the conversation tabs context menu. When a user unpins the currently active tab via the context menu (the "⋮" button), the tab button disappears but the right panel remains open, showing empty or inconsistent content.

## Expected Behavior

When unpinning a tab that is currently selected/active:
1. The tab should be unpinned (removed from the tab bar)
2. The right panel should close
3. Both the Zustand store state and localStorage should be updated to reflect the closed panel

When unpinning a tab that is not the currently selected one:
1. Only the tab should be unpinned
2. The right panel should remain in its current state

## Files to Examine

The relevant files are in the frontend:
- `frontend/src/components/features/conversation/conversation-tabs/conversation-tabs-context-menu.tsx` — the context menu component that handles tab pinning/unpinning
- `frontend/__tests__/components/features/conversation/conversation-tabs-context-menu.test.tsx` — the test file for this component

The component uses `useConversationLocalStorageState` for managing unpinned tabs in localStorage. The conversation store (`useConversationStore`) tracks which tab is currently selected and the right panel visibility state.

## Testing

The repo uses vitest for testing. Run tests with:
```bash
cd frontend && npm run test
```

Add test cases that verify:
1. Unpinning the active tab closes the right panel
2. Unpinning a non-active tab does not close the right panel

The test descriptions should include the phrases:
- "should close the right panel when unpinning the currently active tab"
- "should not close the right panel when unpinning a non-active tab"

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
