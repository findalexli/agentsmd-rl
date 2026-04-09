# Fix User Actions Popup Menu Display

## Problem

In the OpenHands OSS version, the user actions popup menu in the sidebar does not display when the user is not logged in. This is a regression - the menu should be visible even for unauthenticated users in OSS mode.

## What You Need to Fix

The `UserActions` component in `frontend/src/components/features/sidebar/user-actions.tsx` currently uses a hook `useShouldShowUserFeatures` to conditionally render the user context menu. This causes the menu to be hidden when the user is not authenticated.

**Your task is to:**
1. Remove the `useShouldShowUserFeatures` hook usage
2. Make the `UserContextMenu` always render (remove the conditional `{shouldShowUserActions && user && (...)}` wrapper)
3. Ensure the context menu wrapper div is always present in the DOM

## Expected Behavior

- The user actions popup menu should display regardless of authentication state
- The menu should appear on hover/click of the user avatar area
- The fix should be minimal - only remove the conditional rendering logic

## Testing

After making changes:
1. Run `cd frontend && npm run lint:fix` to ensure code passes lint
2. Run `cd frontend && npm run build` to verify TypeScript compiles

## Hints

- Look for where `useShouldShowUserFeatures` is imported and used
- The context menu is wrapped in a conditional that checks both `shouldShowUserActions` and `user`
- The fix is about removing a restriction, not adding new logic
