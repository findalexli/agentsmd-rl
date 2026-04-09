# Add `/new` to Slash Command Menu for V1 Conversations

## Problem

The `/new` command allows users to create a new conversation while preserving the existing runtime/sandbox. However, this command is not discoverable in the slash command menu - users can only learn about it through documentation or release notes.

You need to add `/new` to the slash command menu so users can discover it alongside other slash commands.

## Relevant Files

- `frontend/src/hooks/chat/use-slash-command.ts` - Hook that manages slash command items
- `frontend/src/utils/constants.ts` - Constants file where built-in commands should be defined

## Requirements

1. **V1 conversations only**: The `/new` command should only appear for V1 conversations (not V0). Use the conversation version to gate this.

2. **Built-in commands**: Define a `BUILT_IN_COMMANDS` array in `frontend/src/utils/constants.ts` with `/new` as a standard `SlashCommandItem`. The command should:
   - Have name: "new"
   - Have type: "agentskills"
   - Have content: "Creates a new conversation using the same runtime"
   - Have triggers: ["/new"]
   - Have command: "/new"

3. **Loading state**: Ensure the menu returns empty items while skills are still loading to prevent a "staggered menu bug" where commands appear one by one.

4. **Merge built-in commands**: Modify the `useSlashCommand` hook to merge built-in commands into the existing `slashItems` memo for V1 conversations.

## Testing

Run tests with `npm run test` in the `frontend` directory. The key tests are:
- `/new` appears in filteredItems for V1 conversations
- `/new` does NOT appear for V0 conversations
- Empty items are returned while skills are loading

Also ensure `npm run typecheck` and `npm run lint` pass.

## Notes

- The PR that implements this should NOT change types, the menu component, or the `/new` handler in `chat-interface.tsx`
- The `useActiveConversation` hook can provide the conversation version
- The `useConversationSkills` hook provides `isLoading` state for the loading check
