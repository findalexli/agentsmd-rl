# Fix: Hide Right Panel When Active Tab is Unpinned

## Bug Description

When unpinning the currently selected tab via the context menu, the tab button is removed from the UI but the right panel remains visible. The panel should be closed when the active tab is unpinned.

## Expected Behavior

When a user unpins a tab that is currently active (selected):
1. The tab should be unpinned (removed from tab bar)
2. The right panel should be closed
3. Both the Zustand store state and localStorage should be updated to reflect the panel being hidden

When unpinning a tab that is NOT currently active, only the tab should be unpinned - the panel visibility should remain unchanged.

## Files to Modify

**Primary file:**
- `frontend/src/components/features/conversation/conversation-tabs/conversation-tabs-context-menu.tsx`

**Test file:**
- `frontend/__tests__/components/features/conversation/conversation-tabs-context-menu.test.tsx`

## Testing Requirements

Per repository conventions (AGENTS.md):
- Run `cd frontend && npm run lint:fix && npm run build` before committing
- Run `npm run test` to verify all tests pass

The test file must be updated to include:

1. Import of `useConversationStore` from `"#/stores/conversation-store"`

2. Store initialization in `beforeEach` using `useConversationStore.setState` with:
   - `selectedTab: "editor"`
   - `isRightPanelShown: true`
   - `hasRightPanelToggled: true`

3. A test with the exact description: `"should close the right panel when unpinning the currently active tab"`
   - This test must verify store state with `useConversationStore.getState()`
   - Must assert `hasRightPanelToggled).toBe(false)`
   - Must assert `rightPanelShown).toBe(false)` in localStorage

4. A test with the exact description: `"should not close the right panel when unpinning a non-active tab"`
   - This test must verify `hasRightPanelToggled).toBe(true)` remains true

## Reproduction Steps

1. Open the conversation tabs context menu
2. Ensure a tab (e.g., "Changes") is currently selected and the right panel is visible
3. Click to unpin that tab
4. **Bug:** The tab button disappears but the panel stays open
5. **Expected:** Both the tab button and panel should be hidden

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
