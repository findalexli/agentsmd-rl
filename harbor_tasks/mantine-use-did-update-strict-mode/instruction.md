# Fix useDidUpdate running on mount in React Strict Mode

## Problem

The `useDidUpdate` hook in `@mantine/hooks` is incorrectly running its callback on mount when used inside React's Strict Mode during development. This hook is meant to run effects only when dependencies update, NOT on the initial mount.

## Expected Behavior

- `useDidUpdate` should only execute the callback when dependencies change after the initial mount
- It should NOT run the callback on initial mount
- It should work correctly in React Strict Mode (which double-invokes effects in development)

## Actual Behavior

- In React Strict Mode during development, the hook's callback is being executed on mount
- This happens because React Strict Mode intentionally double-invokes effects to help detect side effects
- The hook's `mounted` ref is not being reset when the component unmounts during the Strict Mode simulation

## Where to Find the Code

The hook is located at:
```
packages/@mantine/hooks/src/use-did-update/use-did-update.ts
```

## What You Need to Do

Fix the `useDidUpdate` hook to handle React Strict Mode correctly. The hook needs to:

1. Add proper cleanup handling that resets the `mounted` ref when the component unmounts
2. This ensures that when React Strict Mode simulates a remount, the hook correctly identifies it as a fresh mount (not an update)

The fix involves:
- Adding a separate `useEffect` that runs only on mount/unmount (empty dependency array)
- This effect should return a cleanup function that sets `mounted.current = false`
- The main effect should explicitly return `undefined` after setting `mounted.current = true` to ensure consistent return types

## Key Points

- The hook uses a ref (`mounted`) to track whether the component has mounted
- The bug is that this ref stays `true` after the first mount, even when Strict Mode simulates an unmount/remount
- The fix ensures the ref is reset to `false` on unmount, so the remount is correctly treated as a fresh mount
- Do NOT change the public API of the hook (function signature should remain the same)
- Do NOT add new dependencies or imports beyond what's needed for the fix

## Testing

After making changes, verify:
1. The TypeScript code compiles without errors
2. The hook structure follows the pattern described above
3. The fix specifically handles the React Strict Mode scenario
