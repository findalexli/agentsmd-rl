# Typography Actions Placement Feature

The Typography component currently renders action buttons (copy, edit, expand/collapse) at the end of the text content. Users need the ability to position these action buttons at the start of the text instead.

## Current Behavior

Action buttons always appear after the text content. There is no way to configure their position.

## Desired Behavior

1. **Configuration Interface**: Add a new exported interface named `ActionsConfig` that allows configuring action button placement. It should support a `placement` property with two possible values: `'start'` or `'end'`.

2. **BlockProps Integration**: The `BlockProps` interface should accept an `actions` prop typed with the `ActionsConfig` interface.

3. **Placement Options**: The action bar should support two placement modes:
   - `'end'` - actions appear after text (current default behavior, should remain the default)
   - `'start'` - actions appear before text

4. **Visual Distinction**: When placement is set to `'start'`, the component must apply a distinguishable CSS class to the actions container so that styles can target this state.

5. **CSS Styling**: The styles must include appropriate styling for the start-positioned actions bar, using RTL-compatible logical margin properties to ensure proper spacing of action buttons when positioned at the start.

6. **Ellipsis Compatibility**: When combined with ellipsis functionality, changing the action bar placement must trigger re-measurement of the text. The `Ellipsis` component must accept a dedicated dependency list for changes that affect content layout measurement (distinct from other miscellaneous dependencies that don't affect layout).

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
