#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the fix for PR #13648: fix(frontend): hide right panel when active tab is unpinned

# Source file changes
SOURCE_FILE="frontend/src/components/features/conversation/conversation-tabs/conversation-tabs-context-menu.tsx"
TEST_FILE="frontend/__tests__/components/features/conversation/conversation-tabs-context-menu.test.tsx"

# 1. Add import for useConversationStore after the local storage import
sed -i 's|import { useConversationLocalStorageState } from "#/utils/conversation-local-storage";|import { useConversationLocalStorageState } from "#/utils/conversation-local-storage";\nimport { useConversationStore } from "#/stores/conversation-store";|' "$SOURCE_FILE"

# 2. Update the destructuring to add setRightPanelShown
sed -i 's|const { state, setUnpinnedTabs } =|const { state, setUnpinnedTabs, setRightPanelShown } =|' "$SOURCE_FILE"

# 3. Add store hooks after the local storage line
sed -i '/useConversationLocalStorageState(conversationId);/a\  const { selectedTab, isRightPanelShown, setHasRightPanelToggled } =\n    useConversationStore();' "$SOURCE_FILE"

# 4. Add the conditional logic inside handleTabClick after "setUnpinnedTabs([...state.unpinnedTabs, tab]);"
sed -i '/setUnpinnedTabs(\[...state.unpinnedTabs, tab\]);/a\      if (selectedTab === tab \&\& isRightPanelShown) {\n        setHasRightPanelToggled(false);\n        setRightPanelShown(false);\n      }' "$SOURCE_FILE"

# Test file changes

# 1. Add import for useConversationStore after the component import
sed -i 's|import { ConversationTabsContextMenu } from "#/components/features/conversation/conversation-tabs/conversation-tabs-context-menu";|import { ConversationTabsContextMenu } from "#/components/features/conversation/conversation-tabs/conversation-tabs-context-menu";\nimport { useConversationStore } from "#/stores/conversation-store";|' "$TEST_FILE"

# 2. Add store state setup in beforeEach after "mockHasTaskList = false;"
sed -i '/mockHasTaskList = false;/a\    useConversationStore.setState({\n      selectedTab: "editor",\n      isRightPanelShown: true,\n      hasRightPanelToggled: true,\n    });' "$TEST_FILE"

# 3. Add the new tests before "describe(\"with tasklist\""
# Create a temp file with the new tests
cat > /tmp/new_tests.txt << 'TESTEOF'

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
TESTEOF

# Get the line number of "describe(\"with tasklist\""
TASKLIST_LINE=$(grep -n 'describe("with tasklist"' "$TEST_FILE" | head -1 | cut -d: -f1)

# Split and reconstruct the file
head -n $((TASKLIST_LINE - 1)) "$TEST_FILE" > /tmp/test_file_part1.txt
tail -n +$TASKLIST_LINE "$TEST_FILE" > /tmp/test_file_part2.txt

cat /tmp/test_file_part1.txt /tmp/new_tests.txt > "$TEST_FILE"
cat /tmp/test_file_part2.txt >> "$TEST_FILE"

# Clean up
rm -f /tmp/test_file_part1.txt /tmp/test_file_part2.txt /tmp/new_tests.txt

# Verify the patch was applied by checking for a distinctive line from the fix
grep -q "setHasRightPanelToggled(false)" "$SOURCE_FILE" && echo "Patch applied successfully"
