# Fix Windows CLI Tests for Slash Command Timing Issues

The CLI has flaky unit tests on Windows due to race conditions in slash command handling. The quit commands (`/q` and `/exit`) are intermittently unavailable when tests try to use them.

## Symptoms

1. **Async-dependent command initialization**: CLI-only commands (like `/q` and `/exit`) are only populated after an async fetch completes, causing timing-dependent test failures
2. **Non-deterministic command filtering**: Command filtering doesn't consistently return the same results for the same input - exact matches aren't always returned first
3. **Standalone command execution issue**: Standalone commands (entered as the only text in input) should execute immediately when Enter is pressed, but this behavior is coupled to UI component state

## Required Behavior

Implement the following behaviors to fix the race conditions:

### 1. Synchronous CLI-only command initialization

CLI-only commands must be available immediately at initialization time, before any async fetch completes. Provide a function that creates these commands synchronously and export it for use by the UI components.

### 2. Standalone slash command detection

When a user types only a slash command (like `/q` or `/exit`) with no other text, the system should detect this as a standalone command. The implementation must:
- Extract the slash command name from input that contains only a command
- Distinguish between standalone commands (just `/q`) and commands with arguments (`/q something`)

### 3. Standalone command execution conditions

The system needs logic to determine when a standalone slash command should execute. This requires:
- Detecting whether a standalone command was detected in the input
- Checking whether the slash command menu/suggestions UI is visible (commands should NOT auto-execute when the menu is open)
- Checking the input text value

Define an interface that captures these state properties for the execution decision logic.

### 4. Deterministic command filtering

The `filterCommands` function must return consistent, deterministic results regardless of how many times it's called with the same input. The filtering should:
- Prioritize exact matches (commands whose names exactly match the input) before any other matches
- Then consider prefix matches (commands that start with the input)
- Apply fuzzy matching only to the remaining commands that weren't exact or prefix matches
- Return results in a defined order: exact matches first, then prefix matches, then fuzzy matches

### 5. ChatView integration

Update `cli/src/components/ChatView.tsx` to:
- Initialize slash command state synchronously at component mount time, not after an async fetch
- Handle standalone slash commands that are entered as the only input text
- Extract command handling logic into a reusable function for clarity

### 6. Test updates

Create a new test file at `cli/src/utils/slash-commands.test.ts` with unit tests covering:
- Exact match prioritization in command filtering
- Prefix match prioritization in command filtering
- Standalone execution logic that respects menu visibility state
- The standalone command execution decision function

Update `cli/src/components/QuitCommand.test.tsx` to:
- Replace timing-dependent integration tests that render the full ChatView component with unit tests
- Add unit tests for standalone slash command detection that verify `/q` and `/exit` are recognized as standalone commands
- Add unit tests for the command filtering logic

## Files to modify

- `cli/src/utils/slash-commands.ts` - Core utility functions
- `cli/src/components/ChatView.tsx` - Component that uses the utilities
- `cli/src/components/QuitCommand.test.tsx` - Test file with flaky integration tests
- Create `cli/src/utils/slash-commands.test.ts` - New unit test file