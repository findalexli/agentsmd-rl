# Add `/new` to Slash Command Menu for V1 Conversations

## Problem

The `/new` command allows users to create a new conversation while preserving the existing runtime/sandbox. However, this command is not discoverable in the slash command menu - users can only learn about it through documentation or release notes.

When a user types `/` in the chat input, they should see `/new` as an available option for V1 conversations (but not for V0 conversations). Additionally, the menu currently shows a staggered loading state where commands appear one by one while skills are still loading, which creates a jarring user experience.

## Required Behavior

1. **V1 conversations**: When a conversation has version "V1", typing `/` should show `/new` as an available built-in command. The test output should contain the string "includes /new built-in command for V1".

2. **V0 conversations**: When a conversation has version "V0", the `/new` command should NOT appear in the menu. The test output should contain the string "does NOT include /new".

3. **Loading state**: While skills are loading, the menu should return empty items to prevent a "staggered menu bug". The test output should contain the string "returns empty items while skills are loading".

## Testing Requirements

The following test file must exist:
- `frontend/__tests__/hooks/chat/use-slash-command.test.ts`

All frontend tests must pass, including tests with these specific descriptions:
- "includes /new built-in command for V1"
- "does NOT include /new"
- "returns empty items while skills are loading"

Additionally, the solution must pass:
- `npm run typecheck` - TypeScript type checking
- `npm run lint` - Linting checks
- `npm run build` - Production build
- `npm run test` - Unit tests

## Notes

- The fix should NOT change types, the menu component, or the `/new` handler in `chat-interface.tsx`
- The solution should be compatible with the existing slash command infrastructure and conversation version detection
