# Actions: ActionLogger drops newest actions when limit is reached

## Problem

The `ActionLogger` component in the Storybook UI has three bugs in its `addAction` callback's state update logic.

### Bug 1: Wrong actions retained when limit is exceeded

When the number of logged actions exceeds the configured limit, the panel discards the newest actions and keeps the oldest. For example:
- With `limit=3` and 5 unique actions triggered (a0 through a4), the panel shows a0, a1, a2 instead of the 3 most recent: a2, a3, a4.
- With `limit=2` and 4 unique actions, the panel should show the last 2, not the first 2.
- With `limit=1` and 3 unique actions, the panel should show only the last action.

The panel should always retain the **newest** actions and discard the oldest when the limit is reached.

### Bug 2: State mutation when incrementing duplicate action count

When the same action is fired repeatedly (duplicates are detected via deep equality on the `data` field), the handler directly mutates the existing state object to increment `count`. This violates React's immutability contract. If previous state objects are frozen (via `Object.freeze`), this mutation throws a `TypeError`.

The duplicate-action path must produce a new state array with a new copy of the matched action whose `count` is incremented (e.g., if the previous count was 1, the updated copy should have count 2). The original state objects must remain unchanged.

### Bug 3: Mutation of the incoming action object

When a new (non-duplicate) action is added, the handler directly mutates the incoming `action` object (setting its `count` property in place). If the input action is frozen, this throws a `TypeError`.

The handler must not modify the incoming action object. It should create a new object with `count` set to `1` for newly added actions (incoming actions arrive with `count: 0`).

## File to modify

- **Path**: `code/core/src/actions/containers/ActionLogger/index.tsx`
- The component is exported as `export default function ActionLogger`.
- The fix is within the `addAction` callback, which calls `setActions` to update React state.

## Action object shape

The action objects passed to the handler have these fields:
- `id`: string identifier
- `data`: object containing `name` (string) and `args` (array)
- `count`: number (arrives as `0`; should become `1` for newly added actions)
- `options`: object containing `limit` (number, default 50) and `clearOnStoryChange` (boolean)

## Validation requirements

The modified file must:

1. **Pass TypeScript typecheck**: `yarn nx run core:check`
2. **Pass formatting**: `yarn exec oxfmt --check code/core/src/actions/containers/ActionLogger/index.tsx`
3. **Pass compilation**: `yarn nx compile core`
4. **Pass existing unit tests**: `yarn test code/core/src/actions/addArgsHelpers.test.ts`
5. **Use explicit file extensions** in all relative imports (`.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`), per project convention.
6. **Contain valid syntax** with balanced braces.
