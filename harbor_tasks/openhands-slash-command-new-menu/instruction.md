# Add /new to Slash Command Menu for V1 Conversations

## Problem

The `/new` slash command exists and works when typed manually, but it doesn't appear in the slash command menu. Users have no visual way to discover this command - they can only learn about it through documentation or release notes.

The slash command menu is controlled by the `useSlashCommand` hook in `frontend/src/hooks/chat/use-slash-command.ts`. Currently, it only shows skills from the `useConversationSkills` hook.

## What You Need to Do

Add the `/new` command to the slash command menu, but **only for V1 conversations**. The command should not appear for V0 conversations.

### Key Requirements

1. **Check conversation version**: Use the `useActiveConversation` hook to get the current conversation. Only show `/new` when `conversation?.conversation_version === "V1"`.

2. **Define built-in commands**: Add a `BUILT_IN_COMMANDS` constant in `frontend/src/utils/constants.ts` containing the `/new` command definition. It should follow the `SlashCommandItem` type structure.

3. **Handle loading state**: Check `isSkillsLoading` from `useConversationSkills` and return empty items while loading. This prevents a "staggered menu" bug where commands appear one at a time.

4. **Update useMemo dependencies**: The `slashItems` useMemo hook needs to depend on the new variables: `skills`, `isV1Conversation`, and `isSkillsLoading`.

### Files to Modify

- `frontend/src/utils/constants.ts` - Add `BUILT_IN_COMMANDS` export with `/new` command
- `frontend/src/hooks/chat/use-slash-command.ts` - Import new dependencies, add V1 check, handle loading state

### Test File (Optional Reference)

The expected behavior is documented in test file at `frontend/__tests__/hooks/chat/use-slash-command.test.ts`:
- Test 1: `/new` appears for V1 conversations
- Test 2: Menu is empty while skills loading
- Test 3: `/new` does NOT appear for V0 conversations

## Verification

After making changes, run the tests:
```bash
cd frontend
npm run test -- use-slash-command
npm run typecheck
npm run lint
```

All tests, typecheck, and linting must pass.
