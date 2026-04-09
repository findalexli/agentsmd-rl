# Actions: ActionLogger drops newest actions when limit is reached

## Problem

The ActionLogger panel in the Storybook UI has incorrect behavior when the number of logged actions exceeds the configured limit:

1. **Wrong actions retained**: When the limit is exceeded, the panel drops the newest actions and keeps the oldest. For example, if the limit is 3 and you trigger 5 different actions, you see actions 1-3 instead of actions 3-5.

2. **Stale counts for repeated actions**: When the same action is fired repeatedly in quick succession, the displayed count may not update correctly and React may skip re-renders. The state updater in the `addAction` handler has issues with how it manages state references.

## Expected Behavior

- The panel should always show the most recent actions, discarding the oldest when the limit is reached.
- Repeated action counts should update reliably on each occurrence.
- State updates should follow React's immutability contract — the handler should not modify existing state objects or incoming action objects in place.

## Files to Look At

- `code/core/src/actions/containers/ActionLogger/index.tsx` — the ActionLogger container component that manages the actions list via React state
