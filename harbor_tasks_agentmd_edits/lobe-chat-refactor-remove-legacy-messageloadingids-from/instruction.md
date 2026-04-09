# Remove legacy messageLoadingIds from chat store

## Problem

The `messageLoadingIds` state and `internal_toggleMessageLoading` action in the chat store are legacy code that has been fully superseded by the operation system. This dead code adds unnecessary complexity:

- `messageLoadingIds` state is written to but never read by any consumer
- All UI components already use operation-based selectors (`isMessageGenerating`, `isMessageProcessing`, etc.)
- The `internal_toggleMessageLoading` action is called throughout the codebase but serves no purpose
- Dead selectors (`isHasMessageLoading`, `isSendButtonDisabledByMessage`) depend on the legacy state

The zustand skill documentation (`.agents/skills/zustand/SKILL.md`) still references these removed concepts, which could mislead developers.

## Expected Behavior

1. Remove `messageLoadingIds` from `ChatMessageState` interface and `initialMessageState`
2. Remove `internal_toggleMessageLoading` action from `MessageRuntimeStateActionImpl`
3. Simplify `isMessageLoading` selector to only use `operationSelectors.isMessageProcessing`
4. Remove dead selectors: `isHasMessageLoading` and `isSendButtonDisabledByMessage`
5. Clean up all call sites that reference `internal_toggleMessageLoading`:
   - `src/store/chat/slices/aiAgent/actions/agentGroup.ts`
   - `src/store/chat/slices/aiAgent/actions/runAgent.ts`
   - `src/store/chat/slices/aiChat/actions/conversationLifecycle.ts`
   - `src/store/chat/slices/message/actions/optimisticUpdate.ts`
   - `src/store/chat/slices/plugin/actions/optimisticUpdate.ts`
6. Update `src/features/Conversation/store/slices/generation/action.ts` to use `operationSelectors.isMessageProcessing` instead of checking `messageLoadingIds`
7. Update `.agents/skills/zustand/SKILL.md` to remove references to `messageLoadingIds` and `internal_toggleMessageLoading`
8. Update `.agents/skills/zustand/references/action-patterns.md` if it references these

## Files to Look At

- `src/store/chat/slices/message/initialState.ts` — Remove `messageLoadingIds` from state interface and initial value
- `src/store/chat/slices/message/actions/runtimeState.ts` — Remove `internal_toggleMessageLoading` action
- `src/store/chat/slices/message/selectors/messageState.ts` — Simplify `isMessageLoading`, remove dead selectors
- `src/store/chat/slices/aiAgent/actions/agentGroup.ts` — Remove calls to `internal_toggleMessageLoading`
- `src/store/chat/slices/aiAgent/actions/runAgent.ts` — Remove calls to `internal_toggleMessageLoading`
- `src/store/chat/slices/aiChat/actions/conversationLifecycle.ts` — Remove calls to `internal_toggleMessageLoading`
- `src/store/chat/slices/message/actions/optimisticUpdate.ts` — Remove calls to `internal_toggleMessageLoading`
- `src/store/chat/slices/plugin/actions/optimisticUpdate.ts` — Remove calls to `internal_toggleMessageLoading`
- `src/features/Conversation/store/slices/generation/action.ts` — Use `operationSelectors.isMessageProcessing`
- `.agents/skills/zustand/SKILL.md` — Remove references to removed state and actions
