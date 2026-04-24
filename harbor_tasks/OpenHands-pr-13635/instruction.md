# Fix: User context menu not visible in OSS mode

## Bug Description

In the OpenHands repository at `frontend/src/components/features/sidebar/user-actions.tsx`, the user context menu popup does not appear for users in OSS mode (unauthenticated or without feature flags). The popup should appear on hover over the user avatar area in the sidebar, but it is completely absent from the DOM for these users instead of being present but hidden via CSS.

The component currently uses a hook that conditionally gates user feature visibility. Due to this gating, `<UserContextMenu>` is not rendered at all for OSS users — the component is removed from the DOM rather than being hidden via CSS.

## Expected Behavior

After the fix:

1. **Context menu always in the DOM**: The `UserContextMenu` component at `frontend/src/components/features/sidebar/user-actions.tsx` must be present in the DOM for all users regardless of authentication state. The visibility should be controlled through CSS (using `opacity`, `pointer-events`, and Tailwind's `group-hover:` pattern), not by conditional removal from the DOM.

2. **CSS-controlled visibility**: When the user hovers over the avatar area (near the `<UserAvatar>` component), the context menu should become visible through CSS hover states. When not hovered, it should be hidden via CSS `opacity` and `pointer-events` rather than removed from the DOM.

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

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
