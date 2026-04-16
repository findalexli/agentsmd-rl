# Fix: User context menu not visible in OSS mode

## Bug Description

In the OpenHands repository, the user context menu popup does not appear for users in OSS mode (unauthenticated or without feature flags). The popup should appear on hover over the user avatar area, but it is completely absent from the DOM for these users instead of being present but hidden via CSS opacity transitions.

The relevant component is at `frontend/src/components/features/sidebar/user-actions.tsx`.

## Expected Behavior

After the fix, the component should behave as follows:

1. **Context menu always in the DOM**: The context menu popup must be present in the DOM for all users regardless of authentication state or feature flags. This means:
   - The `UserContextMenu` component must be rendered unconditionally with `key={menuResetCount}`.
   - It must be wrapped in a `<div>` that uses `className={cn(...)}` containing the exact opacity transition classes `"opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto"`.
   - There must be no conditional rendering guard (e.g., based on a variable like `shouldShowUserActions`) wrapping the context menu or its parent `<div>`.

2. **No feature-flag gating hook**: The file should not reference the hook `useShouldShowUserFeatures` anywhere — neither as an import nor as a call. The context menu visibility is handled purely through CSS, not through conditional removal from the DOM.

3. **Required imports preserved**: The component must still import and use:
   - `UserContextMenu` component
   - `useMe` hook

4. **Build passes**: TypeScript type checking, ESLint, and the frontend build must all pass without errors.

## Verification

After making changes, verify that all of the following pass (run in the `frontend` directory):

- TypeScript type checking: `npx tsc --noEmit`
- Linting: `npm run lint`
- Frontend build: `npm run build`
- Unit tests for `UserContextMenu` component
- Unit tests for `Sidebar` component
