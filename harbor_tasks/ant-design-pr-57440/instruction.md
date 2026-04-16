# Typography Actions Placement Feature

The Typography component currently renders action buttons (copy, edit, expand/collapse) at the end of the text content. Users need the ability to position these action buttons at the start of the text instead.

## Current Behavior

Action buttons always appear after the text content. There is no way to configure their position.

## Desired Behavior

1. **Configuration Interface**: Add a new exported interface named `ActionsConfig` from `components/typography/Base/index.tsx` that allows configuring action button placement. It should support a `placement` property with two possible values: `'start'` or `'end'`.

2. **BlockProps Integration**: The `BlockProps` interface in `components/typography/Base/index.tsx` should accept an `actions` prop typed with the `ActionsConfig` interface.

3. **Placement Options**: The action bar should support two placement modes:
   - `'end'` - actions appear after text (current default behavior, should remain the default)
   - `'start'` - actions appear before text

4. **Visual Distinction**: When placement is set to `'start'`, the component must apply a distinguishable CSS class to the actions container (following the pattern `${prefixCls}-actions-start`) so that styles can target this state.

5. **CSS Styling**: The styles in `components/typography/style/index.ts` must include appropriate styling for the start-positioned actions bar, using RTL-compatible margin properties (such as `marginInlineEnd` instead of `marginInlineStart`) to ensure proper spacing of action buttons when positioned at the start.

6. **Ellipsis Compatibility**: When combined with ellipsis functionality, changing the action bar placement must trigger re-measurement of the text. The `Ellipsis` component in `components/typography/Base/Ellipsis.tsx` must accept a `measureDeps` prop that allows passing dependencies for recalculation, and these dependencies should be incorporated into the measurement logic using spread syntax.

## Files to Modify

- `components/typography/Base/index.tsx` - Main Typography Base component
- `components/typography/Base/Ellipsis.tsx` - Ellipsis measurement component
- `components/typography/style/index.ts` - Typography styles
