# Fix Runtime Crash in Hooks Viewer Modal

## Problem

The hooks viewer modal crashes with the error `Cannot read properties of undefined (reading 'length')` when the API returns a `HookMatcher` object where the `hooks` field is `undefined` (instead of an empty array).

This occurs when the agent finishes but workspace hooks are still executing on the server. The crash happens in the frontend at two locations that access `matcher.hooks.length` and `matcher.hooks.map(...)` without null guards.

## Affected Files

1. `frontend/src/components/features/conversation-panel/hook-event-item.tsx` - Line accessing `matcher.hooks.length`
2. `frontend/src/components/features/conversation-panel/hook-matcher-content.tsx` - Line accessing `matcher.hooks.map(...)`
3. `frontend/src/api/conversation-service/v1-conversation-service.types.ts` - Type definition for `HookMatcher`

## Requirements

1. **Fix the crash**: Add null guards so the components gracefully handle undefined `hooks` data
2. **Update the type**: The `HookMatcher` interface should reflect that `hooks` may be undefined
3. **Follow repo conventions**: Run linting and type checking as specified in `AGENTS.md`

## Expected Behavior

- Components should render without crashing when `hooks` is undefined
- The UI should display "0 hooks" when no hooks are defined
- All existing tests should continue to pass
