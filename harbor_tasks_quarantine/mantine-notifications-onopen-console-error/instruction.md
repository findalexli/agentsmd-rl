# Fix "Unknown event handler property `onOpen`" Console Error

## Problem

When calling `notifications.show({ onOpen: () => {} })`, a React warning appears in the console:

```
Warning: Unknown event handler property `onOpen`. It will be ignored.
```

The `onOpen` callback should fire when a notification is mounted, but instead it triggers this React warning because `onOpen` is being forwarded to a DOM element.

## File to Investigate

- `packages/@mantine/notifications/src/NotificationContainer.tsx`

## Expected Behavior

- `onOpen` must not be forwarded to the DOM — it should be consumed before the rest-spread, following the same destructuring convention already used for `autoClose` (which is aliased as `autoClose: _autoClose`). The `onOpen` property must be aliased as `onOpen: _onOpen` to match this convention.
- The existing `data.onOpen` invocation in `useEffect` must be preserved — `onOpen` should still be called via `data.onOpen` when the notification mounts.
- `onClose` callback should continue to fire when notification unmounts (already working).
- No React warnings about unknown event handler properties should be emitted.

## Testing

The repository has tests in `packages/@mantine/notifications/src/Notifications.test.tsx`. Run tests with:

```bash
npx jest packages/@mantine/notifications/src/Notifications.test.tsx
```

You should also run type checking:

```bash
npx tsc --noEmit
```

## Constraints

- Follow the existing code style in the repository
- Do not add inline comments explaining the change
- Preserve existing functionality for all other props
