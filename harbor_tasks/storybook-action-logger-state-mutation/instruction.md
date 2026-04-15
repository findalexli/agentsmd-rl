# Actions: ActionLogger drops newest actions when limit is reached

## Problem

The ActionLogger panel in the Storybook UI has incorrect behavior when the number of logged actions exceeds the configured limit:

1. **Wrong actions retained**: When the limit is exceeded, the panel drops the newest actions and keeps the oldest. For example, if the limit is 3 and you trigger 5 different actions, you see actions 1-3 instead of actions 3-5.

2. **Stale counts for repeated actions**: When the same action is fired repeatedly in quick succession, the displayed count may not update correctly and React may skip re-renders.

## Expected Behavior

- The panel should always show the most recent actions, discarding the oldest when the limit is reached. When the limit is 3 and 5 actions are triggered, the panel should display actions 3-5 (the last 3 actions based on `slice(-limit)` behavior).
- Repeated action counts should update reliably on each occurrence. When a duplicate action is detected, the count should be incremented immutably (e.g., `previous.count + 1`).
- State updates must follow React's immutability contract — the handler must not modify existing state objects or incoming action objects in place. The implementation must correctly handle cases where objects are frozen (via `Object.freeze`).

## Constraints

- Locate the ActionLogger component source file. It must be exported as `export default function ActionLogger`.
- The action objects passed to the handler contain these fields:
  - `id`: string identifier for the action
  - `data`: object containing `name` (string) and `args` (array)
  - `count`: number (starts at 0, should be set to 1 for new actions)
  - `options`: object containing `limit` (number, default 50) and `clearOnStoryChange` (boolean)
- The modified TypeScript file must pass formatting checks via `oxfmt --check`.
- The code must not mutate frozen objects (use immutable update patterns like object spreading: `{ ...action, count: 1 }` and array spreading: `[...prevActions, newAction]`).
