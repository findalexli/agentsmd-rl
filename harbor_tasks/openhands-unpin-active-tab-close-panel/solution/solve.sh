#!/bin/bash
set -e

cd /workspace/OpenHands/frontend

# Fix 1: Add import for useConversationStore in source file
sed -i 's|import { useConversationLocalStorageState } from "#/utils/conversation-local-storage";|import { useConversationLocalStorageState } from "#/utils/conversation-local-storage";\nimport { useConversationStore } from "#/stores/conversation-store";|' \
  src/components/features/conversation/conversation-tabs/conversation-tabs-context-menu.tsx

# Fix 2: Destructure setRightPanelShown and add conversation store usage
sed -i 's|const { state, setUnpinnedTabs } =|const { state, setUnpinnedTabs, setRightPanelShown } =|' \
  src/components/features/conversation/conversation-tabs/conversation-tabs-context-menu.tsx

# Fix 3: Add conversation store hook usage after the localStorage hook
sed -i '/useConversationLocalStorageState(conversationId);/a\  const { selectedTab, isRightPanelShown, setHasRightPanelToggled } =\n    useConversationStore();' \
  src/components/features/conversation/conversation-tabs/conversation-tabs-context-menu.tsx

# Fix 4: Add panel close logic when unpinning active tab
# Replace the line that just adds tab to unpinnedTabs
sed -i 's|setUnpinnedTabs(\[...state.unpinnedTabs, tab\]);|setUnpinnedTabs([...state.unpinnedTabs, tab]);\n      if (selectedTab === tab \&\& isRightPanelShown) {\n        setHasRightPanelToggled(false);\n        setRightPanelShown(false);\n      }|' \
  src/components/features/conversation/conversation-tabs/conversation-tabs-context-menu.tsx

# Fix 5: Add import for useConversationStore in test file
sed -i 's|import { ConversationTabsContextMenu } from "#/components/features/conversation/conversation-tabs/conversation-tabs-context-menu";|import { ConversationTabsContextMenu } from "#/components/features/conversation/conversation-tabs/conversation-tabs-context-menu";\nimport { useConversationStore } from "#/stores/conversation-store";|' \
  __tests__/components/features/conversation/conversation-tabs-context-menu.test.tsx

# Fix 6: Add store initialization in beforeEach
sed -i '/mockHasTaskList = false;/a\    useConversationStore.setState({\n      selectedTab: "editor",\n      isRightPanelShown: true,\n      hasRightPanelToggled: true,\n    });' \
  __tests__/components/features/conversation/conversation-tabs-context-menu.test.tsx

# Fix 7: Add new test for active tab panel close - after the repin test, before with tasklist
cat > /tmp/new_tests.txt << 'EOF'

  it("should close the right panel when unpinning the currently active tab", async () => {
    const user = userEvent.setup();

    render(<ConversationTabsContextMenu isOpen={true} onClose={vi.fn()} />);

    await user.click(screen.getByText("COMMON$CHANGES"));

    const storeState = useConversationStore.getState();
    expect(storeState.hasRightPanelToggled).toBe(false);

    const storedState = JSON.parse(
      localStorage.getItem(`conversation-state-${CONVERSATION_ID}`)!,
    );
    expect(storedState.rightPanelShown).toBe(false);
  });

  it("should not close the right panel when unpinning a non-active tab", async () => {
    const user = userEvent.setup();

    render(<ConversationTabsContextMenu isOpen={true} onClose={vi.fn()} />);

    await user.click(screen.getByText("COMMON$TERMINAL"));

    const storeState = useConversationStore.getState();
    expect(storeState.hasRightPanelToggled).toBe(true);
  });

EOF

# Insert the new tests before "describe(\"with tasklist\""
sed -i '/describe("with tasklist"/e cat /tmp/new_tests.txt' \
  __tests__/components/features/conversation/conversation-tabs-context-menu.test.tsx

echo "Fixes applied"

# Idempotency check - verify the fix is present
if grep -q "selectedTab === tab && isRightPanelShown" src/components/features/conversation/conversation-tabs/conversation-tabs-context-menu.tsx; then
  echo "Fix verified: active tab check present"
else
  echo "ERROR: Fix not applied correctly"
  exit 1
fi
