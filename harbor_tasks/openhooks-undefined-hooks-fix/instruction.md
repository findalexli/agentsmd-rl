# Fix Runtime Crash in Hooks Modal

## Problem

The hooks viewer modal crashes with `Cannot read properties of undefined (reading 'length')` when the API returns a `HookMatcher` object where the `hooks` field is `undefined` instead of an empty array. This happens when the agent finishes but workspace hooks are still executing on the server.

## Affected Files

1. `frontend/src/components/features/conversation-panel/hook-event-item.tsx` - Accesses `matcher.hooks.length` in a `reduce()` call without null checking
2. `frontend/src/components/features/conversation-panel/hook-matcher-content.tsx` - Calls `matcher.hooks.map()` without null checking
3. `frontend/src/api/conversation-service/v1-conversation-service.types.ts` - Type definition doesn't reflect that `hooks` can be undefined

## What You Need to Do

Fix the runtime crash by handling the case where `matcher.hooks` is `undefined`. You should:

1. Update the TypeScript type definition to mark `hooks` as optional and add a comment explaining why
2. Add nullish coalescing (`?? []`) in both components where `matcher.hooks` is accessed

## Expected Behavior

- Components should gracefully handle `undefined` hooks data
- The UI should display "0 hooks" when hooks are undefined
- The expanded view should not crash when displaying matcher details
- TypeScript should compile without errors
- All frontend linting should pass

## Testing

The repository uses Vitest and React Testing Library for frontend testing. Run tests with `npm run test` in the frontend directory.
