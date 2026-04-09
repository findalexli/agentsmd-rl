# Fix: Hide Right Panel When Active Tab is Unpinned

## Bug Description

When unpinning the currently selected tab via the context menu (⋮), the tab button is removed from the UI but the right panel remains visible. The panel should be closed when the active tab is unpinned.

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

## Implementation Notes

The component uses:
- `useConversationStore()` - Zustand store for UI state (selectedTab, isRightPanelShown, setHasRightPanelToggled)
- `useConversationLocalStorageState()` - Hook for localStorage persistence (setRightPanelShown)

In the `handleTabClick` function, when a tab is being unpinned (the else branch that adds to `unpinnedTabs`), you need to check:
1. Is this tab the currently selected tab? (`selectedTab === tab`)
2. Is the right panel currently shown? (`isRightPanelShown`)

If both conditions are true, close the panel by:
1. Calling `setHasRightPanelToggled(false)` on the store
2. Calling `setRightPanelShown(false)` from the localStorage hook

## Testing Requirements

Per repository conventions (AGENTS.md):
- Run `cd frontend && npm run lint:fix && npm run build` before committing
- Run `npm run test` to verify all tests pass

The test file should be updated to:
1. Import and initialize `useConversationStore` in `beforeEach`
2. Add a test verifying the panel closes when unpinning the active tab
3. Add a test verifying the panel stays open when unpinning a non-active tab

## Reproduction Steps

1. Open the conversation tabs context menu
2. Ensure a tab (e.g., "Changes") is currently selected and the right panel is visible
3. Click to unpin that tab
4. **Bug:** The tab button disappears but the panel stays open
5. **Expected:** Both the tab button and panel should be hidden
